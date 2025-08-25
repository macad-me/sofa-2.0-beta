#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set

import requests
from bs4 import BeautifulSoup, Tag, NavigableString
from dateutil import parser as dateparser

APPLE_RELEASES_URL = "https://developer.apple.com/news/releases/"
OS_PLATFORMS = ("iOS", "iPadOS", "macOS", "tvOS", "watchOS", "visionOS")

TITLE_RE = re.compile(
    r"^(?P<platform>iOS|iPadOS|macOS|tvOS|watchOS|visionOS)\s+"
    r"(?P<version>[^\(]+?)\s*"
    r"\((?P<build>[^)]+)\)\s*$"
)

def _ua(repo_url: str | None) -> str:
    base = "DeclarativeIT-FeedBot/1.0 (+https://sofafeed.macadmins.io)"
    return f"{base} {repo_url}".strip() if repo_url else base

def within_days(date_str: str, days: int) -> bool:
    dt = dateparser.parse(date_str)
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return dt >= cutoff

def find_date_for_card(header: Tag) -> Optional[str]:
    # First try the new structure: look for date in parent section
    parent = header.parent
    if parent:
        date_elem = parent.find('p', class_='lighter article-date')
        if date_elem:
            return date_elem.get_text(strip=True)

    # Fallback to original logic for backwards compatibility
    node = header.next_sibling
    while node:
        text = ""
        if isinstance(node, NavigableString):
            text = str(node).strip()
        elif isinstance(node, Tag):
            text = node.get_text(strip=True)
        if text:
            try:
                dateparser.parse(text, fuzzy=False)
                return text
            except Exception:
                pass
        node = node.next_sibling
    return None

def find_links_for_card(header: Tag) -> Dict[str, str]:
    links: Dict[str, str] = {}
    node = header
    for _ in range(80):
        if node is None:
            break
        node = node.next_sibling
        if not node:
            break
        if isinstance(node, Tag):
            if node.name in ("a", "h2", "h3"):
                t = node.get_text(strip=True)
                if TITLE_RE.search(t):
                    break
            for a in node.find_all("a", href=True):
                label = a.get_text(strip=True).lower()
                href = requests.compat.urljoin(APPLE_RELEASES_URL, a["href"])
                if "release notes" in label and "release_notes_url" not in links:
                    links["release_notes_url"] = href
                elif "view downloads" in label and "downloads_url" not in links:
                    links["downloads_url"] = href
    return links

def scrape_releases(days: int, repo_url: Optional[str]) -> Dict[str, Any]:
    headers = {"User-Agent": _ua(repo_url)}
    r = requests.get(APPLE_RELEASES_URL, headers=headers, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    items: List[Dict[str, Any]] = []
    for a in soup.find_all("a"):
        title = a.get_text(strip=True)
        m = TITLE_RE.match(title)
        if not m:
            continue
        platform = m.group("platform")
        if platform not in OS_PLATFORMS:
            continue
        date_str = find_date_for_card(a)
        if not date_str or not within_days(date_str, days):
            continue
        version_raw = m.group("version").strip()
        build = m.group("build").strip()
        links = find_links_for_card(a)

        items.append({
            # keep a stable key order
            "platform": platform,
            "title": title,
            "version": version_raw,
            "build": build,
            "released": dateparser.parse(date_str).date().isoformat(),
            "release_notes_url": links.get("release_notes_url"),
            "downloads_url": links.get("downloads_url"),
            "source_card_url": APPLE_RELEASES_URL,
        })

    # Sort newest first by date, then platform + version to stabilize output
    items.sort(key=lambda x: (x["released"], x["platform"], x["version"]), reverse=True)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": APPLE_RELEASES_URL,
        "window_days": days,
        "items": items,
    }

def write_json_stable(obj: Dict[str, Any], path: str) -> str:
    # separators ensure consistent whitespace; sort_keys locks map order at top-level
    txt = json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True, separators=(", ", ": "))
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)

    # Calculate and return hash
    return sha256_file(path)

def calculate_content_hash(obj: Dict[str, Any]) -> str:
    """Calculate hash of JSON content excluding timestamp fields that change on every run."""
    # Create a copy and remove fields that change on every run
    temp_obj = obj.copy()

    # Remove timestamp fields that shouldn't affect the hash
    temp_obj.pop("generated_at", None)
    temp_obj.pop("UpdateHash", None)  # Remove existing hash if present

    # Convert to stable JSON string for hashing
    json_str = json.dumps(temp_obj, indent=2, ensure_ascii=False, sort_keys=True, separators=(", ", ": "))

    # Calculate hash of the content
    h = hashlib.sha256()
    h.update(json_str.encode('utf-8'))
    return h.hexdigest()

