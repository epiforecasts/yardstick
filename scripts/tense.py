import json, re
from collections import Counter

rows=json.load(open("data/classified_claims.json"))

FUTURE = re.compile(r'\b(will|shall|would|going to|expect(ed)? to|by (mid|early|late|the end)|'
                    r'in the (coming|next)|over the (coming|next)|future|upcoming|forecast)\b', re.I)
# present state / fixed property of the world — resolves on evidence, not on waiting
FIXED  = re.compile(r'\b(is|are|was|were|has been|have been|had been|remains?)\s+'
                    r'(highly\s+)?(likely|unlikely|probable|almost certain)\b', re.I)
COMPARATIVE_FACT = re.compile(r'\b(lower|higher|greater|less|more|larger|smaller|worse|better)\s+than\b', re.I)

def kind(s):
    if FUTURE.search(s): return "future-event (needs horizon)"
    return "fixed-fact / nowcast (no deadline needed)"

for r in rows:
    r["temporal"] = kind(r["sentence"])
    r["comparative_fact"] = bool(COMPARATIVE_FACT.search(r["sentence"]))

c=Counter(r["temporal"] for r in rows)
print("=== 298 candidate claims by temporal type ===")
for k,n in c.most_common(): print(f"  {k:42s} {n:4d}  ({100*n/len(rows):.0f}%)")
print()
# cross with resolvability class
print("=== cross-tab: temporal type x heuristic class ===")
ct=Counter((r["temporal"][:11], r["class"]) for r in rows)
for k,n in sorted(ct.items()): print(f"  {k[0]:12s} {k[1]:24s} {n:4d}")
print()
nf=[r for r in rows if r["temporal"].startswith("fixed")]
print(f"fixed-fact/nowcast claims that are NOT conditional/counterfactual: "
      f"{sum(1 for r in nf if r['class'] not in ('conditional','counterfactual'))}")
print(f"of those, containing an explicit comparison (scoreable against evidence): "
      f"{sum(1 for r in nf if r['comparative_fact'] and r['class'] not in ('conditional','counterfactual'))}")
json.dump(rows, open("data/classified_claims.json","w"), indent=1)
