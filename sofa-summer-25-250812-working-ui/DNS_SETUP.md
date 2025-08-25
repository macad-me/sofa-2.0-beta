# DNS Configuration for sofa25.macadmin.me

## DNS Records Required

To point `sofa25.macadmin.me` to GitHub Pages, you need to configure the following DNS records:

### Option 1: CNAME Record (Recommended for Subdomains)
If `sofa25` is a subdomain of `macadmin.me`:

```
Type: CNAME
Name: sofa25
Value: headmin.github.io
TTL: 3600 (or auto)
```

### Option 2: A Records (If using apex domain)
If you're using the root domain, add these A records:

```
Type: A
Name: @
Value: 185.199.108.153
TTL: 3600

Type: A
Name: @
Value: 185.199.109.153
TTL: 3600

Type: A
Name: @
Value: 185.199.110.153
TTL: 3600

Type: A
Name: @
Value: 185.199.111.153
TTL: 3600
```

### Option 3: ALIAS/ANAME Record (If your DNS provider supports it)
```
Type: ALIAS (or ANAME)
Name: sofa25
Value: headmin.github.io
TTL: Auto
```

## GitHub Repository Settings

1. Go to https://github.com/headmin/sofa-summer-25/settings/pages
2. Under "Custom domain", enter: `sofa25.macadmin.me`
3. Click "Save"
4. Wait for DNS check to complete (can take up to 24 hours)
5. Once verified, check "Enforce HTTPS" for secure connections

## Verification

After DNS propagation (usually within an hour, but can take up to 24 hours):

1. Visit https://sofa25.macadmin.me
2. Check DNS propagation status at: https://www.whatsmydns.net/
3. Verify GitHub Pages status in repository settings

## Troubleshooting

If the site doesn't load:

1. **Check DNS propagation**: Use `dig sofa25.macadmin.me` or `nslookup sofa25.macadmin.me`
2. **Verify CNAME file**: Ensure `/public/CNAME` contains `sofa25.macadmin.me`
3. **Check GitHub Pages settings**: Verify custom domain is set correctly
4. **Clear browser cache**: Try accessing in incognito/private mode
5. **Check Actions**: Ensure GitHub Actions workflow completed successfully

## SSL Certificate

GitHub Pages automatically provisions an SSL certificate for custom domains. This process:
- Starts after DNS verification
- Can take up to 24 hours
- Is managed by Let's Encrypt
- Auto-renews

## Important Notes

- The CNAME file in `/public/` is automatically copied to the build output
- VitePress base URL is set to `/` for custom domains
- DNS changes can take time to propagate globally
- Always use HTTPS once the certificate is provisioned