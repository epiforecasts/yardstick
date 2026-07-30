import csv, json, html, hashlib
from datetime import datetime

rows=list(csv.DictReader(open("data/propositions_final.csv",encoding="utf-8")))
prov={r["claim_id"]:r for r in csv.DictReader(open("data/provenance.csv",encoding="utf-8"))}
ck={c["claim_id"]:c for c in json.load(open("data/controls_key.json"))}
did_to_uids=json.load(open("data/did_to_uids.json"))

def exact_date(r):
    if r["src_claim_id"][0]=="D": return prov[r["src_claim_id"]]["exact_date"]
    return ck[r["item_id"]]["date"]
def pretty(d):  # 2020-02-03 -> 3 February 2020
    dt=datetime.strptime(d,"%Y-%m-%d")
    return f"{dt.day} {dt.strftime('%B %Y')}"

for r in rows: r["_date"]=exact_date(r)
rows.sort(key=lambda r:(r["_date"], r["item_id"]))

_qn=[0]
def qnum(): _qn[0]+=1; return _qn[0]
_c=[0]
def qid(seed):
    _c[0]+=1
    n=int(hashlib.sha1(f"{seed}-{_c[0]}".encode()).hexdigest(),16)
    a="abcdefghijklmnopqrstuvwxyz0123456789"; s=""
    while len(s)<25: n,r=divmod(n,36); s+=a[r]
    return s[:25]
def optid(seed): return int(hashlib.sha1(seed.encode()).hexdigest(),16)%90000+10000
def NOTE(content,seed): return {"id":qid(seed),"type":"NOTE","content":content,"readonly":True,"isEditing":False}
def CHOICE(title,opts,seed):
    return {"id":qid(seed),"type":"CHOICE","title":title,
        "values":[{"id":optid(f"{seed}-{o}"),"value":o,"allowComments":False} for o in opts],
        "isEditing":False,"isRequired":True,"multicheck":False,"questionNumber":qnum(),
        "randomiseOptionsOrder":False,"prePopulationVisibility":"SHOW","titlePlainText":title}
def TEXT(title,seed,lo,hi,required):
    return {"id":qid(seed),"type":"SINGLE_LINE","title":title,"readonly":False,"isEditing":False,
        "isRequired":required,"validation":{"max":hi,"min":lo,"enabled":True,"inputType":"text"},
        "questionNumber":qnum(),"prePopulationVisibility":"SHOW","titlePlainText":title}
def MULTI(title,seed):
    return {"id":qid(seed),"type":"MULTI_LINE","lines":5,"title":title,"readonly":False,
        "isEditing":False,"isRequired":False,"questionNumber":qnum(),
        "prePopulationVisibility":"SHOW","titlePlainText":title}
def page(pid,qs,title="",desc=""):
    return {"id":pid,"title":title,"isLocked":False,"isEditing":False,"questions":qs,
        "showTitle":bool(title),"description":desc,"showDescription":bool(desc),"preventNewQuestions":False}

INTRO=("<p><strong>Assessing statements about COVID-19</strong></p><p></p>"
 "<p>You are assessing 141 statements about COVID-19 epidemiology. Each was made on the date shown. "
 "Your task is to judge, with hindsight, whether each turned out to be correct.</p>"
 "<p>Some items are constructed for quality-control purposes. Please code every item on its merits.</p><p></p>"
 "<p><strong>For each statement you give</strong></p>"
 "<p><strong>An assessment</strong> — correct, incorrect, or cannot tell. Answer <em>cannot tell</em> "
 "when the statement concerns something that cannot be settled from evidence even in principle — for "
 "example a quantity only knowable through a model (the reproduction number, true infection prevalence, "
 "a transmissibility advantage).</p>"
 "<p><strong>Your confidence</strong> in that assessment — high, medium or low. You can be highly "
 "confident in a <em>cannot tell</em> (a statement you are sure is unresolvable), and you may be "
 "confident a statement was incorrect even when you cannot prove it from independent evidence.</p>"
 "<p><strong>Sources used</strong> — what you actually consulted. This is how we report how each "
 "judgement was settled, so please fill it in even when the answer felt obvious.</p><p></p>"
 "<p><strong>Please note</strong></p>"
 "<p>• <strong>Please do not look up the original SPI-M or SAGE statements.</strong> We are testing "
 "the statements themselves, not your ability to find the source; consulting the originals would "
 "reveal information we are deliberately withholding.</p>"
 "<p>• <strong>Do not discuss items with the other reviewer until you have both finished.</strong> "
 "The two assessments must be independent.</p>"
 "<p>• You can stop at any point and resume later; your progress is saved.</p>"
 "<p>• If a statement is unclear, code it as best you can and say so in the notes.</p>")

