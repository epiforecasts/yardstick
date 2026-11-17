# SEALED answer key. Do not open until coding is complete.

This folder holds the study's answer key:

- `survey_item_map.csv`: each survey item's withheld probability band, resolvability class,
  and real/control status.
- `controls_key.json`: the quality-control items and their known answers.
- `scenario_decisions.json`: the hand-made decisions on items that refer to named model
  scenarios, with their bands.
- `strip_results.json`, `strip_results_new.json`: the output of the two runs that stripped the
  probability wording from the statements, with each statement's band. These cannot be
  regenerated exactly, so they are archived here as raw data.

**These files are not committed to the repository until coding is complete.** Only their
SHA-256 checksums (`CHECKSUMS.txt`) are committed, as a pre-registration proof: the hashes fix
the answer key in place without revealing it. After coding, the files are added and anyone can
verify they match the committed hashes.

The plaintext files are held locally (git-ignored) until then. They are a frozen snapshot taken
when the survey was finalised; the working copies used by the pipeline live in `data/` and are
also not tracked.

## Reviewers' agreement

Each reviewer agrees, before starting and until they have finished coding:

- not to view the files in this folder or anywhere under `data/`;
- to read the repository's files only as they currently stand, not earlier versions in its
  history. Diffs count as history: the "Files changed" view of a pull request, `git log -p`,
  `git show` and blame all show removed lines. Earlier versions of the workflow scripts embedded every statement with its band, and
  an earlier script listed the first version of the quality-control items with their answers.
  Those controls have been replaced (`../../ANALYSIS_PLAN.md` §9).

## Tamper-proof pre-registration (recommended)

A hash committed to a repository the team controls is not, by itself, tamper-proof. For a
defensible pre-registration, register the hashes in `CHECKSUMS.txt` externally (e.g. on OSF),
together with `../../ANALYSIS_PLAN.md`, before coding starts. Then the answer key cannot be
altered after the fact.
