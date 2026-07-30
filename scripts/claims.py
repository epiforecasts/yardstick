import re, glob, os, json

# Comparative / adjectival uses that are NOT yardstick probability assertions
NOT_YARDSTICK = re.compile(
    r'\b(more|less|most|equally|as|how|the|a|of|high|higher|disproportionately|intrinsically|'
    r'upcoming|relatively|no|increasingly|similarly|least)\s+likely\b', re.I)

ASSERT = re.compile(
    r'\b(is|are|was|were|will\s+be|will|would|remains?|seems?|appears?|becomes?|it\s+is)\s+'
    r'(highly\s+likely|highly\s+unlikely|almost\s+certain|very\s+likely|likely|unlikely|'
    r'probably|a\s+realistic\s+possibility)\b', re.I)
STANDALONE = re.compile(r'\b(realistic possibility|remote chance|almost certain|highly likely|highly unlikely)\b', re.I)

def sentences(t):
    t = re.sub(r'\s+', ' ', t)
    return re.split(r'(?<=[.!?])\s+(?=[A-Z(])', t)

rows = []
for f in sorted(glob.glob("data/txt/*.txt")):
    slug = os.path.basename(f)[:-4]
    for s in sentences(open(f, encoding='utf-8', errors='replace').read()):
        if len(s) < 25 or len(s) > 700: continue
        hits = []
        for m in ASSERT.finditer(s):
            hits.append(m.group(2).lower())
        for m in STANDALONE.finditer(s):
            if m.group(1).lower() not in hits: hits.append(m.group(1).lower())
        if not hits: continue
        rows.append({"slug": slug, "sentence": s.strip(), "terms": sorted(set(hits))})

json.dump(rows, open("data/candidate_claims.json","w"), indent=1)
print(f"candidate yardstick claim-sentences: {len(rows)}")
print(f"documents represented: {len(set(r['slug'] for r in rows))}/95")
from collections import Counter
c = Counter(t for r in rows for t in r["terms"])
print("\nterm distribution among candidate claims:")
for t,n in c.most_common(): print(f"  {t:24s} {n:4d}")
