# SOFA Data Processing Pipeline

This directory contains the data processing pipeline for SOFA (Security Orchestration for Apple) feeds.

## Structure

```
data-processing/
├── src/               # Source code
├── data/             # Generated data
│   ├── cache/        # Cached scraped data
│   ├── feeds/        # Output feeds
│   │   ├── v1/       # Legacy format feeds
│   │   └── v2/       # Enhanced format feeds
│   └── security_releases/  # Intermediate data
├── config/           # Configuration files
└── tests/           # Test suite
```

## GitHub Actions Workflow

The pipeline runs automatically via GitHub Actions:
- **Schedule**: Every 6 hours
- **Manual trigger**: Available via workflow_dispatch
- **Caching**: Uses actions/cache@v4 for dependencies and scraped data
- **Output**: v1 feeds are deployed to the `/v1` directory in the repository root

## Running Locally

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv venv
uv pip sync pyproject.toml

# Run complete pipeline
uv run python src/pipeline/run_sofa_pipeline.py

# Run specific stages
uv run python src/pipeline/run_sofa_pipeline.py --stages 1  # Fetch
uv run python src/pipeline/run_sofa_pipeline.py --stages 2  # Process
uv run python src/pipeline/run_sofa_pipeline.py --stages 3  # Produce
```

## Output

The pipeline generates v1 format feeds that are consumed by the web UI:
- `v1/macos_data_feed.json`
- `v1/ios_data_feed.json`
- `v1/watchos_data_feed.json`
- `v1/tvos_data_feed.json`
- `v1/visionos_data_feed.json`
- `v1/safari_data_feed.json`