Packaging Guide — eden-music-scene

Purpose: Steps to build, test, and prepare the project for commercial release.

1) Verify tests

Run the full test-suite:

```powershell
python -m pytest -q
```

2) Update metadata

Edit `pyproject.toml`:
- Set `version` appropriately (semantic versioning recommended).
- Confirm `authors`, `readme`, `license`, and `dependencies`.
- Add classifiers (e.g., `License :: OSI Approved :: MIT License`) if desired.

3) Build artifacts

Install build tools and create artifacts:

```powershell
python -m pip install --upgrade build wheel twine
# If your Python lacks the stdlib `venv` module, use the helper that avoids
# isolated builds (or install virtualenv). The helper installs build deps
# into the current interpreter and runs build without isolation:
python scripts/build_package.py
```

Artifacts will be in `dist/`.

4) Test installation in clean venv

```powershell
python -m venv .test-venv
.\.test-venv\Scripts\Activate.ps1
python -m pip install dist\*.whl
# Try CLI commands
echosplit --help
dj-agent --help
```

5) Static analysis (optional)

Run ruff/black/mypy to ensure code quality.

6) Prepare release assets

- Screenshots and short demo GIFs
- Short README / marketing blurb
- CHANGELOG with notable changes

7) Publish (manual)

Use `twine` with an API token:

```powershell
python -m twine upload dist\* -u __token__ -p <API_TOKEN>
```

8) CI (recommended)

Automate build and publish on GitHub Actions using `pypa/gh-action-pypi-publish` with a secret token.

Security & legal notes

- Remove private credentials and secrets from repo.
- Double-check licenses for included dependencies and music assets.
