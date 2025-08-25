# SOFA VitePress UI - Development Log

## Project Overview
SOFA (Simple Organized Feed for Apple Software Updates) is a VitePress-based web interface for displaying Apple software update information. This document tracks the development progress, architectural decisions, and key implementations.

## Current State (Latest Session - 2024-08-19)

### SOFA Pipeline - Complete Overhaul ✅
**Primary Issue**: The feed data was completely empty - OSVersions arrays had no data.

**Root Causes Discovered**:
1. Version extraction regex failed on multi-word OS names (e.g., "macOS Big Sur 11.7.9" → incorrectly "15.7.1")
2. Config files missing or in wrong locations
3. Directory structure chaos between local and GitHub runner environments
4. Cache not being utilized properly by GitHub Actions
5. SSL certificate failures preventing GDMF data fetch

**Solutions Implemented**:
1. **Fixed Version Extraction**: Changed regex from `\w+` to `(?:\w+\s+)+` to handle multi-word OS names
2. **Standardized Directory Structure**: Added fallback paths to handle different environments
3. **Implemented Cache Usage**: Pipeline can now run stages 2 & 3 using cached data
4. **Created Test Suite**: `test_pipeline.sh` validates all functionality
5. **Fixed GitHub Actions**: Workflow now properly caches and generates feeds

**Key Accomplishments**:
- ✅ Fixed "macOS Big Sur 11.7.9" extraction (now correctly 11.7.9)
- ✅ Pipeline generates 6 v1 feed files with actual data
- ✅ 5 macOS versions tracked with 59 KEVs enriched
- ✅ Pipeline runs in ~2.5 seconds using cache
- ✅ 100% test success rate

### Pipeline Testing with act ✅
**Goal**: Use `act` for local GitHub Actions simulation

**Implementation**:
- Created `.actrc` configuration
- Set up environment variables
- Standardized directory handling
- Enabled rapid local debugging

## Pipeline Architecture

### Three-Stage Pipeline
```
Stage 1: Fetch & Cache (can be skipped)
├── Fetch Apple security pages
├── Fetch GDMF data
├── Fetch KEV catalog
└── Cache all data locally

Stage 2: Process & Build (uses cache)
├── Build security releases from cache
├── Extract CVE information
├── Analyze KEV patterns
└── Enrich with vulnerability data

Stage 3: Produce Feeds (uses processed data)
├── Apply retention policies
├── Generate v1 feeds (backward compatible)
├── Generate RSS feeds
└── Validate output
```

### Key Commands
```bash
# Run full pipeline
cd data-processing
uv run python src/pipeline/run_sofa_pipeline.py

# Run using cache only (stages 2 & 3)
uv run python src/pipeline/run_sofa_pipeline.py --stages 2 3

# Run tests
./test_pipeline.sh

# Test with act (GitHub Actions simulation)
act push --job build
```

## Major Complications & Resolutions

### 1. Directory Structure Chaos
**Problem**: Scripts expected files in different locations
- `data-processing/`, `data/`, `scripts/`, `.cache/` vs `data/cache/`

**Resolution**: Added multiple path searches and standardized on `data-processing/` structure

### 2. Repository Branch Incompatibility
**Problem**: Different branches had entirely different commit histories with no common ancestors

**Resolution**: Created new branch from origin/main and applied fixes cleanly

### 3. Version Extraction Bug
**The Big Sur Problem**: "macOS Big Sur 11.7.9" extracted as "15.7.1"

**Fix Applied**:
```python
# Before (failed on multi-word OS names)
r"macOS\s+\w+\s+(\d+(?:\.\d+)*)"

# After (handles "Big Sur" correctly)
r"macOS\s+(?:\w+\s+)+(\d+(?:\.\d+)*)"
```

### 4. Cache Structure Mismatch
**Problem**: Different pipeline stages expected different cache formats

**Resolution**: 
- Created reparse script to fix cache structure
- Standardized on SHA1 hash-based filenames
- Implemented proper cache loading functions

### 5. SSL Certificate Failures
**Problem**: GDMF fetch failed with SSL certificate errors

**Resolution**: Falls back to cached GDMF data when SSL fails

## Files Modified in Pipeline Fix

### Core Fixes
- `data-processing/src/builders/build_security_releases.py` - Fixed version extraction
- `data-processing/config.json` - Added missing OS versions
- `.github/workflows/build-feeds.yml` - Fixed pipeline execution
- `test_pipeline.sh` - Comprehensive test suite

### Generated/Updated
- `v1/*.json` - All feed files with correct data
- `reparse_cache.py` - Cache repair utility

