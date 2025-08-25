
import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

#!/usr/bin/env python3
"""
Fetch and cache Apple security pages using the existing cache model.
This script uses the same caching system as build_feeds_new.py for consistency.
"""

import hashlib
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urljoin

import certifi
import requests
from bs4 import BeautifulSoup

# Import our consistent logger
from src.utils.logger import configure_logger, get_logger

# Import configuration
try:
    from src.utils.sofa_config import (
        FETCH_INDEX_PAGES,
        FETCH_DETAIL_PAGES,
        HTTP_CONFIG,
        CACHE_DIR,
        URL_META_DIR,
        RAW_HTML_DIR,
        PARSED_DIR,
        should_fetch_detail_url,
        get_enabled_index_pages
    )
except ImportError:
    # Fallback if config not available
    FETCH_INDEX_PAGES = None
    FETCH_DETAIL_PAGES = None

# Get logger for this module
logger = get_logger(__name__)


class SecurityPageFetcher:
    """Fetcher for Apple security pages using existing cache model."""
    
    # Use config if available, otherwise fallback to defaults
    if FETCH_INDEX_PAGES:
        SECURITY_PAGES = FETCH_INDEX_PAGES.copy()
        SECURITY_PAGES["detail-pages"] = {
            "url": "DETAIL_PAGES",
            "enabled": FETCH_DETAIL_PAGES.get("enabled", True),
            "description": "Individual security release detail pages"
        }
    else:
        # Fallback configuration
        SECURITY_PAGES = {
            "current": {
                "url": "https://support.apple.com/en-ca/100100",
                "enabled": True,
                "description": "Current security releases"
            },
            "2022-2023": {
                "url": "https://support.apple.com/en-ca/121012",
                "enabled": True,
                "description": "Security releases 2022-2023"
            },
            "2020-2021": {
                "url": "https://support.apple.com/en-ca/120989",
                "enabled": True,
                "description": "Security releases 2020-2021"
            },
            "2018-2019": {
                "url": "https://support.apple.com/en-ca/103179",
                "enabled": False,
                "description": "Security releases 2018-2019"
            },
            "detail-pages": {
                "url": "DETAIL_PAGES",
                "enabled": True,
                "description": "Individual security release detail pages"
            }
        }
    
    # Use cache directories from config or defaults
    if 'CACHE_DIR' in globals():
        CACHE_DIR = Path(CACHE_DIR)
        URL_META_DIR = Path(URL_META_DIR)
        RAW_DIR = Path(RAW_HTML_DIR)
        PARSED_DIR = Path(PARSED_DIR)
    else:
        CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "cache"
        URL_META_DIR = CACHE_DIR / "urls"
        RAW_DIR = CACHE_DIR / "raw"
        PARSED_DIR = CACHE_DIR / "parsed"
    
    def __init__(self):
        """Initialize security page fetcher."""
        # Ensure cache directories exist
        for directory in [self.URL_META_DIR, self.RAW_DIR, self.PARSED_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("Security page fetcher initialized")
        logger.debug(f"Cache directories: urls={self.URL_META_DIR}, raw={self.RAW_DIR}, parsed={self.PARSED_DIR}")
    
    def _get_url_hash(self, url: str) -> str:
        """Get SHA1 hash of URL for filename."""
        return hashlib.sha1(url.encode()).hexdigest()
    
    def _get_meta_path(self, url: str) -> Path:
        """Get metadata file path for URL."""
        return self.URL_META_DIR / f"{self._get_url_hash(url)}.json"
    
    def _get_raw_path(self, url: str) -> Path:
        """Get raw HTML file path for URL."""
        return self.RAW_DIR / f"{self._get_url_hash(url)}.html"
    
    def _get_parsed_path(self, url: str) -> Path:
        """Get parsed data file path for URL."""
        return self.PARSED_DIR / f"{self._get_url_hash(url)}.json"
    
    def _get_content_hash(self, html: str) -> str:
        """Get stable content hash of HTML."""
        soup = BeautifulSoup(html, "lxml")
        # Remove script/style tags for stable hashing
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ").split())
        return hashlib.sha256(text.encode()).hexdigest()
    
    def load_meta(self, url: str) -> Dict[str, Any]:
        """Load metadata for URL from cache."""
        meta_path = self._get_meta_path(url)
        if meta_path.exists():
            try:
                with open(meta_path, 'r') as f:
                    data = json.load(f)
                    logger.debug(f"Loaded metadata for {url[:50]}... from cache")
                    return data
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")
                return {}
        return {}
    
    def save_meta(self, url: str, last_modified: Optional[str], content_hash: str) -> None:
        """Save metadata for URL to cache."""
        meta = {
            "url": url,
            "last_modified": last_modified or "",
            "content_hash": content_hash,
            "seen": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        meta_path = self._get_meta_path(url)
        try:
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)
            logger.debug(f"Saved metadata for {url[:50]}...")
            logger.debug(f"  Content hash: {content_hash[:16]}...")
            logger.debug(f"  Last-Modified: {last_modified or 'not provided'}")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def save_raw(self, url: str, html: str) -> None:
        """Save raw HTML to cache."""
        raw_path = self._get_raw_path(url)
        try:
            with open(raw_path, 'w', encoding='utf-8') as f:
                f.write(html)
            size = len(html)
            logger.info(f"Saved raw HTML: {size:,} bytes to {raw_path.name}")
        except Exception as e:
            logger.error(f"Failed to save raw HTML: {e}")
    
    def load_raw(self, url: str) -> Optional[str]:
        """Load raw HTML from cache."""
        raw_path = self._get_raw_path(url)
        if raw_path.exists():
            try:
                with open(raw_path, 'r', encoding='utf-8') as f:
                    html = f.read()
                logger.debug(f"Loaded raw HTML from cache: {raw_path.name}")
                return html
            except Exception as e:
                logger.warning(f"Failed to load raw HTML: {e}")
                return None
        return None
    
    def save_parsed(self, url: str, data: Dict[str, Any]) -> None:
        """Save parsed data to cache."""
        parsed_path = self._get_parsed_path(url)
        try:
            with open(parsed_path, 'w') as f:
                json.dump(data, f, indent=2, sort_keys=True)
            logger.debug(f"Saved parsed data to {parsed_path.name}")
        except Exception as e:
            logger.error(f"Failed to save parsed data: {e}")
    
    def load_parsed(self, url: str) -> Optional[Dict[str, Any]]:
        """Load parsed data from cache."""
        parsed_path = self._get_parsed_path(url)
        if parsed_path.exists():
            try:
                with open(parsed_path, 'r') as f:
                    data = json.load(f)
                logger.debug(f"Loaded parsed data from cache: {parsed_path.name}")
                return data
            except Exception as e:
                logger.warning(f"Failed to load parsed data: {e}")
                return None
        return None
    
    def fetch_from_url(self, url: str, page_id: str, force_refresh: bool = False, verify_content: bool = False) -> Tuple[str, bool]:
        """
        Fetch page from URL with conditional GET support.
        
        Args:
            url: URL to fetch
            page_id: Page identifier for logging
            force_refresh: Skip If-Modified-Since header
            verify_content: Always fetch to verify content hash even on 304
            
        Returns (html_content, was_modified).
        """
        logger.info(f"Fetching {page_id} from {url}{' (forced refresh)' if force_refresh else ''}{' (verify mode)' if verify_content else ''}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Check for existing Last-Modified header (skip if forcing refresh or verifying)
        meta = self.load_meta(url)
        if not force_refresh and not verify_content and meta.get('last_modified'):
            headers['If-Modified-Since'] = meta['last_modified']
            logger.debug(f"Using If-Modified-Since: {meta['last_modified']}")
        
        # Use certifi for support.apple.com
        verify = certifi.where()
        
        try:
            # Log download start
            start_time = time.time()
            logger.info(f"Starting HTTP request for {page_id}...")
            
            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                verify=verify
            )
            
            # Log download completion
            elapsed = time.time() - start_time
            logger.info(f"HTTP request completed in {elapsed:.2f}s")
            
            if response.status_code == 304:
                logger.info(f"Page {page_id} not modified (304)")
                # Even on 304, we should periodically verify content hasn't changed
                # (Apple might update content without changing Last-Modified)
                
                # Load from cache
                cached_html = self.load_raw(url)
                if cached_html:
                    # ALWAYS re-fetch periodically to verify, or use --verify flag
                    # For now, trust 304 but log a warning
                    logger.debug("Trusting 304 response - content assumed unchanged")
                    logger.debug("Use --force to re-verify content hash if needed")
                    return cached_html, False
                else:
                    logger.warning("304 received but no cached content found, refetching")
                    # Remove If-Modified-Since and retry
                    headers.pop('If-Modified-Since', None)
                    response = requests.get(url, headers=headers, timeout=30, verify=verify)
            
            response.raise_for_status()
            
            html_content = response.text
            last_modified = response.headers.get('Last-Modified')
            
            logger.info(f"Fetched {page_id} successfully, status: {response.status_code}")
            logger.info(f"Response size: {len(response.text):,} bytes")
            if last_modified:
                logger.debug(f"Last-Modified: {last_modified}")
            
            # Calculate content hash
            logger.debug(f"Calculating content hash...")
            hash_start = time.time()
            content_hash = self._get_content_hash(html_content)
            logger.debug(f"Content hash calculated in {time.time() - hash_start:.3f}s: {content_hash[:16]}...")
            
            # Check if content actually changed (skip if forcing refresh)
            old_hash = meta.get('content_hash', '')
            if not force_refresh and old_hash == content_hash:
                logger.info(f"Content unchanged for {page_id} (hash match)")
                return html_content, False
            elif old_hash and old_hash != content_hash:
                logger.info(f"Content changed for {page_id} (hash mismatch)")
            
            # Save to cache
            logger.debug(f"Saving metadata and raw HTML to cache...")
            save_start = time.time()
            self.save_meta(url, last_modified, content_hash)
            self.save_raw(url, html_content)
            logger.debug(f"Cache save completed in {time.time() - save_start:.3f}s")
            
            # Parse and log summary
            logger.debug(f"Parsing HTML content...")
            parse_start = time.time()
            soup = BeautifulSoup(html_content, "lxml")
            rows = soup.find_all("tr")
            logger.info(f"  Found {len(rows)} table rows")
            
            # Count releases
            release_count = sum(1 for row in rows if len(row.find_all("td")) >= 2)
            logger.info(f"  Found {release_count} potential security releases")
            logger.debug(f"HTML parsing completed in {time.time() - parse_start:.3f}s")
            
            return html_content, True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {page_id}: {e}")
            # Try to load from cache as fallback
            cached_html = self.load_raw(url)
            if cached_html:
                logger.warning(f"Using cached content for {page_id} due to fetch error")
                return cached_html, False
            raise
    
    def parse_security_page(self, html: str, url: str) -> Dict[str, Any]:
        """Parse security page HTML into structured data."""
        soup = BeautifulSoup(html, "lxml")
        rows = soup.find_all("tr")
        
        releases = []
        os_types = set()
        
        for row in rows:
            cells = row.find_all("td")
            if cells and len(cells) >= 2:
                name_info = cells[0].get_text(strip=True)
                date_info = cells[-1].get_text(strip=True) if len(cells) > 1 else "Unknown"
                
                # Detect OS type
                os_type = "unknown"
                if "macOS" in name_info:
                    os_type = "macOS"
                elif "iOS" in name_info or "iPadOS" in name_info:
                    os_type = "iOS"
                elif "watchOS" in name_info:
                    os_type = "watchOS"
                elif "tvOS" in name_info:
                    os_type = "tvOS"
                elif "visionOS" in name_info:
                    os_type = "visionOS"
                elif "Safari" in name_info:
                    os_type = "Safari"
                
                os_types.add(os_type)
                
                # Extract link if present
                link = cells[0].find("a", href=True)
                has_details = link is not None
                detail_url = urljoin(url, link["href"]) if link else None
                
                releases.append({
                    'name': name_info,
                    'date': date_info,
                    'os_type': os_type,
                    'has_details': has_details,
                    'detail_url': detail_url
                })
        
        parsed_data = {
            'url': url,
            'parsed_at': datetime.now().isoformat(),
            'total_releases': len(releases),
            'os_types': list(os_types),
            'releases': releases
        }
        
        return parsed_data
    
    def fetch(self, page_id: str, force_refresh: bool = False, verify_content: bool = False) -> Dict[str, Any]:
        """
        Fetch and parse security page.
        
        Args:
            page_id: ID of the page (e.g., 'current', '2022-2023')
            force_refresh: Force fetching fresh data even if cached
            verify_content: Always verify content hash even on 304
            
        Returns:
            Dict containing parsed security page data
        """
        if page_id not in self.SECURITY_PAGES:
            logger.error(f"Unknown page ID: {page_id}")
            return {}
        
        # Special handling for detail pages
        if page_id == "detail-pages":
            return self.fetch_detail_pages(force_refresh, verify_content)
        
        url = self.SECURITY_PAGES[page_id]['url']
        
        # Check if we have valid parsed data in cache
        if not force_refresh:
            parsed_data = self.load_parsed(url)
            if parsed_data:
                logger.info(f"Using cached parsed data for {page_id}")
                return parsed_data
        
        # Fetch the page (may return cached content if not modified)
        html_content, was_modified = self.fetch_from_url(url, page_id, force_refresh, verify_content)
        
        # Parse the content
        parsed_data = self.parse_security_page(html_content, url)
        
        # Save parsed data if content was modified
        if was_modified or force_refresh:
            self.save_parsed(url, parsed_data)
            logger.info(f"Updated parsed data for {page_id}")
        
        return parsed_data
    
    def get_detail_urls_from_releases(self) -> set:
        """Get all unique detail URLs from security_releases/*.json."""
        urls = set()
        releases_dir = Path('security_releases')
        
        if not releases_dir.exists():
            logger.warning("security_releases/ directory not found")
            return urls
        
        for json_file in releases_dir.glob('*.json'):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    for release in data.get('releases', []):
                        url = release.get('url')
                        if url:
                            urls.add(url)
            except Exception as e:
                logger.error(f"Error reading {json_file}: {e}")
        
        logger.info(f"Found {len(urls)} detail URLs from security releases")
        return urls
    
    def fetch_detail_pages(self, force_refresh: bool = False, verify_content: bool = False) -> Dict[str, Any]:
        """
        Fetch all detail pages by extracting URLs from cached index pages.
        
        This avoids the chicken-egg problem with security_releases/*.json
        """
        logger.info("Fetching detail pages from cached index pages...")
        
        # Extract detail URLs from cached index pages
        detail_urls = set()
        
        # Look through all cached index HTML files
        for html_file in self.RAW_DIR.glob("*.html"):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Parse HTML to find detail page links
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find all links that look like detail pages
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # Look for Apple support article links
                    if '/HT' in href or '/kb/HT' in href:
                        # Convert relative URLs to absolute
                        if href.startswith('/'):
                            full_url = f"https://support.apple.com{href}"
                        elif 'support.apple.com' in href:
                            full_url = href
                        else:
                            continue
                        
                        # Normalize and add
                        if 'support.apple.com' in full_url and '/HT' in full_url:
                            detail_urls.add(full_url)
                            
            except Exception as e:
                logger.warning(f"Error parsing {html_file}: {e}")
        
        logger.info(f"Found {len(detail_urls)} detail URLs from index pages")
        
        if not detail_urls:
            logger.warning("No detail URLs found in cached index pages")
            return {'urls': [], 'fetched': 0, 'cached': 0}
        
        results = {
            'urls': list(detail_urls),
            'fetched': 0,
            'cached': 0,
            'skipped': 0,
            'failed': [],
            'data': {}
        }
        
        # Apply max_pages limit from config
        if FETCH_DETAIL_PAGES and FETCH_DETAIL_PAGES.get('max_pages'):
            max_pages = FETCH_DETAIL_PAGES['max_pages']
            if len(detail_urls) > max_pages:
                logger.info(f"Limiting to {max_pages} detail pages (config setting)")
                detail_urls = list(detail_urls)[:max_pages]
        
        for i, url in enumerate(detail_urls, 1):
            # Check if we should fetch this URL based on config
            if FETCH_DETAIL_PAGES and not should_fetch_detail_url(url):
                results['skipped'] += 1
                logger.debug(f"[{i}/{len(detail_urls)}] Skipping (config filter): {url}")
                continue
            # Check cache with alternate URL formats
            alt_urls = [
                url,
                url.replace('/kb/', '/en-us/'),
                url.replace('support.apple.com/', 'support.apple.com/en-us/'),
                url.replace('support.apple.com/en-ca/', 'support.apple.com/en-us/')
            ]
            
            cached = False
            for alt_url in alt_urls:
                alt_path = self._get_raw_path(alt_url)
                if alt_path.exists() and not force_refresh:
                    cached = True
                    results['cached'] += 1
                    if i % 50 == 0:  # Log progress every 50 pages
                        logger.info(f"[{i}/{len(detail_urls)}] Progress: {results['cached']} cached, {results['fetched']} fetched")
                    break
            
            if not cached:
                # Need to fetch
                logger.info(f"[{i}/{len(detail_urls)}] Fetching: {url[:60]}...")
                try:
                    html, was_cached = self.fetch_from_url(url, page_id=f"detail_{i}", 
                                                          force_refresh=force_refresh,
                                                          verify_content=verify_content)
                    if html:
                        results['fetched'] += 1
                        # Brief delay to be respectful
                        if i < len(detail_urls):
                            time.sleep(1.5)
                    else:
                        results['failed'].append(url)
                        logger.warning(f"Failed to fetch: {url}")
                except Exception as e:
                    logger.error(f"Error fetching {url}: {e}")
                    results['failed'].append(url)
        
        logger.info(f"Detail pages complete: {results['fetched']} fetched, {results['cached']} cached, {len(results['failed'])} failed")
        
        if results['failed']:
            logger.warning(f"Failed to fetch {len(results['failed'])} detail pages")
            # Save failed URLs for debugging
            with open('cache/failed_detail_urls.json', 'w') as f:
                json.dump(results['failed'], f, indent=2)
        
        return results
    
    def fetch_all(self, force_refresh: bool = False, skip_old: bool = False, verify_content: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Fetch all security pages.
        
        Args:
            force_refresh: Force fetching fresh data even if cached
            skip_old: Skip older pages (2020-2021, 2018-2019)
            verify_content: Always verify content hash even on 304
            
        Returns:
            Dict with page ID as key and parsed data as value
        """
        results = {}
        
        # Use config to determine which pages to fetch
        if FETCH_INDEX_PAGES:
            pages_to_fetch = [
                page_id for page_id, config in FETCH_INDEX_PAGES.items()
                if config.get('enabled', False) and page_id != 'detail-pages'
            ]
            if skip_old:
                # Filter out old pages
                pages_to_fetch = [p for p in pages_to_fetch if '201' not in p]
        else:
            # Fallback
            pages_to_fetch = ['current', '2022-2023']
            if not skip_old:
                pages_to_fetch.extend(['2020-2021', '2018-2019'])
        
        # First fetch index pages
        for page_id in pages_to_fetch:
            try:
                results[page_id] = self.fetch(page_id, force_refresh, verify_content)
                logger.info(f"Successfully processed {page_id}")
            except Exception as e:
                logger.error(f"Failed to fetch {page_id}: {e}")
        
        # Now fetch detail pages extracted from index pages
        logger.info("Fetching detail pages extracted from index pages...")
        detail_results = self.fetch_detail_pages(force_refresh, verify_content)
        results['detail-pages'] = detail_results
        logger.info(f"Detail pages: {detail_results.get('fetched', 0)} fetched, {detail_results.get('cached', 0)} cached")
        
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache."""
        stats = {
            'urls_cached': len(list(self.URL_META_DIR.glob('*.json'))),
            'raw_html_cached': len(list(self.RAW_DIR.glob('*.html'))),
            'parsed_data_cached': len(list(self.PARSED_DIR.glob('*.json'))),
            'total_cache_size': 0
        }
        
        # Calculate total cache size
        for directory in [self.URL_META_DIR, self.RAW_DIR, self.PARSED_DIR]:
            for file in directory.glob('*'):
                if file.is_file():
                    stats['total_cache_size'] += file.stat().st_size
        
        return stats
    
    def clean_cache(self, page_ids: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Clean cache files.
        
        Args:
            page_ids: Specific pages to clean, or None to clean all
            
        Returns:
            Dict with counts of deleted files
        """
        deleted = {
            'urls': 0,
            'raw': 0,
            'parsed': 0,
            'bytes': 0
        }
        
        # Determine which URLs to clean
        if page_ids:
            urls_to_clean = []
            for page_id in page_ids:
                if page_id in self.SECURITY_PAGES:
                    urls_to_clean.append(self.SECURITY_PAGES[page_id]['url'])
                else:
                    logger.warning(f"Unknown page ID: {page_id}")
        else:
            # Clean all if no specific pages
            urls_to_clean = None
        
        # Clean cache files
        for directory, ext, key in [
            (self.URL_META_DIR, '.json', 'urls'),
            (self.RAW_DIR, '.html', 'raw'),
            (self.PARSED_DIR, '.json', 'parsed')
        ]:
            for file in directory.glob(f'*{ext}'):
                # If specific URLs requested, check if this file matches
                if urls_to_clean is not None:
                    file_matches = False
                    for url in urls_to_clean:
                        if file.stem == self._get_url_hash(url):
                            file_matches = True
                            break
                    if not file_matches:
                        continue
                
                # Delete the file
                try:
                    size = file.stat().st_size
                    file.unlink()
                    deleted[key] += 1
                    deleted['bytes'] += size
                    logger.debug(f"Deleted {file.name}")
                except Exception as e:
                    logger.error(f"Failed to delete {file}: {e}")
        
        logger.info(f"Cleaned cache: {deleted['urls']} metadata, {deleted['raw']} HTML, {deleted['parsed']} parsed files")
        logger.info(f"Freed {deleted['bytes']:,} bytes")
        
        return deleted


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fetch and cache Apple security pages',
        epilog='''Initial setup flow:
  1. Fetch index pages: fetch_security_pages.py current 2022-2023 2020-2021 2018-2019
  2. Build releases: build_security_releases.py
  3. Fetch detail pages: fetch_security_pages.py detail-pages
  
Or just run: fetch_security_pages.py all (will skip detail pages on first run)''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'pages',
        nargs='*',
        choices=['current', '2022-2023', '2020-2021', '2018-2019', 'detail-pages', 'all'],
        help='Pages to fetch (default: all)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh even if cached'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify content hash even on 304 (detects stealth updates)'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary of fetched pages'
    )
    parser.add_argument(
        '--skip-old',
        action='store_true',
        help='Skip older pages (2020-2021, 2018-2019)'
    )
    parser.add_argument(
        '--cache-stats',
        action='store_true',
        help='Show cache statistics'
    )
    parser.add_argument(
        '--clean-cache',
        action='store_true',
        help='Clean cache for specified pages (or all if no pages specified)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity (-v for INFO, -vv for DEBUG, -vvv for TRACE)'
    )
    
    args = parser.parse_args()
    
    # Configure logging based on verbosity
    # Default to INFO level (1) if no verbosity specified, so user sees progress
    configure_logger(max(1, args.verbose))
    
    try:
        fetcher = SecurityPageFetcher()
        
        # Show cache stats if requested
        if args.cache_stats:
            stats = fetcher.get_cache_stats()
            print("\nCache Statistics:")
            print(f"  URLs metadata: {stats['urls_cached']} files")
            print(f"  Raw HTML: {stats['raw_html_cached']} files")
            print(f"  Parsed data: {stats['parsed_data_cached']} files")
            print(f"  Total size: {stats['total_cache_size']:,} bytes")
            print()
        
        # Clean cache if requested
        if args.clean_cache:
            # Determine which pages to clean
            pages_to_clean = None
            if args.pages and 'all' not in args.pages:
                pages_to_clean = args.pages
            
            print(f"\nCleaning cache{' for: ' + ', '.join(pages_to_clean) if pages_to_clean else ' (all pages)'}...")
            deleted = fetcher.clean_cache(pages_to_clean)
            print(f"Deleted {deleted['urls'] + deleted['raw'] + deleted['parsed']} files")
            print(f"Freed {deleted['bytes']:,} bytes")
            
            # Exit after cleaning unless also fetching
            if not args.force and not any(p in ['current', '2022-2023', '2020-2021', '2018-2019'] for p in args.pages):
                return
        
        # Determine which pages to fetch
        pages = args.pages if args.pages else ['all']
        if 'all' in pages:
            results = fetcher.fetch_all(force_refresh=args.force, skip_old=args.skip_old, verify_content=args.verify)
        else:
            results = {}
            for page_id in args.pages:
                try:
                    results[page_id] = fetcher.fetch(page_id, force_refresh=args.force, verify_content=args.verify)
                except ValueError as e:
                    logger.error(f"Error fetching {page_id}: {e}")
                    continue
        
        if args.summary:
            print("\nSecurity Pages Summary:")
            print("=" * 60)
            
            for page_id, data in results.items():
                print(f"\n{page_id.upper()}:")
                print(f"  URL: {data['url']}")
                print(f"  Parsed at: {data['parsed_at']}")
                print(f"  Total releases: {data['total_releases']}")
                print(f"  OS types: {', '.join(data['os_types'])}")
                
                if data['releases'] and len(data['releases']) >= 5:
                    print("  Recent releases:")
                    for release in data['releases'][:5]:
                        details = "✓" if release['has_details'] else "✗"
                        name = release['name'][:50] + "..." if len(release['name']) > 50 else release['name']
                        print(f"    [{details}] {name} ({release['date']})")
        
        logger.info("Security pages fetch completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to fetch security pages: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()