pages=[page(1,[NOTE(INTRO,"intro"),
    TEXT("Your initials (so we can match your responses)","initials",1,3,True)],title="Introduction")]

itemmap=[]; pid=2; seq=0
for r in rows:
    seq+=1
    note=f"<blockquote><p>{html.escape(r['proposition'])}</p></blockquote>"
    pages.append(page(pid,[
        NOTE(note,f"{r['item_id']}-note"),
        CHOICE("Did this statement turn out to be correct?",["Correct","Incorrect","Cannot tell"],f"{r['item_id']}-a"),
        CHOICE("How confident are you in this assessment?",["High","Medium","Low"],f"{r['item_id']}-c"),
        MULTI("What sources did you use? (URLs, citations, or 'prior knowledge')",f"{r['item_id']}-src"),
        MULTI("Notes (ambiguity, comparators needing definition, why you hesitated)",f"{r['item_id']}-notes"),
    ],title=f"Item {seq}",desc=pretty(r["_date"])))
    kind="control" if r["item_id"][0] in "XY" else "real"
    itemmap.append({"survey_item":f"Item {seq}","item_id":r["item_id"],"src_claim_id":r["src_claim_id"],
        "uid":";".join(did_to_uids.get(r["src_claim_id"],[])) if kind=="real" else "",
        "kind":kind,"band":r["band"],"exact_date":r["_date"],"proposition":r["proposition"]})
    pid+=1

survey={"pages":pages,"title":"SPI-M Yardstick Review",
    "settings":{"theme":{"text":{"color":"#1e2939","fontFamily":"Inter"},
        "title":{"color":"#1e2939","fontFamily":"Inter"},"borders":"#e5e7eb",
        "elements":{"textColor":"#ffffff","backgroundColor":"#1e40af"},"background":{"color":"#ffffff"}}},
    "anonymous":False,
    "finalPage":{"content":"<p><strong>Thank you</strong></p><p></p><p>Your responses are recorded. "
        "Please do not discuss the items with the other reviewer until they have also finished.</p>",
        "isLocked":False,"isEditing":False},
    "isEditing":False,"description":"","showDescription":False,"displayResponseID":False,
    "displayProgressBar":True,"displayQuestionNumbers":False,"pageReorderingDisabled":False,
    "displayResponseDownload":True}
json.dump(survey,open("data/SPI-M_Yardstick_Review_FINAL.json","w"),indent=1,ensure_ascii=False)
with open("data/survey_item_map.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(itemmap[0].keys())); w.writeheader(); w.writerows(itemmap)

from collections import Counter
qids=[q["id"] for p in pages for q in p["questions"]]
print(f"SPI-M_Yardstick_Review_FINAL.json: {len(pages)} pages (1 intro + {seq} items)")
print(f"  ids unique: {len(set(qids))==len(qids)} | kinds: {dict(Counter(m['kind'] for m in itemmap))}")
print(f"  date span : {rows[0]['_date']} -> {rows[-1]['_date']}, shown as e.g. '{pretty(rows[0]['_date'])}'")
