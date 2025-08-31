#!/usr/bin/env python3
"""
Generate manifest.json for SOFA data feeds
Provides metadata about data freshness, sizes, and pipeline status
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()[:16]  # First 16 chars is enough

def get_feed_info(feed_path: Path) -> Dict[str, Any]:
    """Get metadata about a feed file"""
    if not feed_path.exists():
        return {
            "status": "missing",
            "lastUpdate": None,
            "size": 0,
            "entries": 0
        }
    
    stat = feed_path.stat()
    
    # Try to parse JSON to get entry count
    entries = 0
    try:
        with open(feed_path) as f:
            data = json.load(f)
            # Count entries based on feed structure
            if isinstance(data, list):
                entries = len(data)
            elif isinstance(data, dict):
                if "OSVersions" in data:  # v2 feed format
                    entries = sum(len(v.get("SecurityReleases", [])) 
                                for v in data.get("OSVersions", []))
                elif "Updates" in data:  # v1 feed format
                    entries = len(data.get("Updates", []))
    except:
        pass
    
    return {
        "status": "available",
        "lastUpdate": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
        "size": stat.st_size,
        "hash": calculate_file_hash(feed_path),
        "entries": entries
    }

def generate_manifest(base_dir: Path = Path(".")) -> Dict[str, Any]:
    """Generate complete manifest for SOFA data"""
    
    data_dir = base_dir / "data"
    feeds_dir = data_dir / "feeds"
    resources_dir = data_dir / "resources"
    
    manifest = {
        "version": "2.0",
        "generated": datetime.utcnow().isoformat() + "Z",
        "feeds": {
            "v2": {},
            "v1": {}
        },
        "resources": {},
        "pipeline": {
            "lastRun": datetime.utcnow().isoformat() + "Z",
            "stages": [],
            "status": "success"
        },
        "health": {
            "staleness": {},
            "errors": []
        }
    }
    
    # Check v2 feeds
    v2_dir = feeds_dir / "v2"
    if v2_dir.exists():
        for platform in ["macos", "ios", "tvos", "watchos", "visionos", "safari"]:
            feed_file = v2_dir / f"{platform}_data_feed.json"
            manifest["feeds"]["v2"][platform] = get_feed_info(feed_file)
            
            # Check staleness (older than 24 hours)
            if feed_file.exists():
                age_hours = (datetime.now() - datetime.fromtimestamp(feed_file.stat().st_mtime)).total_seconds() / 3600
                if age_hours > 24:
                    manifest["health"]["staleness"][platform] = f"{age_hours:.1f} hours old"
    
    # Check v1 feeds
    v1_dir = feeds_dir / "v1"
    if v1_dir.exists():
        for platform in ["macos", "ios", "tvos", "watchos", "visionos", "safari"]:
            feed_file = v1_dir / f"{platform}_data_feed.json"
            manifest["feeds"]["v1"][platform] = get_feed_info(feed_file)
    
    # Check key resources
    if resources_dir.exists():
        for resource in ["kev_catalog.json", "gdmf_cached.json", "apple_security_releases.json"]:
            resource_file = resources_dir / resource
            if resource_file.exists():
                manifest["resources"][resource.replace("_", "-").replace(".json", "")] = {
                    "available": True,
                    "lastUpdate": datetime.fromtimestamp(resource_file.stat().st_mtime).isoformat() + "Z",
                    "size": resource_file.stat().st_size
                }
    
    # Add metadata file info
    metadata_file = feeds_dir / "v2" / "feed_metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
                manifest["feeds"]["metadata"] = metadata
        except:
            pass
    
    # Calculate overall health score
    total_feeds = len(manifest["feeds"]["v2"]) + len(manifest["feeds"]["v1"])
    available_feeds = sum(1 for f in manifest["feeds"]["v2"].values() if f.get("status") == "available")
    available_feeds += sum(1 for f in manifest["feeds"]["v1"].values() if f.get("status") == "available")
    
    manifest["health"]["score"] = round((available_feeds / max(total_feeds, 1)) * 100)
    manifest["health"]["status"] = "healthy" if manifest["health"]["score"] > 80 else "degraded"
    
    return manifest

def save_manifest(manifest: Dict[str, Any], output_path: Path):
    """Save manifest to file"""
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    
    base_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    output_path = base_dir / "data" / "manifest.json"
    
    print(f"Generating manifest from {base_dir}")
    manifest = generate_manifest(base_dir)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_manifest(manifest, output_path)
    
    print(f"✅ Manifest saved to {output_path}")
    print(f"📊 Health: {manifest['health']['status']} ({manifest['health']['score']}%)")
    print(f"📦 Feeds: {len([f for f in manifest['feeds']['v2'].values() if f.get('status') == 'available'])}/6 v2 available")