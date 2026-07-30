import json, csv, re, hashlib

# canonical claim UID: stable hash of (slug, normalized full sentence)
def norm(s): return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]','',(s or '').lower())).strip()
# aggressive key that removes embedded page-header junk + paragraph numbers
def keynorm(s):
    s=re.sub(r'\b\d+ of \d+\b','',s or '')
    s=re.sub(r'\b(incidence|reproduction number|reissued|final)\b','',s,flags=re.I)
    s=re.sub(r'\d+','',s)
    return re.sub(r'\s+',' ',re.sub(r'[^a-z ]','',s.lower())).strip()

classified=json.load(open("data/classified_claims.json"))            # 298 root, has slug/sentence/class/temporal
dedup=list(csv.DictReader(open("data/coding_frame_dedup.csv",encoding="utf-8")))  # 119, has claim_id + slug + sentence

# uid for each of the 298
for i,c in enumerate(classified):
    c["uid"]="U%03d"%(i+1)

# EXACT join within slug: match each D-id to classified rows sharing slug + keynorm(sentence)
by_slug=lambda rows,getslug: None
cl_by_slug={}
for c in classified: cl_by_slug.setdefault(c["slug"],[]).append(c)

did_to_uids={}   # D-id -> list of candidate uids (the restatements it represents)
unmatched=[]
for r in dedup:
    slug=r["slug"]; k=keynorm(r["sentence"])
    cands=[c for c in cl_by_slug.get(slug,[]) if keynorm(c["sentence"])==k]
    if not cands:   # fall back: prefix within slug
        kk=norm(r["sentence"])[:45]
        cands=[c for c in cl_by_slug.get(slug,[]) if norm(c["sentence"]).startswith(kk[:35])]
    if cands:
        did_to_uids[r["claim_id"]]=[c["uid"] for c in cands]
    else:
        unmatched.append(r["claim_id"])

matched_uids={u for us in did_to_uids.values() for u in us}
print(f"D-ids linked to >=1 candidate: {len(did_to_uids)}/119   (unmatched D-ids: {unmatched or 'none'})")
print(f"candidates linked to a D-id  : {len(matched_uids)}/298")

# also fold in the verbatim-restatement dups dropped later (D013-a/D067/D106) and the filter-passers
# build the master lineage: one row per candidate (298)
uid_to_did={}
for did,us in did_to_uids.items():
    for u in us: uid_to_did[u]=did

def filter_fate(c):
    cls=c.get("class",""); tmp=c.get("temporal","")
    if cls in ("conditional","counterfactual"): return f"excluded: {cls}"
    if cls=="vague": return "excluded: vague/unthresholded"
    if tmp and tmp.startswith("future"): return "excluded: forecast (not fixed-fact)"
    return "passed filter"

lineage=[]
for c in classified:
    did=uid_to_did.get(c["uid"],"")
    passed = c["uid"] in matched_uids
    lineage.append({"uid":c["uid"],"slug":c["slug"],"class":c.get("class",""),
                    "temporal":c.get("temporal",""),
                    "filter_fate": "kept -> "+did if passed else filter_fate(c),
                    "coding_id":did,"sentence":c["sentence"][:110]})
with open("data/lineage_candidates.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(lineage[0].keys())); w.writeheader(); w.writerows(lineage)

from collections import Counter
kept=sum(1 for l in lineage if l["coding_id"])
print(f"\n298 candidates: {kept} linked to a kept claim, {298-kept} excluded")
print("exclusion reasons (deterministic from class/temporal):")
for f,n in Counter(l["filter_fate"] for l in lineage if not l["coding_id"]).most_common():
    print(f"   {n:4d}  {f}")

# write uid back into survey_item_map via src_claim_id (D-id) — one uid group per item
json.dump(did_to_uids, open("data/did_to_uids.json","w"), indent=1)
print("\nwrote data/lineage_candidates.csv (298 rows, exact) + data/did_to_uids.json")
