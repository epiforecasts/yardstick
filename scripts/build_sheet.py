import csv, json, sys, os

ANNOT = "data/annotations.json"
if not os.path.exists(ANNOT):
    sys.exit(f"missing {ANNOT} — waiting on workflow")

ann = {a["claim_id"]: a for a in json.load(open(ANNOT))}
rows = list(csv.DictReader(open("data/coding_frame_dedup.csv", encoding="utf-8")))

def ev(a):
    return " | ".join(f"{e.get('note','')}: {e.get('url','')}" for e in (a.get("evidence") or [])[:3])

# ---------- REVIEWER TAB (goes to Drive; NO outcome, NO AI coding) ----------
rcols = ["claim_id","date","statement","term","band","band_lo","band_hi","n_statements",
         "sentence","argument_for","argument_against","resolve_against","evidence_links",
         "R1_resolvable","R1_outcome","R1_notes","R2_resolvable","R2_outcome","R2_notes",
         "adjudicated_resolvable","adjudicated_outcome","adjudication_notes"]
with open("data/sheet_reviewers.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=rcols); w.writeheader()
    for r in rows:
        a=ann.get(r["claim_id"])
        if not a: continue
        w.writerow({"claim_id":r["claim_id"],"date":r["first_date"],"statement":r["statement"],
            "term":r["term"],"band":r["band"],"band_lo":r["band_lo"],"band_hi":r["band_hi"],
            "n_statements":r["n_statements"],"sentence":r["sentence"],
            "argument_for":a.get("argument_for",""),"argument_against":a.get("argument_against",""),
            "resolve_against":a.get("resolve_against",""),"evidence_links":ev(a),
            "R1_resolvable":"","R1_outcome":"","R1_notes":"","R2_resolvable":"","R2_outcome":"","R2_notes":"",
            "adjudicated_resolvable":"","adjudicated_outcome":"","adjudication_notes":""})

# ---------- LOCKED AI TAB (stays local until humans finish) ----------
acols = ["claim_id","ai_resolvable","ai_outcome","ai_outcome_reason","ai_confidence",
         "verify_verdict","citations_support","verify_issues"]
with open("data/sheet_ai_locked.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=acols); w.writeheader()
    for r in rows:
        a=ann.get(r["claim_id"])
        if not a: continue
        w.writerow({"claim_id":r["claim_id"],"ai_resolvable":a.get("resolvable",""),
            "ai_outcome":a.get("likely_outcome",""),"ai_outcome_reason":a.get("outcome_reason",""),
            "ai_confidence":a.get("confidence",""),"verify_verdict":a.get("verify_verdict",""),
            "citations_support":a.get("citations_support",""),"verify_issues":a.get("verify_issues","")})

n=sum(1 for r in rows if r["claim_id"] in ann)
print(f"sheet_reviewers.csv:  {n} claims, outcome columns BLANK")
print(f"sheet_ai_locked.csv:  {n} claims, AI coding + audit verdicts")
from collections import Counter
print("\nAI resolvable:", dict(Counter(a.get("resolvable") for a in ann.values())))
print("AI outcome   :", dict(Counter(a.get("likely_outcome") for a in ann.values())))
print("audit verdict:", dict(Counter(a.get("verify_verdict") for a in ann.values())))
