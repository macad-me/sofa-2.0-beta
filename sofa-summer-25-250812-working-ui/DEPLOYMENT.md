# GitHub Pages Deployment Guide

## Step 1: Create a New GitHub Repository

1. Go to https://github.com/new
2. Create a new repository with your desired name (e.g., `sofa-web-ui`)
3. Make it public (required for GitHub Pages on free accounts)
4. Don't initialize with README, .gitignore, or license (since we already have code)

## Step 2: Update VitePress Configuration

Update the base URL in `.vitepress/config.ts` to match your new repository name:

```typescript
export default defineConfig({
  base: '/your-repo-name/', // Replace with your actual repo name
  // ... rest of config
})
```

## Step 3: Add GitHub Actions Workflow

Create `.github/workflows/deploy.yml` for automatic deployment:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main, 250812-working-ui ] # Add your branch name
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          
      - name: Install dependencies
        run: npm ci
        
      - name: Build
        run: npm run build
        
      - name: Setup Pages
        uses: actions/configure-pages@v4
        
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: .vitepress/dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## Step 4: Push to New Repository

```bash
# Add the new remote (replace with your repo URL)
git remote add deploy https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push your current branch to the new repo
git push deploy 250812-working-ui

# Or if you want to push as main branch
git push deploy 250812-working-ui:main
```

## Step 5: Enable GitHub Pages

1. Go to your repository on GitHub
2. Navigate to Settings > Pages
3. Under "Build and deployment", select "GitHub Actions" as the source
4. Save the settings

## Step 6: Access Your Site

After the workflow runs successfully, your site will be available at:
`https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/`

## Alternative: Manual Deployment

If you prefer manual deployment:

```bash
# Build the site
npm run build

# Navigate to the dist folder
cd .vitepress/dist

# Initialize git and push to gh-pages branch
git init
git add -A
git commit -m 'deploy'
git push -f https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git main:gh-pages
```

Then set GitHub Pages to deploy from the `gh-pages` branch.

## Notes

- The GitHub Actions workflow will automatically deploy on every push to the specified branches
- Make sure your repository is public for GitHub Pages to work on free accounts
- The first deployment might take a few minutes to become available
- Check the Actions tab in your repository to monitor deployment status