# Notebook

Dated entries, newest first, one per update to a line of inquiry (see `AGENTS.md`). Each entry
is tagged with its line of inquiry, for example `[corpus]`, and links the issues and pull
requests it covers. An entry is never edited once merged; if later work changes what it says,
a new entry records that and names the entry it supersedes.

Each entry has three parts: the intent, in a person's own words, tidied for clean language
(what they set out to do and why); what was decided or changed, including anything dropped; and
what is still uncertain. The last two are brief and only present where there is something to
say. What was done belongs in the pull requests the entry links to. The pull request that does
the work adds its entry, and an LLM may draft it, but a person reviews and edits the text.

## Entries

### 2026-11-17 `[study]` Calibration of SPI-M-O probability statements

**Intent** (@sbfnk): Assess the calibration of SPI-M statements that use the probability yardstick.

**Decided:** the corpus is the SPI-M-O consensus statements from February 2020 to February 2022 (#1, #7). Each statement is stripped of its yardstick term, and independent reviewers judge with hindsight whether it turned out correct, without seeing the term. Calibration comes from grouping their verdicts by the withheld term.

**Still open:** the validation protocol (#3), coverage and confidence wording (#4), sensitivity to the extraction (#5) and the analysis (#6).