## Previous UI Development (2025-01-11)

### Mobile Navigation - FIXED ✅
**Issue**: Mobile hamburger menu behavior was problematic after multiple implementation attempts.

**Solution**: Restored VitePress native mobile navigation (from commit `3105718`):
- Removed custom hamburger menu implementation
- Allow VitePress's built-in mobile menu to work naturally
- Changed mobile breakpoint from 768px to 960px
- Selective hiding of VitePress navbar content while preserving mobile functionality

**Key Files Modified**:
- `.vitepress/theme/components/CustomNavBar.vue` - Removed custom hamburger button
- `.vitepress/theme/custom-layout.css` - Updated to show VitePress mobile menu

### Bento Grid Centering - FIXED ✅
**Issue**: Bento grid was not centering properly during window resize.

**Solution**: Enhanced CSS specificity (from commit `8f89b17`):
- Added explicit grid properties with `!important` declarations
- Restored responsive breakpoints: 1→2→3 columns
- Used `grid-template-columns: repeat(n, 1fr)` for reliable centering

**Key Files Modified**:
- `.vitepress/theme/bento-system.css` - Enhanced centering rules

### VitePress Navbar Title Cleanup - FIXED ✅
**Issue**: Legacy VitePress title element appearing alongside custom navbar.

**Solution**: Added specific CSS to hide VitePress default title elements.

## Architecture Overview

### Theme Structure
```
.vitepress/theme/
├── components/
│   ├── CustomNavBar.vue      # Custom SOFA branding navbar
│   ├── SOFADashboard.vue     # Main dashboard with bento grid
│   ├── BentoGrid.vue         # Bento grid container
│   ├── BentoCard.vue         # Individual bento cards
│   └── BentoButton.vue       # Interactive bento elements
├── bento-system.css          # Bento grid styling system
├── custom-layout.css         # VitePress layout overrides
├── style.css                 # Base theme styles
├── tailwind.css              # Tailwind imports
└── index.ts                  # Theme configuration
```

### Key Components

#### CustomNavBar.vue
- **Purpose**: Custom SOFA branding and navigation
- **Features**: Logo, navigation links, theme toggle, GitHub link
- **Mobile**: Works with VitePress native mobile menu
- **Positioning**: Fixed at top with backdrop blur

#### SOFADashboard.vue
- **Purpose**: Main dashboard with bento grid layout
- **Data Sources**: Real JSON feeds (macos_data_feed.json, ios_data_feed.json, apple-beta-os-feed.json)
- **Features**: Platform navigation, version displays, feed links, community links
- **Container**: `dashboard-container` class with centered layout

#### Bento System
- **Grid**: Responsive 1→2→3 column layout
- **Cards**: Equal height with hover effects
- **Variants**: Platform-specific colors and gradients
- **Interactions**: Clickable buttons, copy functionality

### CSS Architecture

#### Responsive Breakpoints
- **Mobile**: < 768px (1 column)
- **Tablet**: 768px - 1024px (2 columns)
- **Desktop**: > 1024px (3 columns)
- **VitePress Mobile Menu**: < 960px

#### Color System
- **macOS**: Blue theme (`text-blue-600`)
- **iOS**: Purple theme (`text-purple-600`)
- **watchOS/tvOS**: Green theme (`text-green-600`)
- **Safari**: Orange theme (`text-orange-600`)
- **Community**: Indigo theme (`text-indigo-600`)
- **Quick Board**: Emerald theme (`text-emerald-600`)

### Data Integration

#### JSON Feeds
- **macOS Data**: `/v1/macos_data_feed.json`
- **iOS Data**: `/v1/ios_data_feed.json`
- **Beta Data**: `/v1/apple-beta-os-feed.json`
- **External**: `https://beta-feed.macadmin.me/v1/apple-beta-os-feed.json`

#### Data Processing
- Version mapping with security info
- CVE count display
- Release date formatting
- Build number display

## Navigation Configuration

### VitePress Config
```javascript
nav: [
  { text: 'macOS', link: '/macos/sequoia' },
  { text: 'iOS', link: '/ios/ios18' },
  { text: 'tvOS', link: '/tvos/tvos18' },
  { text: 'watchOS', link: '/watchos/watchos11' },
  { text: 'visionOS', link: '/visionos/visionos2' },
  { text: 'Safari', link: '/safari/safari18' }
]
```

