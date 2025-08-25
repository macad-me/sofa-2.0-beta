# SOFA Metrics Collector (Private Repository)

This private repository securely fetches Cloudflare Analytics data and generates a public metrics.json file for the SOFA dashboard.

## Setup Instructions

### 1. Create Private Repository
```bash
# Create new private repo: sofa-metrics-collector
git init
git remote add origin https://github.com/headmin/sofa-metrics-collector.git
```

### 2. Add GitHub Secrets
Go to Settings → Secrets → Actions and add:
- `CLOUDFLARE_API_TOKEN` - Your Cloudflare API token
- `CLOUDFLARE_ZONE_ID` - Your zone ID (from Cloudflare dashboard)
- `GITHUB_TOKEN` - Personal access token with repo write permissions

### 3. Cloudflare API Token Setup
1. Go to Cloudflare → My Profile → API Tokens
2. Create Token → Custom token
3. Permissions needed:
   - Zone → Analytics → Read
   - Zone → Zone → Read
4. Zone Resources: Include → Specific zone → sofa25.macadmin.me

## Metrics Output

The workflow generates `metrics.json` with:
```json
{
  "timestamp": "2025-01-12T10:30:00Z",
  "period": "last_30_days",
  "metrics": {
    "requests": 4560000,
    "pageViews": 1630,
    "uniqueVisitors": 1350,
    "dataTransfer": 387380000000,
    "apiRequests": 3110000
  },
  "calculated": {
    "dailyAverage": {
      "requests": 152000,
      "visitors": 45
    }
  }
}
```

## Security Notes
- API keys never exposed in public repo
- Metrics data is sanitized (no PII)
- Updates every 6 hours via cron schedule