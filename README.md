# SOFA 2.0 - Turnkey Security Data Platform

## 🚀 Quick Start

```bash
# 1. Clone this repository
git clone https://github.com/[your-org]/sofa-2.0
cd sofa-2.0

# 2. Run bootstrap
gh workflow run bootstrap.yml

# 3. View your data at:
# https://[your-org].github.io/sofa-2.0
```

That's it! The system will now automatically update every 6 hours.

## 📊 What You Get

- **Live Dashboard**: Beautiful web interface showing latest Apple security data
- **JSON API**: Machine-readable feeds at `/data/feeds/[platform].json`
- **RSS Feed**: Subscribe to updates at `/data/feeds/rss.xml`
- **Historical Data**: Git history provides complete audit trail
- **Zero Maintenance**: Fully automated updates via GitHub Actions

## 🏗️ Architecture

```
This Repo
    ├── Binaries (pre-compiled, static)
    ├── GitHub Actions (automated updates)
    ├── Data (JSON files, git-tracked)
    └── VitePress Site (web interface)
           ↓
    GitHub Pages (free hosting)
           ↓
    Your Users (web + API access)
```

## 📁 Repository Structure

```
├── bin/                 # Static binaries (no dependencies!)
├── config/              # Simple configuration files
├── data/                # All your security data (auto-updated)
│   ├── raw/            # Source data from Apple
│   ├── feeds/          # Processed platform feeds
│   └── archive/        # Historical snapshots
├── site/               # VitePress website
└── .github/workflows/  # Automation magic
```

## 🔄 Data Update Flow

1. **Every 6 hours**: GitHub Actions runs automatically
2. **Gather**: Binaries fetch latest data from Apple
3. **Process**: Build platform-specific feeds
4. **Commit**: Changes pushed back to repository
5. **Deploy**: Site rebuilds with new data
6. **Serve**: Available instantly via CDN

## 📈 Available Data

### Platform Feeds
- `macos.json` - macOS versions, updates, CVEs
- `ios.json` - iOS/iPadOS security releases  
- `tvos.json` - tvOS updates
- `watchos.json` - watchOS updates
- `visionos.json` - visionOS updates

### Security Data
- `xprotect.json` - XProtect versions and updates
- `gdmf_[platform].json` - Gatekeeper data
- `security_releases.json` - All Apple security bulletins

### Metadata
- `rss.xml` - RSS feed of all updates
- `metadata.json` - Last update time, versions

## 🎨 Customization

### Change Update Frequency
Edit `.github/workflows/update-data.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Change this
```

### Modify Website
Edit files in `site/` directory:
- `index.md` - Homepage content
- `.vitepress/config.ts` - Site configuration
- `.vitepress/theme/` - Custom components

### Add New Data Sources
1. Add gathering logic to binaries
2. Update workflows to process new data
3. Data automatically appears in feeds

## 🔧 Development

### Test Locally
```bash
# Test binaries
./bin/sofa-gather --help

# Test website
cd site
npm install
npm run dev
# Open http://localhost:5173
```

### Test with Act
```bash
# Install Act
brew install act

# Test workflows locally (free!)
act -W .github/workflows/update-data.yml
```

## 📊 API Usage

### JavaScript/TypeScript
```javascript
const response = await fetch('https://[your-org].github.io/sofa-2.0/data/feeds/macos.json');
const data = await response.json();
console.log(data.latest_version);
```

### Python
```python
import requests
data = requests.get('https://[your-org].github.io/sofa-2.0/data/feeds/macos.json').json()
print(data['latest_version'])
```

### curl
```bash
curl https://[your-org].github.io/sofa-2.0/data/feeds/macos.json | jq '.latest_version'
```

## 📈 Monitoring

Check system health:
```bash
# View last update time
curl https://[your-org].github.io/sofa-2.0/data/metadata.json | jq '.last_updated'

# Check workflow runs
gh run list --workflow=update-data.yml
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| No updates | Check Actions tab for errors |
| Old data | Manually trigger: `gh workflow run update-data.yml` |
| Site not loading | Check Pages settings in repo |
| Binaries fail | Ensure `chmod +x bin/*` was run |

## 📜 License

MIT - Use freely for any purpose

## 🤝 Contributing

1. Fork this repository
2. Make your changes
3. Test with Act locally
4. Submit a pull request

## 🎯 Roadmap

- [x] Phase 1: Core data gathering
- [x] Phase 2: Automated updates
- [x] Phase 3: Web interface
- [ ] Phase 4: Advanced analytics
- [ ] Phase 5: Slack/Discord webhooks
- [ ] Phase 6: Custom notifications

## 💡 Why SOFA 2.0?

- **Zero Infrastructure**: Runs entirely on GitHub (free)
- **Zero Dependencies**: Static binaries just work
- **Zero Maintenance**: Self-updating system
- **Zero Cost**: Everything within free tier
- **Maximum Reliability**: GitHub's infrastructure
- **Maximum Performance**: CDN-served static files

---

Built with ❤️ for the Mac Admin community