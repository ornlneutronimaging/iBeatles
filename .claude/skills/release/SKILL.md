---
name: release
description: Cut a new iBeatles release — verify the promoted commit, create and push a v<X.Y.Z> tag, and confirm publish.yaml shipped conda (neutronimaging channel), PyPI (trusted publishing), and the GitHub release. iBeatles versions are tag-derived via versioningit, so there are NO version files to bump. Use when asked to "release", "cut a release", "tag a release", or "publish iBeatles".
disable-model-invocation: false
allowed-tools: Bash, Read, Grep, Glob, Agent
---

# Release Pipeline (iBeatles)

Cut a new iBeatles release. iBeatles versions are **derived from the git tag by
`versioningit`** (`dynamic = ["version"]`; it writes `src/ibeatles/_version.py` at
build time) — there are **no version files to edit**. A release is therefore: verify the
release commit, then **create and push a `v<X.Y.Z>` tag**. Everything else — build,
conda upload, PyPI trusted publishing, GitHub release — happens on CI in
`.github/workflows/publish.yaml` when the tag arrives. This skill gets the pre-flight
right, cuts the tag, and verifies CI published all three artifacts.

> ⚠️ **Do NOT edit any version string.** The version is computed from the tag. The only
> "bump" is choosing the tag name. (This is the key difference from the NEREIDS release
> skill, which bumps version fields in 5 files — iBeatles has none to bump.)

> ⚠️ **Flagship / load-bearing gate.** If the release commit changed the numbers pipeline
> (normalization, binning, fitting, strain, exports), CIS (Jean) must have validated it on
> real data BEFORE it was merged/promoted (CLAUDE.md "Working rules"). Do not cut a release
> tag on an unvalidated load-bearing change. CI-green is not sufficient for these.

> ℹ️ **Release (tags) is NOT the dev-deploy (next) path.** Pushing to `next` triggers
> `dev-conda-publish.yaml` (dev-label conda + the GitLab cluster deploy). That is the DEV
> path. This skill is the tagged RELEASE path (`publish.yaml`). Keep them separate.

## Arguments
- **No argument:** show the latest tag, propose the next version (default: patch bump),
  confirm the choice with the user before tagging.
- **`<version>`:** target version WITHOUT the leading `v` (e.g. `1.2.2`).
- **`--rc`:** cut a release candidate — tag `v<X.Y.Z>rc<N>`. CI uploads the conda package
  under the `rc` label and marks the GitHub release as a prerelease. Use for pre-release
  validation before a full release.
- **`--dry-run`:** build without publishing. Trigger the workflow via `workflow_dispatch`
  (`gh workflow run publish.yaml`); the `linux` build job runs but every upload/publish
  step is tag-gated (`if: startsWith(github.ref, 'refs/tags/v')`), so nothing is published.
  Do NOT push a tag for a dry run.

## Step 1 — Pre-flight gates
1. **On the release branch, clean tree.** Releases are cut from the promoted stable branch
   per the `next → qa → main` model. Confirm you are on the intended release commit
   (normally the tip of `main`) with a clean working tree.
2. **`origin` up to date.** `git fetch origin && git status` → up to date with the release
   branch; `git pull --ff-only` if behind.
3. **Promotion + integration gate done.** The release commit has completed `next → qa → main`
   promotion, its CI is green, and any load-bearing change was CIS-validated (gate above).
4. **Tag does not already exist.** Both must be empty:
   - `git tag -l v<version>` (local)
   - `git ls-remote --tags origin v<version>` (remote)
