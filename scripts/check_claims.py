#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding='utf-8')
hard_banned = [r'kyber-py', r'NBQP-hard', r'strictly stronger than all existing PQC systems', r'quant-ph', r'drop-in replacement for Kyber', r'NIST PQC Round 5']
soft_banned = [(r'production-ready', r'not\s+production-ready|do\s+not\s+claim\s+production\s+readiness')]
required = [r'reference prototype', r'ML-KEM-768', r'key-encapsulation mechanism', r'(we\s+do\s+not\s+claim\s+production\s+readiness|not\s+production-ready)', r'we\s+do\s+not\s+claim\s+constant-time\s+behavior\s+for\s+the\s+Python\s+orchestration\s+layer']
bad=[]
for pat in hard_banned:
    if re.search(pat, text, flags=re.I): bad.append(pat)
for pat, allowed in soft_banned:
    for m in re.finditer(pat, text, flags=re.I):
        window=text[max(0,m.start()-80):min(len(text),m.end()+80)]
        if not re.search(allowed, window, flags=re.I):
            bad.append(pat); break
missing=[pat for pat in required if not re.search(pat, text, flags=re.I)]
if bad or missing:
    print('BANNED:', bad); print('MISSING:', missing); raise SystemExit(1)
print('Claim check passed.')
