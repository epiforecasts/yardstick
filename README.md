# SPI-M yardstick calibration

Assessing how the probability-yardstick language in the UK's SPI-M-O consensus statements
("likely", "highly likely", "realistic possibility", …) corresponds to how often the
statements turned out correct.

The end product is a blinded reviewer survey. Each statement is stripped of its probability
wording and presented as a bare proposition, and independent reviewers judge, with hindsight,
whether it turned out correct. Calibration is then assessed by grouping the verdicts by the
withheld yardstick term.

## Status

Survey built and ready to deploy: **324 items** (306 real statements + 18 hidden
quality-control items), spanning February 2020 – February 2022.

## Pipeline

Scripts live in `scripts/` and are **run from the repository root** (they read and write paths
under `data/`). Rough order:

1. `download.py`: retrieve all consensus statements from gov.uk (rate-limited, identifying
   User-Agent). Produces `data/pdfs/`, `data/txt/`, `data/manifest.json` (provenance with
   SHA-256). *Note: the monthly SAGE collections omit ~12% of statements, including all of
   August 2021; the gov.uk search API is needed for the full set.*
2. `scan.py`, `classify.py`, `claims.py`, `tense.py`, `make_frame.py`, `dedupe_frame.py`:
   extract candidate yardstick statements, classify by resolvability, filter and deduplicate.
3. `wf_strip.js`, `wf_strip_new.js` (multi-agent workflows): strip the probability wording to
   a bare, self-contained proposition, split compounds, and adversarially verify each against
   the source. `build_propositions.py`, `build_new_props.py` assemble the results.
4. `scenario_detailing.py`: resolve named model scenarios (e.g. omicron A–F) to their
   distinguishing claim; drop figure captions; label irreducibly vague references.
5. `build_master.py`: merge everything into `data/propositions_master.csv` (the full item set
   with band and resolvability class).
6. `build_survey_master.py`: emit the JISC survey JSON and the item map.
7. `build_lineage.py`, `build_ledger.py`: the audit trail (see below).

The earlier `gen_*`, `build_sheet*`, `build_final`, `rclaims`, `contexts` scripts are
exploratory or superseded, retained for provenance.

## The deliverable

`data/SPI-M_Yardstick_Review_FINAL.json`: import into JISC Online Surveys
(onlinesurveys.jisc.ac.uk). 325 pages: an intro, then one page per item (statement as a
blockquote, exact date, an assessment of correct / incorrect / cannot tell, and a
High/Medium/Low confidence). Neutral "Item N" titles; no probability term or band shown.

Deploy with **independent** reviewers who do not see each other's responses until all have
finished. Export responses from JISC and join to `data/survey_item_map.csv` on the question to
recover each item's band and resolvability class for analysis.

## Audit trail

Every candidate statement is traceable from raw extraction to final survey item:

- `data/lineage_candidates.csv` / `data/final_lineage.csv`: each candidate's fate and reason
  for inclusion or exclusion.
- `data/audit_ledger.csv`: every proposition's transformations and final status.

## Repository layout

```
scripts/          pipeline code (run from repo root)
data/             inputs, intermediates, outputs (see .gitignore)
README.md
ANALYSIS_PLAN.md  pre-specified analysis plan (WIP)
LICENSE
```

Corpus files (`data/pdfs`, `data/txt`, …) and JSON (build artifacts, large intermediates, and
`controls_key.json`) are git-ignored; regenerate them by running the pipeline. `manifest.json`
holds the provenance record; `git add -f` it if you want that tracked.

## Sharing and embargo

The reviewers are also the co-authors, so the study *design* is not secret to them
(`ANALYSIS_PLAN.md` records it and is shareable). What must stay out of reviewers' hands until
they have finished coding is the **answer key** (the probability band attached to each item)
and the identity of the quality-control items.

The band answer key is scattered through the working files (it appears in
`survey_item_map.csv`, `propositions_master.csv`, `audit_ledger.csv`, and others), which are
all regenerable. The repository therefore **tracks only** the sealed answer key in
`data/answer_key/` and ignores the rest of `data/`; run the pipeline to regenerate the working
files. The sealed folder is committed so the answer key is on file and timestamped before
coding (pre-registration), while a `README` there records the reviewers' agreement not to open
it until coding is done. For tamper-proof pre-registration, register its SHA-256 hashes
externally (e.g. OSF); see `data/answer_key/README.md`.

## Licence and attribution

The code (`scripts/`) is released under the MIT Licence; see `LICENSE`.

The SPI-M-O consensus statements and SAGE minutes are © Crown copyright, published on gov.uk
under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
The statements and the propositions derived from them are adaptations of that material, used
under that licence:

> Contains public sector information licensed under the Open Government Licence v3.0.

Source: SPI-M-O consensus statements and SAGE minutes, gov.uk (Scientific Advisory Group for
Emergencies). The PHIA probability yardstick, against which the statements' verbal terms are
scored, is defined in the Professional Head of Intelligence Assessment's *Professional
Development Framework for All-Source Intelligence Assessment* (2019).

## Code and data availability

Candidate statements were extracted from the source documents and rewritten into blinded
propositions with LLM assistance and adversarial verification against the source. The exact
prompts used are in the workflow scripts (`scripts/wf_strip.js`, `wf_strip_new.js`,
`wf_annotate.js`); the pipeline and audit trail are in this repository. Suggested methods
wording:

> Candidate statements were extracted and rewritten into blinded propositions with LLM
> assistance and adversarial verification against the source; code and prompts are available
> at [DOI].

Replace `[DOI]` with an archived snapshot (e.g. Zenodo or OSF) taken at submission, so the
citation stays stable.
