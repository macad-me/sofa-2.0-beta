#!/bin/bash

# SOFA Preview Script
# Builds and serves the production build locally

echo "👁️  Building and Previewing SOFA 2.0..."
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
echo ""

# Build first
echo "🏗️  Building for production..."
pnpm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "🌐 Starting preview server..."
echo "📱 URL: http://localhost:4173/"
echo ""
echo "💡 Press Ctrl+C to stop the server"
echo "================================================"
echo ""

# Start preview server
pnpm run preview