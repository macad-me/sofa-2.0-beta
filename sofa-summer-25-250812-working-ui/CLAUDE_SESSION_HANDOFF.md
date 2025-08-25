# Claude Session Handoff - 2024-08-19

## Quick Start for Next Session

### Current Working Directory
```bash
cd /Users/henry/Projects/Work/sofa-web-ui-preview
```

### Current Branch
```bash
git branch: 250818-add-builder
```

### Test Everything Works
```bash
./test_pipeline.sh  # Should show all tests passing
```

## Critical Context

### What We Fixed Today
1. **The Big Bug**: "macOS Big Sur 11.7.9" was showing as version "15.7.1" - FIXED
2. **Empty Feeds**: OSVersions arrays were empty - FIXED
3. **GitHub Actions**: Couldn't use cache - FIXED
4. **Directory Chaos**: Files in wrong places - FIXED

### The Magic Fix
```python
# This regex change fixed Big Sur:
# OLD (broken): r"macOS\s+\w+\s+(\d+(?:\.\d+)*)"
# NEW (works):  r"macOS\s+(?:\w+\s+)+(\d+(?:\.\d+)*)"
```

## Repository Structure

### Two Repositories in Play
1. **sofa-web-ui-preview** (current) - The working repo with UI and pipeline
2. **sofa** - Different repo, different structure (be careful!)

### Key Directories
```
/Users/henry/Projects/Work/sofa-web-ui-preview/
├── data-processing/          # Pipeline code
│   ├── src/
│   │   ├── builders/        # Feed builders (VERSION FIX HERE)
│   │   ├── pipeline/        # Main pipeline orchestrator
│   │   └── fetchers/        # Data fetchers
│   ├── data/
│   │   ├── cache/           # Cached HTML and data
│   │   └── feeds/v1/        # Generated feeds
│   └── pyproject.toml       # Python dependencies
├── v1/                       # Public feed location
├── .github/workflows/        # GitHub Actions
└── test_pipeline.sh         # Our test suite
```

## Essential Commands

### Run Pipeline with Cache (No Fetching)
```bash
cd data-processing
uv run python src/pipeline/run_sofa_pipeline.py --stages 2 3
```

### Test Version Extraction
```bash
cd /Users/henry/Projects/Work/sofa-web-ui-preview
uv run python -c "
import sys
sys.path.insert(0, 'data-processing')
from src.builders.build_security_releases import extract_version_from_title
print(extract_version_from_title('About the security content of macOS Big Sur 11.7.9'))
"
# Should output: 11.7.9
```

### Check Feed Quality
```bash
jq '.OSVersions | length' v1/macos_data_feed.json  # Should be 5
jq '.OSVersions[0].Latest.UniqueCVEsCount' v1/macos_data_feed.json  # Should be ~42
```

## Known Issues & Workarounds

### SSL Certificate Error
**Issue**: GDMF fetch fails with SSL error
**Workaround**: Pipeline uses cached GDMF data automatically

### Cache Not Found
**Issue**: "No parsed data found" errors
**Solution**: Cache files must be SHA1 hashed filenames in `data-processing/data/cache/parsed/`

### Act Takes Forever
**Issue**: `act` command times out
**Workaround**: Use `./test_pipeline.sh` for local testing instead

## Working State Verification

### All These Should Work
```bash
# 1. Version extraction test
grep "Big Sur" v1/macos_data_feed.json  # Should find entries

# 2. Pipeline runs without fetching
cd data-processing && uv run python src/pipeline/run_sofa_pipeline.py --stages 2 3

# 3. Feeds have data
jq '.OSVersions[0].SecurityReleases | length' ../v1/macos_data_feed.json  # Should be > 0

# 4. Tests pass
cd .. && ./test_pipeline.sh  # All tests should pass
```

## Git Status

### Clean Working State
- Branch: `250818-add-builder`
- Last commit: "Document complete pipeline overhaul"
- Pushed to: `origin/250818-add-builder`
- Repository: https://github.com/headmin/sofa-summer-25.git

### Important Commits
- `57b0a3d` - Fix version extraction for macOS Big Sur
- `7b3ffd8` - Add pipeline test script
- `82c0200` - Document complete pipeline overhaul

## Dependencies Installed

### Python Environment
```bash
cd /Users/henry/Projects/Work/sofa-web-ui-preview
uv venv  # Virtual environment exists
uv pip list  # Should show: certifi, httpx, lxml, feedgen, loguru, beautifulsoup4, pydantic
```

## What NOT to Touch

### These Files Are Working - Don't Break Them!
1. `data-processing/src/builders/build_security_releases.py` - Has the version fix
2. `test_pipeline.sh` - Our validation suite
3. `v1/*.json` - Feed files with correct data

### Avoid These Directories
- `/Users/henry/Projects/Work/sofa` - Different repo, different structure
- `node_modules/` - UI dependencies, not pipeline
- `.vitepress/` - UI framework, not pipeline

## Testing Checklist for Next Session

```bash
# 1. Go to correct directory
cd /Users/henry/Projects/Work/sofa-web-ui-preview

# 2. Check branch
git branch  # Should show * 250818-add-builder

# 3. Run tests
./test_pipeline.sh  # Should pass all tests

# 4. Check Big Sur fix
grep "Big Sur 11.7.9" v1/macos_data_feed.json | grep -o '"ProductVersion":"[^"]*"'
# Should NOT show 15.7.1, should show 11.7.9

# 5. Verify pipeline works
cd data-processing && uv run python src/pipeline/run_sofa_pipeline.py --stages 2 3
# Should complete in ~2.5 seconds
```

## Key Insights Learned

1. **Regex Word Boundaries**: `\w+` doesn't match spaces - use `(?:\w+\s+)+` for multi-word matches
2. **Directory Flexibility**: Always check multiple paths when files could be in different locations
3. **Cache is King**: Pipeline can run entirely from cache, no network needed
4. **Test Everything**: The test script catches issues before deployment
5. **Document Well**: This handoff ensures continuity

## Contact & Context

- **User**: Henry (working on SOFA project)
- **Project**: SOFA - Security Orchestration for Apple
- **Goal**: Generate security feeds for Apple software updates
- **Status**: ✅ Pipeline working, feeds generating correctly

## Final State Summary

✅ **Version extraction**: Working for all macOS versions including Big Sur
✅ **Feed generation**: 6 files generated with proper data
✅ **Cache usage**: Pipeline runs from cache in 2.5 seconds
✅ **GitHub Actions**: Ready to run with cache
✅ **Testing**: Comprehensive test suite in place
✅ **Documentation**: CLAUDE.md updated with all details

---

*Session End: 2024-08-19*
*Everything is working - don't break it!*