#!/bin/bash

# SOFA Workflow Linter
# Validates GitHub Actions workflow YAML files for syntax and common issues

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKFLOWS_DIR="$REPO_ROOT/.github/workflows"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔍 SOFA Workflow Linter"
echo "======================="
echo "Repository: $REPO_ROOT"
echo "Workflows:  $WORKFLOWS_DIR"
echo ""

# Check if workflows directory exists
if [[ ! -d "$WORKFLOWS_DIR" ]]; then
    echo -e "${RED}❌ Workflows directory not found: $WORKFLOWS_DIR${NC}"
    exit 1
fi

# Find all workflow files
WORKFLOW_FILES=()
while IFS= read -r -d '' file; do
    WORKFLOW_FILES+=("$file")
done < <(find "$WORKFLOWS_DIR" -type f \( -name "*.yml" -o -name "*.yaml" \) -print0)

if [[ ${#WORKFLOW_FILES[@]} -eq 0 ]]; then
    echo -e "${YELLOW}⚠️ No workflow files found in $WORKFLOWS_DIR${NC}"
    exit 0
fi

echo -e "${BLUE}Found ${#WORKFLOW_FILES[@]} workflow file(s):${NC}"
for file in "${WORKFLOW_FILES[@]}"; do
    echo "  - $(basename "$file")"
done
echo ""

# Check for required tools
TOOLS_MISSING=false

# Check for Python (for YAML validation)
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ python3 not found - required for YAML validation${NC}"
    TOOLS_MISSING=true
fi

# Check for yamllint (optional but recommended)
YAMLLINT_AVAILABLE=false
if command -v yamllint &> /dev/null; then
    YAMLLINT_AVAILABLE=true
    echo -e "${GREEN}✅ yamllint found - will use for enhanced validation${NC}"
else
    echo -e "${YELLOW}⚠️ yamllint not found - install with: pip install yamllint${NC}"
fi

# Check for actionlint (optional but recommended)
ACTIONLINT_AVAILABLE=false
if command -v actionlint &> /dev/null; then
    ACTIONLINT_AVAILABLE=true
    echo -e "${GREEN}✅ actionlint found - will validate GitHub Actions syntax${NC}"
else
    echo -e "${YELLOW}⚠️ actionlint not found - install from: https://github.com/rhysd/actionlint${NC}"
fi

if [[ "$TOOLS_MISSING" == "true" ]]; then
    echo ""
    echo -e "${RED}❌ Missing required tools. Please install and try again.${NC}"
    exit 1
fi

echo ""
echo "🧪 Validating workflow files..."
echo "==============================="

TOTAL_FILES=0
VALID_FILES=0
INVALID_FILES=0

# Validation function
validate_workflow() {
    local file="$1"
    local filename=$(basename "$file")
    local errors=()
    local warnings=()
    
    echo -e "\n${BLUE}📄 Validating: $filename${NC}"
    echo "   Path: $file"
    
    # 1. Basic YAML syntax validation with Python
    echo "   🔍 Checking YAML syntax..."
    if ! python3 -c "
import yaml
import sys
try:
    with open('$file', 'r') as f:
        yaml.safe_load(f)
    print('      ✅ Valid YAML syntax')
except yaml.YAMLError as e:
    print(f'      ❌ YAML syntax error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'      ❌ Error reading file: {e}')
    sys.exit(1)
" 2>/dev/null; then
        errors+=("YAML syntax error")
        return 1
    fi
    
    # 2. Check for required GitHub Actions fields
    echo "   🔍 Checking required GitHub Actions fields..."
    if ! python3 -c "
import yaml
import sys
try:
    with open('$file', 'r') as f:
        data = yaml.safe_load(f)
    
    if not isinstance(data, dict):
        print('      ❌ Root must be a dictionary')
        sys.exit(1)
        
    if 'name' not in data:
        print('      ❌ Missing required field: name')
        sys.exit(1)
    
    # Check for 'on' field (YAML parses 'on:' as boolean True)
    if 'on' not in data and True not in data:
        print('      ❌ Missing required field: on (trigger definition)')
        sys.exit(1)
        
    if 'jobs' not in data:
        print('      ❌ Missing required field: jobs')
        sys.exit(1)
        
    if not isinstance(data['jobs'], dict):
        print('      ❌ jobs must be a dictionary')
        sys.exit(1)
        
    if len(data['jobs']) == 0:
        print('      ❌ At least one job is required')
        sys.exit(1)
        
    print('      ✅ Required fields present')
    
except yaml.YAMLError as e:
    print(f'      ❌ YAML error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'      ❌ Validation error: {e}')
    sys.exit(1)
" 2>/dev/null; then
        errors+=("Missing required GitHub Actions fields")
        return 1
    fi
    
    # 3. Check for common issues
    echo "   🔍 Checking for common issues..."
    
    # Check for long lines in shell scripts (potential YAML issue)
    if grep -n '.\{200,\}' "$file" &>/dev/null; then
        warnings+=("Very long lines found (>200 chars) - may indicate YAML formatting issues")
    fi
    
    # Check for unquoted strings that might cause issues
    if grep -n 'run:.*\$[A-Z_]*[^"'"'"']' "$file" &>/dev/null; then
        warnings+=("Potentially unquoted environment variables in run commands")
    fi
    
    # Check for missing checkout action
    if grep -q 'ubuntu-latest\|windows-latest\|macos-latest' "$file" && ! grep -q 'actions/checkout' "$file"; then
        warnings+=("Job uses hosted runner but doesn't checkout repository")
    fi
    
    # 4. Use yamllint if available
    if [[ "$YAMLLINT_AVAILABLE" == "true" ]]; then
        echo "   🔍 Running yamllint..."
        if yamllint_output=$(yamllint -f parsable "$file" 2>&1); then
            if [[ -n "$yamllint_output" ]]; then
                warnings+=("yamllint issues found")
                echo "      ⚠️ yamllint warnings:"
                echo "$yamllint_output" | sed 's/^/        /'
            else
                echo "      ✅ yamllint passed"
            fi
        else
            warnings+=("yamllint failed")
            echo "      ❌ yamllint errors:"
            echo "$yamllint_output" | sed 's/^/        /'
        fi
    fi
    
    # 5. Use actionlint if available
    if [[ "$ACTIONLINT_AVAILABLE" == "true" ]]; then
        echo "   🔍 Running actionlint..."
        if actionlint_output=$(actionlint "$file" 2>&1); then
            if [[ -n "$actionlint_output" ]]; then
                warnings+=("actionlint issues found")
                echo "      ⚠️ actionlint warnings:"
                echo "$actionlint_output" | sed 's/^/        /'
            else
                echo "      ✅ actionlint passed"
            fi
        else
            warnings+=("actionlint failed")
            echo "      ❌ actionlint errors:"
            echo "$actionlint_output" | sed 's/^/        /'
        fi
    fi
    
    echo "      ✅ Common issues check completed"
    
    # Summary for this file
    if [[ ${#errors[@]} -eq 0 ]]; then
        if [[ ${#warnings[@]} -eq 0 ]]; then
            echo -e "   ${GREEN}✅ $filename is valid${NC}"
            return 0
        else
            echo -e "   ${YELLOW}⚠️ $filename is valid but has ${#warnings[@]} warning(s)${NC}"
            for warning in "${warnings[@]}"; do
                echo -e "      ${YELLOW}⚠️ $warning${NC}"
            done
            return 0
        fi
    else
        echo -e "   ${RED}❌ $filename has ${#errors[@]} error(s)${NC}"
        for error in "${errors[@]}"; do
            echo -e "      ${RED}❌ $error${NC}"
        done
        return 1
    fi
}

# Validate all workflow files
for file in "${WORKFLOW_FILES[@]}"; do
    TOTAL_FILES=$((TOTAL_FILES + 1))
    if validate_workflow "$file"; then
        VALID_FILES=$((VALID_FILES + 1))
    else
        INVALID_FILES=$((INVALID_FILES + 1))
    fi
done

echo ""
echo "📊 Validation Summary"
echo "===================="
echo -e "Total files:   $TOTAL_FILES"
echo -e "${GREEN}Valid files:   $VALID_FILES${NC}"
if [[ $INVALID_FILES -gt 0 ]]; then
    echo -e "${RED}Invalid files: $INVALID_FILES${NC}"
else
    echo -e "Invalid files: $INVALID_FILES"
fi

# Final result
if [[ $INVALID_FILES -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}🎉 All workflow files are valid!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}💥 $INVALID_FILES workflow file(s) have errors that need to be fixed.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  • Check YAML indentation (use spaces, not tabs)"
    echo "  • Ensure proper quoting of strings with special characters"
    echo "  • Validate multiline strings are properly formatted"
    echo "  • Check that all required GitHub Actions fields are present"
    echo ""
    echo "Tools to help:"
    echo "  • yamllint: pip install yamllint"
    echo "  • actionlint: https://github.com/rhysd/actionlint"
    echo "  • VS Code: GitHub Actions extension"
    exit 1
fi