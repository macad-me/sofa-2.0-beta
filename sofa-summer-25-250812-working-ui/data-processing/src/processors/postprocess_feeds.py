#!/usr/bin/env python3
"""
Post-process per-OS feeds using Pydantic v2 models.

Pipeline responsibilities:
1) Validate ./data/*.json produced by build_feeds.py.
2) Normalize timestamps to Zulu; parse fuzzy "Released/Veröffentlicht ..." date hints.
3) Sort releases (newest first), compute days_since_previous.
4) Apply pinning (by version and/or build).
5) Apply retention policy:
   - macOS → keep all (default)
   - Others → keep last N majors (default N=2), configurable in config/pinned.json
   - Optional: allow pins to survive outside retention window.
6) Emit:
   - ./data/enriched/<os>.json  (validated + enriched + filtered)
   - ./data/combined.json       (merged, with 'latest' per OS)

Configuration:
- ./config/pinned.json (see version-conf-proc.md)
- Env var LOCALE can hint date parsing (en-us or de-de).

Requirements:
- pydantic v2, python-dateutil
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional

from dateutil import parser as dateparser
from pydantic import BaseModel, Field, HttpUrl, ValidationError, field_validator, model_validator

# ──────────────────────────────────────────────────────────────────────────────
# Paths and env
# ──────────────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "security_releases"
ENRICHED_DIR = DATA_DIR / "enriched"
CONFIG_DIR = REPO_ROOT / "config"
ENRICHED_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

LOCALE = os.getenv("LOCALE", "en-us").strip() or "en-us"

# OS literal union used across models
OSLiteral = Literal["ios", "ipados", "macos", "watchos", "tvos", "visionos", "safari"]

# CVE validator
RE_CVE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)

# ──────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ──────────────────────────────────────────────────────────────────────────────

class ReleaseEntry(BaseModel):
    title: str
    url: HttpUrl
    release_date: Optional[str] = None       # raw text, e.g. "Released August 1, 2025"
    version: Optional[str] = None            # e.g. "18.5"
    build: Optional[str] = None              # e.g. "24B83"
    cve_count: int = 0
    cves: List[str] = Field(default_factory=list)
    
    # KEV enrichment fields
    actively_exploited_cves: List[str] = Field(default_factory=list)
    actively_exploited_count: int = 0
    exploitation_rate: float = 0.0

    # Derived and enrichment fields
    release_date_iso: Optional[date] = None
    days_since_previous: Optional[int] = None
    is_pinned: bool = False

    @field_validator("cves", mode="after")
    def _validate_cves(cls, v: List[str]) -> List[str]:
        # Normalize and deduplicate CVEs; accept only valid tokens.
        uniq, seen = [], set()
        for c in v:
            cc = c.strip().upper()
            if RE_CVE.fullmatch(cc) and cc not in seen:
                seen.add(cc)
                uniq.append(cc)
        return uniq

    @model_validator(mode="after")
    def _sync_cve_count(self) -> "ReleaseEntry":
        # Ensure cve_count equals list length
        if self.cves:
            self.cve_count = len(self.cves)
        return self


class OSFeed(BaseModel):
    os: OSLiteral
    updated: str
    releases: List[ReleaseEntry]

    @field_validator("updated", mode="after")
    def _validate_updated(cls, v: str) -> str:
        # Normalize updated timestamp to Z
        dt = dateparser.parse(v)
        return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class CombinedFeed(BaseModel):
    updated: str
    feeds: Dict[OSLiteral, OSFeed]
    latest: Dict[OSLiteral, Optional[ReleaseEntry]]

# ──────────────────────────────────────────────────────────────────────────────
# Config structures
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class PinnedSpec:
    pinned_version: Optional[str] = None
    pinned_build: Optional[str] = None

@dataclass
class RetentionPolicy:
    mode: str = "all"                       # "all" | "last_n_major" | "whitelist"
    last_n: int = 2                         # used when mode == last_n_major
    allow_pins_outside_window: bool = False
    majors: Optional[List[int]] = None      # used when mode == whitelist

@dataclass
class OSConfig:
    retention: RetentionPolicy
    pin: PinnedSpec

def _to_retention_policy(d: dict | None) -> RetentionPolicy:
    d = d or {}
    return RetentionPolicy(
        mode=d.get("mode", "all"),
        last_n=int(d.get("last_n", 2)),
        allow_pins_outside_window=bool(d.get("allow_pins_outside_window", False)),
        majors=list(d.get("majors", [])) if isinstance(d.get("majors"), list) else None,
    )

def _to_pinned_spec(d: dict | None) -> PinnedSpec:
    d = d or {}
    return PinnedSpec(
        pinned_version=d.get("pinned_version"),
        pinned_build=d.get("pinned_build"),
    )

def load_os_config() -> Dict[str, OSConfig]:
    """
    Reads ./config/pinned.json and returns per-OS config.
    If file missing, defaults:
      - macos: retention all
      - others: last_n_major with last_n=2
    """
    default_map: Dict[str, OSConfig] = {
        "macos": OSConfig(retention=RetentionPolicy(mode="all"), pin=PinnedSpec()),
        "ios": OSConfig(retention=RetentionPolicy(mode="last_n_major", last_n=2), pin=PinnedSpec()),
        "ipados": OSConfig(retention=RetentionPolicy(mode="last_n_major", last_n=2), pin=PinnedSpec()),
        "watchos": OSConfig(retention=RetentionPolicy(mode="last_n_major", last_n=2), pin=PinnedSpec()),
        "tvos": OSConfig(retention=RetentionPolicy(mode="last_n_major", last_n=2), pin=PinnedSpec()),
        "visionos": OSConfig(retention=RetentionPolicy(mode="last_n_major", last_n=2), pin=PinnedSpec()),
        "safari": OSConfig(retention=RetentionPolicy(mode="last_n_major", last_n=2), pin=PinnedSpec()),
    }

    cfg_path = CONFIG_DIR / "pinned.json"
    if not cfg_path.exists():
        return default_map

    try:
        raw = json.loads(cfg_path.read_text())
    except Exception:
        return default_map

    out: Dict[str, OSConfig] = {}
    for os_key, obj in raw.items():
        if os_key not in default_map:
            # quietly ignore unknown OS keys to be forward compatible
            continue
        retention = _to_retention_policy(obj.get("retention"))
        pin = _to_pinned_spec(obj.get("pin"))
        out[os_key] = OSConfig(retention=retention, pin=pin)

    # Fill any missing keys with defaults
    for k, v in default_map.items():
        if k not in out:
            out[k] = v
    return out

# ──────────────────────────────────────────────────────────────────────────────
# Helpers: dates, majors, enrichment, retention
# ──────────────────────────────────────────────────────────────────────────────

def parse_release_date(text: Optional[str]) -> Optional[date]:
    if not text:
        return None
    try:
        t = text.replace("Released", "").replace("Veröffentlicht", "").strip(":,. ").strip()
        dt = dateparser.parse(t, dayfirst=("de-" in LOCALE.lower()))
        return dt.date() if dt else None
    except Exception:
        return None

def major_of(version: Optional[str]) -> Optional[int]:
    """
    Extract major version: "18.5" -> 18; "15" -> 15; None if not parseable.
    """
    if not version:
        return None
    m = re.match(r"^\s*(\d+)", version)
    return int(m.group(1)) if m else None

def enrich_feed(feed: OSFeed, pin: PinnedSpec) -> OSFeed:
    # 1) parse dates
    for r in feed.releases:
        r.release_date_iso = parse_release_date(r.release_date)

    # 2) pin flags
    for r in feed.releases:
        is_ver = bool(pin.pinned_version and r.version == pin.pinned_version)
        is_build = bool(pin.pinned_build and r.build == pin.pinned_build)
        r.is_pinned = bool(is_ver or is_build)

    # 3) sort by date desc then title
    feed.releases.sort(
        key=lambda r: (r.release_date_iso is not None, r.release_date_iso or date.min, r.title),
        reverse=True,
    )

    # 4) days_since_previous
    prev_date: Optional[date] = None
    for r in feed.releases:
        if r.release_date_iso and prev_date:
            r.days_since_previous = (prev_date - r.release_date_iso).days
        else:
            r.days_since_previous = None
        if r.release_date_iso:
            prev_date = r.release_date_iso

    return feed

def apply_retention(feed: OSFeed, policy: RetentionPolicy) -> OSFeed:
    """
    Retention policies:
      - all: keep everything
      - last_n_major: keep entries with major version in the N largest majors present
      - whitelist: keep entries with major version in explicit majors list
    Pins can optionally override filtering if allow_pins_outside_window is True.
    """
    mode = policy.mode or "all"
    if mode == "all":
        return feed

    entries = feed.releases

    # Build set of majors present in the feed
    majors_present: List[int] = []
    for r in entries:
        mj = major_of(r.version)
        if mj is not None and mj not in majors_present:
            majors_present.append(mj)

    kept: List[ReleaseEntry] = []

    if mode == "last_n_major":
        top_majors = sorted([m for m in majors_present if m is not None], reverse=True)[: max(1, int(policy.last_n or 2))]
        for r in entries:
            mj = major_of(r.version)
            in_window = (mj in top_majors) if mj is not None else False
            if in_window or (policy.allow_pins_outside_window and r.is_pinned):
                kept.append(r)

    elif mode == "whitelist":
        allow = set(policy.majors or [])
        for r in entries:
            mj = major_of(r.version)
            if (mj in allow) or (policy.allow_pins_outside_window and r.is_pinned):
                kept.append(r)

    # Replace with filtered list (keep relative order already sorted by date)
    feed.releases = kept
    return feed

def write_enriched_feed(feed: OSFeed) -> None:
    doc = json.loads(feed.model_dump_json(exclude_none=False, indent=2))
    (ENRICHED_DIR / f"{feed.os}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2))

def build_combined(feeds: Dict[OSLiteral, OSFeed]) -> CombinedFeed:
    updated = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    latest: Dict[OSLiteral, Optional[ReleaseEntry]] = {}
    for os_key, feed in feeds.items():
        latest[os_key] = feed.releases[0] if feed.releases else None
    return CombinedFeed(updated=updated, feeds=feeds, latest=latest)

# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    # Load configuration (pin + retention per OS)
    cfg = load_os_config()

    feeds: Dict[OSLiteral, OSFeed] = {}

    for p in sorted(DATA_DIR.glob("*.json")):
        if p.name in ("combined.json",):
            continue

        try:
            raw = json.loads(p.read_text())
            feed = OSFeed.model_validate(raw)
        except ValidationError as e:
            raise SystemExit(f"[postprocess] Validation failed for {p}: {e}") from e

        os_conf = cfg.get(feed.os, OSConfig(retention=RetentionPolicy(mode="all"), pin=PinnedSpec()))

        # Enrich (parse dates, compute deltas, mark pins)
        enriched = enrich_feed(feed, os_conf.pin)

        # Apply retention
        filtered = apply_retention(enriched, os_conf.retention)

        # Persist per-OS enriched output
        write_enriched_feed(filtered)

        feeds[filtered.os] = filtered

    combined = build_combined(feeds)
    (DATA_DIR / "combined.json").write_text(
        combined.model_dump_json(exclude_none=False, indent=2)
    )
    print("[postprocess] wrote enriched feeds and combined.json")

if __name__ == "__main__":
    main()

