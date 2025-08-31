#!/bin/bash
# Test script for SOFA pipeline workflow validation

set -e

echo "🧪 Testing SOFA Pipeline Workflow"
echo "=================================="

# Test 1: Check required files exist
echo "📁 Checking required files..."

REQUIRED_FILES=(
    "scripts/sofa_pipeline.py"
    "scripts/generate_rss.py"
    "config/gather.toml"
    "config/fetch.toml"  
    "config/build.toml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        exit 1
    fi
done

# Test 2: Check scripts are executable or have proper shebang
echo "🔧 Checking script executability..."

SCRIPTS=(
    "scripts/sofa_pipeline.py"
    "scripts/generate_rss.py"
)

for script in "${SCRIPTS[@]}"; do
    if head -1 "$script" | grep -q "uv run"; then
        echo "  ✅ $script (has uv shebang)"
    else
        echo "  ⚠️  $script (no uv shebang - may need manual execution)"
    fi
done

# Test 3: Validate TOML config files
echo "📝 Checking TOML config files..."

if command -v python3 &> /dev/null; then
    python3 -c "
import sys
try:
    import tomllib
except ImportError:
    try:
        import toml as tomllib
    except ImportError:
        print('  ⚠️  No TOML parser available, skipping validation')
        sys.exit(0)

import glob
for toml_file in glob.glob('config/*.toml'):
    try:
        with open(toml_file, 'rb') as f:
            data = tomllib.load(f) if hasattr(tomllib, 'load') else tomllib.loads(f.read().decode())
        print(f'  ✅ {toml_file}')
    except Exception as e:
        print(f'  ❌ {toml_file}: {e}')
        sys.exit(1)
"
else
    echo "  ⚠️  Python3 not available, skipping TOML validation"
fi

# Test 4: Check directory structure
echo "📂 Checking directory structure..."

REQUIRED_DIRS=(
    "data"
    "config"
    "scripts"
    ".github/workflows"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir/"
    else
        echo "  ❌ $dir/ (missing)"
        exit 1
    fi
done

echo ""
echo "✅ All pipeline tests passed!"
echo ""
echo "🚀 Pipeline workflow is ready to run!"
echo "   • Manual: GitHub Actions → 'SOFA Data Pipeline' → Run workflow"  
echo "   • Auto: Runs every 6 hours or when scripts/config change"
echo ""