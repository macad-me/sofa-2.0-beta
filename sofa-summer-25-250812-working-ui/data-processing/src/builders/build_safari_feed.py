#!/usr/bin/env python3
"""Build Safari security feed from scraped data."""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import hashlib
from datetime import datetime
from src.fetchers.kev_fetcher import KEVFetcher

import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


logger = logging.getLogger(__name__)

class SafariFeedBuilder:
    def __init__(self):
        self.kev_fetcher = KEVFetcher()
    
    def _compute_hash(self, data: dict) -> str:
        """Compute SHA256 hash of data."""
        json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _format_date(self, date_str: str) -> str:
        """Format date to ISO format."""
        if not date_str:
            return ""
        try:
            # Try parsing various formats
            for fmt in ["%Y-%m-%d", "%B %d, %Y", "%d %B %Y"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    continue
            return date_str
        except Exception:
            return date_str
    
    def _calculate_days_since_previous(self, releases: List[dict]) -> Dict[str, int]:
        """Calculate days since previous release for each version."""
        days_map = {}
        sorted_releases = sorted(
            releases,
            key=lambda r: datetime.strptime(r["ReleaseDate"], "%Y-%m-%dT%H:%M:%SZ"),
            reverse=True
        )
        
        for i, release in enumerate(sorted_releases):
            version = release.get("ProductVersion", "")
            if i < len(sorted_releases) - 1:
                current_date = datetime.strptime(release["ReleaseDate"], "%Y-%m-%dT%H:%M:%SZ")
                prev_date = datetime.strptime(sorted_releases[i + 1]["ReleaseDate"], "%Y-%m-%dT%H:%M:%SZ")
                days_diff = (current_date - prev_date).days
                days_map[version] = days_diff
            else:
                days_map[version] = 0
        
        return days_map
    
    def build_safari_feed(self) -> dict:
        """Build Safari security feed from scraped data."""
        # Load scraped data
        scraped_file = Path("cache/scraped_data.json")
        if not scraped_file.exists():
            logger.error("No scraped data found")
            return {}
        
        with open(scraped_file) as f:
            scraped_data = json.load(f)
        
        safari_releases = []
        latest_safari = {}
        
        # Process Safari releases from scraped data
        for release in scraped_data.get("releases", []):
            # Look for Safari releases
            title = release.get("title", "")
            if "Safari" not in title:
                continue
            
            # Extract version from title
            import re
            version_match = re.search(r"Safari\s+([\d.]+)", title)
            if not version_match:
                continue
            
            version = version_match.group(1)
            
            # Get CVEs and enrich with KEV
            cves_dict = {cve: False for cve in release.get("cves", [])}
            cves_dict = self.kev_fetcher.enrich_cves_with_kev(cves_dict)
            actively_exploited = [cve for cve, exploited in cves_dict.items() if exploited]
            
            # Extract build number from description or title if available
            build = ""
            # Try to extract build from release data
            if "build" in release:
                build = release["build"]
            
            safari_release = {
                "UpdateName": title,
                "ProductName": "Safari",
                "ProductVersion": version,
                "Build": build,
                "AllBuilds": [build] if build else [],
                "ReleaseDate": self._format_date(release.get("release_date", "")),
                "ReleaseType": "Browser",
                "SecurityInfo": release.get("url", ""),
                "CVEs": cves_dict,
                "ActivelyExploitedCVEs": actively_exploited,
                "UniqueCVEsCount": len(cves_dict),
                "DaysSincePreviousRelease": 0,  # Will be calculated below
            }
            
            safari_releases.append(safari_release)
            
            # Keep track of latest
            if not latest_safari or version > latest_safari.get("ProductVersion", ""):
                latest_safari = {
                    "ProductVersion": version,
                    "Build": build,
                    "AllBuilds": [build] if build else [],
                    "ReleaseDate": safari_release["ReleaseDate"],
                    "SecurityInfo": safari_release["SecurityInfo"],
                    "CVEs": cves_dict,
                    "ActivelyExploitedCVEs": actively_exploited,
                    "UniqueCVEsCount": len(cves_dict),
                }
        
        # Sort releases by version
        from packaging import version as pkg_version
        safari_releases.sort(
            key=lambda r: pkg_version.parse(r.get("ProductVersion", "0")),
            reverse=True
        )
        
        # Calculate days since previous release
        if safari_releases:
            days_map = self._calculate_days_since_previous(safari_releases)
            for release in safari_releases:
                version = release.get("ProductVersion", "")
                if version in days_map:
                    release["DaysSincePreviousRelease"] = days_map[version]
        
        # Build feed structure
        feed = {
            "Latest": latest_safari,
            "SecurityReleases": safari_releases,
        }
        
        # Add update hash
        update_hash = self._compute_hash(feed)
        feed = {"UpdateHash": update_hash, **feed}
        
        return feed
    
    def save_feed(self, feed: dict, filename: str = "safari_data_feed.json"):
        """Save Safari feed to file."""
        if not feed:
            return
        
        # Save to main directory
        with open(filename, "w") as f:
            json.dump(feed, f, indent=4)
        print(f"Written {filename}")
        
        # Also save to v1 directory
        v1_dir = Path(__file__).resolve().parent.parent.parent / "data" / "feeds" / "v1"
        v1_dir.mkdir(exist_ok=True)
        v1_file = v1_dir / filename
        with open(v1_file, "w") as f:
            json.dump(feed, f, indent=4)
        print(f"Written {v1_file}")


def main():
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)
    
    builder = SafariFeedBuilder()
    safari_feed = builder.build_safari_feed()
    
    if safari_feed:
        builder.save_feed(safari_feed)
        print("Safari feed generation complete!")
    else:
        print("No Safari releases found in scraped data")


if __name__ == "__main__":
    main()