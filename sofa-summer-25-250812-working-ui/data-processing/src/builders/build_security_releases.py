#!/usr/bin/env python3
"""
Build per-OS security releases from cached Apple security pages.

This script ONLY reads from the cache populated by fetch_security_pages.py.
It does NOT fetch any data from the internet.

Key features:
- Reads from .cache/parsed/*.json (parsed security pages)
- Outputs to ./security_releases/*.json
- Groups releases by OS type
- Sorts releases by date (newest first)

No network access required - purely processes cached data.
"""

from __future__ import annotations

import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

# Import our consistent logger
from src.utils.logger import configure_logger, get_logger

# Get logger for this module
logger = get_logger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[2]  # src/builders -> src -> root
CACHE_DIR = REPO_ROOT / "data" / "cache"
PARSED_DIR = CACHE_DIR / "parsed"
RAW_DIR = CACHE_DIR / "raw"
SECURITY_RELEASES_DIR = REPO_ROOT / "data" / "security_releases"

# Ensure output directory exists
SECURITY_RELEASES_DIR.mkdir(parents=True, exist_ok=True)

# Map OS types to output file keys
OS_KEYS = {
    "iOS": "ios",
    "iPadOS": "ipados",
    "macOS": "macos",
    "watchOS": "watchos",
    "tvOS": "tvos",
    "visionOS": "visionos",
    "Safari": "safari",
}

# Known security page URLs (must match what fetch_security_pages.py uses)
SECURITY_PAGE_URLS = [
    "https://support.apple.com/en-ca/100100",  # current
    "https://support.apple.com/en-ca/121012",  # 2022-2023
    "https://support.apple.com/en-ca/120989",  # 2020-2021
    "https://support.apple.com/en-ca/103179",  # 2018-2019
]

# Regex helpers for extracting data from parsed pages
RE_CVE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)
# Apple build formats: YYLnnnnn[x] where YY=year, L=letter (A-Z), nnnnn=1-5 digits, x=optional lowercase
# Common patterns: 24G84, 22H722, 21H1320, 18A5351d
# Year must be 18-29 (2018-2029) to avoid false matches
RE_BUILD = re.compile(r"\b(?:1[89]|2[0-9])[A-Z]\d{1,5}[a-z]?\b")  # e.g., 24G84, 22H722, 18A5351d
RE_VERSION = re.compile(r"\b(?:iOS|iPadOS|macOS|watchOS|tvOS|visionOS|Safari)\s+([0-9]+(?:\.[0-9]+)*)", re.I)


# ──────────────────────────────────────────────────────────────────────────────
# Cache reading functions
# ──────────────────────────────────────────────────────────────────────────────

def _get_url_hash(url: str) -> str:
    """Get SHA1 hash of URL for filename."""
    return hashlib.sha1(url.encode()).hexdigest()


