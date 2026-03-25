#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from gce.engine import GodelCryptoEngine
backend=sys.argv[1] if len(sys.argv)>1 else 'auto'
eng=GodelCryptoEngine(backend_name=backend)
pk, sk = eng.keygen(); c, o = eng.commit(pk, 1)
report={'backend': eng.backend_report()['backend'], 'verify': bool(eng.verify(pk,c,o)), 'opened_bit': int(eng.open(sk,c)), 'commitment_size_bytes': c.size_bytes()}
Path('results').mkdir(exist_ok=True)
(Path('results')/f"smoke_{report['backend']}.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
