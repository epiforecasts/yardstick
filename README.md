# SPI-M yardstick calibration

Assessing how the probability-yardstick language in the UK's SPI-M-O consensus statements
("likely", "highly likely", "realistic possibility", and so on) matched how often the
statements turned out correct.

SPI-M-O was the modelling group that fed the UK's Scientific Advisory Group for Emergencies
(SAGE) during COVID-19. Its consensus statements used verbal probability terms from a standard
UK-government probability yardstick (from the Professional Head of Intelligence Assessment,
PHIA), which maps each term to a numeric range (for example "likely" is 55–75%). The question
here: when SPI-M-O said "likely", did the statement come true about 55–75% of the time?

The method is a blinded reviewer survey. Each statement is stripped of its probability wording
and shown as a bare proposition; independent reviewers judge, with hindsight, whether it turned
out correct; and calibration follows from grouping the verdicts by the withheld yardstick term.

The survey is built and ready to deploy: 309 items (291 real statements and 18 hidden
quality-control items), spanning February 2020 to February 2022.

## Start here

New to this project? `NOTEBOOK.md` has a dated entry per update to a line of inquiry: the
intent, what was decided or changed, and what remains uncertain. Read it before the issues and
pull requests behind a line of inquiry, which keep the full detail. `AGENTS.md` sets out the conventions
behind the notebook and this repository's issues and pull requests.

## Repository contents

```
scripts/          pipeline code (run from repo root)
data/answer_key/  sealed answer-key checksums (the only tracked data)
NOTEBOOK.md       dated entry per update to a line of inquiry; start here
AGENTS.md         conventions for issues, pull requests and the notebook
ANALYSIS_PLAN.md  pre-specified analysis plan (work in progress)
README.md
LICENSE
```

