#!/usr/bin/env python3
"""
Device consolidation functions for SOFA feeds.
Handles merging and consolidating device information from various sources.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DeviceConsolidator:
    """Consolidate and manage device information."""
    
    def __init__(self, cache_dir: Path = Path(__file__).resolve().parent.parent.parent / "data" / "cache"):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.device_cache = {}
        self.load_device_mappings()
        
    def load_device_mappings(self):
        """Load device mapping files if available."""
        mapping_files = [
            "device_mappings.json",
            "model_identifiers.json",
            "supported_devices.json"
        ]
        
        for filename in mapping_files:
            filepath = self.cache_dir / filename
            if filepath.exists():
                try:
                    with open(filepath) as f:
                        data = json.load(f)
                        self.device_cache[filename] = data
                        logger.info(f"Loaded device mappings from {filename}")
                except Exception as e:
                    logger.warning(f"Error loading {filename}: {e}")
    
    def merge_device_lists(self, *device_lists: List[str]) -> List[str]:
        """
        Merge multiple device lists, removing duplicates while preserving order.
        
        Args:
            *device_lists: Variable number of device lists
            
        Returns:
            Merged list with duplicates removed
        """
        seen = set()
        merged = []
        
        for device_list in device_lists:
            if not device_list:
                continue
                
            for device in device_list:
                if device and device not in seen:
                    seen.add(device)
                    merged.append(device)
        
        return merged
    
    def extract_device_versions(self, devices: List[str]) -> Dict[str, Set[str]]:
        """
        Extract version information from device names.
        
        Args:
            devices: List of device names
            
        Returns:
            Dictionary mapping device types to version sets
        """
        device_versions = {}
        
        for device in devices:
            # Extract device type and version
            # Examples: "iPhone15,2", "iPad14,1", "Mac14,2"
            if any(prefix in device for prefix in ["iPhone", "iPad", "Mac", "Watch", "AudioAccessory"]):
                # Extract base and version
                for prefix in ["iPhone", "iPad", "Mac", "Watch", "AudioAccessory"]:
                    if device.startswith(prefix):
                        base = prefix
                        version = device[len(prefix):]
                        
                        if base not in device_versions:
                            device_versions[base] = set()
                        device_versions[base].add(version)
                        break
        
        return device_versions
    
    def normalize_device_name(self, device: str) -> str:
        """
        Normalize device name for consistency.
        
        Args:
            device: Device name to normalize
            
        Returns:
            Normalized device name
        """
        # Remove extra spaces
        device = " ".join(device.split())
        
        # Standardize common variations
        replacements = {
            "iPhone ": "iPhone",
            "iPad ": "iPad",
            "Mac ": "Mac",
            "Apple Watch": "Watch",
            "Apple TV": "AppleTV",
            "HomePod ": "HomePod",
        }
        
        for old, new in replacements.items():
            device = device.replace(old, new)
        
        return device
    
    def inject_supported_devices(self, feed_data: dict, gdmf_data: dict) -> dict:
        """
        Inject supported devices from GDMF into feed data.
        
        Args:
            feed_data: Feed data to update
            gdmf_data: GDMF data with device information
            
        Returns:
            Updated feed data with device information
        """
        # Process each OS version
        for os_version in feed_data.get("OSVersions", []):
            version = os_version.get("Latest", {}).get("ProductVersion")
            if not version:
                continue
            
            # Find matching GDMF entry
            gdmf_devices = self._find_gdmf_devices(version, gdmf_data)
            if gdmf_devices:
                # Update Latest
                if "Latest" in os_version:
                    current_devices = os_version["Latest"].get("SupportedDevices", [])
                    merged = self.merge_device_lists(current_devices, gdmf_devices)
                    os_version["Latest"]["SupportedDevices"] = merged
                
                # Update SecurityReleases
                for release in os_version.get("SecurityReleases", []):
                    if release.get("ProductVersion") == version:
                        current_devices = release.get("SupportedDevices", [])
                        merged = self.merge_device_lists(current_devices, gdmf_devices)
                        release["SupportedDevices"] = merged
        
        return feed_data
    
    def _find_gdmf_devices(self, version: str, gdmf_data: dict) -> List[str]:
        """Find supported devices for a version from GDMF data."""
        devices = []
        
        # Search in PublicAssetSets and AssetSets
        for asset_set_key in ["PublicAssetSets", "AssetSets"]:
            asset_sets = gdmf_data.get(asset_set_key, {})
            
            for os_type, assets in asset_sets.items():
                if not isinstance(assets, list):
                    continue
                    
                for asset in assets:
                    if isinstance(asset, dict) and asset.get("ProductVersion") == version:
                        asset_devices = asset.get("SupportedDevices", [])
                        devices.extend(asset_devices)
        
        return list(set(devices))  # Remove duplicates
    
    def layer_supported_devices(self, os_versions: List[dict]) -> List[dict]:
        """
        Layer supported devices across OS versions.
        If a version doesn't have devices, inherit from previous version.
        
        Args:
            os_versions: List of OS version data
            
        Returns:
            Updated OS versions with layered device support
        """
        previous_devices = []
        
        for os_version in os_versions:
            # Check Latest
            latest = os_version.get("Latest", {})
            if latest:
                devices = latest.get("SupportedDevices", [])
                if not devices and previous_devices:
                    latest["SupportedDevices"] = previous_devices
                elif devices:
                    previous_devices = devices
            
            # Process SecurityReleases in reverse chronological order
            releases = os_version.get("SecurityReleases", [])
            for release in releases:
                devices = release.get("SupportedDevices", [])
                if not devices and previous_devices:
                    release["SupportedDevices"] = previous_devices
                elif devices:
                    previous_devices = devices
        
        return os_versions
    
    def update_supported_devices_in_feed(self, feed_path: Path) -> bool:
        """
        Update supported devices in an existing feed file.
        
        Args:
            feed_path: Path to the feed file
            
        Returns:
            True if successful, False otherwise
        """
        if not feed_path.exists():
            logger.error(f"Feed file not found: {feed_path}")
            return False
        
        try:
            with open(feed_path) as f:
                feed_data = json.load(f)
            
            # Layer devices
            os_versions = feed_data.get("OSVersions", [])
            if os_versions:
                feed_data["OSVersions"] = self.layer_supported_devices(os_versions)
            
            # Write back
            with open(feed_path, "w") as f:
                json.dump(feed_data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Updated supported devices in {feed_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating {feed_path}: {e}")
            return False
    
    def consolidate_all_devices(self, feed_dir: Path = Path(".")) -> Dict[str, List[str]]:
        """
        Consolidate all unique devices across all feeds.
        
        Args:
            feed_dir: Directory containing feed files
            
        Returns:
            Dictionary mapping OS types to consolidated device lists
        """
        all_devices = {}
        
        feed_files = [
            "macos_data_feed.json",
            "ios_data_feed.json",
            "tvos_data_feed.json",
            "watchos_data_feed.json",
            "visionos_data_feed.json"
        ]
        
        for filename in feed_files:
            feed_path = feed_dir / filename
            if not feed_path.exists():
                continue
            
            os_type = filename.split("_")[0].upper()
            if os_type == "MACOS":
                os_type = "macOS"
            elif os_type == "IOS":
                os_type = "iOS"
            elif os_type == "TVOS":
                os_type = "tvOS"
            elif os_type == "WATCHOS":
                os_type = "watchOS"
            elif os_type == "VISIONOS":
                os_type = "visionOS"
            
            try:
                with open(feed_path) as f:
                    feed_data = json.load(f)
                
                devices = set()
                
                # Collect from all sources
                for os_version in feed_data.get("OSVersions", []):
                    # From Latest
                    latest_devices = os_version.get("Latest", {}).get("SupportedDevices", [])
                    devices.update(latest_devices)
                    
                    # From SecurityReleases
                    for release in os_version.get("SecurityReleases", []):
                        release_devices = release.get("SupportedDevices", [])
                        devices.update(release_devices)
                
                all_devices[os_type] = sorted(list(devices))
                logger.info(f"Found {len(devices)} unique devices for {os_type}")
                
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
        
        return all_devices


def main():
    """Test device consolidation."""
    consolidator = DeviceConsolidator()
    
    # Test merging
    list1 = ["iPhone15,2", "iPhone15,3", "iPad14,1"]
    list2 = ["iPhone15,3", "iPhone14,2", "Mac14,2"]
    merged = consolidator.merge_device_lists(list1, list2)
    print(f"Merged devices: {merged}")
    
    # Test extraction
    versions = consolidator.extract_device_versions(merged)
    print(f"Device versions: {versions}")
    
    # Consolidate all devices
    all_devices = consolidator.consolidate_all_devices()
    for os_type, devices in all_devices.items():
        print(f"\n{os_type}: {len(devices)} devices")
        if devices:
            print(f"  First 5: {devices[:5]}")


if __name__ == "__main__":
    main()