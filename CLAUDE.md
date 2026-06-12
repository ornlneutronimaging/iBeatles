# iBeatles

PyQt GUI + headless CLI for Bragg-edge neutron imaging analysis (strain
mapping, TOF/wavelength binning) at ORNL. **FLAGSHIP application with active
users — see Working rules below.**

## Names

- PyPI/conda package: `ibeatles` (conda channel: `neutronimaging`, dev label
  auto-published from `next`)
- Python module: `ibeatles` (src layout); entry point `ibeatles`
  (`--no-gui` for the headless CLI)
- GitHub repo: `iBeatles`

## Working rules (flagship)

- Load-bearing changes (anything altering what the numbers pipeline
  produces — normalization, binning, fitting, strain, exports) require
  CIS (Jean) hands-on testing BEFORE merge: side-by-side runs on real data
  against the current release, numeric comparison of exported files. CI
  green + review is NOT sufficient for these.
- The NeuNorm 2.0 port decision (2026-06-12) is route (a): a true 2.0 port
  for `core/processing/normalization.py` (scipp DataArrays from in-memory
  stacks) with six semantic deltas bridged locally; the GUI twin in step2
  consolidates onto core; the four TIFF-writer sites drop NeuNorm for
  direct writes. Contract tests in
  `tests/unit/ibeatles/core/processing/test_normalization_contract.py`
  pin the 1.x numerics (inclusive ROI off-by-one, pooled multi-ROI,
  nanmedian fallback, zero-OB zeroing) — they are the port's gate.

## Environment and commands

Pixi-managed — run everything through `pixi run`.

- `pixi run test` — pytest with coverage
- Packaging lives in the isolated `package` env (`pixi run -e package
  build-conda` / `build`); boa's caps must not rejoin the default
  solve-group
- Python is capped `>=3.12,<3.13` for real reasons: the PyQt5/qt-main 5.15
  conda chain has no coherent 3.13/3.14 build set (verified 2026-06-12);
  revisit on Qt6 or newer conda-forge builds

## Delivery

- push to `next` → dev-conda-publish.yaml builds + uploads the dev conda
  package, then (and only then) triggers the GitLab pipeline that deploys
  to the analysis cluster (the ordering is deliberate — a duplicate
  unordered trigger was removed in #416)
- tags `v*` → publish.yaml: conda to neutronimaging + PyPI trusted
  publishing + GitHub release

## Conventions and caveats

- Committed notebooks keep executed outputs (recorded runs; see
  notebooks/README.md) — NEVER clear outputs; re-execute against real data
- `tests/data` references an SSH-only internal GitLab submodule; CI does
  not fetch it — data-dependent tests must skip cleanly without it
- `reference/` holds publisher PDFs (~28 MB) — redistribution rights
  unverified; do not add more
- Known deferred items: shipped config.json `debugging: true` +
  developer-path probe (fix queued for the CIS-tested batch), boa →
  rattler/pixi-build migration, lockfile-update PRs need a PAT to
  trigger CI
