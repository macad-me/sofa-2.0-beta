#!/bin/bash

# SOFA Build Script
# Builds the VitePress site for production

echo "🏗️  Building SOFA 2.0 for Production..."
echo ""

# Navigate to docs directory
cd "$(dirname "$0")/docs" || {
    echo "❌ Error: docs directory not found"
    exit 1
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found in docs directory"
    exit 1
fi

# Check if pnpm is available
if ! command -v pnpm >/dev/null 2>&1; then
    echo "❌ Error: pnpm not found. Please install pnpm:"
    echo "   npm install -g pnpm"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    pnpm install
fi

echo "📍 Location: $(pwd)"
echo "🎯 Target: .vitepress/dist/"
echo ""
echo "================================================"
echo ""

# Build the site with pnpm
pnpm run build

# Show results
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo "📁 Output: $(pwd)/.vitepress/dist/"
    
    # Show build size
    if [ -d ".vitepress/dist" ]; then
        echo "📊 Build size:"
        du -sh .vitepress/dist/
    fi
else
    echo ""
    echo "❌ Build failed!"
    exit 1
fi