#!/usr/bin/env python3
"""
Extract CVE details from cached Apple security pages.

import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


Extracts:
- Component/framework affected (WebKit, Kernel, Safari, etc.)
- Impact description
- Credit/reporter
- Platform availability
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

from src.utils.logger import configure_logger, get_logger

logger = get_logger(__name__)


class CVEDetailExtractor:
    """Extract CVE details from Apple security pages."""
    
    def __init__(self):
        self.cache_dir = Path(".cache/raw")
        self.output_dir = Path(__file__).resolve().parent.parent.parent / "data" / "cache"
        self.output_dir.mkdir(exist_ok=True)
        self.cve_details_file = self.output_dir / "cve_details.json"
        
        # Load existing details
        self.cve_details = self.load_cve_details()
        
    def load_cve_details(self) -> Dict[str, Any]:
        """Load existing CVE details from cache."""
        if self.cve_details_file.exists():
            try:
                with open(self.cve_details_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load CVE details: {e}")
        return {}
    
    def save_cve_details(self):
        """Save CVE details to cache."""
        with open(self.cve_details_file, 'w') as f:
            json.dump(self.cve_details, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(self.cve_details)} CVE details to cache")
    
    def extract_from_html(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract CVE details from HTML content."""
        details = {}
        
        # Simple regex-based extraction (avoiding BeautifulSoup dependency)
        # Look for component headers followed by CVE listings
        
        # Pattern: <h3>Component Name</h3>...<p>...CVE-XXXX-YYYY...</p>
        component_pattern = r'<h3[^>]*>([^<]+)</h3>.*?(?=<h3|<h2|$)'
        
        for match in re.finditer(component_pattern, html_content, re.DOTALL):
            component = match.group(1).strip()
            section = match.group(0)
            
            # Skip if it's not a real component
            if component in ['Additional recognition', 'Additional recognitions', 'Acknowledgements']:
                continue
            
            # Find CVEs in this section
            cve_pattern = r'CVE-\d{4}-\d+'
            cves = re.findall(cve_pattern, section)
            
            if not cves:
                continue
            
            # Extract impact if available
            impact_match = re.search(r'Impact:\s*([^<]+)', section)
            impact = impact_match.group(1).strip() if impact_match else None
            
            # Extract description (usually after Impact)
            desc_match = re.search(r'Description:\s*([^<]+)', section)
            description = desc_match.group(1).strip() if desc_match else None
            
            # Extract "Available for" information
            available_match = re.search(r'Available for:\s*([^<]+)', section)
            available_for = available_match.group(1).strip() if available_match else None
            
            # Store details for each CVE
            for cve in cves:
                if cve not in details:
                    details[cve] = {
                        'component': component,
                        'impact': impact,
                        'description': description,
                        'available_for': available_for,
                        'url': url
                    }
        
        return details
    
    def extract_from_cache(self, limit: Optional[int] = None):
        """Extract CVE details from all cached security pages."""
        html_files = list(self.cache_dir.glob("*.html"))
        
        if limit:
            html_files = html_files[:limit]
        
        logger.info(f"Processing {len(html_files)} cached security pages")
        
        new_cves = 0
        for html_file in html_files:
            # Skip if we've already processed this file
            file_hash = html_file.stem
            
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Try to find the URL from the HTML
                url_match = re.search(r'<link rel="canonical" href="([^"]+)"', html_content)
                url = url_match.group(1) if url_match else f"https://support.apple.com/{file_hash}"
                
                # Extract CVE details
                page_details = self.extract_from_html(html_content, url)
                
                # Merge with existing details
                for cve, info in page_details.items():
                    if cve not in self.cve_details:
                        self.cve_details[cve] = info
                        new_cves += 1
                        
            except Exception as e:
                logger.warning(f"Error processing {html_file}: {e}")
                continue
        
        logger.info(f"Found {new_cves} new CVE details")
        
        # Save updated details
        if new_cves > 0:
            self.save_cve_details()
    
    def get_cve_info(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific CVE."""
        return self.cve_details.get(cve_id)
    
    def get_component_stats(self) -> Dict[str, int]:
        """Get statistics about affected components."""
        stats = {}
        for cve, info in self.cve_details.items():
            component = info.get('component', 'Unknown')
            stats[component] = stats.get(component, 0) + 1
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract CVE details from cached security pages')
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of pages to process'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show component statistics'
    )
    parser.add_argument(
        '--cve',
        help='Look up specific CVE'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    configure_logger(max(1, args.verbose))
    
    extractor = CVEDetailExtractor()
    
    if args.cve:
        # Look up specific CVE
        info = extractor.get_cve_info(args.cve)
        if info:
            print(json.dumps({args.cve: info}, indent=2))
        else:
            print(f"No details found for {args.cve}")
    elif args.stats:
        # Show statistics
        extractor.extract_from_cache(limit=args.limit)
        stats = extractor.get_component_stats()
        print("\nComponent Statistics:")
        print("=" * 40)
        for component, count in list(stats.items())[:20]:
            print(f"{component:30} {count:5}")
    else:
        # Extract all details
        extractor.extract_from_cache(limit=args.limit)
        print(f"Extracted {len(extractor.cve_details)} CVE details")
    
    return 0


if __name__ == "__main__":
    exit(main())