The repository holds the pipeline code, the analysis plan, the licence, and the sealed
answer-key checksums. It does not hold the source documents, the generated propositions, the
survey file, or the audit tables: everything else under `data/` is git-ignored and regenerated
by the pipeline, and some of it is deliberately withheld until coding is complete (see
[Sharing and embargo](#sharing-and-embargo)). Wherever a `data/...` file is named below, it is
a pipeline output you generate, not a file that ships with the repository.

`manifest.json` holds the provenance record; `git add -f` it if you want that tracked.

## Pipeline

Scripts live in `scripts/` and are run from the repository root (they read and write paths
under `data/`). Rough order:

1. `list_statements.py`: list the SPI-M-O consensus statements and their attachments through
   the gov.uk search and content APIs, into `data/consensus_with_attachments.json`. The search
   API is used because the monthly SAGE collections omit about 12% of statements, including
   all of August 2021. The scope is set out in `ANALYSIS_PLAN.md`.
2. `download.py`: retrieve the statements' PDFs (rate-limited, identifying User-Agent) and
   extract their text with `pdftotext -layout` (poppler). Produces `data/pdfs/`, `data/txt/`,
   and `data/manifest.json` (provenance with SHA-256).
3. `scan.py`, `claims.py`, `classify.py`, `tense.py`, `make_frame.py`, `dedupe_frame.py`:
   extract candidate yardstick statements, classify by resolvability (whether a statement can
   be judged true or false at all), filter and deduplicate into the coding frame
   (`data/coding_frame_dedup.csv`).
4. `build_lineage.py`, `select_new_claims.py`, `build_strip_payload.py`: link each frame claim
   to its candidates, select the candidates outside the frame for a second run, and build the
   claim payloads for both stripping runs.
5. `wf_strip.js`, `wf_strip_new.js` (multi-agent workflows, run with the payloads as their
   `args`): strip the probability wording to a bare, self-contained proposition, split compound
   statements, and adversarially verify each against the source. The results,
   `data/strip_results.json` and `data/strip_results_new.json`, cannot be regenerated exactly
   and are archived with the answer key (below). `build_propositions.py`,
   `finalise_propositions.py` (the edits made on review) and `build_new_props.py` assemble them.
6. `scenario_detailing.py`: renders the decisions on named model scenarios (for example omicron
   A–F) in `data/scenario_decisions.json`: state the distinguishing claim, drop figure captions,
   or label irreducibly vague references.
7. `build_master.py`: merge everything, with the quality-control items from
   `data/controls_key.json`, into `data/propositions_master.csv`, the full item set with its band
   and resolvability class.
8. `build_survey_master.py`: produce the survey file and the item map (below).
9. `build_ledger.py`: the audit trail (below).

Items dropped by scope rule or on review are listed in `exclusions.py`. The `gen_jisc`,
`gen_native`, `build_sheet*`, `build_final`, `build_survey_final`, `rclaims`, and `contexts`
scripts and the `wf_annotate*.js` workflows are exploratory or superseded, kept for provenance;
`data/archive_ai_runs/README.md` describes the abandoned annotation runs.

### Inputs that are not generated

No script can recreate four of the inputs. They are kept as data and, because each reveals bands
or answers, sealed with the answer key (`data/answer_key/CHECKSUMS.txt`):

- `strip_results.json`, `strip_results_new.json`: the output of the two stripping runs (16 and
  28 July 2026). The workflow scripts name the model by an alias that does not pin a version,
  and a rerun can differ.
- `scenario_decisions.json`: the hand-made decisions on scenario references.
- `controls_key.json`: the quality-control items and their answers.

The first stripping run also included the first version of the quality-control items, which
were replaced before coding (`ANALYSIS_PLAN.md` §9); its archived results keep them.

## The survey

`build_survey_master.py` produces `data/SPI-M_Yardstick_Review_FINAL.json`, which imports into
JISC Online Surveys (onlinesurveys.jisc.ac.uk). It has 310 pages: an intro, then one page per
item (the statement as a blockquote, its exact date, an assessment of correct / incorrect /
cannot tell, and a High/Medium/Low confidence). Item titles are neutral ("Item N"), and no
probability term or band is shown.

Deploy it with independent reviewers who do not see each other's responses until all have
finished. Export the responses from JISC and join them to `data/survey_item_map.csv` on the
question to recover each item's band and resolvability class for analysis.

## Audit trail

The pipeline (`build_lineage.py`, `build_ledger.py`) records the fate of every candidate
statement, from raw extraction to final survey item:

- `data/lineage_candidates.csv` and `data/final_lineage.csv`: each candidate's fate and the
  reason it was included or excluded.
- `data/audit_ledger.csv`: every proposition's transformations and final status.

## Sharing and embargo

The reviewers are also the co-authors, so the study design is not secret to them
(`ANALYSIS_PLAN.md` records it and is shareable). What must stay out of reviewers' hands until
they have finished coding is the answer key: the probability band attached to each item, and
the identity of the quality-control items.

The band is scattered through the working files (`survey_item_map.csv`,
`propositions_master.csv`, `audit_ledger.csv`, and others). The repository therefore tracks
only the sealed answer key in `data/answer_key/` and ignores the rest of `data/`, and the
scripts read bands only from those ignored files. Earlier versions of the scripts embedded
claims with their bands, so the repository's history is covered by the same agreement as the
answer key (`data/answer_key/README.md`). That folder holds the SHA-256 checksums of the answer key (committed as a
pre-registration proof) and a README recording the reviewers' agreement not to open it until
coding is done. The plaintext answer key is added only after coding, and anyone can then check
it against the committed checksums. For tamper-proof pre-registration, register the checksums
externally (for example on OSF); see `data/answer_key/README.md`.

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
prompts are in the workflow scripts (`scripts/wf_strip.js`, `wf_strip_new.js`,
`wf_annotate.js`); the pipeline and audit trail are in this repository. Suggested methods
wording:

> Candidate statements were extracted and rewritten into blinded propositions with LLM
> assistance and adversarial verification against the source; code and prompts are available
> at [DOI].

Replace `[DOI]` with an archived snapshot (for example on Zenodo or OSF) taken at submission,
so the citation stays stable.
