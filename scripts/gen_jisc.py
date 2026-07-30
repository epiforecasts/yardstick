import csv, json, html
from itertools import count

rows = list(csv.DictReader(open("data/reviewer_frame.csv", encoding="utf-8")))
_id = count(90000001)
def nid(): return next(_id)
def lab(i): return f"b{i}"

def note(text):
    i=nid(); return {"class":"Note","data_question_visibility":"show","id":i,"label":lab(i),
                     "mandatory":"False","text":text}
def freetext(text, size=5, maxsize=5, fmt="single", mandatory="False"):
    i=nid(); return {"class":"FreeText","data_question_visibility":"show","displayOptionality":True,
                     "format":fmt,"id":i,"is_other":False,"label":lab(i),"mandatory":mandatory,
                     "maxsize":maxsize,"show_hints":True,"size":size,"text":text}
def mchoice(text, opts, mandatory="True"):
    i=nid()
    return {"class":"MultipleChoice","data_question_visibility":"show","displayLegend":False,
            "displayOptionality":True,"has_logic":False,"has_other":False,"id":i,"label":lab(i),
            "layout":"down","mandatory":mandatory,"text":text,
            "options":[{"class":"SelectionOption","id":nid(),"is_not_applicable":False,
                        "is_other":False,"screen_to_message":False,"text":o,"value":n+1}
                       for n,o in enumerate(opts)]}
def page(children):
    i=nid(); return {"class":"Page","data_question_visibility":"show","id":i,"label":lab(i),
                     "mandatory":"False","children":children}

INTRO = """<h2>Assessing probability statements about COVID-19</h2>
<p>You are assessing <strong>137 probability statements</strong> about COVID-19 epidemiology.
Each was made at the time shown (month and year). Your task is to judge, with hindsight,
whether each turned out to be correct.</p>
<p>Some items are constructed for quality-control purposes. Please code every item on its merits.</p>
<h3>For each claim you will give</h3>
<p><strong>An assessment</strong> &mdash; correct, incorrect, or cannot tell.</p>
<p><strong>A confidence, 0&ndash;100</strong> &mdash; your probability that the claim turned out
<em>correct</em>. 95 means near-certain it was right; 5 means near-certain it was wrong; 50 means you
genuinely do not know. This is your judgement of the claim's truth, not of your own reliability.</p>
<p><strong>Please give a confidence even when you cannot prove it.</strong> Many claims here concern
quantities only estimable through a model &mdash; the reproduction number, incidence, transmissibility.
You may be confident about such a claim while being unable to demonstrate it from evidence independent
of modelling. That is legitimate and expected. Record the confidence you actually hold, and use the
sources and notes boxes to say what it rests on.</p>
<p><strong>Sources used</strong> &mdash; what you actually consulted. This is how we report how each
judgement was settled, so please fill it in even when the answer felt obvious.</p>
<h3>Please note</h3>
<ul>
<li><strong>Do not discuss items with the other reviewer until you have both finished.</strong> The two
assessments must be independent; that is the point of having two.</li>
<li>The probability term and its numeric band show what the original author asserted. They are context,
<em>not a hint</em> &mdash; please do not let the stated confidence pull your assessment.</li>
<li>You can stop at any point and resume later; your progress is saved.</li>
<li>If a claim is unclear, code it as best you can and say so in the notes.</li>
</ul>"""

pages = [page([note(INTRO),
               freetext("Your initials (so we can match your responses)", size=8, maxsize=8,
                        mandatory="True")])]

for r in rows:
    band = f"{r['probability_term']} ({r['spim_band']})"
    ctx = (f"<p style='font-size:0.9em;color:#555'>Stated {html.escape(r['month_year'])} &mdash; "
           f"asserted as <strong>{html.escape(band)}</strong></p>"
           f"<blockquote style='font-size:1.1em;border-left:3px solid #ccc;padding-left:12px'>"
           f"{html.escape(r['claim'])}</blockquote>")
    pages.append(page([
        note(f"<p><strong>Claim {r['claim_id']}</strong></p>{ctx}"),
        mchoice("Did this claim turn out to be correct?",
                ["Correct", "Incorrect", "Cannot tell"]),
        freetext("Your confidence, 0&ndash;100: the probability that this claim turned out "
                 "<strong>correct</strong>. (95 = near-certain right, 5 = near-certain wrong, "
                 "50 = genuinely do not know.) Give this even if you cannot prove it.",
                 size=4, maxsize=3, mandatory="True"),
        freetext("What sources did you use? (URLs, citations, or 'prior knowledge')",
                 size=60, maxsize=2000, fmt="multi"),
        freetext("Notes (ambiguity in wording, comparators needing definition, why you hesitated)",
                 size=60, maxsize=2000, fmt="multi"),
    ]))

pages.append(page([note("<h3>Thank you</h3><p>Your responses are recorded. Please do not discuss "
                        "the items with the other reviewer until they have also finished.</p>")]))

tc_id = nid()
survey = {
  "class": "Survey", "id": nid(), "internal_title": "SPIM_Yardstick_Review_R01", "l10n": "en_GB",
  "runs": [{
    "class": "SurveyRun", "alert_frequency": 0, "alert_last_update": 0,
    "contact_message": "<p>For questions about this survey, please contact Sebastian Funk (sebastian.funk@lshtm.ac.uk).</p>",
    "discourage_search_engines": True, "expected_responses": 2,
    "external_title": "Assessing probability statements about COVID-19",
    "id": nid(),
    "login_message": "<p>Please sign in below using the credentials supplied to you.</p>",
    "notification_invite_body": "Dear [EMAIL]\r\nAn online survey has been created for you to complete.\r\n\r\n[CUSTOM_URL]\r\n\r\n- Online surveys Team",
    "notification_invite_subject": "You have been sent a survey to complete",
    "notification_reminder_body": "Dear [EMAIL]\r\nWe have not yet detected your response to our survey.\r\n\r\n[CUSTOM_URL]\r\n\r\n- Online surveys Team",
    "notification_reminder_subject": "Survey completion reminder",
    "permit_back_forth": True,
    "permit_finish_later": True,
    "permit_response_printout": True,
    "sender_name": "Jisc online surveys", "short_name": "spim_yardstick_review_r01",
    "show_completion_receipt": False, "show_numbering": False,
    "show_progress": True, "timezone": 346
  }],
  "top_container": {"class":"Container","data_question_visibility":"show","id":tc_id,
                    "label":lab(tc_id),"mandatory":"False","children":pages}
}
json.dump(survey, open("data/jisc_survey.json","w"), indent=1, ensure_ascii=False)

ids=[]
def w(o):
    if isinstance(o,dict):
        if isinstance(o.get("id"),int): ids.append(o["id"])
        for v in o.values(): w(v)
    elif isinstance(o,list):
        for v in o: w(v)
w(survey)
print(f"data/jisc_survey.json written")
print(f"  pages   : {len(pages)}  (1 intro + {len(rows)} claims + 1 close)")
print(f"  ids     : {len(ids)} total, unique={len(set(ids))==len(ids)}")
print(f"  size    : {len(open('data/jisc_survey.json').read())/1024:.0f} KB")
print(f"  permit_finish_later = True  <- save & resume")
print(f"  permit_back_forth   = True  <- revise earlier items")
