# SOFA - Simple Organized Feed for Apple Software Updates

![Deploy Status](https://github.com/headmin/sofa-summer-25/actions/workflows/deploy.yml/badge.svg)
[![Live Site](https://img.shields.io/badge/Live-sofa25.macadmin.me-blue)](https://sofa25.macadmin.me)

## Overview

SOFA is a comprehensive web interface for tracking Apple software updates, including macOS, iOS, tvOS, watchOS, visionOS, and Safari. Built with VitePress and Vue 3, it provides a modern, responsive dashboard for Mac Admins.

## 🌐 Live Site

Visit: [https://sofa25.macadmin.me](https://sofa25.macadmin.me)

## 🚀 Features

- **Multi-Platform Support**: Track updates for all Apple platforms
- **Real-time Data**: Live JSON feeds with latest release information
- **Security Information**: CVE tracking and security update details
- **Responsive Design**: Optimized for desktop and mobile devices
- **Dark Mode**: Full dark mode support
- **GitHub Integration**: Star count and community links

## 🛠️ Tech Stack

- **Framework**: [VitePress](https://vitepress.dev/)
- **UI Components**: Vue 3 Composition API
- **Styling**: Tailwind CSS
- **Package Manager**: pnpm
- **Deployment**: GitHub Pages with GitHub Actions
- **Domain**: Custom domain via GitHub Pages

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/headmin/sofa-summer-25.git
cd sofa-summer-25

# Install dependencies
pnpm install

# Start development server
pnpm run dev

# Build for production
pnpm run build

# Preview production build
pnpm run preview
```

## 🏗️ Project Structure

```
.
├── .vitepress/
│   ├── config.mts          # VitePress configuration
│   └── theme/
│       ├── components/     # Vue components
│       ├── style.css       # Global styles
│       └── index.ts        # Theme configuration
├── macos/                  # macOS documentation pages
├── ios/                    # iOS documentation pages
├── tvos/                   # tvOS documentation pages
├── watchos/                # watchOS documentation pages
├── visionos/               # visionOS documentation pages
├── safari/                 # Safari documentation pages
├── public/                 # Static assets
│   └── CNAME              # Custom domain configuration
└── .github/
    └── workflows/
        └── deploy.yml      # GitHub Actions deployment
```

## 🚀 Deployment

The site automatically deploys to GitHub Pages when changes are pushed to the main branch.

### Manual Deployment

1. Go to [Actions](https://github.com/headmin/sofa-summer-25/actions)
2. Select "Build and Deploy to GitHub Pages"
3. Click "Run workflow"

## 🔧 Configuration

### Custom Domain

The site is configured to use `sofa25.macadmin.me`. To change:

1. Update `public/CNAME` with your domain
2. Update DNS records to point to GitHub Pages
3. Configure domain in repository settings

### Base URL

For custom domains, the base URL is `/`. For GitHub Pages subdomain, update in `.vitepress/config.mts`:

```javascript
export default defineConfig({
  base: '/', // or '/repository-name/' for github.io subdomain
  // ...
})
```

## 📊 Data Sources

The site fetches data from JSON feeds:
- macOS: `/v1/macos_data_feed.json`
- iOS: `/v1/ios_data_feed.json`
- Beta releases: `/v1/apple-beta-os-feed.json`
- External feed: `https://beta-feed.macadmin.me/v1/apple-beta-os-feed.json`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is part of Mac Admins Open Source.

## 🔗 Links

- **Repository**: [github.com/headmin/sofa-summer-25](https://github.com/headmin/sofa-summer-25)
- **Live Site**: [sofa25.macadmin.me](https://sofa25.macadmin.me)
- **Mac Admins**: [macadmins.org](https://www.macadmins.org/)
- **Original SOFA**: [github.com/macadmins/sofa](https://github.com/macadmins/sofa)

## 📝 Development Notes

See [CLAUDE.md](CLAUDE.md) for detailed development documentation and architectural decisions.

---

Built with ❤️ by Mac Admins Open Source