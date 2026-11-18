export const meta = {
  name: 'annotate-spim-neutral-v2',
  description: 'Re-annotate SPI-M yardstick claims with a neutral prompt, plus synthetic controls to test whether the annotator can output FALSE',
  phases: [
    { title: 'Annotate', detail: 'neutral-prompt resolvability + outcome coding' },
    { title: 'Verify', detail: 'adversarial citation audit' },
  ],
}

// The claims are passed in as the workflow's args: the rows of the coding frame (data/coding_frame_dedup.csv, with
// first_date renamed to date and kind set to "real") plus the first-version controls. They carry the
// withheld bands, so they are kept out of the repository.
const CLAIMS = args;

const ANNOT = {
  type: 'object',
  required: ['resolvable','argument_for','argument_against','resolve_against','outcome','outcome_reason','evidence','confidence'],
  properties: {
    resolvable:       { type: 'string', enum: ['Y','N','MARGINAL'] },
    argument_for:     { type: 'string', description: 'strongest case it CAN be scored, <60 words' },
    argument_against: { type: 'string', description: 'strongest case it CANNOT be scored, <60 words' },
    resolve_against:  { type: 'string', description: 'what data/source would settle it, <40 words' },
    outcome:          { type: 'string', enum: ['TRUE','FALSE','AMBIGUOUS'] },
    outcome_reason:   { type: 'string' },
    evidence:         { type: 'array', maxItems: 3, items: { type: 'object', required: ['url','note'],
                        properties: { url: {type:'string'}, note: {type:'string'} } } },
    confidence:       { type: 'string', enum: ['high','medium','low'] },
  },
};
const VERIFY = {
  type: 'object',
  required: ['citations_support','verdict','issues'],
  properties: {
    citations_support: { type: 'boolean' },
    verdict:           { type: 'string', enum: ['CONFIRMED','OVERSTATED','UNSUPPORTED'] },
    issues:            { type: 'string' },
  },
};

function annotPrompt(c) {
  return `You are assessing a probability statement about COVID-19 epidemiology, dated ${c.date}. This feeds a real academic study; a fabricated citation would invalidate it.

CLAIM ${c.claim_id}:
"${c.sentence}"
Probability term used: "${c.term}" = ${c.band}.

TASK 1 — is the claim RESOLVABLE?
RESOLVABLE means evidence exists, independent of epidemiological modelling, that settles whether it is true.
- A claim about a quantity estimable only via a model (reproduction number R, true infection prevalence or incidence, transmissibility advantage, attack rate) is not resolvable: scoring it would mean scoring one model against another.
- A claim about an intervention contrast that was never actually run is not resolvable.
- A claim whose key term has no threshold ("substantial", "highly limited") may be unresolvable for vagueness. Judge whether direction alone could settle it.
- A claim about measured outcomes (deaths, hospital admissions, reported cases, test positivity) against measured comparators is more likely resolvable.
Judge each claim on its own merits. Do not assume any particular rate of Y or N — some claims are resolvable and some are not.

TASK 2 — what was the OUTCOME?
TRUE, FALSE and AMBIGUOUS are all equally valid and equally expected verdicts.
- Score FALSE when the evidence shows the claim did not hold. Claims made under uncertainty are sometimes wrong; finding that a claim was wrong is a correct and useful result, not a failure.
- Score TRUE when the evidence shows it held.
- Score AMBIGUOUS only when the evidence genuinely cannot settle it — not as a way to avoid committing.
- Do not treat the claim's source as authoritative. Assess only what the evidence shows.
- If the claim is not resolvable, outcome is normally AMBIGUOUS.

RULES:
- Use WebSearch/WebFetch for real evidence. NEVER fabricate a URL, statistic, paper title or author. Cite only URLs you actually fetched.
- Every cited source must actually support the specific point you cite it for. Do not overstate what a source says.
- argument_for and argument_against must both be genuine; no strawmen.

Return the structured object. No preamble.`;
}

function verifyPrompt(c, a) {
  return `You are adversarially auditing a research annotation. Find problems; do not rubber-stamp.

CLAIM (${c.claim_id}, ${c.date}): "${c.sentence}"  [term "${c.term}" = ${c.band}]

ANNOTATION:
  resolvable: ${a.resolvable}
  argument_for: ${a.argument_for}
  argument_against: ${a.argument_against}
  outcome: ${a.outcome} — ${a.outcome_reason}
  evidence: ${JSON.stringify(a.evidence)}

Using WebFetch on each cited URL, check:
1. Does the URL resolve? (A publisher 403 bot-block is NOT a dead link.)
2. Does each source ACTUALLY SAY what it is cited for? "Exists" and "supports the argument" are different tests; only the second matters.
3. Is the resolvable verdict defensible? If the claim is about R, prevalence, incidence, transmissibility or attack rate, resolvable should almost certainly be N.
4. Is the outcome overstated relative to the cited evidence? Check both directions: an unjustified FALSE is as bad as an unjustified TRUE.

verdict: CONFIRMED / OVERSTATED / UNSUPPORTED. Default to OVERSTATED or UNSUPPORTED if you cannot verify.
Return the structured object. No preamble.`;
}

log(`annotating ${CLAIMS.length} claims (${CLAIMS.filter(c=>c.kind==='real').length} real + ${CLAIMS.filter(c=>c.kind==='control').length} controls)`);

const results = await pipeline(
  CLAIMS,
  (c) => agent(annotPrompt(c), { label: `annot:${c.claim_id}`, phase: 'Annotate', schema: ANNOT, model: 'sonnet' }),
  (a, c) => {
    if (!a) return null;
    return agent(verifyPrompt(c, a), { label: `verify:${c.claim_id}`, phase: 'Verify', schema: VERIFY, model: 'sonnet' })
      .then((v) => ({ claim_id: c.claim_id, kind: c.kind, ...a,
                      verify_verdict: v ? v.verdict : 'NOT_VERIFIED',
                      verify_issues: v ? v.issues : '',
                      citations_support: v ? v.citations_support : null }))
      .catch(() => ({ claim_id: c.claim_id, kind: c.kind, ...a, verify_verdict: 'NOT_VERIFIED', verify_issues: 'verify failed', citations_support: null }));
  }
);
const ok = results.filter(Boolean);
log(`done: ${ok.length}/${CLAIMS.length}`);
return ok;
