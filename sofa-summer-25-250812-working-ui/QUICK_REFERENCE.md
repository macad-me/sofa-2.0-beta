# SOFA Pipeline - Quick Reference Card

## 🚀 Quick Test
```bash
cd /Users/henry/Projects/Work/sofa-web-ui-preview
./test_pipeline.sh
```
✅ All tests should pass!

## 🔧 The Fix That Saved Everything
```python
# File: data-processing/src/builders/build_security_releases.py
# Line: 123

# BROKEN: r"macOS\s+\w+\s+(\d+(?:\.\d+)*)"
# FIXED:  r"macOS\s+(?:\w+\s+)+(\d+(?:\.\d+)*)"
#                     ^^^^^^^^^^^
#                This handles "Big Sur"
```

## 📁 Critical Paths
```
/Users/henry/Projects/Work/sofa-web-ui-preview/  # RIGHT ✅
/Users/henry/Projects/Work/sofa/                 # WRONG ❌
```

## 🏃 Run Pipeline (No Internet Needed!)
```bash
cd data-processing
uv run python src/pipeline/run_sofa_pipeline.py --stages 2 3
```

## 🔍 Verify Big Sur Fix
```bash
# Should return "11.7.9" not "15.7.1"
grep "Big Sur 11.7.9" v1/macos_data_feed.json | head -1
```

## 📊 Check Feed Stats
```bash
# macOS versions (should be 5)
jq '.OSVersions | length' v1/macos_data_feed.json

# KEVs enriched (should be ~59)
jq '.OSVersions[0].Latest.UniqueCVEsCount' v1/macos_data_feed.json
```

## 🌿 Git Branch
```bash
git branch  # Should show: * 250818-add-builder
```

## ⚠️ Common Issues

### "No parsed data found"
```bash
# Cache exists but wrong format - run reparse
uv run python reparse_cache.py
```

### SSL Certificate Error
```bash
# Normal - pipeline uses cached GDMF automatically
```

### Pipeline Takes Forever
```bash
# You're probably in stage 1 (fetching)
# Use: --stages 2 3  (skip fetching)
```

## ✨ Success Indicators
- ✅ test_pipeline.sh passes
- ✅ 6 feed files in v1/
- ✅ ~227KB macos_data_feed.json
- ✅ Pipeline runs in ~2.5 seconds
- ✅ Big Sur shows version 11.7.9

## 🔥 Emergency Reset
```bash
# If everything breaks, go back to known good state
git checkout 82c0200  # Last known good commit
```

---
*Keep this handy - it has everything you need!*