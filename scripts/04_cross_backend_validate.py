#!/usr/bin/env python3
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
ENV=os.environ.copy(); ENV['PYTHONPATH']=str(ROOT/'src')
backends=['keeper_mlkem_native','legacy_mlkem_alpha','libfips203_wrapper']
out={'runs':[]}
for backend in backends:
    entry={'backend':backend}
    for script,args in [('00_backend_probe.py',[]),('01_smoke_test.py',[]),('02_proof_bundle.py',['20']),('03_benchmark.py',['20'])]:
        cmd=[sys.executable, str(ROOT/'scripts'/script), backend, *args]
        proc=subprocess.run(cmd,capture_output=True,text=True,env=ENV)
        key=script.split('_',1)[1].replace('.py','')
        if proc.returncode==0:
            entry[key]=json.loads(proc.stdout)
        else:
            entry[key]={'status':'unavailable','stderr':proc.stderr.strip(),'stdout':proc.stdout.strip()}
    out['runs'].append(entry)
(ROOT/'results').mkdir(exist_ok=True)
(ROOT/'results'/'cross_backend_validation.json').write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
