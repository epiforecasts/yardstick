# SEALED answer key. Do not open until coding is complete.

This folder holds the study's answer key:

- `survey_item_map.csv`: each survey item's withheld probability band, resolvability class,
  and real/control status.
- `controls_key.json`: the quality-control items and their known answers.

**These two files are not committed to the repository until coding is complete.** Only their
SHA-256 checksums (`CHECKSUMS.txt`) are committed, as a pre-registration proof: the hashes fix
the answer key in place without revealing it. After coding, the files are added and anyone can
verify they match the committed hashes.

The plaintext files are held locally (git-ignored) until then. All reviewers have agreed not to
view them until they have finished coding.

They are a frozen snapshot taken when the survey was finalised. The working copies used by the
pipeline live in `data/` and are also not tracked.

## Tamper-proof pre-registration (recommended)

A hash committed to a repository the team controls is not, by itself, tamper-proof. For a
defensible pre-registration, register the hashes in `CHECKSUMS.txt` externally (e.g. on OSF),
together with `../../ANALYSIS_PLAN.md`, before coding starts. Then the answer key cannot be
altered after the fact.
