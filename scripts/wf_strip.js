export const meta = {
  name: 'strip-spim-propositions',
  description: 'Re-extract clean SPI-M sentences, strip probability qualifiers to bare propositions, resolve referents, split compounds; verify faithful to source',
  phases: [ { title: 'Strip' }, { title: 'Verify' } ],
}

// The claims are passed in as the workflow's args: data/strip_payload.json (build_strip_payload.py). They carry the
// withheld bands, so they are kept out of the repository. The first run also included the first version of the
// quality-control items, which were later replaced and are not in the rebuilt payload.
const CLAIMS = args;

const STRIP = {
  type: 'object',
  required: ['clean_sentence','propositions','notes'],
  properties: {
    clean_sentence: { type: 'string', description: 'the full original sentence, cleaned of page-header junk and un-truncated, verbatim from source' },
    propositions: { type: 'array', minItems: 1, items: { type: 'object', required: ['text','is_compound_part'],
      properties: {
        text: { type: 'string', description: 'the bare proposition: positive core the probability qualified, self-contained, no probability word' },
        is_compound_part: { type: 'boolean' } } } },
    notes: { type: 'string', description: 'referents resolved, judgement calls, or "none"' },
  },
};
const VERIFY = {
  type: 'object',
  required: ['faithful','issues'],
  properties: {
    faithful: { type: 'boolean' },
    issues: { type: 'string' },
    corrected: { type: 'array', items: { type: 'string' }, description: 'corrected proposition text if not faithful, else empty' },
  },
};

function stripPrompt(c) {
  const src = c.source_window
    ? `SOURCE CONTEXT (the sentence appears within this; use it to un-truncate and to resolve referents):\n"""${c.source_window}"""`
    : `This is a synthetic control with no source document. Work from the sentence text alone.`;
  return `You are preparing statements for a calibration study of the UK SPI-M-O committee's probability language. For each claim you convert a probability statement into the bare PROPOSITION whose truth is being asserted, so a reviewer can later judge whether it turned out true WITHOUT seeing the probability word.

CLAIM ${c.claim_id}. Probability term applied by SPI-M: "${c.band}".
FRAME TEXT (may be truncated or carry page-header junk — trust the source over this): "${c.frame_claim}"

${src}

Produce:

1. clean_sentence — the full original sentence as SPI-M wrote it, verbatim from source, with page-header artefacts removed (e.g. "1 of 9 Reproduction number", "SAGE 99 Page 1 of 4") and any truncation repaired from the source window. If no source, echo the frame text.

2. propositions — the bare proposition(s). RULES:
   - Extract the POSITIVE CORE that the probability qualified. "X is unlikely to reduce Y" -> proposition "X reduces Y" (NOT "X does not reduce Y"). "It is highly likely that Z" -> "Z". The band is the probability OF this proposition; do not negate.
   - Remove every probability word (likely, unlikely, highly likely, almost certain, realistic possibility, probably, very likely, etc.) and meta-framing ("SPI-M-O considers... to be", "consensus view is that").
   - Make it SELF-CONTAINED: resolve leading referents ("Such restrictions", "They", "This", "It") to their antecedent from the source context. A reader with no context must understand it.
   - Drop non-probabilistic editorial tails ("...and so this is of particular importance", "...but should be carefully designed", "...which is concerning").
   - SPLIT compound claims: if the sentence asserts two separable propositions ("unlikely to reduce final size AND unlikely to delay the peak"), emit one proposition per clause, each is_compound_part=true. A single proposition sets is_compound_part=false.
   - Preserve the claim's actual quantitative content (thresholds, comparators, numbers). Do not vague-ify.
   - Keep it faithful: the proposition must be exactly what SPI-M asserted, minus the probability. Do not add, strengthen, or soften.

3. notes — what referents you resolved and any judgement calls, or "none".

Return the structured object. No preamble.`;
}

function verifyPrompt(c, s) {
  return `Adversarially audit a proposition extraction for a calibration study. Find problems.

SPI-M applied probability term "${c.band}" to claim ${c.claim_id}.
CLEAN SENTENCE (as extracted): "${s.clean_sentence}"
${c.source_window ? `SOURCE CONTEXT: """${c.source_window}"""` : 'Synthetic control, no source.'}
EXTRACTED PROPOSITIONS: ${JSON.stringify(s.propositions.map(p => p.text))}

Check each proposition:
1. DIRECTION: it must be the POSITIVE core the probability qualified, NOT negated. "unlikely to reduce" -> "reduces" is correct; "does not reduce" is WRONG.
2. FAITHFUL: exactly what SPI-M asserted minus the probability word. No added/strengthened/softened meaning, no lost quantitative content (numbers, thresholds, comparators).
3. SELF-CONTAINED: no dangling referent ("Such", "They", "It", "this") left unresolved; no dangling comparative ("more effective" with no comparator).
4. NO PROBABILITY WORD leaks through.
5. COMPOUND: genuinely separable claims are split; a single claim is not artificially split.

faithful = true only if ALL propositions pass. If false, put corrected proposition text in corrected[]. Default to faithful=false if you cannot confirm against source.
Return the structured object. No preamble.`;
}

log(`stripping ${CLAIMS.length} claims`);
const results = await pipeline(
  CLAIMS,
  (c) => agent(stripPrompt(c), { label: `strip:${c.claim_id}`, phase: 'Strip', schema: STRIP, model: 'sonnet' }),
  (s, c) => {
    if (!s) return null;
    return agent(verifyPrompt(c, s), { label: `verify:${c.claim_id}`, phase: 'Verify', schema: VERIFY, model: 'sonnet' })
      .then((v) => ({ claim_id: c.claim_id, kind: c.kind, band: c.band, frame_claim: c.frame_claim,
                      clean_sentence: s.clean_sentence, propositions: s.propositions, strip_notes: s.notes,
                      faithful: v ? v.faithful : null, verify_issues: v ? v.issues : '',
                      corrected: v ? (v.corrected||[]) : [] }))
      .catch(() => ({ claim_id: c.claim_id, kind: c.kind, band: c.band, clean_sentence: s.clean_sentence,
                      propositions: s.propositions, strip_notes: s.notes, faithful: null, verify_issues: 'verify failed', corrected: [] }));
  }
);
const ok = results.filter(Boolean);
log(`done: ${ok.length}/${CLAIMS.length}`);
return ok;
