import re, glob, os, json
from collections import Counter, defaultdict

# PHIA yardstick terms, longest-first so "highly unlikely" wins over "unlikely".
# Ranges as in the PHIA yardstick reproduced in the consensus statements' annex
# (same bands as make_frame.py); only the term names are used below.
TERMS = [
    ("almost certain",        (0.95, 1.00)),
    ("highly likely",         (0.80, 0.90)),
    ("highly unlikely",       (0.10, 0.20)),
    ("realistic possibility", (0.40, 0.50)),
    ("remote chance",         (0.00, 0.05)),
    ("likely",                (0.55, 0.75)),
    ("unlikely",              (0.25, 0.35)),
    ("probably",              (0.55, 0.75)),
]
pattern = re.compile(r'\b(' + '|'.join(re.escape(t) for t,_ in TERMS) + r')\b', re.I)

counts = Counter()
per_doc = defaultdict(Counter)
for f in sorted(glob.glob("data/txt/*.txt")):
    txt = re.sub(r'\s+', ' ', open(f, encoding='utf-8', errors='replace').read())
    pos = 0
    while True:
        m = pattern.search(txt, pos)
        if not m: break
        term = m.group(1).lower()
        # resolve overlap: prefer the longest term ending at this match end
        start = m.start()
        for t,_ in TERMS:
            probe = txt[max(0,start-len(t)+len(term)) : start+len(term)]
            if len(t) > len(term) and probe.lower().endswith(t):
                term = t; start = start+len(term)-len(t); break
        counts[term] += 1
        per_doc[os.path.basename(f)][term] += 1
        pos = m.end()

print("=== Yardstick term frequency across 95 statements ===")
tot = 0
for t,_ in TERMS:
    if counts[t]:
        print(f"  {t:24s} {counts[t]:5d}")
        tot += counts[t]
print(f"  {'TOTAL':24s} {tot:5d}")
print()
docs_with = sum(1 for d in per_doc if sum(per_doc[d].values())>0)
print(f"documents containing >=1 term: {docs_with}/95")
print(f"median terms per document: {sorted(sum(c.values()) for c in per_doc.values())[len(per_doc)//2]}")
json.dump({k:dict(v) for k,v in per_doc.items()}, open("data/term_counts.json","w"), indent=1)
