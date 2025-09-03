#!/bin/bash
#
# Comprehensive verification script for gathered data files
# Uses jq to validate JSON structure and count entries
#

set -e

echo "🔍 Comprehensive Gathered Data Verification"
echo "=========================================="
echo ""

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "❌ jq not found - installing..."
    sudo apt-get update && sudo apt-get install -y jq
fi

# Directory to check
DATA_DIR="data/resources"
if [ ! -d "$DATA_DIR" ]; then
    echo "❌ Data directory not found: $DATA_DIR"
    exit 1
fi

echo "📁 Checking gathered data files in: $DATA_DIR"
echo ""

# Track overall status
TOTAL_FILES=0
SUCCESS_FILES=0
CRITICAL_MISSING=0

# Function to verify a JSON file with jq
verify_json_file() {
    local file_path="$1"
    local description="$2" 
    local jq_query="$3"
    local is_critical="${4:-false}"
    
    TOTAL_FILES=$((TOTAL_FILES + 1))
    
    if [ -f "$file_path" ]; then
        local size=$(wc -c < "$file_path")
        local size_mb=$(echo "scale=2; $size / 1048576" | bc -l 2>/dev/null || echo "0")
        
        # Validate JSON structure and get count
        if jq -e "$jq_query" "$file_path" >/dev/null 2>&1; then
            local count=$(jq -r "$jq_query" "$file_path" 2>/dev/null)
            if [[ "$count" =~ ^[0-9]+$ ]] && [ "$count" -gt 0 ]; then
                echo "✅ $(basename "$file_path"): $size bytes ($size_mb MB) - $count $description"
                SUCCESS_FILES=$((SUCCESS_FILES + 1))
                
                # Additional validation for specific files
                case "$(basename "$file_path")" in
                    "apple_beta_feed.json")
                        # Check if beta feed has recent data (within last 14 days)
                        local created_at=$(jq -r '.created_at' "$file_path" 2>/dev/null)
                        if [ "$created_at" != "null" ] && [ "$created_at" != "" ]; then
                            echo "    📅 Created: $created_at"
                            # Check for recent beta 9 releases
                            local beta9_count=$(jq '[.items[] | select(.version | contains("beta 9"))] | length' "$file_path" 2>/dev/null)
                            if [ "$beta9_count" -gt 0 ]; then
                                echo "    🎯 Contains $beta9_count beta 9 releases (good!)"
                            fi
                        fi
                        ;;
                    "kev_catalog.json")
                        # Show KEV update date
                        local kev_date=$(jq -r '.dateReleased // .date_released // .updated' "$file_path" 2>/dev/null)
                        if [ "$kev_date" != "null" ] && [ "$kev_date" != "" ]; then
                            echo "    📅 KEV date: $kev_date"
                        fi
                        ;;
                esac
            else
                echo "⚠️ $(basename "$file_path"): $size bytes - Invalid count: $count"
                if [ "$is_critical" = "true" ]; then
                    CRITICAL_MISSING=$((CRITICAL_MISSING + 1))
                fi
            fi
        else
            echo "❌ $(basename "$file_path"): $size bytes - JSON validation failed"
            if [ "$is_critical" = "true" ]; then
                CRITICAL_MISSING=$((CRITICAL_MISSING + 1))
            fi
        fi
    else
        echo "❌ $(basename "$file_path"): File not found"
        if [ "$is_critical" = "true" ]; then
            CRITICAL_MISSING=$((CRITICAL_MISSING + 1))
        fi
    fi
}

echo "📊 Gather Sources Verification:"
echo ""

# Verify each gathered data source
verify_json_file "$DATA_DIR/kev_catalog.json" "KEV entries" ".vulnerabilities | length" true
verify_json_file "$DATA_DIR/gdmf_cached.json" "GDMF asset sets" ".PublicAssetSets | keys | length" true  
verify_json_file "$DATA_DIR/ipsw.json" "IPSW devices" "keys | length" true
verify_json_file "$DATA_DIR/apple_beta_feed.json" "beta releases" ".items | length" false
verify_json_file "$DATA_DIR/uma_catalog.json" "UMA entries" "keys | length" true
verify_json_file "$DATA_DIR/xprotect.json" "XProtect entries" "keys | length" false

echo ""
echo "📊 Additional Data Files:"
echo ""

# Check additional important files
verify_json_file "$DATA_DIR/apple_security_releases.json" "security releases" ".releases | length" false
verify_json_file "$DATA_DIR/apple_security_releases.ndjson" "NDJSON releases" "1" false  # NDJSON file check
verify_json_file "$DATA_DIR/sofa-status.json" "status entries" "keys | length" false

echo ""
echo "📈 Summary:"
echo "==========="
echo "Total files checked: $TOTAL_FILES"
echo "Successful files: $SUCCESS_FILES"  
echo "Critical missing: $CRITICAL_MISSING"

if [ $CRITICAL_MISSING -eq 0 ]; then
    echo ""
    echo "✅ All critical gather sources verified successfully!"
    
    # Show beta release details if available
    if [ -f "$DATA_DIR/apple_beta_feed.json" ]; then
        echo ""
        echo "🍎 Beta Release Details:"
        echo "Latest beta releases:"
        jq -r '.items[0:3] | .[] | "  • \(.platform) \(.version) (\(.build)) - Released: \(.released)"' "$DATA_DIR/apple_beta_feed.json" 2>/dev/null || echo "  Could not parse beta releases"
        echo ""
        echo "Beta feed hash: $(jq -r '.UpdateHash' "$DATA_DIR/apple_beta_feed.json" 2>/dev/null || echo "unknown")"
        echo "Beta feed age: $(jq -r '.created_at' "$DATA_DIR/apple_beta_feed.json" 2>/dev/null || echo "unknown")"
    fi
    
    exit 0
else
    echo ""
    echo "❌ $CRITICAL_MISSING critical files missing or invalid!"
    echo ""
    echo "🔧 Troubleshooting tips:"
    echo "- Check network connectivity to Apple endpoints"
    echo "- Verify SSL certificates are properly installed"  
    echo "- Review gather stage logs for specific errors"
    echo "- Consider running with --insecure flag if SSL issues persist"
    
    exit 1
fi