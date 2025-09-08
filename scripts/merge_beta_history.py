#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich>=13.7.0",
# ]
# ///
"""
Merge historical beta data chronologically while avoiding duplicates.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from rich.console import Console

console = Console()


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"❌ File not found: {file_path}", style="red")
        return {}
    except json.JSONDecodeError as e:
        console.print(f"❌ JSON decode error in {file_path}: {e}", style="red")
        return {}


def create_item_key(item: Dict[str, Any]) -> str:
    """Create a unique key for an item based on platform, version, build"""
    platform = item.get("platform", "")
    version = item.get("version", "")
    build = item.get("build", "")
    return f"{platform}-{version}-{build}"


def merge_beta_history(current_file: Path, source_file: Path, output_file: Path) -> bool:
    """Merge beta history files chronologically"""
    
    console.print("🔄 Loading current beta history...", style="cyan")
    current_data = load_json(current_file)
    
    console.print("🔄 Loading source beta history...", style="cyan")
    source_data = load_json(source_file)
    
    if not current_data or not source_data:
        console.print("❌ Failed to load one or both files", style="red")
        return False
    
    # Get items from both files
    current_items = current_data.get("items", [])
    source_items = source_data.get("items", [])
    
    console.print(f"📊 Current file has {len(current_items)} items", style="yellow")
    console.print(f"📊 Source file has {len(source_items)} items", style="yellow")
    
    # Create a set of existing item keys to avoid duplicates
    existing_keys = set()
    merged_items = []
    
    # Add all current items first (they are likely newer)
    for item in current_items:
        key = create_item_key(item)
        existing_keys.add(key)
        merged_items.append(item)
    
    # Add items from source that don't already exist
    new_items_added = 0
    for item in source_items:
        key = create_item_key(item)
        if key not in existing_keys:
            existing_keys.add(key)
            merged_items.append(item)
            new_items_added += 1
    
    console.print(f"✅ Added {new_items_added} new historical items", style="green")
    
    # Sort all items by release date (newest first)
    def parse_date(date_str: str) -> datetime:
        """Parse date string, handle various formats"""
        try:
            # Try ISO format first
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            # Try simple date format
            return datetime.fromisoformat(date_str)
        except:
            # Fallback to a very old date if parsing fails
            return datetime(1900, 1, 1)
    
    merged_items.sort(key=lambda x: parse_date(x.get("released", "1900-01-01")), reverse=True)
    
    # Create the merged data structure
    merged_data = {
        "UpdateHash": current_data.get("UpdateHash", "merged-data"),
        "created_at": datetime.now().isoformat() + "Z",
        "description": "Historical archive of Apple OS releases including betas removed from current feed",
        "items": merged_items,
        "last_updated": datetime.now().isoformat() + "Z"
    }
    
    # Add source info if it exists in either file
    if "source" in current_data or "source" in source_data:
        merged_data["source"] = current_data.get("source", source_data.get("source", ""))
    
    # Write merged data
    console.print(f"💾 Writing merged data to {output_file}...", style="cyan")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        console.print(f"❌ Failed to write output file: {e}", style="red")
        return False
    
    console.print(f"✅ Successfully merged {len(merged_items)} total items", style="green")
    console.print(f"   📅 Date range: {merged_items[-1].get('released', 'Unknown')} to {merged_items[0].get('released', 'Unknown')}", style="cyan")
    
    # Show summary by platform
    platform_counts = {}
    for item in merged_items:
        platform = item.get("platform", "Unknown")
        platform_counts[platform] = platform_counts.get(platform, 0) + 1
    
    console.print("📊 Items by platform:", style="bold cyan")
    for platform, count in sorted(platform_counts.items()):
        console.print(f"   {platform}: {count}", style="cyan")
    
    return True


def main():
    """Main function"""
    console.print("🍎 Apple Beta History Merger", style="bold blue")
    console.print("Merging historical beta data chronologically...\n", style="dim")
    
    # File paths
    current_file = Path("data/resources/apple_beta_os_history.json")
    source_file = Path("/Users/henry/Projects/Community/sofa-2.0-starter/docs/public/data/resources/apple_beta_os_history.json")
    output_file = Path("data/resources/apple_beta_os_history.json")
    
    # Verify files exist
    if not current_file.exists():
        console.print(f"❌ Current file not found: {current_file}", style="red")
        return 1
    
    if not source_file.exists():
        console.print(f"❌ Source file not found: {source_file}", style="red")
        return 1
    
    # Create backup
    backup_file = current_file.with_suffix('.json.backup')
    console.print(f"💾 Creating backup: {backup_file}", style="yellow")
    try:
        import shutil
        shutil.copy2(current_file, backup_file)
    except Exception as e:
        console.print(f"⚠️ Failed to create backup: {e}", style="yellow")
    
    # Perform merge
    if merge_beta_history(current_file, source_file, output_file):
        console.print("\n🎉 Merge completed successfully!", style="bold green")
        return 0
    else:
        console.print("\n💥 Merge failed!", style="bold red")
        return 1


if __name__ == "__main__":
    exit(main())