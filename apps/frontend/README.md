# EchoSplit

Web-based audio splitting toolkit.

## Overview
EchoSplit packages the web UI and helper scripts for working with stem-splitting experiments. The project is built with Vite/TypeScript and can be run locally for development or bundled for npm publishing.

## Prerequisites
- Node.js 18+
- npm 9+
- (Optional) Python 3.10+ if you want to run the CLI helpers in `cli.py`

## Installation
Install dependencies from the project root:

```bash
cd EchoSplit
npm install
```

For Python-based helpers:

```bash
pip install -r requirements.txt
```

## Development
Start the dev server with hot reload:

```bash
npm run dev
```

Run the test suite:

```bash
npm test
```

Type-check the project:

```bash
npm run typecheck
```

## Building
Create an optimized production build:

```bash
npm run build
```

The output will live in `dist/` and can be published to npm after verification.

## Release workflow
1. Ensure dependencies are installed (`npm install`).
2. Run `npm test` and `npm run build` to verify the bundle.
3. Publish from the project directory:

```bash
npm publish
```

## Notes
- `node_modules/` is intentionally ignored and should never be committed. Re-install dependencies when switching machines or after cleaning the workspace.
- Keep example assets in `05_data/` and `07_docs/` so the published package stays lean.
