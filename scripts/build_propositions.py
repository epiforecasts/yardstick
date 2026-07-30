import json, csv, re
from collections import Counter
res={r["claim_id"]:r for r in json.load(open("data/strip_results.json"))}
frame={r["claim_id"]:r for r in csv.DictReader(open("data/reviewer_frame.csv",encoding="utf-8"))}

def is_clean_prop(s):
    if not s or not s.strip(): return False
    if re.search(r'UNVERIF|UNVERIFIED|NEEDS? (VERIF|CHECK)|source (window|context)', s, re.I): return False
    if s.strip().isupper(): return False
    if len(s) > 400: return False
    return True

NONCLAIM=re.compile(r'\b(should (not )?be considered|are not forecasts|is a scenario|these scenarios (are|should)|shaded in grey|fit the data poorly|is an assumption|for illustrative)\b', re.I)

out=[]
for cid,fr in frame.items():
    r=res.get(cid)
    band=r.get("band","") if r else f"{fr['probability_term']} ({fr['spim_band']})"
    props=(r.get("propositions") if r else None) or [{"text":fr["claim"]}]
    corr=r.get("corrected") if r else []
    faithful=r.get("faithful") if r else None
    multi=len(props)>1
    for j,p in enumerate(props):
        text=p.get("text","")
        flag=""
        if faithful is False and j < len(corr):
            if is_clean_prop(corr[j]):
                text=corr[j]; flag="corrected"
            else:
                flag="verify-truncated"
        elif faithful is False:
            flag="unfaithful-no-fix"
        if NONCLAIM.search(text): flag=(flag+";" if flag else "")+"possible-non-claim"
        item_id=f"{cid}{'-'+chr(97+j) if multi else ''}"
        out.append({"item_id":item_id,"src_claim_id":cid,"month_year":fr["month_year"],"band":band,
                    "proposition":text,"original_sentence":(r.get("clean_sentence","") if r else fr["claim"]),
                    "review_flag":flag,"strip_notes":(r.get("strip_notes","") if r else ""),
                    "verify_issues":(r.get("verify_issues","") if r else "")})
cols=["item_id","src_claim_id","month_year","band","proposition","original_sentence","review_flag","strip_notes","verify_issues"]
with open("data/propositions_review.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(out)
print(f"data/propositions_review.csv: {len(out)} items ({len(out)-len(frame)} from compound splits)")
fl=Counter(f for o in out for f in o["review_flag"].split(";") if f)
print("review flags:", dict(fl))
print(f"items needing your eye (any flag): {sum(1 for o in out if o['review_flag'])}")
print("clean, no flag:", sum(1 for o in out if not o["review_flag"]))
