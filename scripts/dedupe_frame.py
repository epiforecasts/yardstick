import csv, re
from collections import defaultdict
rows=list(csv.DictReader(open("data/coding_frame.csv",encoding="utf-8")))
def norm(s):
    s=re.sub(r'\s*\d+\.\s*$','',s.strip())
    return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]','',s.lower())).strip()
g=defaultdict(list)
for r in rows: g[norm(r['sentence'])].append(r)
out=[]
for k,v in g.items():
    v.sort(key=lambda r:r['date'])
    f=dict(v[0])
    f["n_statements"]=len(v)
    f["first_date"]=v[0]['date']; f["last_date"]=v[-1]['date']
    f["repeat_dates"]="; ".join(r['date'] for r in v[1:])
    f["sentence"]=re.sub(r'\s*\d+\.\s*$','',v[0]['sentence'].strip())
    out.append(f)
out.sort(key=lambda x:(x["first_date"], x["statement"], x["term"]))
for i,r in enumerate(out,1): r["claim_id"]=f"D{i:03d}"
cols=["claim_id","first_date","last_date","n_statements","statement","term","band","band_lo","band_hi",
      "comparative","sentence","observable","outcome","resolved_against","notes","repeat_dates","slug"]
with open("data/coding_frame_dedup.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore"); w.writeheader(); w.writerows(out)
print(f"distinct claims: {len(out)}")
print(f"restated at least once: {sum(1 for r in out if r['n_statements']>1)}")
print(f"date range: {out[0]['first_date']} -> {max(r['last_date'] for r in out)}")
print(f"comparative: {sum(1 for r in out if r['comparative'])}")
