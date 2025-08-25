# 🚀 SOFA 2.0 - Quick Start Guide

## In 5 Minutes You'll Have:
- ✅ Auto-updating Apple security data
- ✅ Web dashboard on GitHub Pages  
- ✅ JSON API for automation
- ✅ RSS feed for notifications
- ✅ Zero maintenance required

## Step 1: Create Your Repository (1 minute)

```bash
# Option A: Use GitHub CLI
gh repo create sofa-2.0 --public --clone
cd sofa-2.0

# Option B: Use GitHub Web
# 1. Go to github.com/new
# 2. Name: sofa-2.0
# 3. Public repository
# 4. Clone locally
```

## Step 2: Copy Starter Files (1 minute)

```bash
# Copy this starter directory to your new repo
cp -r sofa-2.0-starter/* your-sofa-2.0/
cp -r sofa-2.0-starter/.github your-sofa-2.0/
cp sofa-2.0-starter/.gitignore your-sofa-2.0/

# Copy binaries from current SOFA
cp ../bin/sofa-gather your-sofa-2.0/bin/
cp ../bin/sofa-fetch your-sofa-2.0/bin/
cp ../bin/sofa-build your-sofa-2.0/bin/

cd your-sofa-2.0
```

## Step 3: Initial Commit (30 seconds)

```bash
# Make binaries executable
chmod +x bin/*

# Commit everything
git add .
git commit -m "🎉 Initial SOFA 2.0 setup"
git push origin main
```

## Step 4: Enable GitHub Pages (1 minute)

1. Go to your repo on GitHub
2. Settings → Pages
3. Source: Deploy from a branch
4. Branch: main
5. Folder: / (root)
6. Save

## Step 5: Run Bootstrap (30 seconds)

```bash
# Option A: GitHub CLI
gh workflow run bootstrap.yml

# Option B: GitHub Web
# 1. Go to Actions tab
# 2. Click "Bootstrap SOFA 2.0"
# 3. Click "Run workflow"
```

## Step 6: Verify It's Working (1 minute)

```bash
# Check workflow completed
gh run list --workflow=bootstrap.yml

# Wait 1-2 minutes for Pages to deploy, then visit:
open https://[your-username].github.io/sofa-2.0/
```

## 🎉 That's It! You're Done!

Your SOFA 2.0 is now:
- ✅ Gathering Apple security data
- ✅ Auto-updating every 6 hours
- ✅ Serving data via GitHub Pages
- ✅ Providing JSON API and RSS

## What You Get

### Web Interface
```
https://[your-username].github.io/sofa-2.0/
```

### JSON API Endpoints
```
https://[your-username].github.io/sofa-2.0/data/feeds/macos.json
https://[your-username].github.io/sofa-2.0/data/feeds/ios.json
https://[your-username].github.io/sofa-2.0/data/feeds/rss.xml
```

### Auto-Updates
- Every 6 hours via GitHub Actions
- Manual trigger: `gh workflow run update-data.yml`

## Optional: Add VitePress Site (10 minutes)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# The site will auto-deploy via GitHub Actions
```

## Customization Options

### Change Update Frequency
Edit `.github/workflows/update-data.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Change to your preference
```

### Add Your Branding
1. Edit `site/index.md` for homepage
2. Modify `site/.vitepress/config.ts` for navigation
3. Add logo to `site/public/`

### Custom Domain
1. Add CNAME file: `echo "sofa.yourdomain.com" > CNAME`
2. Configure DNS: CNAME record → [username].github.io
3. Enable HTTPS in Pages settings

## Testing Locally

```bash
# Test binaries work
./bin/sofa-gather --help

# Test with Act (if installed)
act -W .github/workflows/update-data.yml --dryrun

# Test website
npm run dev
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Binaries won't run | `chmod +x bin/*` |
| No data appearing | Check Actions tab for errors |
| Pages not working | Settings → Pages → Check source |
| Old data | Manually run: `gh workflow run update-data.yml` |

## Support

- 📖 [Full Documentation](./README.md)
- 🐛 [Report Issues](https://github.com/[your-username]/sofa-2.0/issues)
- 💬 [Discussions](https://github.com/[your-username]/sofa-2.0/discussions)

---

**Time to complete: ~5 minutes**  
**Maintenance required: Zero**  
**Cost: $0 (all within GitHub free tier)**

Welcome to the future of Apple security data! 🎉