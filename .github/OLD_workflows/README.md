# GitHub Workflows

## SOFA Data Pipeline

The `sofa-pipeline.yml` workflow is the **single comprehensive workflow** that handles all SOFA operations including binary downloads, data processing, and RSS generation.

### Features

- **🔄 Complete Pipeline**: Downloads binaries → gather → fetch → build → RSS (optional)
- **📱 On-Demand Execution**: Full manual control via GitHub Actions interface
- **🎯 Stage Selection**: Run specific pipeline stages or complete workflow
- **⚡ Smart Caching**: Automatic binary caching for faster runs
- **📊 Rich Reporting**: Detailed summaries and artifact management
- **🔧 Auto-commit**: Commits all pipeline results and updated binaries

### Manual Triggers (On-Demand)

1. **Go to GitHub Actions**: Navigate to your repository → Actions tab
2. **Select Workflow**: Click "SOFA Data Pipeline"
3. **Run Workflow**: Click the "Run workflow" button
4. **Configure Options**:
   - **Generate RSS**: Include RSS feed generation (default: true)
   - **Force Run**: Run even if no changes detected (default: false)
   - **Pipeline Stage**: Select stage to run (default: all)
     - `all`: Complete pipeline (recommended)
     - `gather`: Data collection only
     - `fetch`: Download/processing only
     - `build`: Feed generation only

### Automatic Triggers

- **🕕 Every 6 Hours**: Scheduled automatic runs
- **📝 Code Changes**: When scripts/ or config/ directories are modified
- **🔄 Workflow Updates**: When the workflow file itself is changed

### Pipeline Stages

1. **Prepare**: Check for changes and determine SOFA CLI version
2. **Download Binaries**: Get latest SOFA CLI tools from releases
3. **Pipeline Execution**: Run selected stages (gather/fetch/build)
4. **RSS Generation**: Create RSS feeds (if enabled)
5. **Commit Results**: Auto-commit all generated data and binaries

### What Gets Committed

- **`data/feeds/`**: Generated JSON feed files
- **`data/resources/`**: Updated resource files (JSON, NDJSON)  
- **`bin-linux/`**: SOFA CLI binaries (when updated)
- **RSS Feeds**: Generated XML files (in data/feeds/v1/)

### Configuration

- **Environment Variables**: Set in `.env.production`
- **Pipeline Config**: TOML files in `config/` directory
- **Runtime Options**: Via workflow dispatch inputs

## Deploy Pages

The `deploy-pages.yml` workflow handles GitHub Pages deployment for the VitePress documentation site.

### Usage

- **Automatic**: Triggered on pushes to main branch
- **Manual**: Can be triggered manually if needed

This workflow deploys the built documentation site to GitHub Pages for public access.