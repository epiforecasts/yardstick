import json, csv, re
from collections import Counter
from exclusions import EXCLUDE

prov={r["claim_id"]:r for r in csv.DictReader(open("data/provenance.csv",encoding="utf-8"))}
ck={c["claim_id"]:c for c in json.load(open("data/controls_key.json"))}
decisions={d["item_id"]:d for d in json.load(open("data/scenario_decisions.json"))}

def prov_date(src_claim_id):
    return prov.get(src_claim_id,{}).get("exact_date","")

master=[]  # each: item_id, kind, exact_date, band, proposition, orig_class, flags

# ---- 1. existing real items from propositions_final (fixed-fact set) ----
existing=list(csv.DictReader(open("data/propositions_final.csv",encoding="utf-8")))
for r in existing:
    if r["item_id"] in EXCLUDE:
        continue
    if r["src_claim_id"][0]=="D":
        master.append({"item_id":r["item_id"],"kind":"real","exact_date":prov_date(r["src_claim_id"]),
            "band":r["band"],"proposition":r["proposition"],"orig_class":"fixed-fact","flags":""})
    else:  # control
        master.append({"item_id":r["item_id"],"kind":"control","exact_date":ck[r["item_id"]]["date"],
            "band":r["band"],"proposition":r["proposition"],"orig_class":"control","flags":""})

# ---- 2. reinstate D104-a/b/c (detailed) ----
D104_DATE=prov_date("D104")
for iid in ["D104-a","D104-b","D104-c"]:
    d=decisions[iid]
    master.append({"item_id":iid,"kind":"real","exact_date":D104_DATE,
        "band":f"{d['band']} (10-20%)","proposition":d["new_proposition"],
        "orig_class":"fixed-fact","flags":"omicron-scenario-detailed"})

# ---- 3. new batch: apply scenario decisions, tag by original class ----
newmeta={m["new_id"]:m for m in json.load(open("data/new_claims_meta.json")) if m.get("new_id")}
newrows=list(csv.DictReader(open("data/new_propositions_review.csv",encoding="utf-8")))
BANDNUM={"remote chance":">0-5%","highly unlikely":"10-20%","unlikely":"25-35%",
 "realistic possibility":"40-<50%","likely":"55-75%","probably":"55-75%","probable":"55-75%",
 "highly likely":"80-90%","almost certain":"95-<100%","very likely":"OFF-YARDSTICK"}
def bandlabel(terms):
    t=re.sub(r"^an? ","",(terms or "").split(",")[0].strip().lower())
    return f"{t} ({BANDNUM.get(t,'?')})"
def origclass(nid):
    m=newmeta.get(nid,{})
    tmp=m.get("temporal",""); cls=m.get("class","")
    if cls in ("conditional","counterfactual","vague"): return cls
    if tmp.startswith("future"): return "forecast"
    return cls or "other"

for r in newrows:
    iid=r["item_id"]; nid=r["src_new_id"]
    dec=decisions.get(iid)
    if iid in EXCLUDE or (dec and dec["action"]=="drop"):
        continue
    prop=r["proposition"]; flags=[]; band=bandlabel(r["band_terms"])
    if dec:
        if dec["action"] in ("detail","reword"):
            prop=dec["new_proposition"]; flags.append(dec["action"])
            band=f"{dec['band']} ({BANDNUM.get(dec['band'],'?')})"
        elif dec["action"]=="keep_vague":
            prop=dec["new_proposition"]; flags.append("vague-scenario")
            band=f"{dec['band']} ({BANDNUM.get(dec['band'],'?')})"
    oc=origclass(nid)
    if oc=="vague" and "vague-scenario" not in flags: flags.append("vague")
    master.append({"item_id":iid,"kind":"real","exact_date":r["exact_date"],
        "band":band,"proposition":prop,"orig_class":oc,"flags":";".join(flags)})

# ---- checks ----
PROB=re.compile(r'\b(likely|unlikely|almost certain|realistic possibility|probably|probable|remote chance|very (un)?likely|highly (un)?likely)\b',re.I)
leaks=[m for m in master if PROB.search(m["proposition"])]
nodate=[m for m in master if not m["exact_date"]]
dup=[k for k,v in Counter(m["item_id"] for m in master).items() if v>1]

cols=["item_id","kind","exact_date","band","proposition","orig_class","flags"]
with open("data/propositions_master.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(master)

real=[m for m in master if m["kind"]=="real"]; ctrl=[m for m in master if m["kind"]=="control"]
print(f"MASTER: {len(real)} real + {len(ctrl)} controls = {len(master)} items")
print(f"  probability-word leaks : {len(leaks)}  {[m['item_id'] for m in leaks][:6]}")
print(f"  missing exact_date     : {len(nodate)}  {[m['item_id'] for m in nodate][:6]}")
print(f"  duplicate item_ids     : {dup or 'none'}")
print(f"\n  by original class:")
for c,n in Counter(m["orig_class"] for m in real).most_common(): print(f"     {n:4d}  {c}")
print(f"\n  by band:")
for b,n in sorted(Counter(m["band"] for m in real).items(), key=lambda x:-x[1]): print(f"     {n:4d}  {b}")