### Sidebar Structure
- **macOS**: Tahoe 26, Sequoia 15, Sonoma 14, Ventura 13, Monterey 12
- **iOS**: iOS 26, iOS 18, iOS 17
- **tvOS**: tvOS 26, tvOS 18, tvOS 17
- **visionOS**: visionOS 2
- **watchOS**: watchOS 26, watchOS 11
- **Safari**: Safari 18

## Mobile Navigation Behavior

### Desktop (> 960px)
- Custom SOFA navbar visible
- VitePress navbar hidden
- Full navigation links shown
- Sidebar visible on content pages
- No sidebar on home page

### Mobile (≤ 960px)
- Custom SOFA navbar with minimal content
- VitePress native hamburger menu appears
- Navigation links hidden (except GitHub & theme toggle)
- Hamburger reveals VitePress mobile screen overlay
- Sidebar slides in from left with proper animations

## Dark Mode Support

### Implementation
- Uses VitePress built-in dark mode system
- Custom theme toggle in navbar
- Automatic detection of system preference
- Persistent storage of user choice

### Styling
- All components support dark mode variants
- CSS custom properties for theme colors
- Proper contrast ratios maintained

## Performance Considerations

### Optimizations
- Static JSON imports for faster loading
- Lazy loading of components
- Minimal CSS with Tailwind purging
- Optimized images and icons

### Bundle Size
- VitePress static generation
- Tree-shaking unused code
- Minimal JavaScript footprint

## Development Workflow

### Git Workflow
- Main branch: `250530-better-mobile`
- Feature branches for major changes
- Commit messages with context

### Key Commits Referenced
- `cb9ef1815d6ca39e1b73d1e4970f45dd08ce76a1` - Working burger menu
- `3105718` - VitePress native mobile navigation
- `8f89b17c87bc7e387db9ed6f125df2f20ecdc376` - Bento grid centering

### Testing Approach
- Manual testing across device sizes
- Dark/light mode switching
- Navigation functionality
- Data loading verification

## Deployment

### Build Process
```bash
npm run dev     # Development server
npm run build   # Production build
npm run preview # Preview build
```

### GitHub Pages
- Base URL: `/sofa-web-ui-preview/`
- Static site generation
- Automatic deployment on push

## Recent Session Changes (Latest)

### Files Modified
1. **CustomNavBar.vue**:
   - Removed custom hamburger menu button and JavaScript
   - Restored original mobile CSS from commit 3105718
   - Cleaned up mobile button styling

2. **custom-layout.css**:
   - Changed approach to allow VitePress mobile menu
   - Added CSS to hide VitePress title elements
   - Updated mobile breakpoint to 960px
   - Preserved sidebar positioning and styling

3. **bento-system.css**:
   - Enhanced bento grid centering with explicit CSS properties
   - Added responsive grid-template-columns with !important
   - Restored proper 1→2→3 column behavior

### Working Commits Referenced
- **3105718**: VitePress native mobile navigation working
- **8f89b17**: Bento grid centering working properly
- **cb9ef18**: Earlier burger menu implementation

## Troubleshooting

### Common Issues

#### Mobile Menu Not Working
1. Check VitePress config has proper nav/sidebar structure
2. Verify custom-layout.css allows VitePress mobile elements
3. Ensure breakpoint is set to 960px, not 768px

#### Bento Grid Not Centering
1. Check dashboard-container class is present
2. Verify bento-system.css has proper grid properties
3. Ensure no conflicting CSS with higher specificity

#### Dark Mode Issues
1. Check theme toggle JavaScript functionality
2. Verify CSS custom properties are defined
3. Ensure localStorage persistence is working

### Debug Commands
```bash
# Check current git status
git status

# View recent commits
git log --oneline -10

# Check file differences
git diff HEAD~1 filename

# Check VitePress build
npm run build 2>&1 | grep -i error
```

## Future Improvements

### Planned Features
- Real-time data updates
- Enhanced search functionality
- User preferences storage
- Advanced filtering options

### Technical Debt
- Consolidate CSS architecture
- Improve TypeScript coverage
- Add comprehensive testing
- Performance monitoring

## Contact & Resources

### Documentation
- [VitePress Documentation](https://vitepress.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vue 3 Composition API](https://vuejs.org/guide/composition-api-introduction.html)

### Community
- **GitHub**: https://github.com/macadmins/sofa
- **Slack**: MacAdmins Slack workspace
- **Foundation**: https://www.macadmins.org/

---

*Last updated: 2025-01-11*
*Session: Mobile navigation and bento grid centering fixes*
*Status: Both major issues resolved - VitePress native mobile menu working, bento grid centering restored*
- make "star us on GitHub"
- Essential Resources integrated into platform pages (no longer separate page)