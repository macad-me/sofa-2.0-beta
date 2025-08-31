# GitHub Workflows

## Download SOFA Binaries

The `download-sofa-binaries.yml` workflow automatically downloads and updates SOFA CLI binaries from the [sofa-core-cli repository](https://github.com/headmin/sofa-core-cli/releases).

### Features

- **🔄 Automatic Updates**: Runs daily to check for new releases
- **📱 Manual Trigger**: Can be triggered manually with specific version
- **🐧 Multi-Platform**: Downloads both Linux (x86_64) and macOS (ARM64) binaries
- **⚡ Smart Updates**: Only updates if a newer version is available
- **📝 Version Tracking**: Maintains `.sofa-version` files to track current version

### Triggers

1. **Daily Schedule**: Runs at 6 AM UTC to check for new releases
2. **Manual Dispatch**: Trigger manually from GitHub Actions tab
3. **Workflow Changes**: Runs when the workflow file is modified

### Manual Usage

1. Go to **Actions** → **Download SOFA Binaries**
2. Click **Run workflow**
3. Optionally specify a version (e.g., `v0.1.0-beta1`) or use `latest`

### Binary Locations

- **Linux x86_64**: `bin-linux/`
- **macOS ARM64**: `bin/`

### Version Files

- `bin/.sofa-version` - Current macOS binary version
- `bin-linux/.sofa-version` - Current Linux binary version

The workflow will automatically commit and push updates when new binaries are available.