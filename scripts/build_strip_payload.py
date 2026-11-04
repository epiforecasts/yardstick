"""Build the claim payloads for the stripping workflows (wf_strip.js, wf_strip_new.js).

Each claim goes with the text around it in its statement (500 characters before, 300 after), so
the workflow can resolve referents and verify the stripped proposition against the source.
Writes data/strip_payload.json (the coding frame) and data/strip_payload_new.json (the claims
from select_new_claims.py). Both carry the bands, so they stay out of the repository.
"""
import csv, glob, json, re

_text={}
def text(slug):
    if slug not in _text:
        files=sorted(glob.glob(f"data/txt/{slug}*.txt"))
        _text[slug]=" ".join(re.sub(r'\s+',' ',open(f,encoding="utf-8",errors="replace").read()) for f in files)
    return _text[slug]

# The two runs located the claim by different prefix lengths (40 and 50 characters). They are
# kept as run so that the payloads, and hence the archived results, reproduce exactly.
def window(slug, sentence, prefix):
    t=text(slug); i=t.find(sentence[:prefix])
    return t[max(0,i-500):i+len(sentence)+300] if i>=0 else ""

frame=list(csv.DictReader(open("data/coding_frame_dedup.csv",encoding="utf-8")))
payload=[{"claim_id":r["claim_id"],"kind":"real","band":f'{r["term"]} ({r["band"]})',
          "frame_claim":r["sentence"],"source_window":window(r["slug"],r["sentence"],40)}
         for r in frame]

classified=json.load(open("data/classified_claims.json"))
new=[]
for m in json.load(open("data/new_claims_meta.json")):
    c=classified[int(m["uid"][1:])-1]
    new.append({"claim_id":m["new_id"],"uid":m["uid"],"slug":m["slug"],"band":", ".join(c["terms"]),
                "frame_claim":m["sentence"],"source_window":window(m["slug"],m["sentence"],50),
                "class":m["class"],"temporal":m["temporal"]})

for path,rows in [("data/strip_payload.json",payload),("data/strip_payload_new.json",new)]:
    open(path,"w",encoding="utf-8").write(json.dumps(rows,ensure_ascii=False))
    print(f"{path}: {len(rows)} claims, {sum(not r['source_window'] for r in rows)} without a source window")
