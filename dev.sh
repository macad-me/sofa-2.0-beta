#!/bin/bash

# SOFA Development Server Script
# Starts the VitePress development server with pnpm

echo "🚀 Starting SOFA 2.0 Development Server..."
echo ""

# Navigate to docs directory
cd "$(dirname "$0")/docs" || {
    echo "❌ Error: docs directory not found"
    exit 1
}

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

echo "🏗️  Starting development server..."
echo "📍 Location: $(pwd)"
echo "🌐 URL: http://localhost:5173/"
echo ""
echo "💡 Press Ctrl+C to stop the server"
echo "================================================"
echo ""

# Start the development server with pnpm
pnpm run dev