# Distribution and update workflow

The repository has one canonical source: `source/`, `adapters/`, `install.sh`, `platform-manifest.json` and `source-hashes.tsv`. Do not edit generated npm/pip staging copies by hand.

## Build locally

```bash
./scripts/build-distributions.sh
cd dist/npm && npm pack
cd ../pip && python -m build
```

Publish only after running `scripts/pack-smoke-test.sh`, npm package tests, pip wheel tests and a clean isolated install test. Sign release artifacts and publish SHA-256 checksums.

## Global npm installation

```bash
npm install --global @ai-project-pack/cli
ai-project-pack --target /path/to/project --all
```

## Global pip installation

```bash
python -m pip install ai-project-pack
ai-project-pack --target /path/to/project --all
```

## Existing project update

The installer records managed-file fingerprints in `.ai-pack/managed-files.tsv` and package version in `.ai-pack/installation.json`.

```bash
ai-project-pack --target /path/to/project --all --check
ai-project-pack --target /path/to/project --all --update --merge
ai-project-pack --target /path/to/project --all --update --yes
```

`--check` never writes files and returns exit code 1 when a managed file is missing, outdated or locally modified. `--merge` presents `update`, `keep`, `diff`, and `skip` choices. `--update --yes` applies upstream files non-interactively, but every replaced file is backed up under `.ai-pack/backup/`.

Do not silently overwrite project-specific `AGENTS.md`, `PROJECT_STATUS.md`, security policies, credentials, or platform session files. Treat those as human-owned unless an explicit merge decision has been made.
