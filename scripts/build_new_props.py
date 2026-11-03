import json, csv, re, os, sys
from collections import Counter, defaultdict

if not os.path.exists("data/strip_results_new.json"):
    sys.exit("waiting on data/strip_results_new.json")

res=json.load(open("data/strip_results_new.json"))
meta={m["new_id"]:m for m in json.load(open("data/new_claims_meta.json")) if m.get("new_id")}
prov={r["claim_id"]:r for r in csv.DictReader(open("data/provenance.csv",encoding="utf-8"))}

# slug -> exact date, for the new items (via uid->slug in meta). The statement title carries the
# date; the slug is only a fallback because gov.uk slugs contain typos (17-february-2019 for 2020).
MONTHS=["january","february","march","april","may","june","july","august","september","october","november","december"]
DATE_RE=r'(\d{1,2})[ -](%s)[ -](20\d\d)' % "|".join(MONTHS)
titles={x["slug"]:x["title"] for x in json.load(open("data/manifest.json"))}
def date_from_slug(slug):
    # find any provenance row with this slug
    for r in prov.values():
        if r["slug"]==slug: return r["exact_date"]
    m=re.search(DATE_RE, titles.get(slug,""), re.I) or re.search(DATE_RE, slug, re.I)
    if m:
        mm=MONTHS.index(m.group(2).lower())+1
        return f"{m.group(3)}-{mm:02d}-{int(m.group(1)):02d}"
    return ""

def is_clean(s):
    if not s or not s.strip(): return False
    if re.search(r'UNVERIF|source (window|context)|NEEDS? (VERIF|CHECK)', s, re.I): return False
    if len(s)>400 or s.strip().isupper(): return False
    return True
NONCLAIM=re.compile(r'\b(should (not )?be considered|scenario[s]?\s*[A-F]\b|from table\s*\d|figure\s*\d|shaded|fit the data poorly|for illustrative|is an assumption)\b',re.I)
PROB=re.compile(r'\b(likely|unlikely|almost certain|realistic possibility|probably|probable|remote chance|very (un)?likely|highly (un)?likely)\b',re.I)

out=[]
for r in res:
    cid=r["claim_id"]; m=meta.get(cid,{})
    slug=m.get("slug",""); date=date_from_slug(slug)
    band=r.get("band","")
    props=r.get("propositions") or []
    corr=r.get("corrected") or []
    faithful=r.get("faithful")
    multi=len(props)>1
    for j,p in enumerate(props):
        text=p.get("text","")
        flag=[]
        if faithful is False and j<len(corr) and is_clean(corr[j]):
            text=corr[j]; flag.append("corrected")
        elif faithful is False:
            flag.append("unfaithful-no-fix")
        if NONCLAIM.search(text): flag.append("DROP-candidate (non-claim/undefined-ref)")
        if PROB.search(text): flag.append("PROB-LEAK")
        iid=f"{cid}{'-'+chr(97+j) if multi else ''}"
        out.append({"item_id":iid,"src_new_id":cid,"uid":m.get("uid",""),"exact_date":date,
            "class_orig":m.get("class",""),"temporal_orig":m.get("temporal",""),
            "band_terms":band,"proposition":text,"original_sentence":r.get("clean_sentence",""),
            "review_flag":";".join(flag),"strip_notes":r.get("strip_notes","")})
cols=["item_id","src_new_id","uid","exact_date","class_orig","temporal_orig","band_terms",
      "proposition","original_sentence","review_flag","strip_notes"]
with open("data/new_propositions_review.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(out)

flags=Counter(fl for o in out for fl in o["review_flag"].split(";") if fl)
print(f"new propositions: {len(out)} (from {len(res)} new claims; {len(out)-len(res)} compound-split)")
print("flags:", dict(flags))
print("clean, no flag:", sum(1 for o in out if not o['review_flag']))
print("missing date:", sum(1 for o in out if not o['exact_date']))
