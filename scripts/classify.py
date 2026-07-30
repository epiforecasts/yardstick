import re, json
from collections import Counter

rows = json.load(open("data/candidate_claims.json"))

COUNTERFACTUAL = re.compile(
    r'\b(if\s+\w+\s+(were|was|had)|would\s+(be|have|result|lead|need|mean)|were\s+to\b|'
    r'without\s+further\s+(measures|action|intervention)|unless\b|in\s+the\s+absence\s+of|'
    r'had\s+been|could\s+have)\b', re.I)
CONDITIONAL = re.compile(r'\b(if\b|provided\s+that|assuming|conditional\s+on|should\s+\w+\s+(occur|happen)|depending\s+on)\b', re.I)
VAGUE = re.compile(
    r'\b(important|significant|substantial|considerable|some|may|might|could|various|'
    r'a\s+number\s+of|broadly|generally|roughly|approximately|likely\s+include)\b', re.I)
QUANT = re.compile(r'(\d+\s*%|\b\d+\.\d+\b|\bbetween\s+\d|\bexceed\b|\babove\b|\bbelow\b|\bmore\s+than\s+\d|\bthousands\b|\bhigher\s+than\b|\blower\s+than\b)', re.I)
DATED = re.compile(r'\b(by\s+\w+day|within\s+the\s+next|next\s+\w+\s+weeks?|by\s+(mid|early|late)?[-\s]?\w*\s*(January|February|March|April|May|June|July|August|September|October|November|December)|in\s+\d+\s+weeks?|coming\s+weeks?)\b', re.I)

def classify(s):
    if COUNTERFACTUAL.search(s): return "counterfactual"
    if CONDITIONAL.search(s):    return "conditional"
    if QUANT.search(s) or DATED.search(s): return "resolvable-quantitative"
    if VAGUE.search(s):          return "vague"
    return "resolvable-qualitative"

for r in rows:
    r["class"] = classify(r["sentence"])
    r["has_quant"] = bool(QUANT.search(r["sentence"]))
    r["has_date"]  = bool(DATED.search(r["sentence"]))

json.dump(rows, open("data/classified_claims.json","w"), indent=1)
c = Counter(r["class"] for r in rows)
print("=== Heuristic resolvability classification (n=298) ===")
for k in ["resolvable-quantitative","resolvable-qualitative","conditional","counterfactual","vague"]:
    print(f"  {k:26s} {c[k]:4d}   {100*c[k]/len(rows):5.1f}%")
print()
res = c["resolvable-quantitative"]+c["resolvable-qualitative"]
print(f"  plausibly resolvable        {res:4d}   {100*res/len(rows):5.1f}%")
print(f"  with an explicit deadline   {sum(1 for r in rows if r['has_date']):4d}")
print()
print("=== resolvable claims by yardstick term (the calibration cells) ===")
cc = Counter(t for r in rows if r["class"].startswith("resolvable") for t in r["terms"])
for t,n in cc.most_common(): print(f"  {t:24s} {n:4d}")
