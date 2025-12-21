Eden Music Scene — Packaging & Commercial Release Guide

This document helps package, market, and sell the "Eden Music Scene" product.
It assumes you have a working codebase and tests passing (run `python -m pytest`).

Quick summary

- Package name: eden-music-scene
- Console scripts exposed: `dj-agent`, `echoplay-prequel`, `echosplit`
- Python requirement: >=3.10

Quickstart (local install)

1. Create a venv and activate it:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install build tools and dependencies for packaging:

```powershell
python -m pip install --upgrade pip build twine wheel
```

3. Build distributions:

```powershell
python -m build
```

4. Install locally to test entry points:

```powershell
python -m pip install dist\eden-music-scene-0.1.0-py3-none-any.whl
# then run
echosplit --help
dj-agent --help
```

Running the product locally

- Frontend: `echosplit` will run `apps/frontend/04_src/00_core/main.py`. Provide `--audio` or set `AUDIO_PATH` in `.env` and pass `--lyrics`.
- DJ agent GUI: `dj-agent` launches a Tk window (requires `yt-dlp`/`ffmpeg` for full features).

Packaging checklist

- Ensure `pyproject.toml` metadata is complete: authors, license, version, description, dependencies.
- Remove or vendor any large audio assets you cannot license.
- Verify all third-party dependencies have compatible licenses for commercial distribution.
- Add a clear EULA or commercial license (see `EULA_TEMPLATE.txt`).
- Add product screenshots and marketing assets in `assets/` (optimize sizes).
- Digital signing (Windows/Mac) for trustworthiness.

Publishing to PyPI (recommended for Python distribution)

1. Register an account at https://pypi.org/
2. Create an API token and add it to your repository secrets (GITHUB_PYPI_API_TOKEN).
3. Upload using Twine (locally or CI):

```powershell
python -m twine upload dist/* -u __token__ -p <API_TOKEN>
```

Commercial distribution options

- PyPI (free/public) — good for open source or paid-license via separate transaction.
- Private PyPI or artifact repository (e.g., Gemfury, Artifactory).
- Native installers (Windows MSI/EXE, macOS app bundle) — use pyinstaller/briefcase for single-file apps.
- App stores & marketplaces — requires platform-specific packaging and signing.

Legal & music rights checklist (CRITICAL)

- Do not bundle copyrighted audio unless you own the rights or have redistribution licenses.
- If your product uses YouTube downloads or streaming, disclose terms and ensure compliance with providers' TOS.
- Consult a lawyer for a proper commercial license and EULA tailored to selling software that helps users handle music.

Support & maintenance

- Provide a support email or issue tracker link in `README_PUBLISH.md` and packaged docs.
- Decide on update cadence and deprecation policy.

Contact & next steps

If you want, I can:
- Add a CI workflow that builds and uploads releases to PyPI when a GitHub Release is created.
- Create a minimal EULA template and mark the repo with a `LICENSE_COMMERCIAL.md`.
- Produce marketing README content adapted for a sales page / product website.
