# GCE Reference Prototype

Public research repository for the paper **“Incompleteness-Secured Commitments: a Dual-Layer Post-Quantum Framework with Reproducibility Guards, Wrapper Portability Probes, and an ML-KEM-768 Reference Prototype.”**

This repository packages the manuscript, reference code, reproducibility scripts, and recorded run outputs in one place.

## Status

This codebase is a **reference prototype**.

It is **not production-ready**.
It does **not** claim constant-time behavior for the Python orchestration layer.
It does **not** provide a full IND-CPA, IND-CCA, or UC proof of the complete construction.
It does preserve archived continuity measurements together with newer reruns and wrapper-portability probes.

## What is in this repo

- `paper/` — final paper PDF, TeX source, and manuscript support files.
- `src/gce/` — engine, formal-system helpers, Gödel numbering, and backend selection logic.
- `src/gce/kem_wrappers/` — skeleton wrappers for keeper-ML-KEM and libfips203 style integrations.
- `scripts/` — backend probe, smoke test, proof bundle, benchmark, wrapper probe, cross-backend validation, and manuscript claim guard.
- `results/` — JSON outputs from archived runs, current reruns, and wrapper status probes.
- `tests/` — basic property-style tests.

## Repository posture

This repository is designed for:

- reproducibility
- manuscript support
- code review
- security review
- benchmarking and comparison

It is **not** designed for deployment into paid or production cryptographic services.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
```

Run the main reproducibility path:

```bash
python scripts/00_backend_probe.py legacy_mlkem_alpha
python scripts/01_smoke_test.py legacy_mlkem_alpha
python scripts/02_proof_bundle.py legacy_mlkem_alpha 20
python scripts/03_benchmark.py legacy_mlkem_alpha 20
python scripts/04_cross_backend_validate.py
python scripts/05_probe_wrapper_status.py
python scripts/check_claims.py paper/gce_commitment_arxiv.tex
```

## Main recorded result lines

### Archived continuity lines kept in the paper

| Line | Keygen ms | Commit ms | Verify ms | Open ms | Size bytes |
|---|---:|---:|---:|---:|---:|
| Archived baseline | 0.566 | 0.861 | 0.023 | 0.902 | 1153 |
| Archived continuity | 0.580 | 0.870 | 0.025 | 0.910 | 1153 |

### Current rerun line in this package

| Backend | Trials | Keygen ms | Commit ms | Verify ms | Open ms | Size bytes |
|---|---:|---:|---:|---:|---:|---:|
| legacy_mlkem_alpha | 20 | 0.407 | 0.627 | 0.018 | 0.658 | 1153 |

### Cross-backend validation snapshot

| Backend | Status | Keygen ms | Commit ms | Verify ms | Open ms | Size bytes |
|---|---|---:|---:|---:|---:|---:|
| keeper_mlkem_native | passed | 0.343 | 0.503 | 0.011 | 0.514 | 1153 |
| legacy_mlkem_alpha | passed | 0.314 | 0.477 | 0.011 | 0.513 | 1153 |
| libfips203_wrapper | unavailable | — | — | — | — | — |

Wrapper probe details are recorded in `results/wrapper_probe_bundle.json`.

## Honest backend note

The repository includes wrapper skeletons because backend portability matters. The recorded wrapper probe currently shows:

- `keeper_mlkem_skeleton`: unavailable in the probed environment because the installed `mlkem` package did not expose the expected `ML_KEM` API.
- `libfips203_skeleton`: unavailable in the probed environment because `fips203` was not importable or the required native shared library was missing, depending on the run path.

That means the wrapper layer should be treated as **template code plus recorded audit evidence**, not as validated portable production integration.

## Claim guard

The manuscript claim guard helps stop drift back into unsupported language.

It checks for banned phrases such as:

- `NBQP-hard`
- `production-ready`
- strict hierarchy language
- category-positioning drift

It also checks that required caveat language remains present.

Run it with:

```bash
python scripts/check_claims.py paper/gce_commitment_arxiv.tex
```

## Citation

Please cite both the paper and the repository artifact.

- See `CITATION.cff` for GitHub citation support.
- The manuscript source is in `paper/gce_commitment_arxiv.tex`.

## License

This repository is released under **Business Source License 1.1** with an eventual change to Apache-2.0.

That means you can publish the repo publicly, allow review and academic use, and still preserve a monetization path before the change date.

See:

- `LICENSE`
- `LICENSE.md`

## Suggested GitHub repo description

> Reference prototype and reproducibility artifact for an ML-KEM-768-based incompleteness-secured commitment framework with claim guards, benchmark scripts, and wrapper portability probes.

## Suggested GitHub topics

`cryptography` `post-quantum-cryptography` `ml-kem` `research-artifact` `reproducibility` `python` `formal-methods`

## Patent notice

Patent pending. See `NOTICE` for the application notice.
