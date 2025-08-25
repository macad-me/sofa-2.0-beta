
import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

#!/usr/bin/env python3
"""
Enrich security releases with smart KEV (Known Exploited Vulnerabilities) data.
This uses the smart KEV detector to provide nuanced exploitation information.

Key features:
1. Processes against cached Apple security pages (no network calls)
2. Cross-references with CISA KEV catalog (cached)
3. Provides cross-platform exploitation warnings
4. Distinguishes between exploitation sources and confidence levels
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.enrichers.smart_kev_detector import SmartKEVDetector, ExploitationInfo
from src.utils.logger import configure_logger, get_logger

logger = get_logger(__name__)


class SmartKEVEnricher:
    """Enriches security releases with smart KEV detection."""
    
    def __init__(self):
        """Initialize the enricher."""
        self.detector = SmartKEVDetector()
        self.cache_dir = Path(__file__).resolve().parent.parent.parent / "data" / "cache"
        self.parsed_dir = self.cache_dir / "parsed"
        
        # Load Apple exploitation patterns from cache
        self.load_apple_patterns()
        
    def load_apple_patterns(self) -> None:
        """Load pre-analyzed Apple exploitation patterns from cache."""
        patterns_file = Path("cache/apple_exploitation_patterns.json")
        if patterns_file.exists():
            try:
                with open(patterns_file) as f:
                    data = json.load(f)
                    
                # Load CVE exploitation info
                cve_exploitation = data.get("cve_exploitation", {})
                for cve_id, info in cve_exploitation.items():
                    # Convert to ExploitationInfo for cross-platform checks
                    if info.get("exploited"):
                        # Store in detector's cache for cross-platform detection
                        platforms = self._extract_platforms_from_file(info.get("source_file", ""))
                        exploitation_info = ExploitationInfo(
                            cve_id=cve_id,
                            is_exploited=True,
                            confidence="confirmed",
                            sources=["apple_direct"],
                            affected_platforms=platforms,
                            notes=f"Categories: {', '.join(info.get('categories', []))}"
                        )
                        self.detector.apple_exploited[cve_id] = exploitation_info
                        
                logger.info(f"Loaded {len(self.detector.apple_exploited)} Apple-indicated exploited CVEs")
            except Exception as e:
                logger.error(f"Failed to load Apple patterns: {e}")
    
    def _extract_platforms_from_file(self, filename: str) -> set:
        """Extract platform(s) from filename."""
        platforms = set()
        
        # Map common patterns to platforms
        if "macos" in filename.lower() or "mac_os" in filename.lower():
            platforms.add("macOS")
        if "ios" in filename.lower() and "visionos" not in filename.lower():
            platforms.add("iOS")
        if "ipados" in filename.lower():
            platforms.add("iPadOS")
        if "watchos" in filename.lower():
            platforms.add("watchOS")
        if "tvos" in filename.lower():
            platforms.add("tvOS")
        if "visionos" in filename.lower():
            platforms.add("visionOS")
        if "safari" in filename.lower():
            platforms.add("Safari")
            
        return platforms if platforms else {"unknown"}
    
    def get_parsed_data_for_release(self, url: str, platform: str) -> Optional[Dict]:
        """
        Get parsed security release data from cache.
        
        Args:
            url: Security release URL
            platform: Platform name
            
        Returns:
            Parsed release data if available
        """
        # Convert URL to cache filename
        import hashlib
        url_hash = hashlib.sha1(url.encode()).hexdigest()
        parsed_file = self.parsed_dir / f"{url_hash}.json"
        
        if parsed_file.exists():
            try:
                with open(parsed_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading parsed data for {url}: {e}")
        
        return None
    
    def enrich_release(self, release: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """
        Enrich a single release with smart KEV data.
        
        Args:
            release: Security release data
            platform: Platform (iOS, macOS, etc.)
            
        Returns:
            Enriched release
        """
        enriched = release.copy()
        
        # Get CVEs from the release
        cves = release.get("cves", [])
        
        # Track different types of exploitation
        actively_exploited = []  # Confirmed exploited on this platform
        cross_platform_warnings = []  # Exploited on other platforms
        cisa_kevs = []  # In CISA catalog
        
        exploitation_details = {}
        
        for cve in cves:
            # Get comprehensive exploitation status
            info = self.detector.get_exploitation_status(
                cve_id=cve,
                apple_text=None,  # We're using cached patterns
                platform=platform
            )
            
            # Create feed entry
            entry = self.detector.create_feed_entry(info)
            exploitation_details[cve] = entry
            
            # Categorize
            if info.is_exploited:
                actively_exploited.append(cve)
                
            if "cisa_kev" in [s.value for s in info.sources]:
                cisa_kevs.append(cve)
                
            if "cross_platform" in [s.value for s in info.sources]:
                cross_platform_warnings.append({
                    "cve": cve,
                    "note": info.notes
                })
        
        # Add enrichment fields
        enriched["actively_exploited_cves"] = actively_exploited
        enriched["actively_exploited_count"] = len(actively_exploited)
        
        # Add CISA KEVs if different from actively exploited
        if cisa_kevs and set(cisa_kevs) != set(actively_exploited):
            enriched["cisa_kevs"] = cisa_kevs
            
        # Add cross-platform warnings
        if cross_platform_warnings:
            enriched["cross_platform_exploitation_warnings"] = cross_platform_warnings
            
        # Add detailed exploitation info
        if exploitation_details:
            enriched["exploitation_details"] = exploitation_details
        
        # Calculate exploitation rates
        if cves:
            enriched["exploitation_rate"] = round(len(actively_exploited) / len(cves) * 100, 1)
            if cisa_kevs:
                enriched["cisa_kev_rate"] = round(len(cisa_kevs) / len(cves) * 100, 1)
        else:
            enriched["exploitation_rate"] = 0.0
            
        return enriched
    
    def process_security_releases_file(
        self, 
        input_path: Path, 
        output_path: Path
    ) -> Dict[str, Any]:
        """
        Process a single security releases file.
        
        Returns statistics about the enrichment.
        """
        logger.info(f"Processing {input_path.name}")
        
        # Determine platform from filename
        platform = input_path.stem  # macos, ios, ipados, etc.
        if platform == "safari":
            platform = "Safari"
        else:
            # Capitalize properly
            platform_map = {
                "macos": "macOS",
                "ios": "iOS",
                "ipados": "iPadOS",
                "watchos": "watchOS",
                "tvos": "tvOS",
                "visionos": "visionOS"
            }
            platform = platform_map.get(platform, platform)
        
        # Load the releases
        with open(input_path) as f:
            data = json.load(f)
        
        # Enrich releases
        original_releases = data.get("releases", [])
        enriched_releases = []
        
        for release in original_releases:
            enriched = self.enrich_release(release, platform)
            enriched_releases.append(enriched)
        
        # Update the data
        data["releases"] = enriched_releases
        data["enrichment_metadata"] = {
            "enriched_at": datetime.now().isoformat(),
            "apple_exploited_cves_loaded": len(self.detector.apple_exploited),
            "cisa_kevs_loaded": len(self.detector.cisa_kevs)
        }
        
        # Calculate statistics
        stats = {
            "file": input_path.name,
            "platform": platform,
            "total_releases": len(enriched_releases),
            "releases_with_kevs": sum(1 for r in enriched_releases if r.get("actively_exploited_cves")),
            "releases_with_warnings": sum(1 for r in enriched_releases if r.get("cross_platform_exploitation_warnings")),
            "total_cves": sum(len(r.get("cves", [])) for r in enriched_releases),
            "total_kevs": sum(len(r.get("actively_exploited_cves", [])) for r in enriched_releases),
            "total_warnings": sum(len(r.get("cross_platform_exploitation_warnings", [])) for r in enriched_releases)
        }
        
        if stats["total_cves"] > 0:
            stats["exploitation_rate"] = round(stats["total_kevs"] / stats["total_cves"] * 100, 1)
        else:
            stats["exploitation_rate"] = 0.0
        
        # Write enriched data
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  Enriched {len(enriched_releases)} releases")
        logger.info(f"  Found {stats['total_kevs']} KEVs in {stats['total_cves']} CVEs ({stats['exploitation_rate']}%)")
        if stats["total_warnings"] > 0:
            logger.info(f"  Added {stats['total_warnings']} cross-platform warnings")
        
        return stats


def main():
    """Main entry point."""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Smart KEV enrichment for security releases')
    parser.add_argument(
        '--input-dir',
        type=Path,
        default=Path('security_releases'),
        help='Input directory with security releases'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('security_releases/smart_enriched'),
        help='Output directory for enriched releases'
    )
    parser.add_argument(
        '--test-file',
        type=Path,
        help='Test with a single file'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    configure_logger(max(1, args.verbose))
    
    logger.info("Starting smart KEV enrichment")
    
    # Initialize enricher
    enricher = SmartKEVEnricher()
    
    # Process files
    all_stats = []
    
    if args.test_file:
        # Test mode - single file
        output_path = args.output_dir / args.test_file.name
        stats = enricher.process_security_releases_file(args.test_file, output_path)
        all_stats.append(stats)
    else:
        # Process all JSON files
        for json_file in args.input_dir.glob("*.json"):
            # Skip combined.json and other non-OS files
            if json_file.name in ["combined.json"]:
                continue
                
            output_path = args.output_dir / json_file.name
            stats = enricher.process_security_releases_file(json_file, output_path)
            all_stats.append(stats)
    
    # Print summary
    print("\nSmart KEV Enrichment Summary:")
    print("=" * 60)
    
    total_releases = sum(s["total_releases"] for s in all_stats)
    total_cves = sum(s["total_cves"] for s in all_stats)
    total_kevs = sum(s["total_kevs"] for s in all_stats)
    total_warnings = sum(s["total_warnings"] for s in all_stats)
    
    for stats in all_stats:
        print(f"\n{stats['file']} ({stats['platform']}):")
        print(f"  Releases: {stats['total_releases']} ({stats['releases_with_kevs']} with KEVs)")
        print(f"  CVEs: {stats['total_cves']} ({stats['total_kevs']} KEVs)")
        print(f"  Exploitation rate: {stats['exploitation_rate']}%")
        if stats['total_warnings'] > 0:
            print(f"  Cross-platform warnings: {stats['total_warnings']} ({stats['releases_with_warnings']} releases)")
    
    print(f"\nOverall:")
    print(f"  Total releases: {total_releases}")
    print(f"  Total CVEs: {total_cves}")
    print(f"  Total KEVs: {total_kevs}")
    print(f"  Cross-platform warnings: {total_warnings}")
    print(f"  Overall exploitation rate: {round(total_kevs / total_cves * 100, 1) if total_cves > 0 else 0.0}%")
    print(f"\nEnrichment sources:")
    print(f"  Apple-indicated exploited CVEs: {len(enricher.detector.apple_exploited)}")
    print(f"  CISA KEV catalog entries: {len(enricher.detector.cisa_kevs)}")
    
    logger.info("Smart KEV enrichment completed")
    return 0


if __name__ == "__main__":
    exit(main())