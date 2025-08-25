#!/bin/bash

# Test GitHub Actions workflow locally with act
# Requires: act (https://github.com/nektos/act)

echo "Testing SOFA Pipeline GitHub Action locally"
echo "=========================================="

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "Error: 'act' is not installed"
    echo "Install with: brew install act"
    exit 1
fi

# Run the workflow
echo "Running workflow with act..."
act push \
    --job build-and-deploy \
    --workflows .github/workflows/sofa-pipeline.yml \
    --env-file .env.act \
    -P ubuntu-latest=catthehacker/ubuntu:act-latest

echo "Test complete!"