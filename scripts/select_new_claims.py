"""Select the candidate statements outside the coding frame, for the second stripping run.

Takes every candidate in data/classified_claims.json whose sentence does not restate a claim
already in the coding frame (data/did_to_uids.json, from build_lineage.py) or an earlier
candidate, numbers them N001, N002, ... in candidate order, and writes
data/new_claims_meta.json.
"""
import json
from textnorm import keynorm

classified=json.load(open("data/classified_claims.json"))
for i,c in enumerate(classified): c["uid"]="U%03d"%(i+1)
in_frame={u for us in json.load(open("data/did_to_uids.json")).values() for u in us}

seen={keynorm(c["sentence"]) for c in classified if c["uid"] in in_frame}
new=[]
for c in classified:
    k=keynorm(c["sentence"])
    if c["uid"] in in_frame or k in seen: continue
    seen.add(k)
    new.append({"uid":c["uid"],"new_id":"N%03d"%(len(new)+1),"slug":c["slug"],
                "sentence":c["sentence"],"class":c["class"],"temporal":c["temporal"]})

json.dump(new, open("data/new_claims_meta.json","w",encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"{len(new)} candidates outside the coding frame")
