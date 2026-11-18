import json, time, os, re, hashlib, subprocess, urllib.request, urllib.error
UA="yardstick-research/0.1 (academic research on probability language calibration; sebastian.funk@lshtm.ac.uk)"
recs=json.load(open("data/consensus_with_attachments.json"))
os.makedirs("data/pdfs", exist_ok=True)
os.makedirs("data/txt", exist_ok=True)
manifest=[]
ok=skip=err=0
for rec in recs:
    slug=rec["base_path"].split("/")[-1]
    pdfs=[a for a in rec["attachments"] if (a.get("url") or "").lower().endswith(".pdf")]
    for j,a in enumerate(pdfs):
        fn=f"{slug}{'' if len(pdfs)==1 else f'__{j}'}.pdf"
        dest=os.path.join("data/pdfs", fn)
        if os.path.exists(dest) and os.path.getsize(dest)>1000:
            skip+=1
        else:
            try:
                req=urllib.request.Request(a["url"], headers={"User-Agent":UA})
                with urllib.request.urlopen(req, timeout=60) as r, open(dest,"wb") as f:
                    f.write(r.read())
                ok+=1
                time.sleep(1.0)
            except Exception as e:
                print(f"ERR {fn}: {e}"); err+=1; continue
        # The claims were extracted from -layout text (poppler 26.01); other poppler versions can
        # place figure axis labels differently.
        subprocess.run(["pdftotext","-layout",dest,os.path.join("data/txt",fn[:-4]+".txt")],check=True)
        b=open(dest,"rb").read()
        manifest.append({"file":fn, "slug":slug, "title":rec["title"],
                         "first_published_at":rec["first_published_at"],
                         "attachment_title":a.get("title"), "source_url":a["url"],
                         "bytes":len(b), "sha256":hashlib.sha256(b).hexdigest()})
json.dump(manifest, open("data/manifest.json","w"), indent=1)
print(f"\ndownloaded={ok} skipped={skip} errors={err}  manifest={len(manifest)}")
print(f"total size: {sum(m['bytes'] for m in manifest)/1e6:.1f} MB")
