export const meta = {
  name: 'strip-spim-propositions-new',
  description: 'Strip probability qualifiers from the newly-included SPI-M claims (forecast/counterfactual/conditional/vague); verify faithful to source',
  phases: [ { title: 'Strip' }, { title: 'Verify' } ],
}
// The claims are passed in as the workflow's args: data/strip_payload_new.json (build_strip_payload.py). They carry the
// withheld bands, so they are kept out of the repository.
const CLAIMS = args;
const STRIP = {
  type:'object', required:['clean_sentence','propositions','notes'],
  properties:{
    clean_sentence:{type:'string'},
    propositions:{type:'array',minItems:1,items:{type:'object',required:['text','is_compound_part'],
      properties:{text:{type:'string'},is_compound_part:{type:'boolean'}}}},
    notes:{type:'string'} } };
const VERIFY = {
  type:'object', required:['faithful','issues'],
  properties:{faithful:{type:'boolean'},issues:{type:'string'},
    corrected:{type:'array',items:{type:'string'}}} };

function stripPrompt(c){
  const src=c.source_window?`SOURCE CONTEXT (sentence appears within; use to un-truncate and resolve referents):\n"""${c.source_window}"""`:`No source document.`;
  return `You are preparing statements for a calibration study of the UK SPI-M-O committee's probability language. Convert a probability statement into the bare PROPOSITION whose truth is asserted, so a reviewer can later judge whether it turned out true in hindsight WITHOUT seeing the probability word.

CLAIM ${c.claim_id}. Probability term(s): "${c.band}".
FRAME TEXT (may be truncated/junky — trust source): "${c.frame_claim}"

${src}

Produce:
1. clean_sentence — the full original sentence, verbatim from source, page-header artefacts removed ("1 of 9 Reproduction number" etc.), truncation repaired. If no source, echo frame text.
2. propositions — the bare proposition(s). RULES:
   - Extract the POSITIVE CORE the probability qualified. "X is unlikely to reduce Y" -> "X reduces Y" (NOT negated). "It is highly likely that Z" -> "Z". "It is almost certain X will happen" -> "X happens/happened" (a forecast becomes a plain proposition assessable in hindsight). Band is P(proposition); do not negate.
   - Remove EVERY probability word (likely, unlikely, almost certain, realistic possibility, probably, very likely, etc.) and meta-framing ("SPI-M-O considers... to be", "consensus view is that").
   - SELF-CONTAINED: resolve leading referents ("Such", "They", "This", "It") from context. Resolve or REMOVE references to document-internal objects a reviewer cannot see: "Table 1", "Scenario E", "Figure 2", "the projections", named model runs. If the proposition cannot be made self-contained without such a reference, still produce it but note the problem in notes.
   - Drop non-probabilistic editorial tails ("...and so this is of particular importance").
   - SPLIT compound claims into one proposition per separable clause (is_compound_part=true); single claim is_compound_part=false.
   - Preserve quantitative content (thresholds, comparators, numbers). Keep faithful: exactly what SPI-M asserted minus the probability. Do not add/strengthen/soften.
3. notes — referents resolved, document-internal refs, judgement calls, or "none".
Return the structured object. No preamble.`;
}
function verifyPrompt(c,s){
  return `Adversarially audit a proposition extraction. Find problems.
SPI-M term "${c.band}" on ${c.claim_id}. CLEAN SENTENCE: "${s.clean_sentence}"
${c.source_window?`SOURCE: """${c.source_window}"""`:'No source.'}
PROPOSITIONS: ${JSON.stringify(s.propositions.map(p=>p.text))}
Check each: 1. DIRECTION positive core, not negated ("unlikely to reduce"->"reduces"). 2. FAITHFUL: exactly SPI-M's assertion minus probability; no added/lost quantitative content. 3. SELF-CONTAINED: no dangling referent, no un-resolvable document-internal reference (Table/Scenario/Figure). 4. NO probability word leaks. 5. COMPOUND split correctly.
faithful=true only if ALL pass. If false, put corrected text in corrected[]. Flag any proposition that references an undefined Table/Scenario/Figure as NOT faithful (un-self-contained). Default faithful=false if unverifiable.
Return the structured object. No preamble.`;
}
log(`stripping ${CLAIMS.length} new claims`);
const results = await pipeline(CLAIMS,
  (c)=>agent(stripPrompt(c),{label:`strip:${c.claim_id}`,phase:'Strip',schema:STRIP,model:'sonnet'}),
  (s,c)=>{ if(!s) return null;
    return agent(verifyPrompt(c,s),{label:`verify:${c.claim_id}`,phase:'Verify',schema:VERIFY,model:'sonnet'})
      .then(v=>({claim_id:c.claim_id,uid:c.uid,band:c.band,frame_claim:c.frame_claim,
        clean_sentence:s.clean_sentence,propositions:s.propositions,strip_notes:s.notes,
        faithful:v?v.faithful:null,verify_issues:v?v.issues:'',corrected:v?(v.corrected||[]):[]}))
      .catch(()=>({claim_id:c.claim_id,uid:c.uid,band:c.band,clean_sentence:s.clean_sentence,
        propositions:s.propositions,strip_notes:s.notes,faithful:null,verify_issues:'verify failed',corrected:[]}));
  });
const ok=results.filter(Boolean);
log(`done: ${ok.length}/${CLAIMS.length}`);
return ok;
