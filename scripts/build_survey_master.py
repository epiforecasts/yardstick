import csv, json, html, hashlib
from datetime import datetime

rows=list(csv.DictReader(open("data/propositions_master.csv",encoding="utf-8")))
rows.sort(key=lambda r:(r["exact_date"], r["item_id"]))
def pretty(d):
    dt=datetime.strptime(d,"%Y-%m-%d"); return f"{dt.day} {dt.strftime('%B %Y')}"

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
def NOTE(c,s): return {"id":qid(s),"type":"NOTE","content":c,"readonly":True,"isEditing":False}
def CHOICE(t,o,s):
    return {"id":qid(s),"type":"CHOICE","title":t,"values":[{"id":optid(f"{s}-{x}"),"value":x,"allowComments":False} for x in o],
        "isEditing":False,"isRequired":True,"multicheck":False,"questionNumber":qnum(),
        "randomiseOptionsOrder":False,"prePopulationVisibility":"SHOW","titlePlainText":t}
def TEXT(t,s,lo,hi,req):
    return {"id":qid(s),"type":"SINGLE_LINE","title":t,"readonly":False,"isEditing":False,"isRequired":req,
        "validation":{"max":hi,"min":lo,"enabled":True,"inputType":"text"},"questionNumber":qnum(),
        "prePopulationVisibility":"SHOW","titlePlainText":t}
def MULTI(t,s):
    return {"id":qid(s),"type":"MULTI_LINE","lines":5,"title":t,"readonly":False,"isEditing":False,
        "isRequired":False,"questionNumber":qnum(),"prePopulationVisibility":"SHOW","titlePlainText":t}
def page(pid,qs,title="",desc=""):
    return {"id":pid,"title":title,"isLocked":False,"isEditing":False,"questions":qs,
        "showTitle":bool(title),"description":desc,"showDescription":bool(desc),"preventNewQuestions":False}

INTRO=("<p><strong>Assessing statements about COVID-19</strong></p><p></p>"
 f"<p>You are assessing {len(rows)} statements about COVID-19 epidemiology. Each was made on the date "
 "shown. Your task is to judge, with hindsight, whether each turned out to be correct.</p>"
 "<p>Some items are constructed for quality-control purposes. Please code every item on its merits.</p><p></p>"
 "<p><strong>For each statement you give</strong></p>"
 "<p><strong>An assessment</strong>: correct, incorrect, or cannot tell. Answer <em>cannot tell</em> when "
 "the statement cannot be settled from evidence even in principle, for example a quantity only knowable "
 "through a model (the reproduction number, true infection prevalence, a transmissibility advantage), a "
 "hypothetical that never occurred, or a statement too vague to have a definite answer.</p>"
 "<p><strong>Your confidence</strong> in that assessment: high, medium or low. You can be highly confident "
 "in a <em>cannot tell</em>, and confident a statement was incorrect even when you cannot prove it from "
 "independent evidence.</p>"
 "<p><strong>Sources used</strong>: what you actually consulted.</p><p></p>"
 "<p><strong>Please note</strong></p>"
 "<p>• <strong>Please do not look up the original SPI-M or SAGE statements.</strong> We are testing the "
 "statements themselves; consulting the originals would reveal information we are deliberately withholding.</p>"
 "<p>• <strong>Do not discuss items with the other reviewers until everyone has finished.</strong></p>"
 "<p>• You can stop and resume at any point; your progress is saved.</p>"
 "<p>• If a statement is unclear, code it as best you can and say so in the notes.</p>")

pages=[page(1,[NOTE(INTRO,"intro"),TEXT("Your initials (so we can match your responses)","initials",1,3,True)],title="Introduction")]
itemmap=[]; pid=2; seq=0
for r in rows:
    seq+=1
    note=f"<blockquote><p>{html.escape(r['proposition'])}</p></blockquote>"
    pages.append(page(pid,[
        NOTE(note,f"{r['item_id']}-n"),
        CHOICE("Did this statement turn out to be correct?",["Correct","Incorrect","Cannot tell"],f"{r['item_id']}-a"),
        CHOICE("How confident are you in this assessment?",["High","Medium","Low"],f"{r['item_id']}-c"),
        MULTI("What sources did you use? (URLs, citations, or 'prior knowledge')",f"{r['item_id']}-s"),
        MULTI("Notes (ambiguity, comparators needing definition, why you hesitated)",f"{r['item_id']}-nt"),
    ],title=f"Item {seq}",desc=pretty(r["exact_date"])))
    itemmap.append({"survey_item":f"Item {seq}","item_id":r["item_id"],"kind":r["kind"],
        "band":r["band"],"orig_class":r["orig_class"],"flags":r["flags"],
        "exact_date":r["exact_date"],"proposition":r["proposition"]})
    pid+=1

survey={"pages":pages,"title":"SPI-M Yardstick Review",
    "settings":{"theme":{"text":{"color":"#1e2939","fontFamily":"Inter"},"title":{"color":"#1e2939","fontFamily":"Inter"},
        "borders":"#e5e7eb","elements":{"textColor":"#ffffff","backgroundColor":"#1e40af"},"background":{"color":"#ffffff"}}},
    "anonymous":False,
    "finalPage":{"content":"<p><strong>Thank you</strong></p><p></p><p>Your responses are recorded. Please do not "
        "discuss the items with the other reviewers until they have also finished.</p>","isLocked":False,"isEditing":False},
    "isEditing":False,"description":"","showDescription":False,"displayResponseID":False,
    "displayProgressBar":True,"displayQuestionNumbers":False,"pageReorderingDisabled":False,"displayResponseDownload":True}
json.dump(survey,open("data/SPI-M_Yardstick_Review_FINAL.json","w"),indent=1,ensure_ascii=False)
with open("data/survey_item_map.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(itemmap[0].keys())); w.writeheader(); w.writerows(itemmap)

import re
from collections import Counter
qids=[q["id"] for p in pages for q in p["questions"]]
PROB=re.compile(r'\b(likely|unlikely|almost certain|realistic possibility|probably|remote chance|highly (un)?likely|very (un)?likely)\b',re.I)
noteleak=sum(1 for p in pages for q in p["questions"] if q["type"]=="NOTE" and PROB.search(q["content"]))
dc=Counter(x["exact_date"] for x in itemmap)
iso=[x["item_id"] for x in itemmap if x["kind"]=="control" and dc[x["exact_date"]]==1]
print(f"SURVEY: {len(pages)} pages (1 intro + {seq} items)")
print(f"  q-ids unique: {len(set(qids))==len(qids)} | note leaks: {noteleak} | isolated controls: {iso or 'none'}")
print(f"  neutral titles: {all(re.match(r'Item \\d+$',p['title']) for p in pages if p['title'].startswith('Item'))}")
print(f"  kinds: {dict(Counter(x['kind'] for x in itemmap))}")
