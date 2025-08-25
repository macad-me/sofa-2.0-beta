# SOFA Pipeline Scripts

This directory contains orchestration and utility scripts to rapidly build and test the artifacts needed for the SOFA (Simple Organized Feed for Apple software updates) project to build feeds. It composes tools across the core stages of the pipeline:

1. **Fetch**: Scrape Apple security pages for release information
2. **Gather**: Collect data from external sources (XProtect, UMA, Beta, GDMF, IPSW)
3. **Build**: Assemble v1 and v2 format feeds for all Apple platforms
4. **CVE**: Enrich feeds with CVE details and KEV (Known Exploited Vulnerabilities) data

| Tool Name      | Description                                                                                 |
|----------------|---------------------------------------------------------------------------------------------|
| **sofa-fetch** | Scrapes Apple security pages for release information                                        |
| **sofa-gather**| Collects data from external sources (XProtect, UMA, Beta, GDMF, IPSW)                      |
| **sofa-build** | Assembles v1 and v2 format feeds for all Apple platforms                                    |
| **sofa-cve**   | Enriches feeds with CVE details and KEV (Known Exploited Vulnerabilities) data             |

**Note**: This repository is public for transparency, but **not open source**.

## Licensing
- **Source code**: Licensed under **Polyform Internal Use Only**.
  - Use only within your organization.
  - No redistribution, no commercial use.
- **Build artifacts (releases, binaries, containers)**: Licensed under **Polyform Noncommercial**.
  - May be shared and redistributed.
  - Commercial use is forbidden.

See [LICENSE.source](./LICENSE.source) and [LICENSE.artifacts](./LICENSE.artifacts).

## Contributions
- Contributions are welcome, but all contributors must sign our
  [Contributor License Agreement (CLA)](./CLA.md).
