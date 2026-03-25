#!/usr/bin/env python3
from __future__ import annotations
import json, os, statistics as stats, sys, time
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from gce.engine import GodelCryptoEngine
def measure(fn, trials):
    xs=[]; last=None
    for _ in range(trials):
        t0=time.perf_counter_ns(); last=fn(); t1=time.perf_counter_ns(); xs.append((t1-t0)/1e6)
    return round(stats.mean(xs),3), round(stats.pstdev(xs),3), last
backend=sys.argv[1] if len(sys.argv)>1 else 'auto'; trials=int(sys.argv[2]) if len(sys.argv)>2 else 30
eng=GodelCryptoEngine(backend_name=backend)
kg, kgsd, keys = measure(lambda: eng.keygen(), trials); pk, sk = keys
cm, cmsd, out = measure(lambda: eng.commit(pk,1), trials); c, o = out
vm, vmsd, _ = measure(lambda: eng.verify(pk,c,o), trials)
om, omsd, _ = measure(lambda: eng.open(sk,c), trials)
report={'backend': eng.backend_report()['backend'], 'trials': trials, 'keygen_ms': kg, 'commit_ms': cm, 'verify_ms': vm, 'open_ms': om, 'keygen_stdev_ms': kgsd, 'commit_stdev_ms': cmsd, 'verify_stdev_ms': vmsd, 'open_stdev_ms': omsd, 'commitment_size_bytes': c.size_bytes()}
Path('results').mkdir(exist_ok=True)
(Path('results')/f"benchmark_{report['backend']}.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
