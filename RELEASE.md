# Release Process

The Eden Music Scene constellation ships several packages (Python and npm).
This ritual keeps every release predictable and reviewable.

## 1. Preflight checklist

1. Confirm the next version and update every affected `pyproject.toml` or
   `package.json`.
2. Capture the changes inside `CHANGELOG.md` and, if needed, `UPGRADEME.md`.
3. Log in to PyPI (`twine`) and npm (`npm login`) on the machine running the
   release.
4. Install the tooling (once per workstation):
   ```bash
   pip install build twine
   npm install
   ```

## 2. Dry runs and verification

* Run `pytest` locally to ensure the suite is green.
* Optionally produce artifacts to inspect them manually:
  ```bash
  python -m build
  twine check dist/*
  ```
  Remember to delete the temporary `dist/` directory afterwards.

## 3. Execute the release script

From the repository root run:

```bash
./release.sh
```

The script now:

1. Verifies `python`, `twine`, `npm`, and the Python `build` module exist.
2. Runs the full `pytest` suite before any artifacts are created.
3. For each Python package (`EchoDJ`, `EchoPlay`, `EdenOS_EchoShare`):
   * Clears any stale `dist/` contents.
   * Builds via `python -m build`.
   * Uploads to PyPI with `twine upload --skip-existing`.
4. Publishes the `EchoSplit` package to npm with `npm publish`.

If a command fails the process aborts immediately—no partial releases.

## 4. Tag the release

Create and push a signed git tag when the script succeeds:

```bash
git tag -s vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

## 5. Post-release follow-up

* Announce the release to the Dreambearer channels.
* File any follow-up issues or chores the release surfaced.
* Celebrate—resonance maintained.
