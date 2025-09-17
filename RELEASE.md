# Release Process

Each subproject uses [semantic versioning](https://semver.org/).

1. Update the version numbers in the relevant `pyproject.toml` or `package.json` files.
2. Update `CHANGELOG.md` with a summary of the changes.
3. Run the release script:
   ```bash
   ./release.sh
   ```
   This script builds Python packages with `python -m build` and uploads them via `twine`, then publishes the EchoSplit package with `npm publish`.
4. Create a git tag for the new version and push it:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

Ensure you have credentials configured for PyPI and npm before running the script.
