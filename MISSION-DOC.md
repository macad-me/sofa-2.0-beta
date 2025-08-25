# SOFA 2.0 Mission Document - Claude Handoff

## 🎯 Mission Statement

Build and deploy SOFA 2.0 as a **fully autonomous, self-updating Apple security data platform** that runs entirely on GitHub infrastructure at zero cost, requiring zero maintenance after initial deployment.

## 📋 Context for New Claude Session

### What is SOFA?
SOFA (Simple Organized Feed for Apple) tracks Apple security updates, versions, CVEs, and malware definitions. It provides this data as JSON feeds and RSS for the Mac Admin community.

### What is SOFA 2.0?
A complete rewrite that:
- Runs 100% on GitHub (Actions + Pages)
- Uses pre-compiled static Linux binaries (no dependencies)
- Stores all data as JSON files in git (repository = database)
- Auto-updates every 6 hours forever
- Provides web interface via VitePress
- Costs $0 to operate

## 🏗️ Current State

### What's Ready
```
✅ Static binaries (pre-compiled, in bin/ directory)
   - sofa-gather: Collects data from Apple
   - sofa-fetch: Scrapes HTML pages
   - sofa-build: Generates platform feeds

✅ GitHub Workflows
   - bootstrap.yml: One-time setup
   - update-data.yml: Scheduled updates

✅ Configuration
   - config/gather.toml: URLs and settings

✅ Documentation
   - README.md: Full documentation
   - QUICK_START.md: 5-minute setup
   - SOFA_2.0_BLUEPRINT.md: Architecture
```

### What Needs Completion
```
🚧 VitePress Site
   - Basic structure exists
   - Needs components for dashboard
   - Needs data visualization

🚧 Data Processing
   - RSS generation script
   - Data validation
   - Error handling

🚧 Testing
   - Verify binaries work on GitHub Actions Ubuntu
   - Test data gathering from Apple
   - Validate JSON output
```

## 🎮 Your Mission

### Phase 1: Repository Setup (Day 1)
1. **Create new public repository** named `sofa-2.0`
2. **Copy all files** from `sofa-2.0-starter/` directory
3. **Add binaries** from parent `bin/` directory
4. **Initial commit** and push to GitHub
5. **Enable GitHub Pages** (Settings → Pages → main branch)
6. **Run bootstrap workflow** to initialize data

### Phase 2: Verify Core Functionality (Day 2)
1. **Test data gathering**
   - Confirm XProtect data updates
   - Verify GDMF collection works
   - Check security releases fetch
2. **Validate JSON feeds**
   - Ensure all platform feeds generate
   - Verify RSS feed creation
   - Check data structure correctness
3. **Confirm auto-updates**
   - Test scheduled workflow
   - Verify change detection
   - Validate git commits

### Phase 3: VitePress Development (Week 1)
1. **Setup VitePress site**
   ```bash
   cd site
   npm install
   npm run dev
   ```
2. **Create dashboard components**
   - Latest versions display
   - Update timeline
   - CVE statistics
3. **Implement data loading**
   - Fetch JSON from repository
   - Parse and display
   - Auto-refresh

### Phase 4: Production Ready (Week 2)
1. **Error handling**
   - Graceful failures
   - Retry logic
   - Notifications
2. **Performance optimization**
   - Minimize JSON size
   - Optimize build times
   - Cache strategies
3. **Documentation**
   - API documentation
   - Integration examples
   - Troubleshooting guide

## 🛠️ Technical Requirements

### Binary Execution
```bash
# Binaries are static Linux x64 compiled with musl
# No dependencies required, just chmod +x and run

./bin/sofa-gather xprotect --output data/raw/xprotect.json
./bin/sofa-fetch --output data/raw/security_releases.json
./bin/sofa-build macos --input data/raw/ --output data/feeds/macos.json
```

### Data Structure
```
data/
├── raw/                    # Source data from Apple
│   ├── xprotect.json      # XProtect/Gatekeeper versions
│   ├── gdmf_*.json        # Platform-specific GDMF
│   └── security_releases.json # CVE and version data
├── feeds/                  # Built platform feeds
│   ├── macos.json         # macOS versions and updates
│   ├── ios.json           # iOS/iPadOS data
│   └── rss.xml            # RSS feed of all updates
└── metadata.json          # System status and timestamps
```

