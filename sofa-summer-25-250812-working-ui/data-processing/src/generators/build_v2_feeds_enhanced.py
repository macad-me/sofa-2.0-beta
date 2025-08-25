
import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

#!/usr/bin/env python3
"""
Build enhanced v2 feeds that keep v1 structure while adding rich CVE details.

V2 Enhanced Features:
- Keep v1's OSVersions structure (e.g., "Sequoia 15", "Sonoma 14")
- Keep Latest, SecurityReleases organization
- Add CVE component details (WebKit, Kernel, etc.)
- Add impact descriptions where available
- Keep all v1 data (SupportedDevices, ExpirationDate, etc.)
- Enhance with KEV confidence and sources
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from src.utils.logger import configure_logger, get_logger
from src.builders.build_complete_feeds import CompleteFeedBuilder
from src.enrichers.extract_cve_details import CVEDetailExtractor
from src.enrichers.component_normalizer import ComponentNormalizer

logger = get_logger(__name__)


class V2EnhancedFeedBuilder(CompleteFeedBuilder):
    """Build enhanced v2 feeds with v1 structure plus CVE details."""
    
    def __init__(self):
        super().__init__()
        self.v2_dir = Path(__file__).resolve().parent.parent.parent / "data" / "feeds" / "v2"
        self.v2_dir.mkdir(exist_ok=True)
        
        # Load CVE details
        self.cve_extractor = CVEDetailExtractor()
        logger.info(f"Loaded {len(self.cve_extractor.cve_details)} CVE details")
        
        # Initialize component normalizer
        self.component_normalizer = ComponentNormalizer()
        
    def enhance_cve_dict(self, cves_dict: Dict[str, bool], 
                        actively_exploited: List[str]) -> Dict[str, Any]:
        """Enhance CVE dictionary with detailed information."""
        enhanced = {}
        
        for cve_id, is_kev in cves_dict.items():
            # Start with basic info
            cve_info = {
                "id": cve_id,
                "is_exploited": is_kev,
            }
            
            # Add details from extractor
            details = self.cve_extractor.get_cve_info(cve_id)
            if details:
                raw_component = details.get("component", "Unknown")
                # Normalize component to standard category
                normalized_component = self.component_normalizer.normalize(raw_component)
                cve_info.update({
                    "component": normalized_component,
                    "component_raw": raw_component,  # Keep original for reference
                    "impact": details.get("impact"),
                    "description": details.get("description"),
                    "platforms": details.get("available_for")
                })
            else:
                # Use System as default for unknown CVEs
                cve_info["component"] = "System"
            
            enhanced[cve_id] = cve_info
            
        return enhanced
    def create_v2_enhanced_feed(self, os_type: str, scraped_data: dict, gdmf_data: Any) -> dict:
        """Create v2 enhanced feed with v1 structure plus enrichments."""
        # Start with v1 feed structure
        v1_feed = self.create_legacy_feed(os_type, scraped_data, gdmf_data)
        
        # Convert to v2 with enhancements
        v2_feed = {
            "schema_version": "2.0",
            "os_type": os_type,
            "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            
            # Keep v1 UpdateTimestamp
            "UpdateTimestamp": v1_feed.get("UpdateTimestamp"),
            
            # Enhanced Latest section
            "Latest": self.enhance_latest(v1_feed.get("Latest", {})),
            
            # Enhanced OSVersions with component breakdown
            "OSVersions": []
        }
        
        # Process each OS version
        for os_version in v1_feed.get("OSVersions", []):
            enhanced_version = {
                "OSVersion": os_version["OSVersion"],
                "Latest": self.enhance_latest(os_version.get("Latest", {})),
                "SecurityReleases": []
            }
            
            # Collect component statistics for this OS version
            component_stats = {}
            total_cves = 0
            total_kevs = 0
            
            # Enhance each security release
            for release in os_version.get("SecurityReleases", []):
                enhanced_release = release.copy()
                
                # Convert CVEs dict to enhanced format
                if "CVEs" in enhanced_release:
                    original_cves = enhanced_release["CVEs"]
                    actively_exploited = enhanced_release.get("ActivelyExploitedCVEs", [])
                    
                    # Create enhanced CVE structure
                    enhanced_cves = self.enhance_cve_dict(original_cves, actively_exploited)
                    
                    # Add component breakdown
                    components = {}
                    for cve_id, cve_info in enhanced_cves.items():
                        component = cve_info.get("component", "Unknown")
                        if component not in components:
                            components[component] = {
                                "cves": [],
                                "exploited": []
                            }
                        components[component]["cves"].append(cve_id)
                        if cve_info["is_exploited"]:
                            components[component]["exploited"].append(cve_id)
                            total_kevs += 1
                        total_cves += 1
                        
                        # Update stats
                        component_stats[component] = component_stats.get(component, 0) + 1
                    
                    # Replace simple CVE dict with enhanced structure
                    enhanced_release["CVEs"] = enhanced_cves
                    enhanced_release["ComponentBreakdown"] = components
                    
                    # Add summary metrics
                    enhanced_release["CVEMetrics"] = {
                        "total": len(enhanced_cves),
                        "exploited": len(actively_exploited),
                        "components_affected": len(components),
                        "exploitation_rate": round(len(actively_exploited) / len(enhanced_cves) * 100, 1) if enhanced_cves else 0
                    }
                
                enhanced_version["SecurityReleases"].append(enhanced_release)
            
            # Add OS version level statistics
            enhanced_version["Statistics"] = {
                "total_releases": len(enhanced_version["SecurityReleases"]),
                "total_cves": total_cves,
                "total_kevs": total_kevs,
                "component_distribution": dict(sorted(component_stats.items(), 
                                                     key=lambda x: x[1], 
                                                     reverse=True)[:10]),  # Top 10 components
                "exploitation_rate": round(total_kevs / total_cves * 100, 2) if total_cves > 0 else 0
            }
            
            v2_feed["OSVersions"].append(enhanced_version)
        
        # Add global insights
        v2_feed["GlobalInsights"] = self.build_global_insights(v2_feed["OSVersions"])
        
        return v2_feed
    
    def enhance_latest(self, latest: Dict) -> Dict:
        """Enhance Latest section with additional info."""
        if not latest:
            return latest
            
        enhanced = latest.copy()
        
        # Add CVE component summary if CVEs present
        if "CVEs" in enhanced and isinstance(enhanced["CVEs"], dict):
            components = set()
            for cve_id in enhanced["CVEs"]:
                info = self.cve_extractor.get_cve_info(cve_id)
                if info:
                    components.add(info.get("component", "Unknown"))
            
            enhanced["ComponentsAffected"] = sorted(list(components))
        
        return enhanced
    
    def build_global_insights(self, os_versions: List[Dict]) -> Dict:
        """Build global insights across all OS versions."""
        insights = {
            "most_affected_components": {},
            "recent_kevs": [],
            "high_risk_releases": []
        }
        
        # Aggregate component stats
        global_components = {}
        
        for os_version in os_versions:
            stats = os_version.get("Statistics", {})
            for component, count in stats.get("component_distribution", {}).items():
                global_components[component] = global_components.get(component, 0) + count
            
            # Find high risk releases (high KEV rate)
            for release in os_version.get("SecurityReleases", []):
                metrics = release.get("CVEMetrics", {})
                if metrics.get("exploitation_rate", 0) > 50:  # More than 50% KEVs
                    insights["high_risk_releases"].append({
                        "os_version": os_version["OSVersion"],
                        "version": release.get("ProductVersion"),
                        "exploitation_rate": metrics["exploitation_rate"],
                        "release_date": release.get("ReleaseDate")
                    })
        
        # Sort components by frequency
        insights["most_affected_components"] = dict(
            sorted(global_components.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        # Sort high risk releases by exploitation rate
        insights["high_risk_releases"].sort(key=lambda x: x["exploitation_rate"], reverse=True)
        insights["high_risk_releases"] = insights["high_risk_releases"][:10]
        
        return insights
    
    def build_all_v2_enhanced_feeds(self):
        """Build enhanced v2 feeds for all OS types."""
        # Load GDMF data
        gdmf_data = self.fetch_gdmf_data()
        
        # First extract more CVE details if needed
        logger.info("Extracting CVE details from cached pages...")
        self.cve_extractor.extract_from_cache(limit=100)  # Process up to 100 pages
        
        os_types = ["macOS", "iOS", "tvOS", "watchOS", "visionOS"]
        
        for os_type in os_types:
            logger.info(f"Building enhanced v2 feed for {os_type}")
            
            os_lower = os_type.lower()
            scraped_file = self.data_dir / f"{os_lower}.json"
            
            if not scraped_file.exists():
                logger.warning(f"No enriched data for {os_type}")
                continue
            
            # Load enriched data
            with open(scraped_file) as f:
                scraped_data = json.load(f)
            
            # Create enhanced v2 feed
            v2_feed = self.create_v2_enhanced_feed(os_type, scraped_data, gdmf_data)
            
            # Write v2 feed
            output_file = self.v2_dir / f"{os_lower}_data_feed_v2.json"
            with open(output_file, 'w') as f:
                json.dump(v2_feed, f, indent=2, ensure_ascii=False)
            logger.info(f"  Wrote {output_file}")
        
        # Write v2 manifest
        self.write_v2_manifest()
        
    def write_v2_manifest(self):
        """Write v2 manifest with feed metadata."""
        manifest = {
            "version": "2.0-enhanced",
            "description": "SOFA v2 feeds with v1 structure plus CVE component details",
            "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "features": [
                "Maintains v1 OSVersions structure",
                "CVE component identification (WebKit, Kernel, etc.)",
                "Impact and description when available",
                "Component distribution statistics",
                "High-risk release identification",
                "Global insights across OS versions"
            ],
            "feeds": []
        }
        
        for feed_file in sorted(self.v2_dir.glob("*_v2.json")):
            manifest["feeds"].append({
                "os": feed_file.stem.replace("_data_feed_v2", ""),
                "file": feed_file.name,
                "size": feed_file.stat().st_size,
                "modified": datetime.fromtimestamp(feed_file.stat().st_mtime, tz=timezone.utc).isoformat().replace('+00:00', 'Z')
            })
        
        with open(self.v2_dir / "manifest_v2.json", 'w') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        logger.info("Wrote v2 enhanced manifest")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Build enhanced v2 feeds with v1 structure plus CVE details'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity'
    )
    parser.add_argument(
        '--os',
        help='Build feed for specific OS only'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    configure_logger(max(1, args.verbose))
    
    logger.info("Building enhanced v2 feeds")
    
    builder = V2EnhancedFeedBuilder()
    
    if args.os:
        # Build single OS (implementation would go here)
        logger.warning("Single OS build not yet implemented for v2 enhanced")
    else:
        builder.build_all_v2_enhanced_feeds()
    
    logger.info("Enhanced v2 feed generation complete!")
    
    return 0


if __name__ == "__main__":
    exit(main())