#!/bin/bash
set -euo pipefail

require_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required tool '$1' is not installed or not on PATH." >&2
    exit 1
  fi
}

echo "🔍 Verifying release tooling"
require_tool python
require_tool twine
require_tool npm

python -c "import build" 2>/dev/null || {
  echo "Python package 'build' is required. Install it with 'pip install build'." >&2
  exit 1
}

echo "🧪 Running test suite"
pytest

echo "📦 Building and publishing Python packages"
for project in EchoDJ EchoPlay EdenOS_EchoShare; do
  echo "→ Releasing $project"
  pushd "$project" >/dev/null
  rm -rf dist
  python -m build
  twine upload --skip-existing dist/*
  popd >/dev/null
done

echo "📦 Publishing EchoSplit to npm"
pushd EchoSplit >/dev/null
npm install
npm test
npm run build
npm publish
popd >/dev/null

echo "✨ Release flow complete"
