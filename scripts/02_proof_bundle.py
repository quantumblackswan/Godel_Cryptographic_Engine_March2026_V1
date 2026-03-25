#!/usr/bin/env python3
from __future__ import annotations
import copy, json, os, sys, time
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from gce.engine import GodelCryptoEngine
backend=sys.argv[1] if len(sys.argv)>1 else 'auto'; rounds=int(sys.argv[2]) if len(sys.argv)>2 else 50
eng=GodelCryptoEngine(backend_name=backend)
rt=wo=td=0; uniq=set()
for i in range(rounds):
    bit=i%2; pk, sk = eng.keygen(); c, o = eng.commit(pk, bit)
    if eng.verify(pk,c,o) and eng.open(sk,c)==bit: rt+=1
    bad=copy.deepcopy(o); object.__setattr__(bad,'message_bit',1-bit)
    if not eng.verify(pk,c,bad): wo+=1
    tc=copy.deepcopy(c); raw=bytearray(tc.c_g); raw[0]^=1; object.__setattr__(tc,'c_g',bytes(raw))
    if not eng.verify(pk,tc,o): td+=1
    uniq.add(eng.gnum.number_to_bytes(o.formula))
t0=time.perf_counter();
for _ in range(20):
    pk, sk = eng.keygen(); c, o = eng.commit(pk, 1); assert eng.verify(pk,c,o)
t1=time.perf_counter()
report={'backend': eng.backend_report()['backend'], 'round_trip': f'{rt}/{rounds}', 'wrong_opening_rejected': f'{wo}/{rounds}', 'tamper_detected': f'{td}/{rounds}', 'godel_number_uniqueness_sample': f'{len(uniq)}/{rounds} unique', 'backend_presence_test': {'passes':20, 'time_s': round(t1-t0,6)}}
Path('results').mkdir(exist_ok=True)
(Path('results')/f"proof_{report['backend']}.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
