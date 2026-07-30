import csv, json, os, sys
from datetime import datetime
from collections import Counter

if not os.path.exists("data/annotations_v2.json"):
    sys.exit("waiting on data/annotations_v2.json")

ann  = {a["claim_id"]: a for a in json.load(open("data/annotations_v2.json"))}
real = {r["claim_id"]: r for r in csv.DictReader(open("data/coding_frame_dedup.csv", encoding="utf-8"))}
ctrl = {c["claim_id"]: c for c in json.load(open("data/controls_key.json"))}

def my(d):  # 2021-12-22 -> December 2021
    return datetime.strptime(d, "%Y-%m-%d").strftime("%B %Y")

items = []
for cid, a in ann.items():
    if cid in real:
        r = real[cid]; date, kind = r["first_date"], "real"
    elif cid in ctrl:
        c = ctrl[cid]; date, kind = c["date"], "control"
    else:
        continue
    items.append({"claim_id": cid, "kind": kind, "date": date, "a": a,
                  "sentence": (real[cid]["sentence"] if kind=="real" else ctrl[cid]["sentence"]),
                  "term": (real[cid]["term"] if kind=="real" else ctrl[cid]["term"]),
                  "band": (real[cid]["band"] if kind=="real" else ctrl[cid]["band"])})
items.sort(key=lambda x: (x["date"], x["claim_id"]))

def ev(a): return " | ".join(f"{e.get('note','')}: {e.get('url','')}" for e in (a.get("evidence") or [])[:3])

# ---- REVIEWER SHEET: month+year only, no statement, no kind, no outcome ----
cols = ["claim_id","month_year","term","band","band_lo","band_hi","claim",
        "argument_for","argument_against","what_would_settle_it","evidence_links",
        "R1_resolvable","R1_outcome","R1_notes","R2_resolvable","R2_outcome","R2_notes",
        "adjudicated_resolvable","adjudicated_outcome","adjudication_notes"]
LO={">0-5%":0.0,"10-20%":0.10,"25-35%":0.25,"40-<50%":0.40,"55-75%":0.55,"80-90%":0.80,"95-<100%":0.95}
HI={">0-5%":0.05,"10-20%":0.20,"25-35%":0.35,"40-<50%":0.50,"55-75%":0.75,"80-90%":0.90,"95-<100%":1.00}
with open("data/sheet_reviewers.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for it in items:
        a=it["a"]
        w.writerow({"claim_id":it["claim_id"],"month_year":my(it["date"]),"term":it["term"],
            "band":it["band"],"band_lo":LO.get(it["band"],""),"band_hi":HI.get(it["band"],""),
            "claim":it["sentence"],"argument_for":a.get("argument_for",""),
            "argument_against":a.get("argument_against",""),"what_would_settle_it":a.get("resolve_against",""),
            "evidence_links":ev(a),"R1_resolvable":"","R1_outcome":"","R1_notes":"",
            "R2_resolvable":"","R2_outcome":"","R2_notes":"",
            "adjudicated_resolvable":"","adjudicated_outcome":"","adjudication_notes":""})

# ---- LOCAL: provenance (rejoin after coding) ----
with open("data/provenance.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["claim_id","kind","exact_date","statement","slug","n_statements"])
    for it in items:
        if it["kind"]=="real":
            r=real[it["claim_id"]]
            w.writerow([it["claim_id"],"real",r["first_date"],r["statement"],r["slug"],r["n_statements"]])
        else:
            w.writerow([it["claim_id"],"control",it["date"],"SYNTHETIC CONTROL - NOT AN SPI-M STATEMENT","",""])

# ---- LOCKED AI ARM ----
with open("data/sheet_ai_locked.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["claim_id","kind","ai_resolvable","ai_outcome","ai_outcome_reason",
                                 "ai_confidence","verify_verdict","citations_support","verify_issues"])
    for it in items:
        a=it["a"]
        w.writerow([it["claim_id"],it["kind"],a.get("resolvable",""),a.get("outcome",""),
                    a.get("outcome_reason",""),a.get("confidence",""),a.get("verify_verdict",""),
                    a.get("citations_support",""),a.get("verify_issues","")])

nr=sum(1 for i in items if i["kind"]=="real"); nc=len(items)-nr
print(f"sheet_reviewers.csv : {len(items)} rows ({nr} real + {nc} controls, interleaved by date)")
print(f"  columns exposed   : month_year, term, band, claim, arguments, evidence — NO statement, NO kind, NO outcome")
print(f"provenance.csv      : exact dates + statement titles, local only")
print(f"sheet_ai_locked.csv : AI arm, local only until humans finish")