def write_json_with_hash(obj: Dict[str, Any], path: str, hash_path: str) -> str:
    """Write JSON file and include the hash both in the file and in a separate hash file."""
    # Calculate hash of content (excluding generated_at)
    content_hash = calculate_content_hash(obj)

    # Add hash to the object and write
    temp_obj = obj.copy()
    temp_obj["UpdateHash"] = content_hash
    write_json_stable(temp_obj, path)

    # Write separate hash file
    with open(hash_path, "w", encoding="utf-8") as f:
        f.write(content_hash + "\n")

    return content_hash

def create_timestamp_file(feed_hash: str, history_hash: str, timestamp_path: str) -> None:
    """Create a timestamp file similar to SOFA's format."""
    timestamp_data = {
        "AppleBetaOSFeed": {
            "LastCheck": datetime.now(timezone.utc).isoformat().replace("+00:00", "+00:00Z"),
            "UpdateHash": feed_hash
        },
        "AppleBetaOSHistory": {
            "LastCheck": datetime.now(timezone.utc).isoformat().replace("+00:00", "+00:00Z"),
            "UpdateHash": history_hash
        }
    }

    write_json_stable(timestamp_data, timestamp_path)
    print(f"Wrote timestamp file: {timestamp_path}")

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_history(history_path: str) -> Dict[str, Any]:
    """Load existing history file or create empty structure."""
    if not os.path.exists(history_path):
        return {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "source": APPLE_RELEASES_URL,
            "description": "Historical archive of Apple OS releases including betas removed from current feed",
            "items": []
        }

    with open(history_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # Remove any existing hash fields to avoid conflicts
        if "file_hash" in data:
            del data["file_hash"]
        if "UpdateHash" in data:
            del data["UpdateHash"]
        return data

def create_item_key(item: Dict[str, Any]) -> str:
    """Create a unique key for an item to detect duplicates."""
    return f"{item['platform']}:{item['version']}:{item['build']}"

def merge_into_history(current_items: List[Dict[str, Any]], history_path: str) -> Dict[str, Any]:
    """Merge current items into history, preserving all unique releases."""
    history = load_history(history_path)

    # Create a set of existing items for fast lookup
    existing_keys: Set[str] = set()
    for item in history["items"]:
        existing_keys.add(create_item_key(item))

    # Add new items that don't exist in history
    new_items = []
    for item in current_items:
        key = create_item_key(item)
        if key not in existing_keys:
            new_items.append(item)
            existing_keys.add(key)

    if new_items:
        # Add new items to history
        history["items"].extend(new_items)
        # Sort by release date (newest first), then by platform and version for stability
        history["items"].sort(key=lambda x: (x["released"], x["platform"], x["version"]), reverse=True)
        history["last_updated"] = datetime.now(timezone.utc).isoformat()

        print(f"Added {len(new_items)} new items to history")
        for item in new_items:
            print(f"  + {item['platform']} {item['version']} ({item['build']}) - {item['released']}")
    else:
        print("No new items to add to history")

    return history

def main() -> int:
    ap = argparse.ArgumentParser(description="Scrape Apple OS releases and maintain historical archive")
    ap.add_argument("--out", default="v1/apple-beta-os-feed.json",
                    help="Output path for current feed (default: v1/apple-beta-os-feed.json)")
    ap.add_argument("--out-hash", default="v1/apple-beta-os-feed.sha256",
                    help="Output path for current feed hash (default: v1/apple-beta-os-feed.sha256)")
    ap.add_argument("--history", default="v1/apple-beta-os-history.json",
                    help="Output path for historical archive (default: v1/apple-beta-os-history.json)")
    ap.add_argument("--history-hash", default="v1/apple-beta-os-history.sha256",
                    help="Output path for historical archive hash (default: v1/apple-beta-os-history.sha256)")
    ap.add_argument("--timestamp", default="v1/timestamp.json",
                    help="Output path for timestamp file (default: v1/timestamp.json)")
    ap.add_argument("--days", type=int, default=90,
                    help="Number of days to include in current feed (default: 90)")
    ap.add_argument("--repo-url", default="",
                    help="Repository URL for user agent")
    ap.add_argument("--no-history", action="store_true",
                    help="Skip updating historical archive")
    args = ap.parse_args()

    # Scrape current releases
    data = scrape_releases(days=args.days, repo_url=args.repo_url or None)

    # Write current feed with hash
    digest = write_json_with_hash(data, args.out, args.out_hash)
    print(f"Wrote current feed: {args.out} ({digest})")

    # Update historical archive unless disabled
    if not args.no_history:
        history = merge_into_history(data["items"], args.history)
        history_digest = write_json_with_hash(history, args.history, args.history_hash)
        print(f"Wrote historical archive: {args.history} ({history_digest})")
        print(f"Historical archive contains {len(history['items'])} total items")

        # Create timestamp file
        create_timestamp_file(digest, history_digest, args.timestamp)
    else:
        # Create timestamp file with only feed hash
        create_timestamp_file(digest, "", args.timestamp)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
