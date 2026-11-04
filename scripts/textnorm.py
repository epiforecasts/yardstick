"""Sentence normalisation shared by the scripts that match candidate statements."""
import re

def norm(s): return re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]','',(s or '').lower())).strip()

def keynorm(s):
    """Key that ignores embedded page headers and paragraph numbers, so restatements match."""
    s=re.sub(r'\b\d+ of \d+\b','',s or '')
    s=re.sub(r'\b(incidence|reproduction number|reissued|final)\b','',s,flags=re.I)
    s=re.sub(r'\d+','',s)
    return re.sub(r'\s+',' ',re.sub(r'[^a-z ]','',s.lower())).strip()
