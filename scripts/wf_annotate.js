export const meta = {
  name: 'annotate-spim-yardstick-claims',
  description: 'Research each SPI-M-O yardstick claim for resolvability; verify citations support the arguments',
  phases: [
    { title: 'Annotate', detail: 'research each claim: arguments for/against resolvability, evidence, blind coding' },
    { title: 'Verify', detail: 'adversarially check each citation actually supports what it is cited for' },
  ],
}

// The claims are passed in as the workflow's args: the coding frame, data/coding_frame_dedup.csv. They carry the
// withheld bands, so they are kept out of the repository.
const CLAIMS = args;

const ANNOT = {
  type: 'object',
  required: ['resolvable','argument_for','argument_against','resolve_against','likely_outcome','outcome_reason','evidence','confidence'],
  properties: {
    resolvable:       { type: 'string', enum: ['Y','N','MARGINAL'] },
    argument_for:     { type: 'string', description: 'strongest case it CAN be scored, <60 words' },
    argument_against: { type: 'string', description: 'strongest case it CANNOT be scored, <60 words' },
    resolve_against:  { type: 'string', description: 'what specific data/source would settle it, <40 words' },
    likely_outcome:   { type: 'string', enum: ['TRUE','FALSE','AMBIGUOUS'] },
    outcome_reason:   { type: 'string', description: 'one line' },
    evidence:         { type: 'array', maxItems: 3, items: { type: 'object', required: ['url','note'],
                        properties: { url: {type:'string'}, note: {type:'string'} } } },
    confidence:       { type: 'string', enum: ['high','medium','low'] },
  },
};

const VERIFY = {
  type: 'object',
  required: ['citations_support','verdict','issues'],
  properties: {
    citations_support: { type: 'boolean', description: 'do the cited sources actually support the arguments made?' },
    verdict:           { type: 'string', enum: ['CONFIRMED','OVERSTATED','UNSUPPORTED'] },
    issues:            { type: 'string', description: 'what is wrong, or "none", <50 words' },
    dead_urls:         { type: 'array', items: { type: 'string' } },
  },
};

function annotPrompt(c) {
  return `You are assessing whether a probability statement made by the UK's SPI-M-O committee during COVID-19 can be empirically resolved (scored true/false) in hindsight. This feeds a real academic study; a fabricated citation would invalidate it.

CLAIM ${c.claim_id}, from "${c.statement}" (${c.date}):
"${c.sentence}"
Yardstick term: "${c.term}" = ${c.band} probability.

RESOLVABLE means: evidence exists, INDEPENDENT OF EPIDEMIOLOGICAL MODELLING, that settles whether the claim is true.
- A claim about a LATENT quantity estimable only via a model (reproduction number R, true infection prevalence/incidence, transmissibility advantage, attack rate) is NOT resolvable — scoring it means scoring a model against a model. This is the single most important test. Apply it strictly.
- A COUNTERFACTUAL claim (about an intervention contrast never actually run, or "without further measures") is NOT resolvable.
- A claim with an unthresholded magnitude word ("substantial", "highly limited", "significant") may be unresolvable for vagueness — judge whether a direction alone could settle it.
- A claim that is a methodological aside or figure caption rather than an assertion about the world is NOT resolvable.
- Claims about MEASURED outcomes (deaths, hospitalisations, reported cases, test positivity) against MEASURED comparators are the strongest candidates.

RULES:
- Use WebSearch/WebFetch for real evidence. NEVER fabricate a URL, statistic, paper title or author. Only cite URLs you actually fetched successfully.
- If evidence is ambiguous or contested, say so. Do NOT manufacture a clean answer. AMBIGUOUS and low confidence are correct answers when warranted.
- Be sceptical. Do not strain to make a claim resolvable. Most claims in this corpus are NOT cleanly resolvable; a high rate of N/MARGINAL is expected and correct.
- argument_for and argument_against must BOTH be genuine. Do not write a strawman for the side you disagree with.

Return the structured object. No preamble.`;
}

function verifyPrompt(c, a) {
  return `You are adversarially auditing a research annotation for a real academic study. Your job is to find problems, not to agree.

THE CLAIM (${c.claim_id}, ${c.date}): "${c.sentence}"
Yardstick term "${c.term}" = ${c.band}.

THE ANNOTATION TO AUDIT:
  resolvable: ${a.resolvable}
  argument_for: ${a.argument_for}
  argument_against: ${a.argument_against}
  likely_outcome: ${a.likely_outcome} — ${a.outcome_reason}
  evidence: ${JSON.stringify(a.evidence)}

Check, using WebFetch on each cited URL:
1. Does each URL resolve? (A 403 from a publisher bot-blocker is NOT a dead link — judge by whether the URL is a real article.)
2. Does each source ACTUALLY SAY what it is cited for? "The URL exists" and "the URL supports the argument" are different tests. Only the second matters.
3. Is the resolvable verdict defensible, especially the latent-quantity test? If the claim is about R, prevalence, incidence, transmissibility or attack rate, resolvable should almost certainly be N — flag it if it isn't.
4. Is likely_outcome overstated relative to the evidence actually cited?

verdict: CONFIRMED (citations support the arguments), OVERSTATED (sources real but claims go beyond them), UNSUPPORTED (sources do not support, or are fabricated).
Default to OVERSTATED or UNSUPPORTED if you cannot verify. Do not rubber-stamp.

Return the structured object. No preamble.`;
}

log(`annotating ${CLAIMS.length} claims`);

const results = await pipeline(
  CLAIMS,
  (c) => agent(annotPrompt(c), { label: `annot:${c.claim_id}`, phase: 'Annotate', schema: ANNOT, model: 'sonnet' }),
  (a, c) => {
    if (!a) return null;
    return agent(verifyPrompt(c, a), { label: `verify:${c.claim_id}`, phase: 'Verify', schema: VERIFY, model: 'sonnet' })
      .then((v) => ({ claim_id: c.claim_id, ...a, verify_verdict: v ? v.verdict : 'NOT_VERIFIED',
                      verify_issues: v ? v.issues : '', citations_support: v ? v.citations_support : null }))
      .catch(() => ({ claim_id: c.claim_id, ...a, verify_verdict: 'NOT_VERIFIED', verify_issues: 'verify agent failed', citations_support: null }));
  }
);

const ok = results.filter(Boolean);
log(`done: ${ok.length}/${CLAIMS.length} annotated`);
return ok;