def load_parsed_page(url: str) -> Optional[Dict]:
    """Load parsed security page data from cache."""
    parsed_path = PARSED_DIR / f"{_get_url_hash(url)}.json"
    if parsed_path.exists():
        try:
            with open(parsed_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load parsed data for {url}: {e}")
    return None


def load_raw_page(url: str) -> Optional[str]:
    """Load raw HTML from cache if needed."""
    raw_path = RAW_DIR / f"{_get_url_hash(url)}.html"
    if raw_path.exists():
        try:
            with open(raw_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load raw HTML for {url}: {e}")
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Parsing functions
# ──────────────────────────────────────────────────────────────────────────────

def extract_version_from_title(title: str) -> Optional[str]:
    """Extract version number from release title."""
    # Try to extract version from title patterns like "macOS Sequoia 15.3" or "macOS Big Sur 11.7.9"
    patterns = [
        r"macOS\s+(?:\w+\s+)+(\d+(?:\.\d+)*)",  # macOS Sequoia 15.3 or macOS Big Sur 11.7.9
        r"iOS\s+(\d+(?:\.\d+)*)",               # iOS 18.2
        r"iPadOS\s+(\d+(?:\.\d+)*)",            # iPadOS 18.2
        r"watchOS\s+(\d+(?:\.\d+)*)",           # watchOS 11.2
        r"tvOS\s+(\d+(?:\.\d+)*)",              # tvOS 18.2
        r"visionOS\s+(\d+(?:\.\d+)*)",          # visionOS 2.2
        r"Safari\s+(\d+(?:\.\d+)*)",            # Safari 18.2
    ]
    
    for pattern in patterns:
        m = re.search(pattern, title, re.IGNORECASE)
        if m:
            return m.group(1)
    
    return None


def extract_build_from_text(text: str) -> Optional[str]:
    """Extract build number from text."""
    m = RE_BUILD.search(text)
    return m.group(0) if m else None


def extract_cves_from_text(text: str) -> List[str]:
    """Extract CVE IDs from text."""
    cves = RE_CVE.findall(text)
    # Normalize and deduplicate
    return sorted(set(c.upper() for c in cves), key=lambda s: (s.split("-")[1], int(s.split("-")[2])))


def parse_detail_page(url: str, html: str) -> Dict:
    """Parse a detail page into structured data."""
    soup = BeautifulSoup(html, "lxml")
    
    # Extract title
    title_el = soup.find(["h1", "h2"])
    title = title_el.get_text(" ").strip() if title_el else ""
    
    # Extract text for analysis
    text = " ".join(soup.get_text(" ").split())
    
    # Extract version
    version = extract_version_from_title(title)
    if not version:
        # Fallback to searching in text
        mv = RE_VERSION.search(text)
        if mv:
            version = mv.group(1)
    
    # Extract build - search in raw HTML since build numbers may be in scripts/meta tags
    build = extract_build_from_text(html)
    if not build:
        # Fallback to searching in visible text
        build = extract_build_from_text(text)
    
    # Extract CVEs - search in raw HTML first, then in visible text
    cves = extract_cves_from_text(html)
    if not cves:
        cves = extract_cves_from_text(text)
    
    # Extract release date (if present in text)
    release_date = ""
    for pattern in [
        r"Released\s+[A-Za-z]+\s+\d{1,2},\s+\d{4}",
        r"Veröffentlicht\s+\d{1,2}\.\s*[A-Za-zäöüÄÖÜ]+\s*\d{4}"
    ]:
        m = re.search(pattern, text)
        if m:
            release_date = m.group(0)
            break
    
    return {
        "title": title,
        "url": url,
        "release_date": release_date,
        "version": version,
        "build": build,
        "cve_count": len(cves),
        "cves": cves
    }


# ──────────────────────────────────────────────────────────────────────────────
# Main processing
# ──────────────────────────────────────────────────────────────────────────────

def fetch_missing_detail(url: str) -> Optional[Dict]:
    """
    Fetch and parse a missing detail page.
    This should ONLY be called with --fetch-missing flag.
    """
    import requests
    import certifi
    
    logger.warning(f"FETCHING missing detail page: {url}")
    logger.warning("This requires network access and should not be done in normal operation!")
    
    try:
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'},
            timeout=30,
            verify=certifi.where()
        )
        response.raise_for_status()
        
        # Parse the fetched HTML
        parsed = parse_detail_page(url, response.text)
        
        # Save to cache for next time
        raw_path = RAW_DIR / f"{_get_url_hash(url)}.html"
        parsed_path = PARSED_DIR / f"{_get_url_hash(url)}.json"
        
        with open(raw_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        with open(parsed_path, 'w') as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Fetched and cached missing detail page: {url}")
        return parsed
        
    except Exception as e:
        logger.error(f"Failed to fetch missing detail page {url}: {e}")
        return None


def build_releases_from_cache(fetch_missing: bool = False) -> Dict[str, List[Dict]]:
    """
    Build security releases from cached data.
    
    Args:
        fetch_missing: If True, fetch missing detail pages (requires network)
    
    Returns dict mapping OS key to list of releases.
    """
    # Initialize per-OS release lists
    per_os_releases: Dict[str, List[Dict]] = {v: [] for v in OS_KEYS.values()}
    
    # Process each known security page
    for page_url in SECURITY_PAGE_URLS:
        logger.info(f"Processing cached data for {page_url}")
        
        # Load parsed data from cache
        parsed_data = load_parsed_page(page_url)
        if not parsed_data:
            logger.warning(f"No parsed data found for {page_url}, skipping")
            continue
        
        # Process each release in the parsed data
        releases = parsed_data.get("releases", [])
        logger.info(f"  Found {len(releases)} releases")
        
        for release in releases:
            # Determine OS type
            os_type = release.get("os_type", "unknown")
            
            # Map to our OS key
            os_key = None
            for orig_key, mapped_key in OS_KEYS.items():
                if orig_key.lower() == os_type.lower():
                    os_key = mapped_key
                    break
            
            if not os_key:
                if os_type != "unknown":
                    logger.debug(f"  Unknown OS type: {os_type}")
                continue
            
            # Get detail URL if available
            detail_url = release.get("detail_url")
            
            # If we have a detail URL, try to get more info from its cached data
            if detail_url:
                detail_parsed = load_parsed_page(detail_url)
                if detail_parsed:
                    # We have parsed detail page data
                    entry = detail_parsed
                else:
                    # Try to parse from raw HTML if available
                    detail_html = load_raw_page(detail_url)
                    if detail_html:
                        entry = parse_detail_page(detail_url, detail_html)
                    else:
                        # No cached data
                        if fetch_missing:
                            # Fetch if explicitly requested
                            fetched = fetch_missing_detail(detail_url)
                            if fetched:
                                entry = fetched
                            else:
                                # Fetch failed, use basic info
                                entry = {
                                    "title": release.get("name", ""),
                                    "url": detail_url,
                                    "release_date": release.get("date", ""),
                                    "version": extract_version_from_title(release.get("name", "")),
                                    "build": None,
                                    "cve_count": 0,
                                    "cves": []
                                }
                        else:
                            # Use basic info without fetching
                            logger.debug(f"No cached detail for {detail_url}, using basic info")
                            entry = {
                                "title": release.get("name", ""),
                                "url": detail_url,
                                "release_date": release.get("date", ""),
                                "version": extract_version_from_title(release.get("name", "")),
                                "build": None,
                                "cve_count": 0,
                                "cves": []
                            }
            else:
                # No detail URL, use basic info
                entry = {
                    "title": release.get("name", ""),
                    "url": page_url,  # Use the main page URL
                    "release_date": release.get("date", ""),
                    "version": extract_version_from_title(release.get("name", "")),
                    "build": None,
                    "cve_count": 0,
                    "cves": []
                }
            
            per_os_releases[os_key].append(entry)
    
    return per_os_releases


def sort_releases(releases: List[Dict]) -> List[Dict]:
    """Sort releases by date (newest first)."""
    def sort_key(e: Dict) -> Tuple[int, str]:
        # Extract year from release_date string if possible
        m = re.search(r"(20\d{2})", e.get("release_date") or "")
        year = int(m.group(1)) if m else 0
        return (-year, e.get("title") or "")
    
    return sorted(releases, key=sort_key)


def write_security_releases(os_key: str, releases: List[Dict]) -> None:
    """Write security releases to JSON file."""
    doc = {
        "os": os_key,
        "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "releases": releases
    }
    
    out_path = SECURITY_RELEASES_DIR / f"{os_key}.json"
    with open(out_path, 'w') as f:
        json.dump(doc, f, ensure_ascii=False, sort_keys=False, indent=2)
    
    logger.info(f"Wrote {len(releases)} releases to {out_path.name}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build security releases from cached data')
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity'
    )
    parser.add_argument(
        '--check-cache',
        action='store_true',
        help='Check cache status before building'
    )
    parser.add_argument(
        '--fetch-missing',
        action='store_true',
        help='Fetch missing detail pages if not in cache (requires network)'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    configure_logger(max(1, args.verbose))
    
    logger.info("[build_security_releases] Starting build from cache")
    
    # Check cache if requested
    if args.check_cache:
        parsed_count = len(list(PARSED_DIR.glob("*.json")))
        raw_count = len(list(RAW_DIR.glob("*.html")))
        logger.info(f"Cache status: {parsed_count} parsed, {raw_count} raw HTML files")
        
        if parsed_count == 0:
            logger.error("No parsed data in cache! Run fetch_security_pages.py first")
            return 1
    
    # Build releases from cache
    if args.fetch_missing:
        logger.warning("--fetch-missing enabled: Will fetch missing detail pages from network")
        logger.warning("This should only be used for validation/recovery, not in normal operation!")
    
    per_os_releases = build_releases_from_cache(fetch_missing=args.fetch_missing)
    
    # Write output files
    total_releases = 0
    for os_key, releases in per_os_releases.items():
        if releases:
            sorted_releases = sort_releases(releases)
            write_security_releases(os_key, sorted_releases)
            total_releases += len(sorted_releases)
    
    logger.info(f"[build_security_releases] Done. Wrote {total_releases} total releases")
    return 0


if __name__ == "__main__":
    exit(main())