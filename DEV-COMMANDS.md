# 🚀 SOFA 2.0 Development Commands

Quick reference for local development with the new Tailwind CSS 4.1.12 setup.

## 📁 Project Structure
```
sofa-2.0-beta/
├── docs/           # VitePress documentation site (main development area)
├── data/           # SOFA data feeds and resources
├── bin/            # Binary tools
└── scripts/        # Automation scripts
```

## 🛠️ Development Commands

### Quick Start (Recommended)
```bash
# Start development server (uses pnpm)
./dev.sh
# or  
pnpm run dev
```
**Opens:** http://localhost:5173/

### Build Commands
```bash
# Build for production (uses pnpm)
./build.sh
# or
pnpm run build

# Build and preview production build locally (uses pnpm)  
./preview.sh
# or
pnpm run preview
```
**Preview opens:** http://localhost:4173/

### Direct pnpm Commands
```bash
pnpm install         # Install dependencies 
pnpm run dev         # Start dev server
pnpm run build       # Build for production
pnpm run preview     # Preview production build
pnpm run clean       # Clean install (removes node_modules & cache)
```

## 📦 Package Manager

The project **exclusively uses pnpm**:
- **GitHub Actions:** Uses pnpm 
- **Local development:** Uses pnpm only
- **All scripts:** Configured for pnpm

### Install pnpm (if needed)
```bash
npm install -g pnpm
```

## 🎨 Tailwind CSS 4.1.12

### Key Changes from v3:
- ✅ **CSS-based configuration** using `@theme` directive
- ✅ **Faster builds** with new engine
- ✅ **@reference directive** for @apply usage
- ✅ **All styling preserved** from v3

### Configuration Files:
- `docs/.vitepress/theme/tailwind.css` - Main Tailwind file with @theme config
- `docs/.vitepress/theme/bento-system.css` - Custom component styles
- `docs/postcss.config.js` - PostCSS configuration

## 🔧 Development Tips

### Hot Reload Issues?
```bash
# Clear VitePress cache
rm -rf docs/.vitepress/cache
./dev.sh
```

### Build Issues?
```bash
# Clear node_modules and reinstall
cd docs
rm -rf node_modules pnpm-lock.yaml
pnpm install
cd ..
./build.sh
```

### Mobile Testing
The project includes mobile-specific fixes for:
- Bento box overflow on narrow screens (≤360px)
- Responsive typography and spacing
- Touch-friendly navigation

## 📱 Mobile Development
```bash
# Start dev server with network access
cd docs
pnpm run dev --host
# Access from mobile device at: http://your-ip:5173
```

## 🚀 Deployment

### GitHub Pages (Automatic)
Push to `main` branch triggers automatic deployment via GitHub Actions.

### Manual Deployment
```bash
git push origin main
# Then go to GitHub Actions → "Deploy to GitHub Pages" → "Run workflow"
```

### Rollback (if needed)
```bash
git checkout backup-tailwind-3
git push origin backup-tailwind-3 --force-with-lease
```

## 📊 Performance

### Build Times (with Tailwind 4):
- **Development:** ~1-2s startup
- **Production build:** ~2-3s  
- **Data generation:** ~1-2s

### Bundle Size:
- **CSS:** Optimized with Tailwind 4 engine
- **JS:** VitePress optimizations
- **Assets:** Data feeds served efficiently

---

**Happy coding! 🎉**