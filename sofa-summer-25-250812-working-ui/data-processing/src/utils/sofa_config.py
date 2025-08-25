#!/usr/bin/env python3
"""
SOFA Configuration File

Central configuration for all SOFA scripts.
This controls what data is fetched, processed, and how far back we go.
"""

import os
from pathlib import Path
from datetime import datetime, timedelta

#------------------------------------------------------------------------------
# DIRECTORY STRUCTURE
#------------------------------------------------------------------------------

# Project root (src directory parent)
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()

# Cache directories - using the unified structure
CACHE_DIR = PROJECT_ROOT / "data" / "cache"  # Main cache directory
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Subdirectories of cache
URL_META_DIR = CACHE_DIR / "urls"      # URL metadata
RAW_HTML_DIR = CACHE_DIR / "raw"       # Raw HTML files
PARSED_DIR = CACHE_DIR / "parsed"      # Parsed JSON data

# Simple cache directory (same as main cache for unified structure)
SIMPLE_CACHE_DIR = CACHE_DIR
SIMPLE_CACHE_DIR.mkdir(exist_ok=True)

# Output directories
SECURITY_RELEASES_DIR = PROJECT_ROOT / "data" / "security_releases"
SECURITY_RELEASES_DIR.mkdir(parents=True, exist_ok=True)

ENRICHED_DIR = SECURITY_RELEASES_DIR / "enriched"
ENRICHED_DIR.mkdir(parents=True, exist_ok=True)

# V1 compatibility directory
V1_DIR = PROJECT_ROOT / "data" / "feeds" / "v1"
V1_DIR.mkdir(parents=True, exist_ok=True)

# Config directory
CONFIG_DIR = PROJECT_ROOT / "config"
CONFIG_DIR.mkdir(exist_ok=True)

#------------------------------------------------------------------------------
# APPLE SECURITY PAGES TO FETCH
#------------------------------------------------------------------------------

# Control which index pages to fetch
FETCH_INDEX_PAGES = {
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
        "enabled": False,  # Set to False to skip older releases
        "description": "Security releases 2020-2021"
    },
    "2018-2019": {
        "url": "https://support.apple.com/en-ca/103179",
        "enabled": False,  # Disabled by default (very old)
        "description": "Security releases 2018-2019"
    }
}

# Control detail page fetching
FETCH_DETAIL_PAGES = {
    "enabled": True,  # Master switch for detail pages
    "max_pages": None,  # Set to limit number of pages (None = all)
    "skip_older_than_days": 365 * 2,  # Skip pages older than 2 years
    "required_patterns": [  # Only fetch if URL contains these
        # Add patterns here if you want to filter
    ],
    "exclude_patterns": [  # Skip URLs containing these
        "/HT20",  # Very old (2010s)
        "/HT19",  # Even older
    ]
}

#------------------------------------------------------------------------------
# OPERATING SYSTEM CONFIGURATION
#------------------------------------------------------------------------------

# Which OS feeds to generate
ENABLED_OS_FEEDS = {
    "macos": True,
    "ios": True,
    "ipados": True,
    "watchos": True,
    "tvos": True,
    "visionos": True,
    "safari": True,
}

# Retention policy for each OS (how many major versions to keep)
OS_RETENTION_POLICY = {
    "macos": None,  # Keep all versions
    "ios": 2,       # Keep last 2 major versions
    "ipados": 2,    # Keep last 2 major versions
    "watchos": 2,   # Keep last 2 major versions
    "tvos": 2,      # Keep last 2 major versions
    "visionos": 2,  # Keep last 2 major versions
    "safari": 3,    # Keep last 3 major versions
}

# Minimum supported versions (don't process older than these)
MIN_SUPPORTED_VERSIONS = {
    "macos": 12.0,    # Monterey
    "ios": 18.0,      # iOS 16
    "ipados": 18.0,   # iPadOS 16
    "watchos": 11.0,   # watchOS 9
    "tvos": 18.0,     # tvOS 16
    "visionos": 2.0,  # visionOS 1
    "safari": 16.0,   # Safari 16
}

