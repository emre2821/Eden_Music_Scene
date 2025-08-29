#!/bin/bash
set -e

# Build and publish Python packages
for project in EchoDJ EchoPlay EdenOS_EchoShare; do
  echo "Releasing $project"
  pushd "$project" >/dev/null
  python -m build
  twine upload dist/*
  popd >/dev/null
done

# Publish EchoSplit to npm
pushd EchoSplit >/dev/null
npm publish
popd >/dev/null