- See [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## FAQ
See [FAQ.md](./FAQ.md) for common questions.

## Main Pipeline Script

### `sofa_pipeline.py`

The main orchestration script that runs the complete SOFA data pipeline. It coordinates the four main stages:
1. **Fetch** - Scrape Apple security pages for release information
2. **Gather** - Collect data from external sources (XProtect, UMA, Beta, GDMF, IPSW)
3. **Build** - Assemble v1 and v2 format feeds for all Apple platforms
4. **CVE** - Enrich feeds with CVE details and KEV data

#### Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Compiled SOFA binaries in `bin/`

#### Usage

The script uses uv for dependency management and can be run directly:

```bash
# Show help
uv run scripts/sofa_pipeline.py --help

# Show pipeline information
uv run scripts/sofa_pipeline.py info

# Run complete pipeline (all stages)
uv run scripts/sofa_pipeline.py run

# Run specific stages
uv run scripts/sofa_pipeline.py run --stage fetch
uv run scripts/sofa_pipeline.py run --stage gather
uv run scripts/sofa_pipeline.py run --stage build
uv run scripts/sofa_pipeline.py run --stage cve

# Skip stages (useful for re-running only CVE enrichment)
uv run scripts/sofa_pipeline.py run --skip-fetch --skip-gather --skip-build

# Clean all outputs (calls each tool's clean command)
# Note: Configuration files are never cleaned
uv run scripts/sofa_pipeline.py clean

# Clean with auto-confirmation (skip prompts)
uv run scripts/sofa_pipeline.py clean --yes

# Dry run - see what would be cleaned without actually cleaning
uv run scripts/sofa_pipeline.py clean --dry-run

# Check for drift between models and resources directories
uv run scripts/sofa_pipeline.py check-models

# Check models with detailed differences
uv run scripts/sofa_pipeline.py check-models --verbose
```

#### Directory Structure

The pipeline expects and creates the following directory structure:

```
.
├── bin/                    # Compiled binaries
│   ├── sofa-fetch         # Web scraping tool
│   ├── sofa-gather        # Data gathering tool
│   ├── sofa-build         # Feed assembly tool
│   └── sofa-cve           # CVE enrichment tool
├── config/                 # Configuration files
│   ├── build.toml         # Build configuration
│   └── AppleRoot.pem      # Apple SSL certificate (optional)
├── data/                   # Working data directory
│   ├── fetch/             # Fetched data
│   │   ├── apple_security_releases.json
│   │   └── html_cache/
│   ├── gather/            # Gathered external data
│   │   ├── xprotect.json
│   │   ├── uma_catalog.json
│   │   ├── apple_beta_feed.json
│   │   ├── gdmf_cached.json
│   │   ├── ipsw.json
│   │   └── history/       # Historical snapshots
│   ├── resources/         # Static resources
│   │   ├── supported_devices.json
│   │   ├── mac_models_mapping.json
│   │   ├── cve_lookup.ndjson
│   │   └── kev_catalog.json
│   ├── feeds/             # Built feeds
│   │   ├── v1/           # Version 1 feeds
│   │   │   ├── macos_data_feed.json
│   │   │   ├── ios_data_feed.json
│   │   │   └── [other platform feeds]
│   │   └── v2/           # Version 2 feeds
│   │       └── [same structure as v1]
│   └── cve/              # CVE enrichment data
│       ├── enriched_feeds/
│       └── cve_state.json
```

#### Configuration

The pipeline script automatically uses embedded defaults in the binaries. Optional configuration:

- **AppleRoot.pem**: Place Apple's root certificate in `config/` to avoid using `--insecure` flag for GDMF
- **pipeline.toml**: Optional TOML configuration for custom paths (see example below)

Example `pipeline.toml` (optional - defaults work for most cases):
```toml
# All settings are optional - shown with defaults
[pipeline]
base_dir = "."
data_dir = "data"
v1_output_dir = "data/feeds/v1"
v2_output_dir = "data/feeds/v2"

[gather]
# Available sources: kev, gdmf, ipsw, xprotect, beta, uma
sources = ["kev", "gdmf", "ipsw", "xprotect", "beta", "uma"]

[build]
# Available products: safari, ios, macos, tvos, watchos, visionos
products = ["safari", "ios", "macos", "tvos", "watchos", "visionos"]
```

#### Binary Requirements

The pipeline requires the following compiled Rust binaries:

1. **sofa-fetch**: Scrapes Apple security pages
   - Processes support.apple.com pages
   - Extracts release information
   - Caches HTML for analysis

2. **sofa-gather**: Fetches external data sources
   - XProtect configuration data
   - UMA (Unified Mac Analytics) catalog
   - Apple Beta feeds
   - GDMF (Apple device firmware) from Apple
   - IPSW firmware data

3. **sofa-build**: Assembles final feeds
   - Combines all data sources
   - Generates v1 and v2 format feeds
   - Supports all Apple platforms
   - Validates data integrity

4. **sofa-cve**: Enriches feeds with security data
   - Adds CVE details to feeds
   - Integrates KEV (Known Exploited Vulnerabilities) data
   - Enriches with severity and exploitation status

#### Output Formats

**v1 Format (Legacy)**
- Simplified CVE representation (boolean values)
- Compatible with existing SOFA consumers
- Smaller file size

**v2 Format (Modern)**
- Detailed CVE objects with severity, exploitation status
- Includes KEV (Known Exploited Vulnerabilities) data
- Richer metadata for security analysis

#### Logging

The pipeline creates detailed logs in the `logs/` directory with timestamps. Each run generates:
- `logs/sofa_pipeline_YYYYMMDD_HHMMSS.log`

#### Error Handling

The pipeline provides detailed error reporting:
- Stage-level success/failure tracking
- Detailed error messages for debugging
- Automatic validation of outputs
- Binary availability checking

#### Performance

Typical execution times:
- Fetch: 30-60 seconds (scraping multiple pages)
- Gather: 10-30 seconds (depends on network)
- Build: 30-60 seconds (all products, both v1 and v2)
- CVE: 20-40 seconds (enriching all feeds)

Total pipeline: ~2-3 minutes for all stages

## Development

To modify the pipeline:

1. Edit `sofa_pipeline.py`
2. Test with a single stage first: `uv run scripts/sofa_pipeline.py run --stage gather`
3. Check logs for detailed debugging information
4. Validate outputs with the verify command

## Troubleshooting

Common issues and solutions:

**Missing binaries**
```bash
# Build all binaries
cargo build --release

# Copy to bin/ directory
mkdir -p bin
cp target/release/sofa-* bin/  # After building, copy binaries to bin/
```

**GDMF SSL certificate errors**
```bash
# Option 1: Add Apple root certificate
cp /path/to/AppleRoot.pem config/

# Option 2: Pipeline will automatically use --insecure flag if certificate is missing
```

**Missing supported_devices.json**
```bash
# This file should be in data/models/
# It provides device identifier mappings for each OS version
```

## License

Part of the SOFA project - see main repository for license details.