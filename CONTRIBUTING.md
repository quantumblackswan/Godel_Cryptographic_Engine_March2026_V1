# Contributing

Thanks for taking a look.

This repository is a research artifact first. Please keep changes disciplined.

## Before opening a PR

- Run the scripts in `README.md`.
- Run the claim guard:

```bash
python scripts/check_claims.py paper/gce_commitment_arxiv.tex
```

- Keep manuscript claims aligned with recorded result files.
- Do not introduce production-readiness language unless backed by new evidence.
- Do not describe the Python glue as constant-time.

## Good contribution types

- backend integration cleanup
- reproducibility improvements
- better error reporting
- manuscript typo fixes
- benchmark harness cleanup
- native backend documentation

## Contribution style

- keep changes small and reviewable
- add or update JSON result artifacts when behavior changes
- update the paper only when the code and recorded results justify it
