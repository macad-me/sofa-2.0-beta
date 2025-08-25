#!/bin/bash
set -e

echo "=== Testing SOFA Pipeline ==="
cd data-processing

echo "1. Setting up environment..."
uv venv >/dev/null 2>&1 || true
uv pip sync pyproject.toml >/dev/null 2>&1

echo "2. Running pipeline (stages 2 & 3 - using cache)..."
uv run python src/pipeline/run_sofa_pipeline.py --stages 2 3 --skip-v2

echo "3. Checking generated feeds..."
if [ -f data/feeds/v1/macos_data_feed.json ]; then
    echo "✅ macOS feed generated"
    echo "   Size: $(wc -c < data/feeds/v1/macos_data_feed.json) bytes"
    echo "   OS versions: $(jq '.OSVersions | length' data/feeds/v1/macos_data_feed.json)"
else
    echo "❌ macOS feed NOT found"
    exit 1
fi

if [ -f data/feeds/v1/ios_data_feed.json ]; then
    echo "✅ iOS feed generated"
else
    echo "❌ iOS feed NOT found"
    exit 1
fi

echo ""
echo "=== Testing version extraction ==="
uv run python -c "
import sys
sys.path.insert(0, '.')
from src.builders.build_security_releases import extract_version_from_title

tests = [
    ('macOS Big Sur 11.7.9', '11.7.9'),
    ('macOS Sequoia 15.3', '15.3'),
    ('macOS Monterey 12.6', '12.6'),
]

all_pass = True
for title, expected in tests:
    result = extract_version_from_title(f'About the security content of {title}')
    if result == expected:
        print(f'✅ {title} → {result}')
    else:
        print(f'❌ {title} → {result} (expected {expected})')
        all_pass = False

if not all_pass:
    sys.exit(1)
"

echo ""
echo "=== All tests passed! ==="