import re, glob, os, json
from collections import Counter

# yardstick term + R + numeric interval, in the same sentence
RTERM = re.compile(
    r'\b(almost certain|highly likely|highly unlikely|realistic possibility|very likely|likely|unlikely)\b', re.I)
RNUM = re.compile(r'\bR\b[^.]{0,80}?between\s+(\d\.\d+)\s*and\s*(\d\.\d+)', re.I)

hits=[]
for f in sorted(glob.glob("data/txt/*.txt")):
    txt=re.sub(r'\s+',' ',open(f,encoding='utf-8',errors='replace').read())
    for s in re.split(r'(?<=[.!?])\s+(?=[A-Z(])', txt):
        if len(s)>700: continue
        t=RTERM.search(s); n=RNUM.search(s)
        if t and n:
            hits.append({"slug":os.path.basename(f)[:-4],"term":t.group(1).lower(),
                         "lo":float(n.group(1)),"hi":float(n.group(2)),"sentence":s.strip()})
json.dump(hits, open("data/r_interval_claims.json","w"), indent=1)
print(f"R-interval claims with a yardstick term: {len(hits)}")
print(f"across documents: {len(set(h['slug'] for h in hits))}")
print("\nterm used:", Counter(h['term'] for h in hits).most_common())
print("\n--- examples ---")
for h in hits[:6]:
    print(f"  [{h['term']}] {h['lo']}-{h['hi']}  ({h['slug'][-17:]})")
    print(f"      {h['sentence'][:150]}")
