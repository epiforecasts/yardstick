import json, csv, re
from datetime import datetime

BANDS = {
    "remote chance":          ">0-5%",
    "highly unlikely":        "10-20%",
    "unlikely":               "25-35%",
    "realistic possibility":  "40-<50%",
    "a realistic possibility":"40-<50%",
    "likely":                 "55-75%",
    "probably":               "55-75%",
    "probable":               "55-75%",
    "highly likely":          "80-90%",
    "almost certain":         "95-<100%",
    "very likely":            "OFF-YARDSTICK",
}
LO = {">0-5%":0.0,"10-20%":0.10,"25-35%":0.25,"40-<50%":0.40,"55-75%":0.55,"80-90%":0.80,"95-<100%":0.95}
HI = {">0-5%":0.05,"10-20%":0.20,"25-35%":0.35,"40-<50%":0.50,"55-75%":0.75,"80-90%":0.90,"95-<100%":1.00}

man = {m['file'][:-4]: m for m in json.load(open("data/manifest.json"))}
def sdate(slug):
    t = (man.get(slug, {}).get('title') or '')
    m = re.search(r'(\d{1,2}\s+\w+\s+20\d\d)\s*$', t)
    if m:
        try: return datetime.strptime(m.group(1), "%d %B %Y").date()
        except ValueError: pass
    return None

rows = json.load(open("data/classified_claims.json"))
clean = [r for r in rows if r["temporal"].startswith("fixed")
         and r["class"] not in ("conditional","counterfactual","vague")]

out = []
for r in clean:
    d = sdate(r["slug"])
    for t in r["terms"]:
        band = BANDS.get(t, "?")
        out.append({
            "claim_id": "",
            "date": d.isoformat() if d else "",
            "statement": (man.get(r["slug"], {}).get("title") or r["slug"]),
            "term": t,
            "band": band,
            "band_lo": LO.get(band, ""),
            "band_hi": HI.get(band, ""),
            "comparative": "Y" if r["comparative_fact"] else "",
            "sentence": r["sentence"],
            "observable": "",      # Y / N / ? — is this measurable, not model output?
            "outcome": "",         # TRUE / FALSE / AMBIGUOUS
            "resolved_against": "",
            "notes": "",
            "slug": r["slug"],
        })

out.sort(key=lambda x: (x["date"] or "9999", x["statement"], x["term"]))
for i, r in enumerate(out, 1):
    r["claim_id"] = f"C{i:03d}"

cols = ["claim_id","date","statement","term","band","band_lo","band_hi","comparative",
        "sentence","observable","outcome","resolved_against","notes","slug"]
with open("data/coding_frame.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)

print(f"rows: {len(out)}  (claims x terms; a sentence with 2 terms gets 2 rows)")
print(f"unique sentences: {len(clean)} | documents: {len(set(r['slug'] for r in clean))}")
ds = [r['date'] for r in out if r['date']]
print(f"date range: {min(ds)} -> {max(ds)} | undated rows: {sum(1 for r in out if not r['date'])}")
print(f"comparative (likeliest to survive): {sum(1 for r in out if r['comparative'])}")
