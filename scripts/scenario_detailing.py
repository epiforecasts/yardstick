import json, csv

# hand-authored decisions for the scenario-reference items, drawn from source tables
# each: item_id, action, band, new_proposition (or ""), rationale
DECISIONS = [
 # --- DETAIL: omicron scenarios A-F, by distinguishing feature (Dec 2021 Table 1) ---
 ("N107","detail","almost certain",
  "Omicron has immune escape from prior infection- or vaccine-acquired immunity and increased transmission, and replaces delta as the dominant variant in the UK.",
  "A/B/C shared core = immune escape + increased R + replaces delta. Outcome: TRUE."),
 ("N108","detail","highly likely",
  "If omicron has immune escape and increased transmission, very stringent measures are required to control growth and keep R at or below 1.",
  "Conditional on the A/B/C scenario set; kept as a conditional proposition."),
 # reinstate the dropped D104 as three low-band items (D/E/F = no immune escape)
 ("D104-a","reinstate","highly unlikely",
  "Omicron spreads through higher intrinsic transmission without immune escape, producing a short-lived wave.",
  "Scenario D. Outcome: FALSE (omicron had immune escape)."),
 ("D104-b","reinstate","highly unlikely",
  "Omicron replaces delta without immune escape and with no marked change in the hospitalisation trajectory.",
  "Scenario E. Outcome: FALSE."),
 ("D104-c","reinstate","highly unlikely",
  "Omicron causes only small, self-limiting flares and does not replace delta.",
  "Scenario F. Outcome: FALSE."),
 # --- REWORD: R-value / conceptual scenarios (strip chart cruft, spell out concept) ---
 ("N122","reword","highly unlikely",
  "An R of 2.0 for COVID-19 in England is an extreme trajectory for daily hospital admissions over the eight weeks following 6 September 2021.",
  "R=2.0 is the definition; stripped chart colour '(red)'."),
 ("N076-a","reword","highly likely",
  "In England, the actual trajectory of hospitalisations and deaths falls between a projection based on current trends (no future policy change) and a projection in which stringent measures (R=0.6) are maintained for the full six weeks.",
  "'R=0.6 scenario' spelled out."),
 ("N076-b","reword","highly likely",
  "In England, current and future measures reduce transmission somewhat, but by much less than a scenario in which stringent measures (R=0.6) are maintained for the full six weeks.",
  "'R=0.6 scenario' spelled out."),
 ("N094","reword","unlikely",
  "Under a policy of allowing incidence to remain high while progressively relaxing measures as population immunity develops, significant population immunity is achieved by autumn without ICU capacity being overwhelmed.",
  "'high-incidence scenario' = the policy, spelled out."),
 ("N113","reword","highly likely",
  "Absent any mitigations, very stringent measures are required to control epidemic growth and keep R close to or below 1.",
  "'unmitigated scenario' = absent mitigations."),
 # --- KEEP, LABEL VAGUE: cross-document scenario refs not in corpus ---
 ("N120","keep_vague","likely",
  "The future trajectory of the epidemic is some combination of the Step 4 Roadmap scenarios, but with peaks delayed (e.g. October to December instead of August to October).",
  "Step 4 Roadmap scenarios not in corpus; kept, tagged vague."),
 ("N121","keep_vague","unlikely",
  "The highest levels seen in the Step 4 Roadmap scenarios from July are reached, without waning immunity or a new variant emerging.",
  "Same; tagged vague."),
 ("N118-a","keep_vague","likely",
  "The autumn and winter COVID-19 trajectory is a mixture of previous SPI-M-O modelling scenarios, with peaks delayed and possibly broader and longer than originally estimated.",
  "Irreducibly vague ('previous scenarios'); tagged vague."),
 # --- DROP: figure captions / data-revision artefacts (not world-claims) ---
 ("N037","drop","", "", "Figure caption: red data points on deaths chart."),
 ("N038","drop","", "", "Figure caption: red data points revised due to reporting."),
 ("N039","drop","", "", "Figure caption: red data points on the chart."),
 ("N127","drop","", "", "Figure caption: red dots in Figure 1."),
]
json.dump([{"item_id":d[0],"action":d[1],"band":d[2],"new_proposition":d[3],"rationale":d[4]} for d in DECISIONS],
          open("data/scenario_decisions.json","w"), indent=1, ensure_ascii=False)

# build review markdown
rows={r["item_id"]:r for r in csv.DictReader(open("data/new_propositions_review.csv",encoding="utf-8"))}
from collections import Counter
act=Counter(d[1] for d in DECISIONS)
with open("data/scenario_detailing_review.md","w",encoding="utf-8") as f:
    f.write("# Scenario references — detailing decisions for review\n\n")
    f.write(f"{len(DECISIONS)} items: {act['detail']} detailed, {act['reinstate']} reinstated (D104), "
            f"{act['reword']} reworded, {act['keep_vague']} kept-and-tagged-vague, {act['drop']} dropped.\n\n")
    f.write("For each: **original SPI-M sentence** → **new proposition** (what the reviewer sees). "
            "Band held aside as before.\n\n")
    labels={"detail":"🔬 DETAILED (omicron scenario → distinguishing feature)",
            "reinstate":"↩️ REINSTATED D104 (was dropped; now detailed, low-band FALSE items)",
            "reword":"✏️ REWORDED (R-value / concept spelled out)",
            "keep_vague":"🏷️ KEPT, TAGGED VAGUE (not in corpus)","drop":"🗑️ DROPPED (figure caption)"}
    for act_k in ["detail","reinstate","reword","keep_vague","drop"]:
        ds=[d for d in DECISIONS if d[1]==act_k]
        f.write(f"## {labels[act_k]}  ({len(ds)})\n\n")
        for iid,a,band,prop,rat in ds:
            src=rows.get(iid,{}).get("original_sentence","") or "(reinstated from earlier D104 set)"
            f.write(f"**{iid}** · {band or '—'}\n\n")
            f.write(f"<sub>original: {src[:200]}</sub>\n\n")
            if prop: f.write(f"> {prop}\n\n")
            else: f.write(f"*dropped — {rat}*\n\n")
            f.write(f"<sub>· {rat}</sub>\n\n")
print("wrote data/scenario_detailing_review.md + data/scenario_decisions.json")
print("actions:", dict(act))
