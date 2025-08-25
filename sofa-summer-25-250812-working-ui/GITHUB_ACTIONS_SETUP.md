# GitHub Actions Setup Guide

## Workflows Included

### 1. `deploy.yml` - Main Deployment Workflow
- **Triggers on**: Push to `main` branch, Pull Requests, Manual trigger
- **Purpose**: Build and deploy VitePress site to GitHub Pages
- **Features**:
  - Builds with pnpm and Node.js 20
  - Copies CNAME file for custom domain
  - Deploys to GitHub Pages environment

### 2. `test.yml` - Test Workflow
- **Triggers on**: Push to `main` branch, Manual trigger
- **Purpose**: Verify GitHub Actions is working properly

## Required Repository Settings

### 1. Enable GitHub Actions
1. Go to Settings → Actions → General
2. Under "Actions permissions", select:
   - "Allow all actions and reusable workflows"
3. Under "Workflow permissions", select:
   - "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"
4. Save changes

### 2. Configure GitHub Pages
1. Go to Settings → Pages
2. Under "Build and deployment":
   - Source: **GitHub Actions** (NOT "Deploy from a branch")
3. Under "Custom domain":
   - Enter: `sofa25.macadmin.me`
   - Save and wait for DNS check
4. After DNS verification:
   - Check "Enforce HTTPS"

### 3. Create Environments (Optional)
1. Go to Settings → Environments
2. Click "New environment"
3. Name: `github-pages`
4. Configure protection rules if needed

## Manual Workflow Trigger

To manually trigger the deployment:
1. Go to Actions tab
2. Select "Build and Deploy to GitHub Pages"
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow" button

## Troubleshooting

### Workflow Not Showing in Actions Tab
1. Ensure `.github/workflows/` directory exists
2. Check workflow files have `.yml` extension
3. Verify YAML syntax is correct
4. Push changes to repository

### Build Failures
Check the error logs for:
- Missing dependencies
- Node/pnpm version issues
- VitePress configuration errors

### Deployment Not Working
1. Verify GitHub Pages is enabled
2. Check "GitHub Actions" is selected as source
3. Ensure workflow has proper permissions
4. Check environment URL in deploy job output

### Custom Domain Issues
1. Verify CNAME file exists in `/public/`
2. Check DNS records point to GitHub Pages
3. Wait for DNS propagation
4. Ensure HTTPS certificate is provisioned

## Workflow Status Badge

Add this to your README to show workflow status:

```markdown
![Deploy Status](https://github.com/headmin/sofa-summer-25/actions/workflows/deploy.yml/badge.svg)
```

## Important Notes

- The workflow runs on every push to `main` branch
- Pull requests trigger build but not deployment
- Manual trigger is available via workflow_dispatch
- CNAME file is automatically copied during build
- Base URL is set to `/` for custom domain