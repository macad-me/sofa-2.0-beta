# GitHub Workflows

## SOFA Data Pipeline

The `sofa-pipeline.yml` workflow runs the complete SOFA data processing pipeline, including data gathering, fetching, building, and optional RSS generation.

### Features

- **🔄 Full Pipeline**: Runs gather → fetch → build stages automatically
- **📱 Manual Control**: Trigger manually with custom options
- **📡 RSS Generation**: Optional RSS feed generation after pipeline
- **🎯 Stage Selection**: Run specific pipeline stages (gather, fetch, build, or all)
- **⚡ Smart Caching**: Caches SOFA binaries and dependencies for faster runs
- **📊 Rich Reporting**: Detailed summaries and artifact uploads
- **🔧 Auto-commit**: Automatically commits pipeline results

### Triggers

1. **Every 6 Hours**: Scheduled automatic runs
2. **Manual Dispatch**: Trigger from GitHub Actions with options:
   - Generate RSS feeds (default: true)
   - Force run (ignore change detection)
   - Pipeline stage (all, gather, fetch, build)
3. **Code Changes**: Runs when scripts/ or config/ directories change

### Manual Usage

1. Go to **Actions** → **SOFA Data Pipeline**
2. Click **Run workflow**
3. Configure options:
   - **Generate RSS**: Include RSS feed generation
   - **Force Run**: Run even if no changes detected
   - **Pipeline Stage**: Select which stage(s) to run

### Pipeline Stages

- **Gather**: Collect source data using `sofa-gather`
- **Fetch**: Download and process updates using `sofa-fetch`  
- **Build**: Generate feeds and resources using `sofa-build`
- **RSS** (optional): Generate RSS feeds using `generate_rss.py`

### Configuration

Pipeline behavior is configured via:
- `pipeline-config.yml`: Workflow settings and defaults
- `config/*.toml`: SOFA CLI configuration files
- Workflow inputs: Runtime parameters

### Artifacts

The workflow generates:
- **Pipeline Data**: All generated feeds and resources
- **RSS Feeds**: Generated RSS XML files
- **Status Reports**: Detailed execution summaries

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