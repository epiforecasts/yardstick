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

- **Items.** 324 survey items: 306 statements extracted from the consensus statements and
  stripped of their probability wording, plus 18 synthetic quality-control items. Construction
  is described in `README.md` and the pipeline; the per-item band is sealed in
  `data/answer_key/`.
TODO retry prompt on other models or tweak prompt wording to check sensitivity to volume and content 
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
<!-- TODO llm first pass at which are resolvable to prioritise. or extract all statements, group and human classify. for latent quantities we need a consistent guide to resolution eg by case count, infection survey.-->
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
TODO I'm not sure about the clustering given reports covered diverse quantities. also need to report frequency of use of each band in its own right.
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
TODO off yardstick needs more detail and is more interesting and complex (eg scrape all probabilistic language around the same set of quantities; identify where reporting is binary (we believe that X)?
## 6. Reviewers and agreement

- Number of reviewers: **[TBD]**.
- **Inter-rater reliability** on the assessment (three categories): **[TBD: Cohen's κ for two
  reviewers, Fleiss' κ or averaged pairwise agreement for more]**, reported separately for the
  resolvable/cannot-tell distinction and for correct/incorrect among resolved items.
- **Disagreements.** Adjudication procedure **[TBD]**. Pre-specify handling of the case where
  reviewers split between *cannot tell* and a definite verdict.
- The primary calibration analysis uses **[TBD: adjudicated verdicts / verdicts where reviewers
  agree / each reviewer separately then pooled]**.
TODO specify
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
TODO add a pilot phase to test procedure and rater reliability
## 9. Deviations

Any departure from this plan will be recorded here with its reason.
