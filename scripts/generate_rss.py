#!/usr/bin/env python3
"""Generate RSS feed from SOFA security data."""

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import argparse
from typing import List, Dict, Any

def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON data from file."""
    if not file_path.exists():
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)

def format_rfc822_date(date_str: str) -> str:
    """Convert date string to RFC 822 format for RSS."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%a, %d %b %Y %H:%M:%S %z')
    except:
        return datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

def create_rss_item(title: str, description: str, pub_date: str, link: str = "") -> ET.Element:
    """Create an RSS item element."""
    item = ET.Element('item')
    
    title_elem = ET.SubElement(item, 'title')
    title_elem.text = title
    
    desc_elem = ET.SubElement(item, 'description')
    desc_elem.text = description
    
    pub_elem = ET.SubElement(item, 'pubDate')
    pub_elem.text = format_rfc822_date(pub_date)
    
    if link:
        link_elem = ET.SubElement(item, 'link')
        link_elem.text = link
    
    guid_elem = ET.SubElement(item, 'guid')
    guid_elem.text = f"{title}_{pub_date}"
    guid_elem.set('isPermaLink', 'false')
    
    return item

def generate_rss(input_dir: Path, output_file: Path) -> None:
    """Generate RSS feed from SOFA data."""
    # Create RSS root
    rss = ET.Element('rss')
    rss.set('version', '2.0')
    
    channel = ET.SubElement(rss, 'channel')
    
    # Channel metadata
    title = ET.SubElement(channel, 'title')
    title.text = 'SOFA - Apple Security Updates'
    
    link = ET.SubElement(channel, 'link')
    link.text = 'https://sofa.macadmins.io'
    
    desc = ET.SubElement(channel, 'description')
    desc.text = 'Simple Organized Feed for Apple Security Updates'
    
    lang = ET.SubElement(channel, 'language')
    lang.text = 'en-us'
    
    # Load data
    macos_data = load_json(input_dir / 'macos.json')
    ios_data = load_json(input_dir / 'ios.json')
    metadata = load_json(input_dir.parent / 'metadata.json')
    
    items = []
    
    # Add macOS updates
    if macos_data.get('versions'):
        for version in macos_data['versions'][:5]:  # Latest 5
            if version.get('release_date'):
                item = create_rss_item(
                    f"macOS {version.get('version', 'Unknown')}",
                    f"Security update for macOS {version.get('version', '')}",
                    version['release_date']
                )
                items.append((version['release_date'], item))
    
    # Add iOS updates
    if ios_data.get('versions'):
        for version in ios_data['versions'][:5]:  # Latest 5
            if version.get('release_date'):
                item = create_rss_item(
                    f"iOS {version.get('version', 'Unknown')}",
                    f"Security update for iOS {version.get('version', '')}",
                    version['release_date']
                )
                items.append((version['release_date'], item))
    
    # Sort by date and add to channel
    items.sort(key=lambda x: x[0], reverse=True)
    for _, item in items[:20]:  # Keep 20 most recent
        channel.append(item)
    
    # Write RSS file
    tree = ET.ElementTree(rss)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"RSS feed generated: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate RSS feed from SOFA data')
    parser.add_argument('--input', type=Path, default=Path('data/feeds'),
                        help='Input directory containing JSON feeds')
    parser.add_argument('--output', type=Path, default=Path('data/feeds/rss.xml'),
                        help='Output RSS file path')
    
    args = parser.parse_args()
    
    generate_rss(args.input, args.output)

if __name__ == '__main__':
    main()