#!/usr/bin/env python3
"""
SOFA Pipeline Orchestrator

Runs the complete SOFA pipeline in organized stages:

Stage 1: Fetch & Cache
- Security pages from Apple
- GDMF data
- CISA KEV catalog
- Apple OS releases (betas)
- CVE details (optional, with API key)

Stage 2: Process & Build
- Build security releases from cached pages
- Extract CVE details from cached pages
- Analyze KEV patterns
- Enrich with KEV data

Stage 3: Produce Feeds
- Apply retention policies (postprocess)
- Generate v1 feeds (backward compatible)
- Generate v2 feeds (enhanced, optional)
- Validate integrity
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import sys
from pathlib import Path
# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.logger import configure_logger, get_logger

logger = get_logger(__name__)


class SOFAPipeline:
    """SOFA Pipeline orchestrator."""
    
    def __init__(self, verbose: int = 1):
        """Initialize pipeline."""
        self.verbose = verbose
        configure_logger(max(1, verbose))
        
        # Directories
        self.project_root = Path(__file__).parent.parent.parent
        self.cache_dir = self.project_root / "data" / "cache"
        self.simple_cache_dir = self.cache_dir  # Unified cache
        self.security_releases_dir = self.project_root / "data" / "security_releases"
        self.v1_dir = self.project_root / "data" / "feeds" / "v1"
        self.v2_dir = self.project_root / "data" / "feeds" / "v2"
        
        # Track execution times
        self.timings = {}
        
    def run_command(self, cmd: str, description: str, 
                   check: bool = True, env: Optional[Dict] = None) -> bool:
        """Run a command and track timing."""
        logger.info(f"[{description}]")
        start_time = datetime.now(timezone.utc)
        
        try:
            # Merge environment variables
            cmd_env = os.environ.copy()
            if env:
                cmd_env.update(env)
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=check,
                env=cmd_env
            )
            
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.timings[description] = elapsed
            
            if result.returncode == 0:
                logger.info(f"  ✓ Completed in {elapsed:.1f}s")
                return True
            else:
                if check:
                    logger.error(f"  ✗ Failed with code {result.returncode}")
                    if result.stderr and self.verbose > 1:
                        logger.error(f"  Error: {result.stderr}")
                else:
                    logger.warning(f"  ⚠ Completed with warnings in {elapsed:.1f}s")
                return False
                
        except Exception as e:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.timings[description] = elapsed
            logger.error(f"  ✗ Failed after {elapsed:.1f}s: {e}")
            return False
    
    def stage1_fetch_and_cache(self, skip_beta: bool = False, 
                              skip_cve_cache: bool = False) -> bool:
        """
        Stage 1: Fetch and cache all data sources.
        """
        logger.info("=" * 60)
        logger.info("STAGE 1: FETCH & CACHE")
        logger.info("=" * 60)
        
        success = True
        
        # 1. Fetch Apple security pages
        if not self.run_command(
            f"uv run python {self.project_root}/src/fetchers/fetch_security_pages.py",
            "Fetch Apple security pages",
            check=False
        ):
            logger.warning("Some security pages may not have been fetched")
        
        # 2. Fetch GDMF data
        if not self.run_command(
            f"uv run python {self.project_root}/src/fetchers/fetch_gdmf.py",
            "Fetch GDMF data",
            check=False
        ):
            logger.warning("GDMF data fetch had issues")
        
        # 3. Fetch CISA KEV catalog
        if not self.run_command(
            f"uv run python {self.project_root}/src/fetchers/kev_fetcher.py",
            "Fetch CISA KEV catalog",
            check=False
        ):
            logger.warning("KEV catalog fetch had issues")
        
        # 4. Fetch Apple OS releases (betas)
        if not skip_beta:
            if not self.run_command(
                f"uv run python {self.project_root}/src/fetchers/apple_os_releases_scraper.py",
                "Fetch Apple OS releases (betas)",
                check=False
            ):
                logger.warning("Beta releases fetch had issues")
        else:
            logger.info("  → Skipping beta releases fetch")
        
        # 5. Build CVE cache (optional, requires API key)
        if not skip_cve_cache and os.getenv('API_KEY'):
            if not self.run_command(
                "uv run python build-cve-cache.py",
                "Build CVE details cache",
                check=False
            ):
                logger.warning("CVE cache build had issues")
        elif skip_cve_cache:
            logger.info("  → Skipping CVE cache build")
        else:
            logger.info("  → Skipping CVE cache (no API_KEY)")
        
        # 6. Extract CVE details from cached pages
        if not self.run_command(
            f"uv run python {self.project_root}/src/enrichers/extract_cve_details.py --limit 200",
            "Extract CVE details from pages",
            check=False
        ):
            logger.warning("CVE detail extraction had issues")
        
        return success
    
    def stage2_process_and_build(self, skip_kev_analysis: bool = False) -> bool:
        """
        Stage 2: Process cached data and build intermediate files.
        """
        logger.info("=" * 60)
        logger.info("STAGE 2: PROCESS & BUILD")
        logger.info("=" * 60)
        
        # 1. Build security releases from cache
        if not self.run_command(
            f"uv run python {self.project_root}/src/builders/build_security_releases.py",
            "Build security releases",
            check=True
        ):
            logger.error("Failed to build security releases")
            return False
        
        # 2. Analyze KEV patterns from Apple pages
        if not skip_kev_analysis:
            if not self.run_command(
                f"uv run python {self.project_root}/src/enrichers/enrich_with_smart_kev.py --analyze-patterns",
                "Analyze Apple KEV patterns",
                check=False
            ):
                logger.warning("KEV pattern analysis had issues")
        
        # 3. Enrich with KEV data (in-place)
        if not self.run_command(
            f"uv run python {self.project_root}/src/enrichers/enrich_with_smart_kev.py",
            "Enrich with KEV data",
            check=False
        ):
            logger.warning("KEV enrichment had issues")
        
        # 4. Apply retention and pinning policies
        if not self.run_command(
            f"uv run python {self.project_root}/src/processors/postprocess_feeds.py",
            "Apply retention policies",
            check=True
        ):
            logger.error("Failed to postprocess feeds")
            return False
        
        return True
    
    def stage3_produce_feeds(self, skip_v2: bool = False) -> bool:
        """
        Stage 3: Produce final feed files (v1 and optionally v2).
        """
        logger.info("=" * 60)
        logger.info("STAGE 3: PRODUCE FEEDS")
        logger.info("=" * 60)
        
        # 1. Build v1 feeds (backward compatible)
        if not self.run_command(
            f"uv run python {self.project_root}/src/builders/build_complete_feeds.py",
            "Build v1 feeds",
            check=True
        ):
            logger.error("Failed to build v1 feeds")
            return False
        
        # 2. Build v2 feeds (enhanced, optional)
        if not skip_v2:
            if not self.run_command(
                f"uv run python {self.project_root}/src/generators/build_v2_feeds_enhanced.py",
                "Build v2 enhanced feeds",
                check=False
            ):
                logger.warning("v2 feed generation had issues")
        else:
            logger.info("  → Skipping v2 feed generation")
        
        # 3. Generate RSS feeds
        if not self.run_command(
            f"uv run python {self.project_root}/src/generators/generate_rss_feeds.py",
            "Generate RSS feeds",
            check=False
        ):
            logger.warning("RSS feed generation had issues")
        
        # 4. Validate feed integrity
        if not self.run_command(
            "uv run python scripts/validate_feeds.py --dir v1",
            "Validate v1 feeds",
            check=False
        ):
            logger.warning("v1 feed validation had issues")
        
        if not skip_v2 and self.v2_dir.exists():
            if not self.run_command(
                "uv run python scripts/verify_integrity.py",
                "Verify v2 integrity",
                check=False
            ):
                logger.warning("v2 integrity check had issues")
        
        return True
    
    def print_summary(self):
        """Print execution summary."""
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE SUMMARY")
        logger.info("=" * 60)
        
        # Output statistics
        outputs = {
            "Cache (HTML)": len(list(self.cache_dir.glob("raw/*.html"))) if self.cache_dir.exists() else 0,
            "Security releases": len(list(self.security_releases_dir.glob("*.json"))) if self.security_releases_dir.exists() else 0,
            "Enriched": len(list((self.security_releases_dir / "enriched").glob("*.json"))) if (self.security_releases_dir / "enriched").exists() else 0,
            "v1 feeds": len(list(self.v1_dir.glob("*.json"))) if self.v1_dir.exists() else 0,
            "v2 feeds": len(list(self.v2_dir.glob("*_v2.json"))) if self.v2_dir.exists() else 0,
        }
        
        logger.info("\nOutputs:")
        for name, count in outputs.items():
            logger.info(f"  {name:20} {count:3} files")
        
        # KEV statistics
        if self.v1_dir.exists():
            try:
                with open(self.v1_dir / "macos_data_feed.json") as f:
                    data = json.load(f)
                    total_kevs = 0
                    for os_ver in data.get("OSVersions", []):
                        for release in os_ver.get("SecurityReleases", []):
                            kevs = release.get("ActivelyExploitedCVEs", [])
                            total_kevs += len(kevs)
                    logger.info(f"\n  Total KEVs in macOS: {total_kevs}")
            except:
                pass
        
        # Timing summary
        if self.timings:
            logger.info("\nExecution times:")
            total_time = sum(self.timings.values())
            for stage, elapsed in self.timings.items():
                pct = (elapsed / total_time * 100) if total_time > 0 else 0
                logger.info(f"  {stage:40} {elapsed:6.1f}s ({pct:4.1f}%)")
            logger.info(f"  {'Total':40} {total_time:6.1f}s")
        
        logger.info("\n✅ Pipeline completed successfully!")
    
    def run(self, skip_beta: bool = False, skip_cve_cache: bool = False,
            skip_kev_analysis: bool = False, skip_v2: bool = False,
            stages: Optional[List[int]] = None) -> int:
        """
        Run the pipeline.
        
        Args:
            skip_beta: Skip fetching beta releases
            skip_cve_cache: Skip building CVE cache
            skip_kev_analysis: Skip KEV pattern analysis
            skip_v2: Skip v2 feed generation
            stages: List of stages to run (1, 2, 3), None for all
        
        Returns:
            Exit code (0 for success)
        """
        logger.info("Starting SOFA Pipeline")
        logger.info(f"Configuration: verbose={self.verbose}, stages={stages or 'all'}")
        
        if stages is None:
            stages = [1, 2, 3]
        
        success = True
        
        # Run requested stages
        if 1 in stages:
            if not self.stage1_fetch_and_cache(skip_beta, skip_cve_cache):
                success = False
        
        if 2 in stages:
            if not self.stage2_process_and_build(skip_kev_analysis):
                success = False
        
        if 3 in stages:
            if not self.stage3_produce_feeds(skip_v2):
                success = False
        
        # Print summary
        self.print_summary()
        
        return 0 if success else 1


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='SOFA Pipeline Orchestrator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Pipeline Stages:
  Stage 1: Fetch & Cache
    - Apple security pages
    - GDMF data
    - CISA KEV catalog
    - Beta releases
    - CVE details
    
  Stage 2: Process & Build
    - Build security releases
    - Analyze KEV patterns
    - Enrich with KEV data
    - Apply retention policies
    
  Stage 3: Produce Feeds
    - Generate v1 feeds
    - Generate v2 feeds (optional)
    - Generate RSS feeds
    - Validate integrity

Examples:
  # Run complete pipeline
  python run_sofa_pipeline.py
  
  # Run only fetch stage
  python run_sofa_pipeline.py --stages 1
  
  # Run process and produce stages
  python run_sofa_pipeline.py --stages 2 3
  
  # Skip optional components
  python run_sofa_pipeline.py --skip-beta --skip-v2
'''
    )
    
    parser.add_argument(
        '--stages',
        nargs='+',
        type=int,
        choices=[1, 2, 3],
        help='Stages to run (default: all)'
    )
    
    parser.add_argument(
        '--skip-beta',
        action='store_true',
        help='Skip fetching beta releases'
    )
    
    parser.add_argument(
        '--skip-cve-cache',
        action='store_true',
        help='Skip building CVE cache (VulnCheck API)'
    )
    
    parser.add_argument(
        '--skip-kev-analysis',
        action='store_true',
        help='Skip KEV pattern analysis'
    )
    
    parser.add_argument(
        '--skip-v2',
        action='store_true',
        help='Skip v2 feed generation'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=1,
        help='Increase verbosity'
    )
    
    args = parser.parse_args()
    
    pipeline = SOFAPipeline(verbose=args.verbose)
    
    return pipeline.run(
        skip_beta=args.skip_beta,
        skip_cve_cache=args.skip_cve_cache,
        skip_kev_analysis=args.skip_kev_analysis,
        skip_v2=args.skip_v2,
        stages=args.stages
    )


if __name__ == "__main__":
    sys.exit(main())