5. **Secrets (informational).** conda upload needs the `ANACONDA_TOKEN` repo secret; PyPI
   uses **trusted publishing** (OIDC — no token; configured on PyPI against the
   `publish.yaml` filename, so no per-release setup, see #423); the GitHub release uses the
   built-in `GITHUB_TOKEN`.

## Step 2 — Pick the version
- Latest tag: `git describe --tags --abbrev=0` (e.g. `v1.2.1`).
- SemVer `vMAJOR.MINOR.PATCH`. Choose patch/minor/major deliberately with the user.
  (versioningit's own `next-version` heuristic is `minor`, but the release version is
  whatever you tag.)
- RC: append `rc<N>`, e.g. `v1.2.2rc1`. The lowercase substring `rc` is what flips the
  conda label to `rc` and the GitHub release to prerelease — a typo like `RC1` won't match.

## Step 3 — Create and push the tag (this is the trigger)
```
git tag -a v<X.Y.Z> -m "Release v<X.Y.Z>"    # add -s to sign if your git is configured for GPG
# push the release branch first if it has unpushed commits, so the tagged commit is on origin:
git push origin <release-branch>
git push origin v<X.Y.Z>
```
- The tag **message** is minor — the GitHub release body is auto-generated
  (`generate_release_notes: true`) from merged PRs since the previous tag. Keep it short.
- `publish.yaml` fires on `tags: ['v*']`.
- **`--dry-run`:** skip the tag entirely; run `gh workflow run publish.yaml` and watch the
  build only.

## Step 4 — Monitor the pipeline
```
gh run watch $(gh run list --repo ornlneutronimaging/iBeatles --workflow=publish.yaml \
  --limit 1 --json databaseId --jq '.[0].databaseId')
```
Jobs (from `.github/workflows/publish.yaml`):
1. **`linux`** — builds the conda package (`pixi run -e package build-conda`) and the PyPI
   package (`pixi run -e package build`); on a tag it uploads conda to the `neutronimaging`
   channel (label `main`, or `rc` when the tag contains `rc`) and uploads the conda + PyPI
   build artifacts.
2. **`pypi-publish`** (tag-only, `needs: linux`) — downloads the PyPI artifact and publishes
   to PyPI via **trusted publishing**. `id-token: write` is isolated to this job (never
   present while fork-PR build code runs — #423).
3. **`github-release`** (tag-only, `needs: linux`) — downloads both artifacts and creates the
   GitHub Release with auto-generated notes; `prerelease: true` for `rc`/`alpha`/`beta` tags.

## Step 5 — Verify artifacts landed
Run all three; report any MISSING explicitly.
```
V=<X.Y.Z>
# PyPI
curl -sf "https://pypi.org/pypi/ibeatles/${V}/json" >/dev/null && echo "PyPI OK" || echo "PyPI MISSING"
# conda on the neutronimaging channel (lists all versions; grep the new one)
curl -sf "https://api.anaconda.org/package/neutronimaging/ibeatles" | grep -q "\"${V}\"" \
  && echo "conda OK" || echo "conda MISSING"
# GitHub release
gh release view "v${V}" --repo ornlneutronimaging/iBeatles >/dev/null 2>&1 \
  && echo "release OK" || echo "release MISSING"
```
For an RC, confirm the package is under the `rc` label at
`https://anaconda.org/neutronimaging/ibeatles/files`.

## Step 6 — Post-release housekeeping
1. Open the GitHub Release page; confirm the auto-notes captured the expected PRs and the
   assets include the conda `.tar.bz2` and the PyPI sdist/wheel.
2. Confirm the conda package appears under the correct label (`main` for a full release,
   `rc` for an RC).
3. **Memory:** record only a non-obvious release lesson (a new/expired secret, a CI flake,
   a recipe gotcha). Routine outcomes are not memory-worthy.

## Step 7 — Report
```markdown
### iBeatles v<X.Y.Z> — published

| Artifact | Status | URL |
|---|---|---|
| GitHub Release | ✓ | https://github.com/ornlneutronimaging/iBeatles/releases/tag/v<X.Y.Z> |
| PyPI (ibeatles) | ✓ | https://pypi.org/project/ibeatles/<X.Y.Z>/ |
| conda (neutronimaging) | ✓ | https://anaconda.org/neutronimaging/ibeatles |

Pipeline: <publish.yaml run URL>
Release notes auto-generated from PRs since v<PREV>.
```
If this was an `--rc`, say so and note the `rc` label / prerelease flag.

## Failure modes & remediation
- **Tag exists local vs origin mismatch.** `git tag -d v<X.Y.Z>` (local) or
  `git push --delete origin v<X.Y.Z>` (remote), then re-tag and push fresh.
- **`pypi-publish` failed after a partial upload.** PyPI rejects re-uploading the same
  version/filename, so re-running the same tag won't republish. Fix: cut the next patch
  (`v<X.Y.Z+1>`) and re-release. (If it errors with an OIDC / trusted-publisher message,
  confirm PyPI's trusted publisher is configured against the `publish.yaml` workflow — #423;
  no per-release change is normally needed.)
- **conda upload failed.** Usually a missing/expired `ANACONDA_TOKEN`, or the build produced
  no `conda.recipe/noarch/ibeatles*.tar.bz2`. Check the `linux` job log.
- **conda build itself failed** (`Cannot import 'hatchling.build'`, or a `git+` source dep).
  See #411 — the recipe must install NeuNorm from the `neutronimaging` conda channel, NOT a
  `git+` source. Do not reintroduce a `git+NeuNorm` build install.
- **Pipeline didn't start after the tag push.** The tag must match `v*`, and the branch must
  be pushed so the tagged commit is reachable on origin. Check the Actions tab and that the
  workflow is enabled.
- **Wrong conda label / prerelease flag.** Both are driven by whether the tag string contains
  `rc` (`v1.2.2rc1` → conda `rc` + GitHub prerelease; `v1.2.2` → conda `main`). Use lowercase
  `rc`/`alpha`/`beta`.
