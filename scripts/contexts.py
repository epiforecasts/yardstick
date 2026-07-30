import re, glob
from collections import Counter
txts = {f: re.sub(r'\s+',' ', open(f,encoding='utf-8',errors='replace').read()) for f in sorted(glob.glob("data/txt/*.txt"))}

# classify bare "likely" (not preceded by highly/un) by preceding word
prev = Counter()
bare = re.compile(r'(\w+)\s+likely\b', re.I)
for t in txts.values():
    for m in bare.finditer(t):
        prev[m.group(1).lower()] += 1
print("=== word preceding 'likely' (top 25) ===")
for w,c in prev.most_common(25):
    print(f"  {w:18s} {c:4d}")
