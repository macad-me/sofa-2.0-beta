#!/usr/bin/env python3
"""Reparse cached HTML files with fixed version extraction."""

import sys
import json
from pathlib import Path

# Add the data-processing directory to path
sys.path.insert(0, 'data-processing')

from src.builders.build_security_releases import parse_detail_page

# Paths
CACHE_RAW = Path("data-processing/data/cache/raw")
CACHE_PARSED = Path("data-processing/data/cache/parsed")

# Ensure parsed cache directory exists
CACHE_PARSED.mkdir(parents=True, exist_ok=True)

# Process all raw HTML files
count = 0
for html_file in CACHE_RAW.glob("*.html"):
    # Read raw HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse it (construct URL from filename)
    # Filename format: support.apple.com_en-ca_100100.html
    url_parts = html_file.stem.replace('_', '/')
    url = f"https://{url_parts}"
    parsed = parse_detail_page(url, html_content)
    
    # Save parsed data
    parsed_file = CACHE_PARSED / html_file.name.replace('.html', '.json')
    with open(parsed_file, 'w', encoding='utf-8') as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    
    count += 1
    if count % 50 == 0:
        print(f"Processed {count} files...")

print(f"Reparsed {count} cached HTML files")