#------------------------------------------------------------------------------
# KEV (KNOWN EXPLOITED VULNERABILITIES) CONFIGURATION
#------------------------------------------------------------------------------

KEV_CONFIG = {
    # CISA KEV fetching
    "fetch_cisa_kev": True,
    "cisa_kev_url": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
    "cisa_cache_hours": 6,  # Refresh every 6 hours
    
    # Apple exploitation pattern analysis
    "analyze_apple_patterns": True,
    "apple_pattern_categories": [
        "ACTIVELY_EXPLOITED",
        "EXPLOITED_BEFORE_VERSION", 
        "TARGETED_ATTACK",
        "SUPPLEMENTARY_FIX",
        "PHYSICAL_ATTACK_EXPLOITED"
    ],
    
    # Cross-platform warnings
    "enable_cross_platform_warnings": True,
    "cross_platform_warning_text": "Known exploited on: {platforms}",
    
    # Confidence thresholds
    "min_confidence_for_kev": 90,  # Minimum confidence to mark as KEV
    "min_confidence_for_warning": 70,  # Minimum for warning
}

#------------------------------------------------------------------------------
# DATA SOURCES
#------------------------------------------------------------------------------

# GDMF (Global Data Management Facility)
GDMF_CONFIG = {
    "enabled": True,
    "base_url": "https://gdmf.apple.com/v2/pmv",
    "cache_hours": 24,
    "fetch_timeout": 30,
}

# RSS Feeds
RSS_CONFIG = {
    "enabled": True,
    "feeds": {
        "macos": "https://developer.apple.com/news/releases/rss/releases.rss",
        "ios": "https://developer.apple.com/news/releases/rss/releases.rss",
    },
    "cache_hours": 12,
}

# XProtect configuration
XPROTECT_CONFIG = {
    "enabled": False,  # Not implemented yet
    "url": "https://mesu.apple.com/assets/com_apple_MobileAsset_XProtectPlistConfigData/com_apple_MobileAsset_XProtectPlistConfigData.xml",
}

#------------------------------------------------------------------------------
# NETWORK AND CACHING
#------------------------------------------------------------------------------

# HTTP request configuration
HTTP_CONFIG = {
    "user_agent": "SOFA/2.0 (github.com/macadmins/sofa)",
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 2,
    "respect_rate_limit": True,
    "rate_limit_delay": 1.5,  # Seconds between requests to same domain
}

# Cache configuration
CACHE_CONFIG = {
    "max_age_hours": 24,  # Default cache age
    "verify_on_304": True,  # Verify content even on HTTP 304
    "clean_old_files": True,
    "old_file_days": 90,  # Clean files older than this
}

#------------------------------------------------------------------------------
# PROCESSING OPTIONS
#------------------------------------------------------------------------------

PROCESSING_CONFIG = {
    # CVE enrichment
    "fetch_cve_details": True,
    "enrich_with_cvss_scores": True,
    
    # Device/model enrichment
    "enrich_with_device_info": True,
    "enrich_with_model_identifiers": True,
    
    # Date calculations
    "calculate_days_since_release": True,
    "calculate_days_between_releases": True,
    
    # Output formatting
    "pretty_print_json": True,
    "json_indent": 2,
    "ensure_ascii": False,
}

#------------------------------------------------------------------------------
# LOGGING CONFIGURATION
#------------------------------------------------------------------------------

LOGGING_CONFIG = {
    "default_level": "INFO",
    "file_logging": False,
    "log_file": "logs/sofa.log",
    "log_rotation": "daily",
    "log_retention_days": 30,
    "show_timestamps": True,
    "show_module_name": True,
}

#------------------------------------------------------------------------------
# PINNED VERSIONS (override retention policy)
#------------------------------------------------------------------------------

# Path to pinned versions file
PINNED_VERSIONS_FILE = CONFIG_DIR / "pinned.json"

