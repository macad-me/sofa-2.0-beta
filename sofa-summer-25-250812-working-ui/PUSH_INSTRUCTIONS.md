# Push to sofa-summer-25 Repository

## Manual Push Instructions

Since we're having authentication issues, here are the manual steps to push your code:

### Option 1: Using GitHub Desktop or a Git GUI
1. Add the new remote in your Git GUI
2. Push the `250812-working-ui` branch to `sofa-summer-25` as the `main` branch

### Option 2: Using Command Line with Personal Access Token

1. Create a Personal Access Token on GitHub:
   - Go to https://github.com/settings/tokens
   - Generate new token (classic)
   - Give it `repo` scope
   - Copy the token

2. Push using the token:
```bash
git push https://YOUR_TOKEN@github.com/headmin/sofa-summer-25.git 250812-working-ui:main
```

### Option 3: Fix SSH and Push

1. Check if you have SSH keys:
```bash
ls -la ~/.ssh
```

2. If not, generate one:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

3. Add the SSH key to ssh-agent:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

4. Copy your public key:
```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

5. Add it to GitHub:
   - Go to https://github.com/settings/keys
   - New SSH key
   - Paste the key

6. Test the connection:
```bash
ssh -T git@github.com
```

7. Push your code:
```bash
git push summer 250812-working-ui:main
```

## After Pushing

1. Go to your repository: https://github.com/headmin/sofa-summer-25
2. Navigate to Settings > Pages
3. Under "Build and deployment":
   - Source: Select "GitHub Actions"
4. Save the settings
5. The workflow should trigger automatically when you push
6. Check the Actions tab to monitor deployment

## Verify Deployment

Once deployed, your site will be available at:
- If using custom domain: Configure in Settings > Pages
- Default URL: https://headmin.github.io/sofa-summer-25/

## Note for Private Repositories

Private repositories require a GitHub Pro, Team, or Enterprise account for GitHub Pages. If you're on a free plan, you'll need to either:
1. Make the repository public
2. Use GitHub Pro/Team/Enterprise
3. Deploy to an alternative service like Vercel or Netlify