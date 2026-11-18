# Analysis plan (work in progress)

Pre-specified plan for assessing the calibration of probability-yardstick language in the
SPI-M-O consensus statements. To be finalised and registered (with the SHA-256 hashes of the
sealed answer key, see `data/answer_key/`) before the answer key is unsealed.

Status: draft. Open decisions are marked **[TBD]**.

## 1. Question

When SPI-M-O attached a yardstick term to a statement ("likely", "highly likely", …), how
often did the statement turn out to be correct, and does that frequency fall within the term's
numeric band?

## 2. Data

- **Corpus.** The SPI-M-O consensus statements and consensus views published on gov.uk by the
  Scientific Advisory Group for Emergencies: 94 publications (95 PDFs), dated February 2020 to
  February 2022 and published from March 2020 to February 2022. They were found through the
  gov.uk search API (query `SPI-M-O`, organisation SAGE, title naming SPI-M and a consensus
  statement or view; `scripts/list_statements.py`). The monthly SAGE collections omit about
  12% of them.
- **Excluded from the corpus.**
  - *UKHSA EMRG consensus statements* (54, July 2021 to December 2022). These are UKHSA
    summaries of R, growth rate, incidence and prevalence. They reprint the yardstick in an
    annex but use it in the text only about ten times, each time for a caveat about the data
    ("unlikely to have materially impacted the estimates").
  - *SPI-M statements from the 2009 H1N1 pandemic.* These concern a different epidemic, and it
    is unclear whether they followed the yardstick convention.
- **Excluded from the items.** Claims that put a value on R other than its position relative
  to 1: estimates of the current R ("R in England is between 0.8 and 1.0", "close to 1"),
  forecasts of the value R will reach ("as low as 0.6"), and estimated effects on R ("increases
  R by a factor of 1.1 to 1.5"), 15 items in all. Because R is latent, checking such a value
  needs another model estimate. Claims about whether R is above or below 1 are kept and
  resolved as in §3.
- **Items.** 309 survey items: 291 statements extracted from the consensus statements and
  stripped of their probability wording, plus 18 synthetic quality-control items. Construction
  is described in `README.md` and the pipeline; the per-item band is sealed in
  `data/answer_key/`.
- **Verdicts.** Each item is assessed independently by every reviewer as *correct*,
  *incorrect*, or *cannot tell*, with a *high / medium / low* confidence in that assessment,
  plus free-text sources and notes.
- **Bands.** The PHIA yardstick: remote chance (>0–5%), highly unlikely (10–20%), unlikely
  (25–35%), realistic possibility (40–<50%), likely / probable (55–75%), highly likely
  (80–90%), almost certain (95–<100%). Propositions were extracted in their positive form, so a
  band is the probability of the stated proposition.

## 3. Resolvability convention (codebook)

Applied uniformly by all reviewers, agreed before coding:

- A statement is coded **cannot tell** when its truth cannot be settled from evidence
  independent of a model: a quantity knowable only through modelling (a precise reproduction
  number, true prevalence or incidence, a transmissibility advantage), a hypothetical that
  never occurred, or wording too vague to have a definite answer.
- A **direction or threshold** that maps onto an observable is resolvable even when the
  underlying quantity is latent: "R below 1" is assessed against whether the epidemic declined
  (hospitalisations, deaths), not against a modelled R value.
- Reviewers record which basis they used in the notes.

Consequence: the resolvability rate is partly set by this convention and is reported as a
stated scope decision, not an emergent finding.

## 4. Primary analysis

1. Restrict to items resolved as **correct** or **incorrect** (drop *cannot tell*).
2. Group by yardstick band. For each band, compute the observed proportion correct with a
   confidence interval **[TBD: exact binomial vs a model that accounts for clustering]**.
3. **Calibration** holds for a band if the observed proportion falls within its stated range.
   Report a reliability diagram (observed proportion against band midpoint) and a summary
   calibration error (mean absolute deviation of observed proportion from band midpoint,
   weighted by number of items).
4. Clustering: statements within a document and across consecutive weeks are not independent.
   Account for this in the intervals **[TBD: cluster by document / epidemic phase, or a
   mixed-effects model]**.

## 5. Secondary analyses

- **By resolvability class.** Calibration and resolvability rate reported separately for
  fixed-fact, forecast, conditional, counterfactual and vague statements (`orig_class` in the
  item map).
- **Resolvability rate.** The fraction of statements each reviewer could resolve, overall and
  by band and class (a result in its own right).
- **Confidence.** Repeat the primary analysis restricted to high-confidence verdicts, as a
  sensitivity check.
- **Off-yardstick terms.** "Very likely" and other non-yardstick terms are described, not
  scored against a band.
- **Over- vs under-confidence.** Whether observed proportions sit systematically above or below
  band midpoints.

## 6. Reviewers and agreement

- Number of reviewers: **[TBD]**.
- **Inter-rater reliability** on the assessment (three categories): **[TBD: Cohen's κ for two
  reviewers, Fleiss' κ or averaged pairwise agreement for more]**, reported separately for the
  resolvable/cannot-tell distinction and for correct/incorrect among resolved items.
- **Disagreements.** Adjudication procedure **[TBD]**. Pre-specify handling of the case where
  reviewers split between *cannot tell* and a definite verdict.
- The primary calibration analysis uses **[TBD: adjudicated verdicts / verdicts where reviewers
  agree / each reviewer separately then pooled]**.

## 7. Quality-control items

The 18 synthetic items have known answers (12 false, 5 true, 1 latent "cannot tell"). Reviewer
accuracy against these is reported as a check on the coding, and as calibration of the
reviewers themselves (do their confidence ratings track their accuracy). Control items are
excluded from the calibration of SPI-M.

## 8. Pre-specification

Fixed before the answer key is unsealed: the resolvability convention (§3), the primary
analysis (§4), the item set and their (sealed) bands, and this plan. The reviewer-dependent
choices in §6 and the interval methods in §4 are to be settled **[TBD]** and pinned before
unsealing.

## 9. Deviations

Any departure from this plan will be recorded here with its reason.

- **Answer key exposed in the repository history (found November 2026, before coding).** The
  first versions of the stripping workflows embedded every statement with its band, a
  superseded script listed the 18 quality-control items with their answers, and the scenario
  decisions named the bands of 13 items. All of these were in the tracked scripts, which the
  reviewers can read. The scripts now read claims, bands and controls from git-ignored files,
  and the hand-made inputs are sealed with the answer key. The commits remain in the history.
  - *Bands.* Recovering an item's band means matching its wording against the old scripts
    deliberately, so reviewers instead agree not to read the history
    (`data/answer_key/README.md`).
  - *Controls.* A reviewer who had seen the old list would recognise a control on sight, so all
    18 were replaced by new items with the same composition, written by someone outside the
    reviewer pool and kept out of the repository. The first stripping run's archived results
    keep the old controls; nothing downstream reads them.
  - *Worked example.* The strip prompt in `scripts/wf_strip.js` used one real claim, with its
    probability term, as its example of a compound claim, and that line stayed in the current
    version of the file until 18 November 2026. It is now a placeholder. A reviewer who read the
    script before then could know the band of that one item.
  - *Checksums.* The checksums first committed for `survey_item_map.csv` and `controls_key.json`
    (commit 24028e8) were replaced when the controls changed (commit 93dde5d); both versions stay
    in the history of `data/answer_key/CHECKSUMS.txt`. Before the reseal, the item map rebuilt by
    the converted scripts was compared with a copy of the data taken before any of these changes:
    all 291 real items matched in every field apart from the survey item number, which was left
    out of the comparison.
