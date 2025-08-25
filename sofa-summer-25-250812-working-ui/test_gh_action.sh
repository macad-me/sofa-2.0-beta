#!/bin/bash
# Test GitHub Actions locally with act

set -e

echo "=== Testing GitHub Actions with act ==="
echo "This will simulate the GitHub Actions workflow locally"
echo

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "Installing act..."
    brew install act
fi

# Create environment file for act if it doesn't exist
if [ ! -f .github/workflows/.env.act ]; then
    echo "Creating environment file for act..."
    mkdir -p .github/workflows
    cat > .github/workflows/.env.act << 'EOF'
GITHUB_REPOSITORY=macadmins/sofa
GITHUB_REF=refs/heads/main
GITHUB_SHA=test-sha
GITHUB_RUN_ID=test-run
GITHUB_RUN_NUMBER=1
EOF
fi

# First, let's check the current state
echo "=== Current state check ==="
echo "1. Checking cache directories..."
for dir in data-processing/data/cache data-processing/cache; do
    if [ -d "$dir" ]; then
        echo "  $dir exists:"
        echo "    HTML files: $(find "$dir" -name "*.html" 2>/dev/null | wc -l)"
        echo "    JSON files: $(find "$dir" -name "*.json" 2>/dev/null | wc -l)"
        echo "    Total size: $(du -sh "$dir" 2>/dev/null | cut -f1)"
    else
        echo "  $dir does not exist"
    fi
done

echo
echo "2. Checking existing feeds..."
for dir in v1 data-processing/data/feeds/v1; do
    if [ -d "$dir" ]; then
        echo "  $dir exists with $(ls "$dir"/*.json 2>/dev/null | wc -l) JSON files"
    else
        echo "  $dir does not exist"
    fi
done

echo
echo "=== Running act (dry run first) ==="
echo "This shows what would happen without actually running..."
act push -W .github/workflows/build-feeds.yml --job build --dryrun || true

echo
read -p "Do you want to run the actual workflow? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "=== Running actual workflow with act ==="
    act push -W .github/workflows/build-feeds.yml --job build -v
    
    echo
    echo "=== Post-run check ==="
    echo "Checking generated feeds..."
    for dir in v1 data-processing/data/feeds/v1 data-processing; do
        if [ -d "$dir" ]; then
            echo "  Files in $dir:"
            ls -la "$dir"/*.json 2>/dev/null | head -5 || echo "    No JSON files"
        fi
    done
else
    echo "Skipping actual run"
fi

echo
echo "=== Diagnostics complete ==="