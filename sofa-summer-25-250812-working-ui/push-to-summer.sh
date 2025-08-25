#!/bin/bash

echo "🚀 Pushing to sofa-summer-25 repository..."
echo ""
echo "Current branch: 250812-working-ui"
echo "Target repository: https://github.com/headmin/sofa-summer-25.git"
echo "Target branch: main"
echo ""

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "Using GitHub CLI..."
    gh auth login
    git push https://github.com/headmin/sofa-summer-25.git 250812-working-ui:main
else
    echo "GitHub CLI not found. Please use one of these methods:"
    echo ""
    echo "Option 1: Use GitHub Desktop"
    echo "  - Open GitHub Desktop"
    echo "  - Add remote: sofa-summer-25"
    echo "  - Push branch 250812-working-ui as main"
    echo ""
    echo "Option 2: Use Personal Access Token"
    echo "  1. Go to: https://github.com/settings/tokens"
    echo "  2. Generate new token with 'repo' scope"
    echo "  3. Run: git push https://YOUR_TOKEN@github.com/headmin/sofa-summer-25.git 250812-working-ui:main"
    echo ""
    echo "Option 3: Install GitHub CLI"
    echo "  brew install gh"
    echo "  gh auth login"
    echo "  git push summer 250812-working-ui:main"
fi