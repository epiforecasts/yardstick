import csv, json, html, hashlib

rows = list(csv.DictReader(open("data/reviewer_frame.csv", encoding="utf-8")))
_qn = [0]
def qnum():
    _qn[0] += 1
    return _qn[0]
_ctr = [0]
def qid(seed):
    _ctr[0] += 1
    n = int(hashlib.sha1(f"{seed}-{_ctr[0]}".encode()).hexdigest(), 16)
    alpha = "abcdefghijklmnopqrstuvwxyz0123456789"; s = ""
    while len(s) < 25:
        n, r = divmod(n, 36); s += alpha[r]
    return s[:25]
def optid(seed): return int(hashlib.sha1(seed.encode()).hexdigest(), 16) % 90000 + 10000

def NOTE(content, seed):
    return {"id": qid(seed), "type": "NOTE", "content": content, "readonly": True, "isEditing": False}
def CHOICE(title, opts, seed):
    return {"id": qid(seed), "type": "CHOICE", "title": title,
            "values": [{"id": optid(f"{seed}-{o}"), "value": o, "allowComments": False} for o in opts],
            "isEditing": False, "isRequired": True, "multicheck": False, "questionNumber": qnum(),
            "randomiseOptionsOrder": False, "prePopulationVisibility": "SHOW", "titlePlainText": title}
def NUMBER(title, seed, lo=0, hi=100, required=True):
    return {"id": qid(seed), "type": "SINGLE_LINE", "title": title, "readonly": False,
            "isEditing": False, "isRequired": required,
            "validation": {"max": hi, "min": lo, "enabled": True, "inputType": "number-integer"},
            "defaultValue": None, "questionNumber": qnum(),
            "prePopulationVisibility": "SHOW", "titlePlainText": title}
def TEXT(title, seed, lo, hi, required=False):
    return {"id": qid(seed), "type": "SINGLE_LINE", "title": title, "readonly": False,
            "isEditing": False, "isRequired": required,
            "validation": {"max": hi, "min": lo, "enabled": True, "inputType": "text"},
            "questionNumber": qnum(), "prePopulationVisibility": "SHOW", "titlePlainText": title}
def MULTI(title, seed, lines=5, required=False):
    return {"id": qid(seed), "type": "MULTI_LINE", "lines": lines, "title": title,
            "readonly": False, "isEditing": False, "isRequired": required, "questionNumber": qnum(),
            "prePopulationVisibility": "SHOW", "titlePlainText": title}
def page(pid, questions, title="", description="", showTitle=False, showDescription=False):
    return {"id": pid, "title": title, "isLocked": False, "isEditing": False,
            "questions": questions, "showTitle": showTitle, "description": description,
            "showDescription": showDescription, "preventNewQuestions": False}

INTRO = ("<p><strong>Assessing probability statements about COVID-19</strong></p><p></p>"
 "<p>You are assessing <strong>137 probability statements</strong> about COVID-19 epidemiology. "
 "Each was made at the time shown (month and year). Your task is to judge, with hindsight, whether "
 "each turned out to be correct.</p>"
 "<p>Some items are constructed for quality-control purposes. Please code every item on its merits.</p><p></p>"
 "<p><strong>For each claim you will give</strong></p>"
 "<p><strong>An assessment</strong> — correct, incorrect, or cannot tell.</p>"
 "<p><strong>A confidence in that assessment</strong>, from 0 to 100. This is how sure you are of the "
 "judgement you just made, not the probability the claim was correct. If a claim genuinely cannot be "
 "resolved, a confident answer is <em>“cannot tell” with high confidence</em> — 100 is entirely "
 "appropriate there. Likewise you may be fully confident a claim was incorrect even when you cannot "
 "prove it from evidence independent of modelling.</p>"
 "<p>Many claims here concern quantities only estimable through a model — the reproduction number, "
 "incidence, transmissibility. Being unable to demonstrate such a claim from independent evidence is "
 "expected; record the assessment and confidence you actually hold, and use the sources and notes "
 "boxes to say what they rest on.</p>"
 "<p><strong>Sources used</strong> — what you actually consulted. This is how we report how each "
 "judgement was settled, so please fill it in even when the answer felt obvious.</p><p></p>"
 "<p><strong>Please note</strong></p>"
 "<p>• <strong>Do not discuss items with the other reviewer until you have both finished.</strong> "
 "The two assessments must be independent; that is the point of having two.</p>"
 "<p>• The probability term and its numeric band show what the original author asserted. They are "
 "context, <em>not a hint</em> — please do not let the stated confidence pull your assessment.</p>"
 "<p>• You can stop at any point and resume later; your progress is saved.</p>"
 "<p>• If a claim is unclear, code it as best you can and say so in the notes.</p>")

pages = [page(1,
    [NOTE(INTRO, "intro-note"),
     TEXT("Your initials (so we can match your responses)", "initials", lo=1, hi=3, required=True)],
    title="Introduction")]

pid = 2
for r in rows:
    note = (f"<p>Asserted as <strong>{html.escape(r['probability_term'])}</strong> ({r['spim_band']})</p>"
            f"<p></p><p>{html.escape(r['claim'])}</p>")
    pages.append(page(pid,
        [NOTE(note, f"{r['claim_id']}-note"),
         CHOICE("Did this claim turn out to be correct?",
                ["Correct", "Incorrect", "Cannot tell"], f"{r['claim_id']}-choice"),
         NUMBER("How confident are you in this assessment? (0 = no confidence, 100 = full confidence)",
                f"{r['claim_id']}-conf"),
         MULTI("What sources did you use? (URLs, citations, or 'prior knowledge')", f"{r['claim_id']}-src"),
         MULTI("Notes (ambiguity in wording, comparators needing definition, why you hesitated)", f"{r['claim_id']}-notes")],
        title=f"Claim {r['claim_id']}", description=f"Stated {html.escape(r['month_year'])}.",
        showTitle=True, showDescription=True))
    pid += 1

survey = {
    "pages": pages, "title": "SPI-M Yardstick Review",
    "settings": {"theme": {"text": {"color": "#1e2939", "fontFamily": "Inter"},
        "title": {"color": "#1e2939", "fontFamily": "Inter"}, "borders": "#e5e7eb",
        "elements": {"textColor": "#ffffff", "backgroundColor": "#1e40af"},
        "background": {"color": "#ffffff"}}},
    "anonymous": False,
    "finalPage": {"content": "<p><strong>Thank you</strong></p><p></p><p>Your responses are recorded. "
        "Please do not discuss the items with the other reviewer until they have also finished.</p>",
        "isLocked": False, "isEditing": False},
    "isEditing": False, "description": "", "showDescription": False, "displayResponseID": False,
    "displayProgressBar": True, "displayQuestionNumbers": False, "pageReorderingDisabled": False,
    "displayResponseDownload": True,
}
json.dump(survey, open("data/jisc_survey_native.json", "w"), indent=1, ensure_ascii=False)
qids=[q["id"] for p in pages for q in p["questions"]]
print(f"written: {len(pages)} pages (1 intro + {len(rows)} claims), {len(open('data/jisc_survey_native.json').read())/1024:.0f} KB")
print(f"question ids unique: {len(set(qids))==len(qids)} ({len(qids)})")
