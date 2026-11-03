"""List the SPI-M-O consensus statements on gov.uk with their attachments.

Scope: documents published by the Scientific Advisory Group for Emergencies whose title names
SPI-M(-O) and a consensus statement or view. Writes data/consensus_with_attachments.json, the
input to download.py.
"""
import json, re, time, urllib.parse, urllib.request

UA={"User-Agent":"yardstick-research/0.1 (academic research on probability language calibration; sebastian.funk@lshtm.ac.uk)"}
SEARCH="https://www.gov.uk/api/search.json"
CONTENT="https://www.gov.uk/api/content"

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)

results=[]; start=0
while True:
    q=urllib.parse.urlencode({"q":"SPI-M-O","filter_organisations":"scientific-advisory-group-for-emergencies",
        "fields":"link,title","count":1000,"start":start})
    d=get(f"{SEARCH}?{q}"); results+=d["results"]; start+=1000
    if start>=d["total"]: break

links=sorted({r["link"] for r in results
              if re.search(r"SPI-?M", r["title"]) and re.search(r"consensus", r["title"], re.I)})
recs=[]
for link in links:
    c=get(CONTENT+link)
    recs.append({"base_path":link, "title":c["title"], "first_published_at":c["first_published_at"],
        "attachments":[{"title":a.get("title"), "url":a.get("url"), "content_type":a.get("content_type")}
                       for a in c["details"].get("attachments",[])]})
    time.sleep(0.5)

json.dump(recs, open("data/consensus_with_attachments.json","w"), indent=1)
print(f"{len(results)} search results -> {len(recs)} consensus statements, "
      f"{sum(len(r['attachments']) for r in recs)} attachments")
