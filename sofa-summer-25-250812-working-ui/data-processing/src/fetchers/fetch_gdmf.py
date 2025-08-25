#!/usr/bin/env python3
"""
Fetch and cache GDMF (Global Data Management Facility) data from Apple.

import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

This script can be run independently to update the GDMF cache.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

import certifi
import requests

# Import our consistent logger
from src.utils.logger import configure_logger, get_logger

# Get logger for this module
logger = get_logger(__name__)

class GDMFClient:
    """Client for fetching GDMF data from Apple."""
    
    GDMF_URL = "https://gdmf.apple.com/v2/pmv"
    CACHE_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "cache" / "gdmf_cached.json"
    CACHE_DURATION = timedelta(hours=6)
    
    def __init__(self):
        """Initialize GDMF client."""
        # Ensure cache directory exists
        self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        logger.info("GDMF client initialized")
    
    def is_cache_valid(self) -> bool:
        """Check if the cache is still valid."""
        if not self.CACHE_FILE.exists():
            logger.info("Cache file does not exist")
            return False
        
        try:
            with open(self.CACHE_FILE, 'r') as f:
                cached_data = json.load(f)
            
            if 'etag' not in cached_data or 'data' not in cached_data:
                logger.warning("Cache file missing required fields")
                return False
            
            # Check cache age
            cache_stat = self.CACHE_FILE.stat()
            cache_age = datetime.now() - datetime.fromtimestamp(cache_stat.st_mtime)
            
            if cache_age > self.CACHE_DURATION:
                logger.info(f"Cache is {cache_age} old, exceeds {self.CACHE_DURATION}")
                return False
            
            logger.info(f"Cache is valid, age: {cache_age}")
            return True
            
        except Exception as e:
            logger.error(f"Error checking cache validity: {e}")
            return False
    
    def fetch_from_api(self, skip_ssl_verify: bool = False) -> Dict[str, Any]:
        """Fetch fresh GDMF data from Apple API."""
        logger.info(f"Fetching GDMF data from {self.GDMF_URL}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Check for existing etag
        etag = None
        if self.CACHE_FILE.exists():
            try:
                with open(self.CACHE_FILE, 'r') as f:
                    cached_data = json.load(f)
                    etag = cached_data.get('etag')
                    if etag:
                        headers['If-None-Match'] = etag
                        logger.debug(f"Using etag: {etag}")
            except Exception as e:
                logger.warning(f"Could not read etag from cache: {e}")
        
        # Determine SSL verification setting
        if skip_ssl_verify:
            logger.warning("SSL verification disabled (--insecure flag)")
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            verify = False
        else:
            # Always prefer AppleRoot.pem for Apple services
            apple_cert = Path(__file__).resolve().parent.parent.parent / "config" / "certificates" / "AppleRoot.pem"
            if apple_cert.exists():
                verify = str(apple_cert)
                logger.info(f"Using Apple certificate: {verify}")
            else:
                logger.warning("AppleRoot.pem not found, falling back to certifi")
                verify = certifi.where()
        
        try:
            # Make request with configured verification
            response = requests.get(
                self.GDMF_URL,
                headers=headers,
                timeout=30,
                verify=verify
            )
            
            if response.status_code == 304:
                logger.info("GDMF data not modified (304), using cached version")
                with open(self.CACHE_FILE, 'r') as f:
                    return json.load(f)
            
            response.raise_for_status()
            
            data = response.json()
            new_etag = response.headers.get('ETag', '') or response.headers.get('etag', '')
            
            logger.info(f"Fetched GDMF data successfully, status: {response.status_code}")
            logger.info(f"Response size: {len(response.text)} bytes")
            if new_etag:
                logger.debug(f"Received ETag: {new_etag}")
            
            # Log summary of fetched data
            if 'PublicAssetSets' in data:
                for os_type, assets in data['PublicAssetSets'].items():
                    logger.info(f"  {os_type}: {len(assets)} assets")
            
            return {
                'etag': new_etag,
                'data': data,
                'fetched_at': datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch GDMF data: {e}")
            raise
    
    def save_to_cache(self, data: Dict[str, Any]) -> None:
        """Save GDMF data to cache file."""
        try:
            with open(self.CACHE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved GDMF data to {self.CACHE_FILE}")
            
            # Log cache file size
            size = self.CACHE_FILE.stat().st_size
            logger.info(f"Cache file size: {size:,} bytes")
            
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
            raise
    
    def fetch(self, force_refresh: bool = False, skip_ssl_verify: bool = False) -> Dict[str, Any]:
        """
        Fetch GDMF data, using cache if valid.
        
        Args:
            force_refresh: Force fetching fresh data even if cache is valid
            skip_ssl_verify: Skip SSL certificate verification
            
        Returns:
            Dict containing GDMF data
        """
        if not force_refresh and self.is_cache_valid():
            logger.info("Using cached GDMF data")
            with open(self.CACHE_FILE, 'r') as f:
                return json.load(f)
        
        try:
            logger.info("Fetching fresh GDMF data")
            data = self.fetch_from_api(skip_ssl_verify=skip_ssl_verify)
            self.save_to_cache(data)
            return data
        except Exception as e:
            # If fetch fails and we have a stale cache, use it
            if self.CACHE_FILE.exists():
                logger.warning(f"Fetch failed, using stale cache: {e}")
                with open(self.CACHE_FILE, 'r') as f:
                    return json.load(f)
            else:
                raise
    
    def get_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the GDMF data."""
        summary = {
            'fetched_at': data.get('fetched_at', 'unknown'),
            'etag': data.get('etag', 'none'),
            'os_types': {}
        }
        
        if 'data' in data and 'PublicAssetSets' in data['data']:
            # Process standard OS types first
            for os_type, assets in data['data']['PublicAssetSets'].items():
                versions = set()
                builds = set()
                devices = set()
                
                for asset in assets:
                    if 'ProductVersion' in asset:
                        versions.add(asset['ProductVersion'])
                    if 'Build' in asset:
                        builds.add(asset['Build'])
                    if 'SupportedDevices' in asset:
                        for device in asset['SupportedDevices']:
                            devices.add(device)
                
                # Sort versions properly (handle version numbers like 18.6 vs 9.6.3)
                def version_key(v):
                    try:
                        parts = v.split('.')
                        return tuple(int(p) if p.isdigit() else p for p in parts)
                    except:
                        return (0,)
                
                sorted_versions = sorted(versions, key=version_key, reverse=True) if versions else []
                
                summary['os_types'][os_type] = {
                    'asset_count': len(assets),
                    'unique_versions': len(versions),
                    'unique_builds': len(builds),
                    'unique_devices': len(devices),
                    'latest_version': sorted_versions[0] if sorted_versions else None,
                    'versions_sample': sorted_versions[:5] if sorted_versions else []
                }
            
            # Extract watchOS and tvOS from iOS assets
            if 'iOS' in data['data']['PublicAssetSets']:
                for embedded_os, device_prefix in [('watchOS', 'Watch'), ('tvOS', 'AppleTV')]:
                    versions = set()
                    builds = set()
                    devices = set()
                    asset_count = 0
                    
                    for asset in data['data']['PublicAssetSets']['iOS']:
                        if 'SupportedDevices' in asset:
                            has_device = any(dev.startswith(device_prefix) for dev in asset['SupportedDevices'])
                            if has_device:
                                asset_count += 1
                                if 'ProductVersion' in asset:
                                    versions.add(asset['ProductVersion'])
                                if 'Build' in asset:
                                    builds.add(asset['Build'])
                                for device in asset['SupportedDevices']:
                                    if device.startswith(device_prefix):
                                        devices.add(device)
                    
                    if versions:  # Only add if we found any data
                        sorted_versions = sorted(versions, key=version_key, reverse=True)
                        summary['os_types'][embedded_os] = {
                            'asset_count': asset_count,
                            'unique_versions': len(versions),
                            'unique_builds': len(builds),
                            'unique_devices': len(devices),
                            'latest_version': sorted_versions[0] if sorted_versions else None,
                            'versions_sample': sorted_versions[:5] if sorted_versions else []
                        }
        
        return summary


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch and cache GDMF data')
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh even if cache is valid'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show summary of fetched data'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity (-v for INFO, -vv for DEBUG, -vvv for TRACE)'
    )
    parser.add_argument(
        '--insecure',
        action='store_true',
        help='Skip SSL certificate verification (use with caution)'
    )
    
    args = parser.parse_args()
    
    # Configure logging based on verbosity
    configure_logger(args.verbose)
    
    try:
        client = GDMFClient()
        data = client.fetch(force_refresh=args.force, skip_ssl_verify=args.insecure)
        
        if args.summary:
            summary = client.get_summary(data)
            print("\nGDMF Data Summary:")
            print(f"  Fetched at: {summary['fetched_at']}")
            print(f"  ETag: {summary['etag'] or '(none)'}")
            print("\nOS Types:")
            for os_type, info in summary['os_types'].items():
                print(f"\n  {os_type}:")
                print(f"    Assets: {info['asset_count']}")
                print(f"    Versions: {info['unique_versions']}")
                print(f"    Builds: {info['unique_builds']}")
                print(f"    Devices: {info['unique_devices']}")
                print(f"    Latest: {info['latest_version']}")
                if info.get('versions_sample'):
                    print(f"    Top versions: {', '.join(info['versions_sample'][:3])}")
        
        logger.info("GDMF fetch completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to fetch GDMF data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()