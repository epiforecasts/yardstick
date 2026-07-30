import csv, json

rows = list(csv.DictReader(open("data/coding_frame_dedup.csv", encoding="utf-8")))
real = [{"claim_id": r["claim_id"], "date": r["first_date"], "term": r["term"],
         "band": r["band"], "sentence": r["sentence"], "kind": "real"} for r in rows]

# ---- SYNTHETIC CONTROLS -- NOT SPI-M QUOTES. Negations/affirmations of established facts.
# Purpose: can the annotator output FALSE at all, and does it over-fire?
controls = [
 ("X01","2020-02-10","almost certain","95-<100%","It is almost certain that the average case fatality ratio of COVID-19 exceeds that of SARS.","FALSE"),
 ("X02","2020-03-02","highly likely","80-90%","It is highly likely that the epidemic in Wuhan is still growing.","FALSE"),
 ("X03","2021-12-22","likely","55-75%","It is likely that the intrinsic hospitalisation rate of omicron is higher than that of delta.","FALSE"),
 ("X04","2021-05-12","highly likely","80-90%","It is highly likely that B.1.617.2 is less transmissible than B.1.1.7.","FALSE"),
 ("X05","2021-12-15","almost certain","95-<100%","It is almost certain that data on hospital admissions are reported with no delay.","FALSE"),
 ("X06","2021-09-08","highly likely","80-90%","It is highly likely that the age distribution of cases will remain unchanged following the return of children to schools.","FALSE"),
 ("X07","2021-11-24","likely","55-75%","It is likely that contact patterns remain unchanged during the festive period.","FALSE"),
 ("X08","2021-06-16","almost certain","95-<100%","It is almost certain that vaccination has no effect on the transmission of SARS-CoV-2.","FALSE"),
 ("X09","2020-09-02","highly likely","80-90%","It is highly likely that COVID-19 mortality is concentrated in children under ten years of age.","FALSE"),
 ("X10","2020-06-10","likely","55-75%","It is likely that the UK epidemic peaked in January 2020.","FALSE"),
 ("X11","2021-12-22","almost certain","95-<100%","It is almost certain that omicron is less transmissible than delta.","FALSE"),
 ("X12","2020-04-01","highly likely","80-90%","It is highly likely that no sustained community transmission of COVID-19 occurred in the UK during March 2020.","FALSE"),
 ("Y01","2020-09-02","almost certain","95-<100%","It is almost certain that the risk of death from COVID-19 increases with age.","TRUE"),
 ("Y02","2021-01-06","highly likely","80-90%","It is highly likely that the UK experienced a substantial wave of COVID-19 hospital admissions during winter 2020 to 2021.","TRUE"),
 ("Y03","2021-12-22","likely","55-75%","It is likely that omicron spread more rapidly in the UK than delta did.","TRUE"),
 ("Y04","2020-03-02","highly likely","80-90%","It is highly likely that COVID-19 transmits from person to person.","TRUE"),
 ("Y05","2021-05-12","likely","55-75%","It is likely that COVID-19 vaccines reduce the risk of hospitalisation.","TRUE"),
 ("Y06","2020-10-08","highly likely","80-90%","It is highly likely that reported COVID-19 deaths in England increased between October and December 2020.","TRUE"),
]
ctrl = [{"claim_id":c[0],"date":c[1],"term":c[2],"band":c[3],"sentence":c[4],
         "kind":"control","truth":c[5]} for c in controls]
json.dump(ctrl, open("data/controls_key.json","w"), indent=1)

ALL = real + [{k:v for k,v in c.items() if k!="truth"} for c in ctrl]

js = '''export const meta = {
  name: 'annotate-spim-neutral-v2',
  description: 'Re-annotate SPI-M yardstick claims with a neutral prompt, plus synthetic controls to test whether the annotator can output FALSE',
  phases: [
    { title: 'Annotate', detail: 'neutral-prompt resolvability + outcome coding' },
    { title: 'Verify', detail: 'adversarial citation audit' },
  ],
}

const CLAIMS = ''' + json.dumps(ALL, ensure_ascii=False) + ''';

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
'''
open("wf_annotate2.js","w").write(js)
print(f"wrote wf_annotate2.js ({len(js)/1024:.0f} KB)")
print(f"  real claims: {len(real)}  |  controls: {len(ctrl)} ({sum(1 for c in ctrl if c['truth']=='FALSE')} known-FALSE, {sum(1 for c in ctrl if c['truth']=='TRUE')} known-TRUE)")
print("  control key written to data/controls_key.json (NOT given to agents)")