# Default pinned versions (if file doesn't exist)
DEFAULT_PINNED_VERSIONS = {
    "macos": [],  # e.g., ["11.7.10", "10.15.7"]
    "ios": [],
    "ipados": [],
    "allow_pins_outside_window": True,
}

#------------------------------------------------------------------------------
# ENVIRONMENT VARIABLE OVERRIDES
#------------------------------------------------------------------------------

# Allow environment variables to override settings
if os.getenv("SOFA_CACHE_DIR"):
    CACHE_DIR = Path(os.getenv("SOFA_CACHE_DIR"))

if os.getenv("SOFA_SKIP_OLD_RELEASES"):
    FETCH_INDEX_PAGES["2020-2021"]["enabled"] = False
    FETCH_INDEX_PAGES["2018-2019"]["enabled"] = False

if os.getenv("SOFA_MAX_DETAIL_PAGES"):
    FETCH_DETAIL_PAGES["max_pages"] = int(os.getenv("SOFA_MAX_DETAIL_PAGES"))

if os.getenv("SOFA_DISABLE_KEV"):
    KEV_CONFIG["fetch_cisa_kev"] = False
    KEV_CONFIG["analyze_apple_patterns"] = False

#------------------------------------------------------------------------------
# HELPER FUNCTIONS
#------------------------------------------------------------------------------

def get_enabled_index_pages():
    """Get list of enabled index page IDs."""
    return [
        page_id 
        for page_id, config in FETCH_INDEX_PAGES.items() 
        if config.get("enabled", False)
    ]

def get_enabled_os_feeds():
    """Get list of enabled OS feed names."""
    return [
        os_name 
        for os_name, enabled in ENABLED_OS_FEEDS.items() 
        if enabled
    ]

def should_fetch_detail_url(url: str, release_date: datetime = None) -> bool:
    """
    Check if a detail URL should be fetched based on config.
    
    Args:
        url: The detail page URL
        release_date: Optional release date to check age
        
    Returns:
        True if URL should be fetched
    """
    if not FETCH_DETAIL_PAGES["enabled"]:
        return False
    
    # Check exclude patterns
    for pattern in FETCH_DETAIL_PAGES.get("exclude_patterns", []):
        if pattern in url:
            return False
    
    # Check required patterns
    required = FETCH_DETAIL_PAGES.get("required_patterns", [])
    if required and not any(pattern in url for pattern in required):
        return False
    
    # Check age if date provided
    if release_date and FETCH_DETAIL_PAGES.get("skip_older_than_days"):
        age = (datetime.now() - release_date).days
        if age > FETCH_DETAIL_PAGES["skip_older_than_days"]:
            return False
    
    return True

def get_retention_cutoff(os_name: str) -> tuple:
    """
    Get the retention cutoff for an OS.
    
    Returns:
        (major_version_cutoff, minor_version_cutoff) or (None, None) for no limit
    """
    policy = OS_RETENTION_POLICY.get(os_name)
    if policy is None:
        return (None, None)
    
    # This would need OS-specific logic to determine current version
    # For now, return the policy value
    return (policy, None)

#------------------------------------------------------------------------------
# VALIDATION
#------------------------------------------------------------------------------

def validate_config():
    """Validate configuration settings."""
    errors = []
    
    # Check directories exist or can be created
    for dir_var in [CACHE_DIR, SIMPLE_CACHE_DIR, SECURITY_RELEASES_DIR]:
        try:
            dir_var.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create directory {dir_var}: {e}")
    
    # Check at least one OS is enabled
    if not any(ENABLED_OS_FEEDS.values()):
        errors.append("No OS feeds are enabled")
    
    # Check at least one index page is enabled
    if not any(config["enabled"] for config in FETCH_INDEX_PAGES.values()):
        errors.append("No index pages are enabled for fetching")
    
    return errors

# Run validation on import
validation_errors = validate_config()
if validation_errors:
    import sys
    print("Configuration errors:", file=sys.stderr)
    for error in validation_errors:
        print(f"  - {error}", file=sys.stderr)