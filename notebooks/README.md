# Notebooks

These notebooks document the headless (`--no-gui`) iBeatles workflow:

- `ibeatles_cli_step_by_step.py` — marimo notebook (source of truth)
- `cli_step_by_step.ipynb` — Jupyter version

## Provenance of the committed outputs

Both notebooks are committed WITH executed outputs (repo convention: browsers
read the expected results on GitHub without setting up an environment). The
outputs document a recorded run against `tests/data/json/demo_config.json`,
whose data paths point at the original analysis machine — re-executing the
notebooks therefore requires adapting the config paths to a local copy of the
referenced IPTS datasets. Refresh outputs by re-running against real data;
NEVER clear them.
