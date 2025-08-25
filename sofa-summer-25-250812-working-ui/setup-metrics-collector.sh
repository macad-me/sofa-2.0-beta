#!/bin/bash

# Setup script for sofa-metrics-collector repository
# Run this from the sofa-web-ui-preview directory

METRICS_DIR="/Users/henry/Projects/Work/sofa-metrics-collector"

echo "🚀 Setting up SOFA Metrics Collector..."

# Create directory if it doesn't exist
if [ ! -d "$METRICS_DIR" ]; then
  echo "Creating metrics collector directory..."
  mkdir -p "$METRICS_DIR"
fi

# Copy all necessary files
echo "📁 Copying workflow and documentation files..."

# Create directories
mkdir -p "$METRICS_DIR/.github/workflows"

# Copy workflow file
cp "/Users/henry/Projects/Work/sofa-web-ui-preview/metrics-collector/fetch-metrics.yml" \
   "$METRICS_DIR/.github/workflows/fetch-metrics.yml"

# Copy README if it doesn't exist or is different
if [ ! -f "$METRICS_DIR/README.md" ]; then
  cp "/Users/henry/Projects/Work/sofa-web-ui-preview/metrics-collector/README.md" \
     "$METRICS_DIR/README.md" 2>/dev/null || echo "README already exists"
fi

# Copy other documentation
cp "/Users/henry/Projects/Work/sofa-web-ui-preview/metrics-collector/SETUP_GUIDE.md" \
   "$METRICS_DIR/SETUP_GUIDE.md" 2>/dev/null || echo "SETUP_GUIDE already exists"

# Navigate to metrics directory
cd "$METRICS_DIR"

# Initialize git if needed
if [ ! -d ".git" ]; then
  echo "📝 Initializing git repository..."
  git init
fi

# Add git remote if not already added
if ! git remote | grep -q origin; then
  echo "🔗 Adding GitHub remote..."
  git remote add origin https://github.com/headmin/sofa-metrics-collector.git
fi

# Create initial commit
echo "💾 Creating initial commit..."
git add .
git commit -m "Initial setup of SOFA metrics collector" || echo "Nothing to commit"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to: https://github.com/headmin/sofa-metrics-collector/settings/secrets/actions"
echo "2. Add these secrets:"
echo "   - CLOUDFLARE_API_TOKEN"
echo "   - CLOUDFLARE_ZONE_ID" 
echo "   - PUBLIC_REPO_TOKEN"
echo ""
echo "3. Push to GitHub:"
echo "   cd $METRICS_DIR"
echo "   git push -u origin main"
echo ""
echo "4. Test the workflow:"
echo "   Go to Actions tab → Run workflow"
echo ""
echo "📚 See SECRETS_SETUP.md for detailed instructions"