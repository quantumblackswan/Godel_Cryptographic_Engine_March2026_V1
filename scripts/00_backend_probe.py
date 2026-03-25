#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from gce.engine import GodelCryptoEngine
backend=sys.argv[1] if len(sys.argv)>1 else 'auto'
eng=GodelCryptoEngine(backend_name=backend)
report=eng.backend_report(); report['selected_backend_argument']=backend
Path('results').mkdir(exist_ok=True)
(Path('results')/f"backend_probe_{report['backend']}.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
