#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys, traceback
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from gce.kem_wrappers.keeper_mlkem_wrapper import KeeperMlkemSkeleton
from gce.kem_wrappers.libfips203_wrapper import LibFips203Skeleton
OUT=Path('results'); OUT.mkdir(exist_ok=True)

def run_probe(name, cls):
    result={'wrapper':name}
    try:
        w=cls(); pk, sk = w.keygen(); ss, ct = w.encaps(pk); ss2 = w.decaps(sk, ct)
        result.update({'status':'available','round_trip_match':ss==ss2,'public_key_bytes':len(pk.to_bytes()),'private_key_bytes':len(sk.to_bytes()),'ciphertext_bytes':len(ct.to_bytes()),'shared_secret_bytes':len(ss)})
    except Exception as exc:
        result.update({'status':'unavailable','error':str(exc),'traceback':traceback.format_exc()})
    return result

def main():
    keeper=run_probe('keeper_mlkem_skeleton', KeeperMlkemSkeleton)
    fips=run_probe('libfips203_skeleton', LibFips203Skeleton)
    (OUT/'wrapper_probe_keeper_mlkem_skeleton.json').write_text(json.dumps(keeper, indent=2))
    (OUT/'wrapper_probe_libfips203_skeleton.json').write_text(json.dumps(fips, indent=2))
    bundle={'keeper_mlkem_skeleton':keeper,'libfips203_skeleton':fips}
    (OUT/'wrapper_probe_bundle.json').write_text(json.dumps(bundle, indent=2))
    print(json.dumps(bundle, indent=2))
if __name__=='__main__':
    main()
