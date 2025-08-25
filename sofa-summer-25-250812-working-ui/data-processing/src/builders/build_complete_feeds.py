#!/usr/bin/env python3
"""
Complete SOFA feed builder integrating new scraper with GDMF and legacy compatibility.
Combines build_security_releases.py scraping with GDMF enrichment and Pydantic validation.
"""

from __future__ import annotations

import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import certifi
import httpx
import requests
from bs4 import BeautifulSoup, NavigableString

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    import process_ipsw
    import process_uma
except ImportError:
    process_ipsw = None
    process_uma = None

from src.models.models import (
    GDMFData,
    LatestVersion,
    OSVersion,
    SecurityRelease,
    SupportedModel,
    TimestampData,
)
from src.fetchers.kev_fetcher import KEVFetcher


class CompleteFeedBuilder:
    """Unified feed builder combining scraped data with GDMF."""
    
    def __init__(self):
        # Always use paths relative to project root
        if Path.cwd().name == 'scripts':
            project_root = Path.cwd().parent
        else:
            project_root = Path.cwd()
        
        self.cache_dir = project_root / "data" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = project_root / "data" / "security_releases" / "enriched"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.v1_dir = project_root / "data" / "feeds" / "v1"
        self.v1_dir.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        self.kev_fetcher = KEVFetcher(self.cache_dir)
        
    def _load_config(self) -> dict:
        """Load configuration."""
        config_path = Path("config.json")
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {"softwareReleases": []}
    
    def _compute_hash(self, data: Any) -> str:
        """Compute SHA-256 hash."""
        if isinstance(data, dict):
            json_str = json.dumps(data, sort_keys=True)
        else:
            json_str = str(data)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def fetch_gdmf_data(self) -> Optional[GDMFData]:
        """Fetch GDMF data with caching."""
        cache_file = self.cache_dir / "gdmf_cached.json"
        log_file = self.cache_dir / "gdmf_log.json"
        
        # Check cache
        cached_data = None
        cached_etag = None
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    cache_content = json.load(f)
                    if "etag" in cache_content and "data" in cache_content:
                        cached_data = cache_content["data"]
                        cached_etag = cache_content["etag"]
                        print("Validated local cached GDMF data.")
            except Exception as e:
                print(f"Cache read error: {e}")
        
        # Fetch live
        url = "https://gdmf.apple.com/v2/pmv"
        # Check for AppleRoot.pem in project root
        if Path.cwd().name == 'scripts':
            project_root = Path.cwd().parent
        else:
            project_root = Path.cwd()
        
        pemname = project_root / "config" / "certificates" / "AppleRoot.pem"
        
        if not pemname.exists():
            print(f"Warning: {pemname} not found, using certifi")
            pemname = certifi.where()
        
        headers = {"User-Agent": "macadmins-sofa"}
        
        try:
            response = requests.get(url, headers=headers, verify=pemname, timeout=30)
            response.raise_for_status()
            live_data = response.json()
            
            if live_data:
                live_etag = self._compute_hash(live_data)
                if live_etag != cached_etag:
                    # Update cache
                    cache_content = {"etag": live_etag, "data": live_data}
                    with open(cache_file, "w") as f:
                        json.dump(cache_content, f, indent=4)
                    print("Updated GDMF cache")
                else:
                    print("GDMF data unchanged")
                
                self._write_gdmf_log(log_file, response.status_code, live_data)
                return GDMFData(**live_data)
                
        except Exception as e:
            print(f"GDMF fetch error: {e}")
            if cached_data:
                print("Using cached GDMF data")
                return GDMFData(**cached_data)
        
        return None
    
    def _write_gdmf_log(self, log_file: Path, status_code: int, data: dict):
        """Write GDMF log."""
        current_time = datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z"
        new_etag = self._compute_hash(data)
        
        log_data = {"latest_etag": {}, "log": []}
        if log_file.exists():
            try:
                with open(log_file) as f:
                    log_data = json.load(f)
            except:
                pass
        
        log_entry = {
            "timestamp": current_time,
            "new_etag": new_etag,
            "status": f"success ({status_code})" if status_code == 200 else f"failed ({status_code})",
            "previous_etag": log_data["log"][0]["new_etag"] if log_data["log"] else "",
        }
        
        log_data["latest_etag"] = {"LastCheck": current_time, "UpdateHash": new_etag}
        log_data["log"].insert(0, log_entry)
        log_data["log"] = log_data["log"][:10]
        
        with open(log_file, "w") as f:
            json.dump(log_data, f, indent=4)
    
    async def run_new_scraper(self):
        """Run the new build_security_releases.py scraper."""
        script_path = Path(__file__).parent / "build_security_releases.py"
        if script_path.exists():
            print("Running new scraper...")
            # Run as subprocess to avoid module conflicts
            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if stdout:
                print(stdout.decode())
            if stderr and proc.returncode != 0:
                print(f"Scraper error: {stderr.decode()}")
        else:
            print(f"Warning: {script_path} not found")
    
    def enrich_with_gdmf(self, os_type: str, scraped_data: dict, gdmf_data: GDMFData) -> dict:
        """Enrich scraped data with GDMF information."""
        if not gdmf_data:
            return scraped_data
        
        os_key = self._normalize_os_key(os_type)
        enriched_releases = []
        
        for release in scraped_data.get("releases", []):
            version = release.get("version")
            if not version:
                enriched_releases.append(release)
                continue
            
            # Find matching GDMF data
            gdmf_match = self._find_gdmf_match(os_key, version, gdmf_data)
            if gdmf_match:
                release["Build"] = gdmf_match.get("Build", release.get("build"))
                release["SupportedDevices"] = gdmf_match.get("SupportedDevices", [])
                if gdmf_match.get("ExpirationDate"):
                    release["ExpirationDate"] = gdmf_match["ExpirationDate"]
            
            enriched_releases.append(release)
        
        scraped_data["releases"] = enriched_releases
        return scraped_data
    
    def _normalize_os_key(self, os_type: str) -> str:
        """Normalize OS type for GDMF lookup."""
        mapping = {
            "macos": "macOS",
            "ios": "iOS",
            "ipados": "iPadOS",
            "tvos": "tvOS",
            "watchos": "watchOS",
            "visionos": "visionOS",
        }
        return mapping.get(os_type.lower(), os_type)
    
    def _find_gdmf_match(self, os_key: str, version: str, gdmf_data: GDMFData) -> Optional[dict]:
        """Find matching GDMF entry for version with device filtering and merging."""
        all_matches = []
        
        for asset_set in [gdmf_data.PublicAssetSets, gdmf_data.AssetSets]:
            if not asset_set:
                continue
            
            # For watchOS and tvOS, look in iOS section since they're stored there
            if os_key in ["watchOS", "tvOS"]:
                search_keys = ["iOS"]
            else:
                search_keys = [os_key]
            
            for search_key in search_keys:
                os_assets = asset_set.get(search_key, [])
                for asset in os_assets:
                    asset_dict = asset if isinstance(asset, dict) else asset.model_dump()
                    if asset_dict.get("ProductVersion") == version:
                        # For watchOS/tvOS, only include if it has the right device type
                        if os_key == "watchOS":
                            devices = asset_dict.get("SupportedDevices", [])
                            if devices and any(d.startswith("Watch") for d in devices):
                                all_matches.append(asset_dict)
                        elif os_key == "tvOS":
                            devices = asset_dict.get("SupportedDevices", [])
                            if devices and any(d.startswith("AppleTV") for d in devices):
                                all_matches.append(asset_dict)
                        else:
                            all_matches.append(asset_dict)
        
        if not all_matches:
            return None
        
        # Filter and merge devices based on OS type
        os_key_lower = os_key.lower()
        filtered_matches = []
        
        if os_key_lower == "ios":
            # For iOS, collect all entries with iPhone or iPad devices
            for match in all_matches:
                devices = match.get("SupportedDevices", [])
                if devices and any(d.startswith(("iPhone", "iPad")) for d in devices):
                    filtered_matches.append(match)
        elif os_key_lower == "tvos":
            # For tvOS, collect all entries with AppleTV devices
            for match in all_matches:
                devices = match.get("SupportedDevices", [])
                if devices and any(d.startswith("AppleTV") for d in devices):
                    filtered_matches.append(match)
        elif os_key_lower == "watchos":
            # For watchOS, collect all entries with Watch devices
            for match in all_matches:
                devices = match.get("SupportedDevices", [])
                if devices and any(d.startswith("Watch") for d in devices):
                    filtered_matches.append(match)
        elif os_key_lower == "visionos":
            # For visionOS, collect all entries with RealityDevice
            for match in all_matches:
                devices = match.get("SupportedDevices", [])
                if devices and any(d.startswith("RealityDevice") for d in devices):
                    filtered_matches.append(match)
        elif os_key_lower == "macos":
            # For macOS, collect all entries with Mac devices
            for match in all_matches:
                devices = match.get("SupportedDevices", [])
                if devices and any(d.startswith(("Mac", "MacBook")) for d in devices):
                    filtered_matches.append(match)
        
        # Use filtered matches if we found any, otherwise use all matches
        matches_to_merge = filtered_matches if filtered_matches else all_matches
        
        # Always merge all devices and builds from matching entries
        if len(matches_to_merge) >= 1:
            merged = matches_to_merge[0].copy()
            
            # Merge all devices
            all_devices = []
            for match in matches_to_merge:
                devices = match.get("SupportedDevices", [])
                all_devices.extend(devices)
            # Remove duplicates while preserving order
            seen = set()
            unique_devices = []
            for device in all_devices:
                if device not in seen:
                    seen.add(device)
                    unique_devices.append(device)
            merged["SupportedDevices"] = unique_devices
            
            # Collect all builds
            all_builds = []
            for match in matches_to_merge:
                build = match.get("Build")
                if build and build not in all_builds:
                    all_builds.append(build)
            
            # Sort builds to ensure consistent ordering
            all_builds.sort()
            merged["AllBuilds"] = all_builds if all_builds else []
            
            return merged
        
        # Return None if no matches
        return None
    
    def fetch_xprotect_data(self) -> dict:
        """Fetch XProtect data for macOS."""
        catalog_url = (
            "https://swscan.apple.com/content/catalogs/others/"
            "index-15-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-"
            "mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
        )
        
        try:
            response = requests.get(catalog_url, timeout=30)
            if not response.ok:
                return {}
            
            catalog_content = response.text
            result = {}
            
            # Extract XProtect Config
            config_matches = re.findall(
                r"https.*XProtectPlistConfigData.*?\.pkm", catalog_content
            )
            if config_matches:
                for url in config_matches:
                    version_info = self._extract_xprotect_version(catalog_content, url)
                    if version_info:
                        result["XProtectPlistConfigData"] = version_info
                        break
            
            # Extract XProtect Payloads
            payload_matches = re.findall(
                r"https.*XProtectPayloads.*?\.pkm", catalog_content
            )
            if payload_matches:
                for url in payload_matches:
                    version_info = self._extract_xprotect_version(catalog_content, url)
                    if version_info:
                        result["XProtectPayloads"] = version_info
                        break
            
            return result
            
        except Exception as e:
            print(f"XProtect fetch error: {e}")
            return {}
    
    def _extract_xprotect_version(self, catalog_content: str, pkm_url: str) -> Optional[dict]:
        """Extract XProtect version from PKM."""
        try:
            response = requests.get(pkm_url, timeout=30)
            if not response.ok:
                return None
            
            version_info = {}
            root = ET.fromstring(response.text)
            
            for bundle in root.findall(".//bundle"):
                id_attr = bundle.get("id")
                version = bundle.get("CFBundleShortVersionString")
                
                if id_attr and ("XProtect" in id_attr or "PluginService" in id_attr):
                    version_info[id_attr] = version
            
            # Extract release date
            date_regex = rf"<string>{re.escape(pkm_url)}</string>.*?<date>(.*?)</date>"
            date_match = re.search(date_regex, catalog_content, re.DOTALL)
            
            if date_match:
                release_date = date_match.group(1)
                # Format to ISO
                try:
                    dt = datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%SZ")
                    version_info["ReleaseDate"] = dt.isoformat() + "Z"
                except:
                    version_info["ReleaseDate"] = release_date
            
            return version_info
            
        except Exception as e:
            print(f"XProtect extraction error: {e}")
            return None
    
    def load_uma_data(self) -> dict:
        """Load UMA installation apps data."""
        if not process_uma:
            return {}
        
        catalog_url = (
            "https://swscan.apple.com/content/catalogs/others/"
            "index-15-14-13-12-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-"
            "mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
        )
        
        try:
            response = requests.get(catalog_url, timeout=30)
            if not response.ok:
                return {}
            
            unrefined = process_uma.initial_uma_parse(response.content)
            print(f"Found {len(unrefined)} UMA packages")
            
            ctx = __import__("ssl").create_default_context()
            ctx.load_verify_locations(cafile=certifi.where())
            
            filtered = {}
            for slug, prod in unrefined.items():
                title, build, version = process_uma.get_metadata(ctx, prod.get("dist_url"))
                if title:
                    filtered[slug] = {
                        "title": title,
                        "version": version,
                        "build": build,
                        "apple_slug": slug,
                        "url": prod.get("URL"),
                    }
            
            latest, rest = process_uma.sort_installers(filtered)
            return {
                "LatestUMA": latest,
                "AllPreviousUMA": rest,
            }
            
        except Exception as e:
            print(f"UMA fetch error: {e}")
            return {}
    
    def load_ipsw_data(self) -> dict:
        """Load IPSW data."""
        if not process_ipsw:
            return {}
        
        mesu_url = "https://mesu.apple.com/assets/macos/com_apple_macOSIPSW/com_apple_macOSIPSW.xml"
        
        try:
            import ssl
            import urllib.request
            
            ctx = ssl.create_default_context()
            ctx.load_verify_locations(cafile=certifi.where())
            
            with urllib.request.urlopen(mesu_url, context=ctx) as response:
                mesu_cat = response.read()
            
            import plistlib
            mesu_catalog = plistlib.loads(mesu_cat)
            
            restore_datas = process_ipsw.extract_ipsw_raw(mesu_catalog)
            url, build, version = process_ipsw.process_ipsw_data(restore_datas)
            apple_slug = process_ipsw.process_slug(url)
            
            print(f"Found IPSW: {version} ({build})")
            
            return {
                "LatestMacIPSW": {
                    "macos_ipsw_url": url,
                    "macos_ipsw_build": build,
                    "macos_ipsw_version": version,
                    "macos_ipsw_apple_slug": apple_slug,
                }
            }
            
        except Exception as e:
            print(f"IPSW fetch error: {e}")
            return {}
    
    def load_models_data(self) -> dict:
        """Load Mac models data."""
        models_info = {}
        model_files = [
            ("model_identifier_sequoia.json", "macOS Sequoia 15"),
            ("model_identifier_sonoma.json", "macOS Sonoma 14"),
            ("model_identifier_ventura.json", "macOS Ventura 13"),
            ("model_identifier_monterey.json", "macOS Monterey 12"),
        ]
        
        for filename, os_version in model_files:
            if not Path(filename).exists():
                continue
            
            try:
                with open(filename) as f:
                    data = json.load(f)
                
                for model in data:
                    for identifier, name in model["Identifiers"].items():
                        formatted_os = " ".join(os_version.split()[1:]).strip()
                        if identifier not in models_info:
                            models_info[identifier] = {
                                "MarketingName": name,
                                "SupportedOS": [formatted_os],
                                "OSVersions": [int(formatted_os.split()[-1])],
                            }
                        else:
                            if formatted_os not in models_info[identifier]["SupportedOS"]:
                                models_info[identifier]["SupportedOS"].append(formatted_os)
                                models_info[identifier]["OSVersions"].append(
                                    int(formatted_os.split()[-1])
                                )
            
            except Exception as e:
                print(f"Model load error {filename}: {e}")
        
        return models_info
    
    def create_legacy_feed(self, os_type: str, scraped_data: dict, gdmf_data: GDMFData) -> dict:
        """Create legacy format feed compatible with original build-sofa-feed.py."""
        os_type_lower = os_type.lower()
        
        # Build OSVersions structure
        os_versions = []
        
        if os_type_lower == "macos":
            # Process macOS with full features
            for release_config in self.config["softwareReleases"]:
                if release_config["osType"] != "macOS":
                    continue
                
                os_version_name = release_config["name"]
                
                # Build legacy structure
                os_version_data = {
                    "OSVersion": os_version_name,
                    "Latest": {},
                    "SecurityReleases": [],
                    "SupportedModels": self.load_supported_models(
                        os_version_name.split()[0].lower()
                    ),
                }
                
                # Find latest version from scraped data
                # First, collect all matching versions for this OS version
                matching_releases = []
                target_major = os_version_name.split()[-1]  # e.g., "15" from "Sequoia 15"
                
                for release in scraped_data.get("releases", []):
                    version = release.get("version")
                    if not version:
                        continue
                    if version.startswith(target_major + "."):
                        matching_releases.append(release)
                
                # Sort by version to get the latest
                if matching_releases:
                    from packaging import version as pkg_version
                    matching_releases.sort(
                        key=lambda r: pkg_version.parse(r.get("version", "0")),
                        reverse=True
                    )
                    
                    # Use the latest release
                    release = matching_releases[0]
                    version = release.get("version")
                    if version:
                        # Enrich with GDMF
                        gdmf_match = self._find_gdmf_match("macOS", version, gdmf_data)
                        
                        # Build CVEs dictionary from enriched data
                        # Mark CVEs as exploited based on actively_exploited_cves field
                        all_cves = release.get("cves", [])
                        actively_exploited = release.get("actively_exploited_cves", [])
                        
                        # Create CVEs dict with exploitation status
                        cves_dict = {}
                        for cve in all_cves:
                            cves_dict[cve] = cve in actively_exploited
                        
                        all_builds = gdmf_match.get("AllBuilds", []) if gdmf_match else []
                        # Use first build from AllBuilds if available, otherwise fall back to other sources
                        build = ""
                        if all_builds:
                            build = all_builds[0]
                        elif release.get("build"):
                            build = release.get("build")
                        elif gdmf_match and gdmf_match.get("Build"):
                            build = gdmf_match.get("Build")
                        
                        os_version_data["Latest"] = {
                            "ProductVersion": version,
                            "Build": build,
                            "AllBuilds": all_builds,
                            "ReleaseDate": self._format_date(release.get("release_date", "")),
                            "ExpirationDate": gdmf_match.get("ExpirationDate", "") if gdmf_match else "",
                            "SupportedDevices": gdmf_match.get("SupportedDevices", []) if gdmf_match else [],
                            "SecurityInfo": release.get("url", ""),
                            "CVEs": cves_dict,
                            "ActivelyExploitedCVEs": actively_exploited,
                            "UniqueCVEsCount": len(cves_dict),
                        }
                        
                        # Add ALL matching releases to SecurityReleases
                        for rel in matching_releases:
                            rel_version = rel.get("version")
                            if rel_version:
                                rel_gdmf = self._find_gdmf_match("macOS", rel_version, gdmf_data)
                                
                                # Start with scraped CVEs, then enrich with KEV
                                rel_cves = {cve: False for cve in rel.get("cves", [])}
                                # Enrich with KEV data (doesn't require fetching from Apple)
                                rel_cves = self.kev_fetcher.enrich_cves_with_kev(rel_cves)
                                rel_exploited = [cve for cve, exploited in rel_cves.items() if exploited]
                                
                                rel_all_builds = rel_gdmf.get("AllBuilds", []) if rel_gdmf else []
                                # Use first build from AllBuilds if available
                                rel_build = ""
                                if rel_all_builds:
                                    rel_build = rel_all_builds[0]
                                elif rel.get("build"):
                                    rel_build = rel.get("build")
                                elif rel_gdmf and rel_gdmf.get("Build"):
                                    rel_build = rel_gdmf.get("Build")
                                
                                os_version_data["SecurityReleases"].append({
                                    "UpdateName": rel.get("title", ""),
                                    "ProductName": "macOS",
                                    "ProductVersion": rel_version,
                                    "ReleaseDate": self._format_date(rel.get("release_date", "")),
                                    "ReleaseType": "OS",
                                    "SecurityInfo": rel.get("url", ""),
                                    "SupportedDevices": rel_gdmf.get("SupportedDevices", []) if rel_gdmf else [],
                                    "CVEs": rel_cves,
                                    "ActivelyExploitedCVEs": rel_exploited,
                                    "UniqueCVEsCount": len(rel_cves),
                                    "DaysSincePreviousRelease": 0,  # Will be calculated below
                                })
                        
                        # Calculate days since previous release
                        if os_version_data["SecurityReleases"]:
                            days_map = self._calculate_days_since_previous(os_version_data["SecurityReleases"])
                            for release in os_version_data["SecurityReleases"]:
                                version = release.get("ProductVersion", "")
                                if version in days_map:
                                    release["DaysSincePreviousRelease"] = days_map[version]
                
                os_versions.append(os_version_data)
            
            # Add XProtect data
            xprotect_data = self.fetch_xprotect_data()
            
            # Add installation apps
            installation_apps = self.load_uma_data()
            ipsw_data = self.load_ipsw_data()
            if ipsw_data:
                installation_apps.update(ipsw_data)
            
            # Add models
            models = self.load_models_data()
            
            # Build complete feed
            feed = {
                "OSVersions": os_versions,
                "XProtectPayloads": xprotect_data.get("XProtectPayloads"),
                "XProtectPlistConfigData": xprotect_data.get("XProtectPlistConfigData"),
                "Models": models,
                "InstallationApps": installation_apps,
            }
            
        else:
            # Process iOS/other OS types
            for release_config in self.config["softwareReleases"]:
                # Match the actual OS type (iOS, tvOS, watchOS, visionOS)
                if release_config["osType"] != os_type:
                    continue
                
                os_version_name = release_config["name"]
                
                os_version_data = {
                    "OSVersion": os_version_name,
                    "Latest": {},
                    "SecurityReleases": [],
                }
                
                # Process releases - collect all matching versions
                matching_releases = []
                for release in scraped_data.get("releases", []):
                    version = release.get("version")
                    if not version:
                        continue
                    if version.startswith(os_version_name + "."):
                        matching_releases.append(release)
                
                # Sort by version to get the latest
                if matching_releases:
                    from packaging import version as pkg_version
                    matching_releases.sort(
                        key=lambda r: pkg_version.parse(r.get("version", "0")),
                        reverse=True
                    )
                    
                    # Use the latest release
                    release = matching_releases[0]
                    version = release.get("version")
                    if version:
                        gdmf_match = self._find_gdmf_match(os_type, version, gdmf_data)
                        
                        # Build CVEs dictionary from enriched data
                        # Mark CVEs as exploited based on actively_exploited_cves field
                        all_cves = release.get("cves", [])
                        actively_exploited = release.get("actively_exploited_cves", [])
                        
                        # Create CVEs dict with exploitation status
                        cves_dict = {}
                        for cve in all_cves:
                            cves_dict[cve] = cve in actively_exploited
                        
                        all_builds = gdmf_match.get("AllBuilds", []) if gdmf_match else []
                        # Use first build from AllBuilds if available, otherwise fall back to other sources
                        build = ""
                        if all_builds:
                            build = all_builds[0]
                        elif release.get("build"):
                            build = release.get("build")
                        elif gdmf_match and gdmf_match.get("Build"):
                            build = gdmf_match.get("Build")
                        
                        os_version_data["Latest"] = {
                            "ProductVersion": version,
                            "Build": build,
                            "AllBuilds": all_builds,
                            "ReleaseDate": self._format_date(release.get("release_date", "")),
                            "ExpirationDate": gdmf_match.get("ExpirationDate", "") if gdmf_match else "",
                            "SupportedDevices": gdmf_match.get("SupportedDevices", []) if gdmf_match else [],
                            "SecurityInfo": release.get("url", ""),
                            "CVEs": cves_dict,
                            "ActivelyExploitedCVEs": actively_exploited,
                            "UniqueCVEsCount": len(cves_dict),
                        }
                        
                        # Add all matching releases to SecurityReleases
                        for rel in matching_releases:
                            rel_version = rel.get("version")
                            if rel_version:
                                rel_gdmf = self._find_gdmf_match(os_type, rel_version, gdmf_data)
                                
                                # Start with scraped CVEs, then enrich with KEV
                                rel_cves = {cve: False for cve in rel.get("cves", [])}
                                # Enrich with KEV data (doesn't require fetching from Apple)
                                rel_cves = self.kev_fetcher.enrich_cves_with_kev(rel_cves)
                                rel_exploited = [cve for cve, exploited in rel_cves.items() if exploited]
                                
                                rel_all_builds = rel_gdmf.get("AllBuilds", []) if rel_gdmf else []
                                # Use first build from AllBuilds if available
                                rel_build = ""
                                if rel_all_builds:
                                    rel_build = rel_all_builds[0]
                                elif rel.get("build"):
                                    rel_build = rel.get("build")
                                elif rel_gdmf and rel_gdmf.get("Build"):
                                    rel_build = rel_gdmf.get("Build")
                                
                                os_version_data["SecurityReleases"].append({
                                    "UpdateName": rel.get("title", ""),
                                    "ProductName": os_type,
                                    "ProductVersion": rel_version,
                                    "ReleaseDate": self._format_date(rel.get("release_date", "")),
                                    "ReleaseType": "OS",
                                    "SecurityInfo": rel.get("url", ""),
                                    "SupportedDevices": rel_gdmf.get("SupportedDevices", []) if rel_gdmf else [],
                                    "CVEs": rel_cves,
                                    "ActivelyExploitedCVEs": rel_exploited,
                                    "UniqueCVEsCount": len(rel_cves),
                                    "DaysSincePreviousRelease": 0,  # Will be calculated below
                                })
                        
                        # Calculate days since previous release
                        if os_version_data["SecurityReleases"]:
                            days_map = self._calculate_days_since_previous(os_version_data["SecurityReleases"])
                            for release in os_version_data["SecurityReleases"]:
                                version = release.get("ProductVersion", "")
                                if version in days_map:
                                    release["DaysSincePreviousRelease"] = days_map[version]
                
                os_versions.append(os_version_data)
            
            feed = {"OSVersions": os_versions}
        
        # Add update hash
        update_hash = self._compute_hash(feed)
        feed = {"UpdateHash": update_hash, **feed}
        
        return feed
    
    def load_supported_models(self, os_name: str) -> list:
        """Load supported models for OS."""
        model_file = f"model_identifier_{os_name}.json"
        
        if not Path(model_file).exists():
            return []
        
        try:
            with open(model_file) as f:
                data = json.load(f)
            
            models = []
            for entry in data:
                models.append({
                    "Model": entry["Model"],
                    "URL": entry["URL"],
                    "Identifiers": entry["Identifiers"],
                })
            
            return models
            
        except Exception as e:
            print(f"Model load error: {e}")
            return []
    
    def _fetch_cves_cached(self, url: str) -> Dict[str, bool]:
        """Fetch CVEs with caching to avoid repeated fetches."""
        # Check cache
        cache_file = self.cache_dir / "cve_details.json"
        cve_cache = {}
        
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    cve_cache = json.load(f)
            except:
                pass
        
        # Use cache if available
        if url in cve_cache:
            return cve_cache[url]
        
        # Fetch if not cached
        result = self._fetch_cves(url)
        
        # Update cache
        cve_cache[url] = result
        try:
            with open(cache_file, "w") as f:
                json.dump(cve_cache, f, indent=2)
        except:
            pass
        
        return result
    
    def _fetch_cves(self, url: str) -> Dict[str, bool]:
        """Fetch CVEs from security page and determine exploitation status."""
        try:
            response = requests.get(url, timeout=30)
            if not response.ok:
                return {}
            
            from bs4 import BeautifulSoup, NavigableString
            soup = BeautifulSoup(response.text, "html.parser")
            
            if "no published CVE entries" in response.text:
                return {}
            
            # Pattern for actively exploited
            exploited_pattern = re.compile(
                r"Impact:.*Apple is aware.*may have been.*exploited", re.DOTALL
            )
            
            cves_info = {}
            text_blocks = []
            
            for child in soup.recursiveChildGenerator():
                if isinstance(child, NavigableString) and child.strip():
                    text_blocks.append(child.strip())
                    
                    # Find CVEs
                    cve_ids = re.findall(r"\bCVE-\d{4,}-\d{4,}\b", child)
                    for cve_id in cve_ids:
                        if cve_id not in cves_info:
                            recent_text = " ".join(text_blocks[-5:])
                            cves_info[cve_id] = bool(exploited_pattern.search(recent_text))
                    
                    # Keep recent context
                    if len(text_blocks) > 10:
                        text_blocks.pop(0)
            
            # Enrich with CISA KEV data
            cves_info = self.kev_fetcher.enrich_cves_with_kev(cves_info)
            
            return cves_info
            
        except Exception as e:
            print(f"Error fetching CVEs from {url}: {e}")
            return {}
    
    def _format_date(self, date_str: str) -> str:
        """Format date to ISO format."""
        if not date_str or date_str == "Unknown":
            return date_str
        
        if "T" in date_str and date_str.endswith("Z"):
            return date_str
        
        # Try parsing various formats
        formats = [
            "%B %d, %Y",  # December 11, 2024
            "%d %b %Y",   # 11 Dec 2024
            "%Y-%m-%d",   # 2024-12-11
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.replace("Released ", ""), fmt)
                return dt.isoformat() + "Z"
            except:
                continue
        
        return date_str
    
    def _calculate_days_since_previous(self, releases: list) -> dict:
        """Calculate days between consecutive releases."""
        days_map = {}
        
        # Parse dates and sort
        dated_releases = []
        for release in releases:
            date_str = release.get("ReleaseDate", "")
            if not date_str or date_str == "Unknown":
                continue
                
            # Parse the date
            parsed_date = None
            if "T" in date_str and date_str.endswith("Z"):
                try:
                    parsed_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except:
                    pass
            else:
                for fmt in ["%B %d, %Y", "%d %b %Y", "%Y-%m-%d"]:
                    try:
                        parsed_date = datetime.strptime(date_str.replace("Released ", ""), fmt)
                        parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                        break
                    except:
                        continue
            
            if parsed_date:
                dated_releases.append((release, parsed_date))
        
        # Sort by date descending (newest first)
        dated_releases.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate days between consecutive releases
        for i in range(len(dated_releases)):
            release, date = dated_releases[i]
            
            if i < len(dated_releases) - 1:
                # Calculate days since next older release
                _, prev_date = dated_releases[i + 1]
                days = (date - prev_date).days
                days_map[release.get("ProductVersion", "")] = days
            else:
                # Oldest release has 0 days
                days_map[release.get("ProductVersion", "")] = 0
        
        return days_map
    
    def write_timestamp(self, os_type: str, hash_value: str):
        """Write timestamp file."""
        timestamp_file = "timestamp.json"
        
        timestamp_data = {}
        if Path(timestamp_file).exists():
            try:
                with open(timestamp_file) as f:
                    timestamp_data = json.load(f)
            except:
                pass
        
        timestamp_data[os_type] = {
            "LastCheck": datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z",
            "UpdateHash": hash_value,
        }
        
        with open(timestamp_file, "w") as f:
            json.dump(timestamp_data, f, indent=4)
    
    async def build_all_feeds(self):
        """Build all feeds."""
        # Run new scraper
        await self.run_new_scraper()
        
        # Load GDMF data
        gdmf_data = self.fetch_gdmf_data()
        if not gdmf_data:
            print("Warning: No GDMF data available")
            gdmf_data = GDMFData(PublicAssetSets={}, AssetSets={})
        
        # Process each OS type
        os_types = ["macOS", "iOS", "tvOS", "watchOS", "visionOS"]
        
        for os_type in os_types:
            os_lower = os_type.lower()
            
            # Try enriched first, then fall back to unenriched
            scraped_file = self.data_dir / f"{os_lower}.json"
            if not scraped_file.exists():
                # Try unenriched location
                scraped_file = self.data_dir.parent / f"{os_lower}.json"
                if not scraped_file.exists():
                    print(f"No scraped data for {os_type}")
                    continue
                print(f"Using unenriched data for {os_type} from {scraped_file}")
            
            print(f"\nProcessing {os_type}...")
            
            # Load scraped data
            with open(scraped_file) as f:
                scraped_data = json.load(f)
            
            # Enrich with GDMF
            enriched_data = self.enrich_with_gdmf(os_type, scraped_data, gdmf_data)
            
            # Create legacy format feed
            legacy_feed = self.create_legacy_feed(os_type, enriched_data, gdmf_data)
            
            # Write main feed file
            feed_file = f"{os_lower}_data_feed.json"
            with open(feed_file, "w") as f:
                json.dump(legacy_feed, f, indent=4, ensure_ascii=False)
            print(f"Written {feed_file}")
            
            # Write to v1/ directory
            v1_file = self.v1_dir / feed_file
            with open(v1_file, "w") as f:
                json.dump(legacy_feed, f, indent=4, ensure_ascii=False)
            print(f"Written {v1_file}")
            
            # Update timestamp
            self.write_timestamp(os_type, legacy_feed["UpdateHash"])
        
        # Copy timestamp to v1/
        if Path("timestamp.json").exists():
            import shutil
            shutil.copy("timestamp.json", self.v1_dir / "timestamp.json")
        
        print("\nFeed generation complete!")


async def main():
    """Main entry point."""
    builder = CompleteFeedBuilder()
    await builder.build_all_feeds()


if __name__ == "__main__":
    asyncio.run(main())