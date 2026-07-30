import csv, json
from datetime import datetime

real = {r["claim_id"]: r for r in csv.DictReader(open("data/coding_frame_dedup.csv", encoding="utf-8"))}
ctrl = {c["claim_id"]: c for c in json.load(open("data/controls_key.json"))}
LO={">0-5%":0.0,"10-20%":0.10,"25-35%":0.25,"40-<50%":0.40,"55-75%":0.55,"80-90%":0.80,"95-<100%":0.95}
HI={">0-5%":0.05,"10-20%":0.20,"25-35%":0.35,"40-<50%":0.50,"55-75%":0.75,"80-90%":0.90,"95-<100%":1.00}
def my(d): return datetime.strptime(d,"%Y-%m-%d").strftime("%B %Y")

items=[]
for cid,r in real.items():
    items.append({"claim_id":cid,"kind":"real","date":r["first_date"],"term":r["term"],
                  "band":r["band"],"claim":r["sentence"]})
for cid,c in ctrl.items():
    items.append({"claim_id":cid,"kind":"control","date":c["date"],"term":c["term"],
                  "band":c["band"],"claim":c["sentence"]})
items.sort(key=lambda x:(x["date"],x["claim_id"]))

# ---- REVIEWER FRAME: claims only. No AI arguments, no evidence, no outcome. ----
cols=["claim_id","month_year","probability_term","band","band_lo","band_hi","claim",
      "resolvable","outcome","sources_used","notes"]
with open("data/reviewer_frame.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for it in items:
        w.writerow({"claim_id":it["claim_id"],"month_year":my(it["date"]),
            "probability_term":it["term"],"band":it["band"],
            "band_lo":LO.get(it["band"],""),"band_hi":HI.get(it["band"],""),
            "claim":it["claim"],"resolvable":"","outcome":"","sources_used":"","notes":""})

# ---- LOCAL: provenance ----
with open("data/provenance.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["claim_id","kind","exact_date","statement","slug","n_statements"])
    for it in items:
        if it["kind"]=="real":
            r=real[it["claim_id"]]
            w.writerow([it["claim_id"],"real",r["first_date"],r["statement"],r["slug"],r["n_statements"]])
        else:
            w.writerow([it["claim_id"],"control",it["date"],"SYNTHETIC CONTROL - NOT AN SPI-M STATEMENT","",""])

nr=sum(1 for i in items if i["kind"]=="real")
print(f"data/reviewer_frame.csv : {len(items)} rows ({nr} real + {len(items)-nr} controls, interleaved by date)")
print(f"  exposed : month_year, probability_term, band, claim + blank coding columns")
print(f"  withheld: statement title, exact date, kind, all AI output")
print(f"data/provenance.csv     : local rejoin key")
