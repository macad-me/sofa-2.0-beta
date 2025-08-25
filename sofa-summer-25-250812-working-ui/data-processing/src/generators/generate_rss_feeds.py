#!/usr/bin/env python3
"""
RSS Feed Generator for SOFA
Generates RSS feeds from JSON feed data for each OS type.
"""

import argparse
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from feedgen.feed import FeedGenerator
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RSSConfig(BaseModel):
    """RSS feed configuration."""
    title: str
    link: str
    description: str
    language: str = "en-US"
    ttl: int = 60  # Minutes
    author_name: str = "macadmins SOFA"
    author_email: str = "sofa@macadmins.io"
    copyright: str = "Apple Inc."


class RSSFeedGenerator:
    """Generate RSS feeds from SOFA JSON data."""
    
    FEED_CONFIGS = {
        "macOS": RSSConfig(
            title="SOFA - macOS Security Updates",
            link="https://sofa.macadmins.io",
            description="Apple macOS Security Updates and CVE Information"
        ),
        "iOS": RSSConfig(
            title="SOFA - iOS Security Updates",
            link="https://sofa.macadmins.io",
            description="Apple iOS Security Updates and CVE Information"
        ),
        "tvOS": RSSConfig(
            title="SOFA - tvOS Security Updates",
            link="https://sofa.macadmins.io",
            description="Apple tvOS Security Updates and CVE Information"
        ),
        "watchOS": RSSConfig(
            title="SOFA - watchOS Security Updates",
            link="https://sofa.macadmins.io",
            description="Apple watchOS Security Updates and CVE Information"
        ),
        "visionOS": RSSConfig(
            title="SOFA - visionOS Security Updates",
            link="https://sofa.macadmins.io",
            description="Apple visionOS Security Updates and CVE Information"
        ),
    }
    
    def __init__(self, cache_dir: Path = Path(__file__).resolve().parent.parent.parent / "data" / "cache", output_dir: Path = Path("rss")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "rss_cache.json"
        self.rss_cache = self._load_cache()
        
    def _load_cache(self) -> Dict[str, Any]:
        """Load RSS cache."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading RSS cache: {e}")
        return {}
        
    def _save_cache(self):
        """Save RSS cache."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.rss_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving RSS cache: {e}")
    
    def _get_content_hash(self, data: Any) -> str:
        """Get SHA-256 hash of content."""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _should_update_feed(self, os_type: str, feed_data: dict) -> bool:
        """Check if RSS feed needs updating."""
        content_hash = self._get_content_hash(feed_data)
        
        if os_type not in self.rss_cache:
            return True
            
        cached_hash = self.rss_cache[os_type].get("content_hash")
        return cached_hash != content_hash
    
    def _format_cve_list(self, cves: Dict[str, bool], actively_exploited: List[str]) -> str:
        """Format CVE list for RSS entry."""
        if not cves:
            return "No CVEs listed"
            
        lines = []
        lines.append(f"Total CVEs: {len(cves)}")
        
        if actively_exploited:
            lines.append(f"Actively Exploited (KEV): {len(actively_exploited)}")
            lines.append("🔥 " + ", ".join(actively_exploited))
            
        # List all CVEs
        all_cves = sorted(cves.keys())
        lines.append("\nAll CVEs:")
        for i in range(0, len(all_cves), 10):
            batch = all_cves[i:i+10]
            lines.append(", ".join(batch))
            
        return "\n".join(lines)
    
    def _create_feed_entry(self, fg: FeedGenerator, release: dict, os_type: str):
        """Create a feed entry for a security release."""
        fe = fg.add_entry()
        
        # Generate unique ID
        version = release.get("ProductVersion", "")
        release_date = release.get("ReleaseDate", "")
        entry_id = f"{os_type}-{version}-{release_date}"
        fe.id(entry_id)
        
        # Title
        title = f"{os_type} {version}"
        if release.get("UpdateName"):
            title = release["UpdateName"]
        fe.title(title)
        
        # Link
        if release.get("SecurityInfo") and release["SecurityInfo"].startswith("http"):
            fe.link(href=release["SecurityInfo"])
        
        # Description/Content
        description_parts = []
        
        # Basic info
        description_parts.append(f"Product: {release.get('ProductName', os_type)}")
        description_parts.append(f"Version: {version}")
        
        if release.get("Build"):
            description_parts.append(f"Build: {release['Build']}")
            
        if release.get("ReleaseDate"):
            description_parts.append(f"Release Date: {release['ReleaseDate']}")
            
        if release.get("ExpirationDate"):
            description_parts.append(f"Expiration Date: {release['ExpirationDate']}")
            
        if release.get("DaysSincePreviousRelease"):
            description_parts.append(f"Days Since Previous: {release['DaysSincePreviousRelease']}")
            
        # CVE information
        cves = release.get("CVEs", {})
        actively_exploited = release.get("ActivelyExploitedCVEs", [])
        
        description_parts.append("")  # Empty line
        description_parts.append(self._format_cve_list(cves, actively_exploited))
        
        # Supported devices (limit to avoid too long description)
        devices = release.get("SupportedDevices", [])
        if devices:
            description_parts.append("")
            description_parts.append(f"Supported Devices ({len(devices)} total):")
            description_parts.append(", ".join(devices[:10]))
            if len(devices) > 10:
                description_parts.append(f"... and {len(devices) - 10} more")
        
        fe.description("\n".join(description_parts))
        
        # Publication date
        try:
            if release_date:
                # Parse various date formats
                for fmt in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d", "%B %d, %Y"]:
                    try:
                        dt = datetime.strptime(release_date.replace("Released ", ""), fmt)
                        if not dt.tzinfo:
                            dt = dt.replace(tzinfo=timezone.utc)
                        fe.pubDate(dt)
                        break
                    except:
                        continue
        except Exception as e:
            logger.warning(f"Error parsing date {release_date}: {e}")
    
    def generate_feed(self, os_type: str, feed_file: Path) -> Optional[Path]:
        """Generate RSS feed for an OS type."""
        if not feed_file.exists():
            logger.warning(f"Feed file not found: {feed_file}")
            return None
            
        try:
            with open(feed_file) as f:
                feed_data = json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading feed file {feed_file}: {e}")
            return None
        
        # Check if update needed
        if not self._should_update_feed(os_type, feed_data):
            logger.info(f"RSS feed for {os_type} is up-to-date")
            return self.output_dir / f"{os_type.lower()}_feed.xml"
        
        # Get configuration
        config = self.FEED_CONFIGS.get(os_type)
        if not config:
            logger.warning(f"No RSS configuration for {os_type}")
            return None
        
        # Create feed generator
        fg = FeedGenerator()
        fg.title(config.title)
        fg.link(href=config.link, rel='alternate')
        fg.description(config.description)
        fg.language(config.language)
        fg.ttl(config.ttl)
        fg.author({'name': config.author_name, 'email': config.author_email})
        fg.copyright(config.copyright)
        
        # Add generator info
        fg.generator("SOFA RSS Generator")
        
        # Add last build date
        fg.lastBuildDate(datetime.now(timezone.utc))
        
        # Process OS versions and releases
        entries_added = 0
        
        for os_version in feed_data.get("OSVersions", []):
            # Add latest version if available
            latest = os_version.get("Latest", {})
            if latest and latest.get("ProductVersion"):
                self._create_feed_entry(fg, latest, os_type)
                entries_added += 1
            
            # Add security releases (limit to recent ones)
            releases = os_version.get("SecurityReleases", [])
            for release in releases[:20]:  # Limit to 20 most recent per OS version
                if release.get("ProductVersion"):
                    self._create_feed_entry(fg, release, os_type)
                    entries_added += 1
        
        if entries_added == 0:
            logger.warning(f"No entries to add for {os_type} RSS feed")
            return None
        
        # Write RSS feed
        output_file = self.output_dir / f"{os_type.lower()}_feed.xml"
        fg.rss_file(str(output_file))
        
        # Update cache
        self.rss_cache[os_type] = {
            "content_hash": self._get_content_hash(feed_data),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "entries": entries_added
        }
        self._save_cache()
        
        logger.info(f"Generated RSS feed for {os_type}: {output_file} ({entries_added} entries)")
        return output_file
    
    def generate_all_feeds(self):
        """Generate RSS feeds for all OS types."""
        results = {}
        
        for os_type in ["macOS", "iOS", "tvOS", "watchOS", "visionOS"]:
            feed_file = Path(f"{os_type.lower()}_data_feed.json")
            if not feed_file.exists():
                feed_file = Path(__file__).resolve().parent.parent.parent / "data" / "feeds" / "v1" / feed_file.name
                
            if feed_file.exists():
                output = self.generate_feed(os_type, feed_file)
                if output:
                    results[os_type] = str(output)
                else:
                    logger.warning(f"Failed to generate RSS for {os_type}")
            else:
                logger.info(f"No feed data for {os_type}")
        
        # Write summary
        summary_file = self.output_dir / "rss_summary.json"
        with open(summary_file, "w") as f:
            json.dump({
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "feeds": results,
                "cache": self.rss_cache
            }, f, indent=2)
            
        logger.info(f"RSS generation complete. Summary: {summary_file}")
        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate RSS feeds from SOFA data")
    parser.add_argument(
        "--os-type",
        choices=["macOS", "iOS", "tvOS", "watchOS", "visionOS"],
        help="Generate RSS for specific OS type only"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("rss"),
        help="Output directory for RSS feeds"
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent / "data" / "cache",
        help="Cache directory"
    )
    
    args = parser.parse_args()
    
    generator = RSSFeedGenerator(cache_dir=args.cache_dir, output_dir=args.output_dir)
    
    if args.os_type:
        # Generate single feed
        feed_file = Path(f"{args.os_type.lower()}_data_feed.json")
        if not feed_file.exists():
            feed_file = Path(__file__).resolve().parent.parent.parent / "data" / "feeds" / "v1" / feed_file.name
            
        result = generator.generate_feed(args.os_type, feed_file)
        if result:
            print(f"Generated: {result}")
        else:
            print(f"Failed to generate RSS for {args.os_type}")
    else:
        # Generate all feeds
        results = generator.generate_all_feeds()
        print(f"Generated {len(results)} RSS feeds:")
        for os_type, path in results.items():
            print(f"  - {os_type}: {path}")


if __name__ == "__main__":
    main()