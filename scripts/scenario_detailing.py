"""Render data/scenario_detailing_review.md from data/scenario_decisions.json.

The decisions are hand-authored: for each item that refers to a named model scenario (omicron
A-F and the like), whether to state the scenario's distinguishing claim, reinstate, reword, keep
and tag as vague, or drop it as a figure caption. They give each item's band, so the file is a
sealed input (data/answer_key/CHECKSUMS.txt) rather than part of this script.
"""
import json, csv

DECISIONS=[(d["item_id"],d["action"],d["band"],d["new_proposition"],d["rationale"])
           for d in json.load(open("data/scenario_decisions.json",encoding="utf-8"))]

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
            "reinstate":"↩️ REINSTATED D104 (was dropped; now detailed)",
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
print("wrote data/scenario_detailing_review.md")
print("actions:", dict(act))