### GitHub Actions Schedule
```yaml
# Runs every 6 hours
schedule:
  - cron: '0 */6 * * *'
  
# Also manual trigger
workflow_dispatch:
```

## 🚀 Success Criteria

### Minimum Viable Product (MVP)
- [ ] Repository created and public
- [ ] Binaries execute on GitHub Actions
- [ ] Data gathering works
- [ ] JSON feeds generate correctly
- [ ] Auto-updates run on schedule
- [ ] Data accessible via GitHub Pages

### Full Product
- [ ] VitePress dashboard live
- [ ] All platforms supported (macOS, iOS, tvOS, watchOS, visionOS)
- [ ] RSS feed functional
- [ ] API documentation complete
- [ ] 99.9% uptime achieved
- [ ] Zero manual intervention required

## 📚 Key Resources

### Documentation to Read
1. `docs/SOFA_2.0_BLUEPRINT.md` - Complete architecture
2. `QUICK_START.md` - Deployment guide
3. `docs/static_build_and_test_guide.md` - Binary information

### External Resources
- [VitePress Documentation](https://vitepress.dev/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [GitHub Pages Docs](https://docs.github.com/en/pages)

### Testing Tools
```bash
# Test locally with Act
brew install act
act -W .github/workflows/update-data.yml --dryrun

# Test binaries
./bin/sofa-gather --help
./bin/sofa-fetch --help
./bin/sofa-build --help
```

## 💡 Design Principles

1. **Zero Dependencies** - Static binaries, no runtime requirements
2. **Zero Infrastructure** - GitHub provides everything
3. **Zero Maintenance** - Self-updating, self-healing
4. **Zero Cost** - Within free tier limits
5. **Maximum Simplicity** - Anyone can fork and deploy

## ⚠️ Critical Warnings

### Do NOT
- ❌ Add external dependencies
- ❌ Use paid services
- ❌ Require manual updates
- ❌ Store secrets in code
- ❌ Exceed GitHub rate limits

### Always
- ✅ Keep binaries static
- ✅ Store data in git
- ✅ Use GitHub Pages for hosting
- ✅ Test with Act first
- ✅ Document everything

## 🎯 Final Goal

**In 2 weeks, SOFA 2.0 should be:**
- Fully deployed and public
- Auto-updating every 6 hours
- Serving thousands of users
- Requiring zero maintenance
- Costing zero dollars
- Setting the standard for open security data

## 🤝 Handoff Checklist

When starting new Claude session:
1. Share this MISSION-DOC.md
2. Provide access to `sofa-2.0-starter/` directory
3. Confirm binaries are in `bin/` directory
4. Point to SOFA_2.0_BLUEPRINT.md for architecture
5. Mention any specific customizations needed

## 📝 Initial Prompt for New Claude

```
I need to complete the deployment of SOFA 2.0, an Apple security data platform. 

I have:
- Pre-compiled static binaries in bin/
- Starter files in sofa-2.0-starter/
- Mission document in MISSION-DOC.md
- Architecture in SOFA_2.0_BLUEPRINT.md

Please help me:
1. Create the public repository
2. Deploy the initial version
3. Verify auto-updates work
4. Build the VitePress dashboard

The goal is a fully autonomous system running on GitHub that requires zero maintenance and costs nothing to operate.

Let's start with [specific task].
```

## 🏁 Definition of Done

SOFA 2.0 is complete when:
1. **It runs without human intervention** for 30 days
2. **Data updates every 6 hours** successfully
3. **Web interface** displays current data
4. **API endpoints** serve valid JSON
5. **RSS feed** updates with changes
6. **Zero errors** in GitHub Actions logs
7. **Zero cost** incurred
8. **Community adopts it** as primary source

---

**This document contains everything needed for a fresh Claude session to take over and complete SOFA 2.0.**

Good luck! 🚀