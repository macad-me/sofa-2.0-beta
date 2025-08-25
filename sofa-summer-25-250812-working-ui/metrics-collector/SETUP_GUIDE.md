# Direct Push Setup Guide

## Quick Setup for Private Metrics Collector Repository

### Step 1: Create Private Repository

1. Go to GitHub and create a new **private** repository:
   - Name: `sofa-metrics-collector`
   - Visibility: **Private**
   - Initialize with README: Yes

### Step 2: Add GitHub Secrets

In your **private** repository (`sofa-metrics-collector`), go to:
**Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | How to Get It |
|-------------|---------------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare Dashboard → My Profile → API Tokens → Create Token |
| `CLOUDFLARE_ZONE_ID` | Cloudflare Dashboard → sofa25.macadmin.me → Right sidebar → Zone ID |
| `PUBLIC_REPO_TOKEN` | GitHub → Settings → Developer settings → Personal access tokens → Generate new token |

#### Creating the PUBLIC_REPO_TOKEN:
1. Go to https://github.com/settings/tokens/new
2. Name: "SOFA Metrics Push"
3. Expiration: 90 days (or longer)
4. Permissions needed:
   - ✅ repo (Full control of private repositories)
   - ✅ workflow (Update GitHub Action workflows)
5. Click "Generate token"
6. Copy the token immediately (you won't see it again!)

### Step 3: Add Workflow File

1. In your private repository, create the workflow directory:
```bash
mkdir -p .github/workflows
```

2. Copy the `fetch-metrics.yml` file to:
`.github/workflows/fetch-metrics.yml`

### Step 4: Test the Workflow

1. Go to your private repo's **Actions** tab
2. You should see "Fetch Cloudflare Metrics and Push to Public Repo"
3. Click on it, then click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow" button

### Step 5: Verify It Works

After the workflow runs:
1. Check the workflow logs for any errors
2. Go to your public repo (`sofa-summer-25`)
3. Check for the new file: `public/v1/metrics.json`
4. You should see a commit from "SOFA Metrics Bot"

---

## Update Dashboard to Use Metrics

Now update your SOFA dashboard to display the metrics: