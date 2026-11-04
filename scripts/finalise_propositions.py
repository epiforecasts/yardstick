"""Apply the review of the stripped propositions: data/propositions_review.csv ->
data/propositions_final.csv.

Each edit was made by reading the proposition against its source statement. The D104 scenario
items dropped here are reinstated in a self-contained form by build_master.py.
"""
import csv, re
from exclusions import DROPPED, DUPLICATE_OF

MERGED={"D093":(["D093-a","D093-b"], "The increasing numbers of detected cases \"not compatible with the UK variant\" are the delta variant, indicating its increasing prevalence.")}
REWORDED={
 # "likely" inside the parenthesis is a probability word that would reveal the band.
 "D102":("The observed excess in SARS-CoV-2 reinfections in a highly immune population (over 70% immune from a mixture of natural infection and vaccination) suggests that there is some form of escape from immunity by the omicron variant", "corrected;leak-fixed"),
 # The tail named the modelled scenarios, which are not part of the claim being assessed.
 "D099":("Hospital admissions in England declined during September and October 2021.", "tail-trimmed"),
}
# The verifier saw a truncated source window; both were confirmed against the full statement.
VERIFIED={"D036","D054-b"}

rows=list(csv.DictReader(open("data/propositions_review.csv",encoding="utf-8")))
by_id={r["item_id"]:r for r in rows}
merged_parts={p:k for k,(parts,_) in MERGED.items() for p in parts}

out=[]
for r in rows:
    iid=r["item_id"]
    if iid in DROPPED: continue
    if iid in merged_parts:
        target=merged_parts[iid]; parts,text=MERGED[target]
        if iid!=parts[0]: continue
        r=dict(r, item_id=target, proposition=text, review_flag=f"merged (was {parts[0]}/-{parts[1][-1]})")
    if iid in REWORDED:
        text,flag=REWORDED[iid]; r=dict(r, proposition=text, review_flag=flag)
    if iid in VERIFIED:
        r=dict(r, review_flag="verified-ok (checker context was truncated; confirmed against full source)")
    r=dict(r, band=re.sub(r"^an? ","",r["band"]))
    out.append(r)

for dup,kept in DUPLICATE_OF.items():
    k=next(r for r in out if r["item_id"]==kept)
    k["strip_notes"]+=f" [also stated {by_id[dup]['month_year']} as {dup}]"

with open("data/propositions_final.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(out)
print(f"data/propositions_final.csv: {len(out)} propositions ({len(rows)-len(out)} removed or merged)")
