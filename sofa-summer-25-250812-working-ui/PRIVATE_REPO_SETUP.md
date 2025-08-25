# Private Metrics Collector Repository Setup

## Complete Setup Instructions

### 1. Create the Private Repository

```bash
# Go to GitHub and create:
Repository name: sofa-metrics-collector
Visibility: Private
Initialize with: README
```

### 2. Clone and Setup

```bash
git clone https://github.com/headmin/sofa-metrics-collector.git
cd sofa-metrics-collector
```

### 3. Create Directory Structure

```bash
mkdir -p .github/workflows
```

### 4. Add the Workflow File

Create `.github/workflows/fetch-metrics.yml` with the content from:
`/Users/henry/Projects/Work/sofa-web-ui-preview/metrics-collector/fetch-metrics.yml`

### 5. Configure GitHub Secrets

Go to your **private repo**: Settings → Secrets and variables → Actions

Add these secrets:

#### CLOUDFLARE_API_TOKEN
1. Go to: https://dash.cloudflare.com/profile/api-tokens
2. Click "Create Token"
3. Use "Custom token" template
4. Set permissions:
   - Zone → Analytics → Read
   - Zone → Zone → Read
5. Zone Resources:
   - Include → Specific zone → sofa25.macadmin.me
6. Click "Continue to summary" → "Create Token"
7. Copy the token (you won't see it again!)

#### CLOUDFLARE_ZONE_ID
1. Go to: https://dash.cloudflare.com
2. Select: sofa25.macadmin.me
3. Right sidebar → Copy Zone ID

#### PUBLIC_REPO_TOKEN
1. Go to: https://github.com/settings/tokens/new
2. Note: "SOFA Metrics Push"
3. Expiration: 90 days
4. Select scopes:
   - ✅ repo (all)
   - ✅ workflow
5. Generate token and copy it

### 6. Commit and Push

```bash
git add .
git commit -m "Add metrics fetcher workflow"
git push origin main
```

### 7. Test the Workflow

1. Go to: https://github.com/headmin/sofa-metrics-collector/actions
2. Click: "Fetch Cloudflare Metrics and Push to Public Repo"
3. Click: "Run workflow" → Select main → Run

### 8. Verify Success

Check these locations:
1. **Workflow logs**: Should show green checkmarks
2. **Public repo**: Check for new file at `public/v1/metrics.json`
3. **Dashboard**: Visit https://sofa25.macadmin.me and check Data Statistics bento

## Troubleshooting

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "Bad credentials" error | Regenerate PUBLIC_REPO_TOKEN with correct permissions |
| "Zone not found" error | Verify CLOUDFLARE_ZONE_ID is correct |
| "Authentication error" | Check CLOUDFLARE_API_TOKEN has Analytics:Read permission |
| No metrics.json created | Check workflow logs for JavaScript errors |
| Push fails | Ensure PUBLIC_REPO_TOKEN has repo write access |

### Manual Test Commands

Test Cloudflare API locally:
```bash
curl -X GET "https://api.cloudflare.com/client/v4/zones/YOUR_ZONE_ID/analytics/dashboard?since=2024-12-13&until=2025-01-12" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json"
```

## Workflow Schedule

The workflow runs:
- **Automatically**: Every 6 hours (0, 6, 12, 18 UTC)
- **Manually**: Via Actions tab → Run workflow

To change schedule, edit the cron expression:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
  # Examples:
  # - cron: '0 */3 * * *'  # Every 3 hours
  # - cron: '0 0 * * *'    # Once daily at midnight
  # - cron: '*/30 * * * *' # Every 30 minutes
```

## Metrics Data Structure

The workflow generates this JSON structure:
```json
{
  "timestamp": "ISO 8601 timestamp",
  "period": {
    "start": "30 days ago",
    "end": "today",
    "days": 30
  },
  "metrics": {
    "totalRequests": { "value": number, "formatted": "4.56M" },
    "pageViews": { "value": number, "formatted": "1.6k" },
    "uniqueVisitors": { "value": number, "formatted": "1.4k" },
    "bandwidth": { "bytes": number, "formatted": "387.38 GB" },
    "apiRequests": { "value": number, "formatted": "3.11M" }
  },
  "calculated": {
    "dailyAverage": {
      "requests": number,
      "visitors": number,
      "formatted": { ... }
    }
  }
}
```

## Dashboard Integration

The SOFA dashboard automatically:
1. Fetches `/v1/metrics.json` on page load
2. Displays metrics in Data Statistics bento
3. Shows "Live" badge when data is fresh
4. Falls back to "--" if data unavailable
5. Shows relative update time (e.g., "2h ago")

## Next Steps

After setup:
1. ✅ Workflow runs every 6 hours automatically
2. ✅ Metrics display on dashboard
3. ✅ History kept for 7 days
4. ✅ No manual intervention needed

Optional enhancements:
- Add more metrics (top pages, countries)
- Create graphs/charts
- Add email alerts for anomalies
- Export historical data

---

**Security Note**: Never commit API tokens to code. Always use GitHub Secrets.