import json, csv, re
from collections import Counter
from exclusions import R_VALUE, R_VALUE_REASON, DROPPED

# ---- Stage A: exact candidate lineage (298 -> filter -> dedup -> 119) ----
lin=list(csv.DictReader(open("data/lineage_candidates.csv",encoding="utf-8")))
# relabel: passed filter but no coding_id == dropped as verbatim duplicate at dedup
for r in lin:
    if not r["coding_id"] and r["filter_fate"]=="passed filter":
        r["filter_fate"]="excluded at dedup: verbatim duplicate"
with open("data/lineage_candidates.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(lin[0].keys())); w.writeheader(); w.writerows(lin)

kept=sum(1 for r in lin if r["coding_id"])
print("STAGE A  — 298 candidates:")
for fate,n in Counter(r["filter_fate"] if not r["coding_id"] else "kept -> coding frame" for r in lin).most_common():
    print(f"   {n:4d}  {fate}")

# ---- Stage B/C: 119 D-ids -> strip -> propositions -> survey/dropped ----
strip={r["claim_id"]:r for r in json.load(open("data/strip_results.json"))}
survey={r["item_id"]:r for r in csv.DictReader(open("data/survey_item_map.csv",encoding="utf-8"))}
frame={r["claim_id"]:r for r in csv.DictReader(open("data/coding_frame_dedup.csv",encoding="utf-8"))}

ledger=[]
for cid in frame:
    r=strip.get(cid)
    band=frame[cid]["term"]+" ("+frame[cid]["band"]+")"
    props=(r.get("propositions") if r else None) or [{"text":frame[cid]["sentence"]}]
    multi=len(props)>1
    for j,p in enumerate(props):
        iid=f"{cid}{'-'+chr(97+j) if multi else ''}"
        trans=[]
        if multi: trans.append("compound-split")
        if r and r.get("faithful") is False: trans.append("verifier-corrected")
        if iid=="D099": trans.append("model-tail trimmed")
        if iid in ("D093-a","D093-b"): trans.append("merged->D093")
        # final status
        if iid in survey: status="IN SURVEY as "+survey[iid]["survey_item"]
        elif iid in ("D093-a","D093-b"): status="merged into D093 (IN SURVEY as "+survey.get("D093",{}).get("survey_item","?")+")"
        elif iid in DROPPED: status="DROPPED: "+DROPPED[iid]
        elif iid in R_VALUE: status="DROPPED: "+R_VALUE_REASON
        else: status="CHECK"
        ledger.append({"source_id":cid,"item_id":iid,"band":band,
            "proposition":(survey.get(iid,{}).get("proposition") or p.get("text",""))[:150],
            "faithful":(r.get("faithful") if r else ""),"transformations":"; ".join(trans) or "none",
            "final_status":status})
with open("data/audit_ledger.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(ledger[0].keys())); w.writeheader(); w.writerows(ledger)

print("\nSTAGE B/C — 119 coding claims -> 150 propositions:")
for s,n in Counter(re.split(r'[:(]',l["final_status"])[0].strip() for l in ledger).most_common():
    print(f"   {n:4d}  {s}")
unexplained=[l for l in ledger if l["final_status"]=="CHECK"]
print(f"\nunexplained rows (must be 0): {len(unexplained)}")

# ---- full reconciliation ----
insurvey_real=sum(1 for l in ledger if l["final_status"].startswith("IN SURVEY"))
print(f"\nRECONCILIATION")
print(f"  298 candidates = {kept} kept + {298-kept} excluded")
print(f"  119 coding claims -> {len([l for l in ledger])} propositions -> "
      f"{insurvey_real} real survey items + drops/merges")
print(f"  survey_item_map real items: {sum(1 for v in survey.values() if v['kind']=='real')}")
print("wrote data/audit_ledger.csv + data/lineage_candidates.csv (relabelled)")
