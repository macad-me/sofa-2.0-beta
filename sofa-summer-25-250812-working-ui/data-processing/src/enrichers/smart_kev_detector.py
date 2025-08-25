#!/usr/bin/env python3
"""
Smart KEV (Known Exploited Vulnerabilities) detector.
Combines multiple sources and provides nuanced exploitation information.

This system:
1. Detects Apple's exploitation indicators with context
2. Cross-references with CISA KEV catalog
3. Provides exploitation metadata (platform, confidence, source)
4. Handles cross-platform warnings (e.g., "exploited on iOS" for macOS releases)
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum

from bs4 import BeautifulSoup
import sys
from pathlib import Path
# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.utils.logger import configure_logger, get_logger

logger = get_logger(__name__)


class ExploitationSource(str, Enum):
    """Source of exploitation information."""
    APPLE_DIRECT = "apple_direct"  # Apple says "may have been exploited"
    APPLE_TARGETED = "apple_targeted"  # "sophisticated attack against specific individuals"
    APPLE_VERSION_SPECIFIC = "apple_version_specific"  # "exploited against versions before X"
    CISA_KEV = "cisa_kev"  # In CISA's KEV catalog
    CROSS_PLATFORM = "cross_platform"  # Exploited on different OS


class ExploitationConfidence(str, Enum):
    """Confidence level of exploitation."""
    CONFIRMED = "confirmed"  # Apple confirms or CISA KEV
    HIGH = "high"  # Strong indicators
    MEDIUM = "medium"  # Some indicators
    LOW = "low"  # Weak indicators


@dataclass
class ExploitationInfo:
    """Detailed exploitation information for a CVE."""
    cve_id: str
    is_exploited: bool
    confidence: ExploitationConfidence
    sources: List[ExploitationSource]
    affected_platforms: Set[str]  # iOS, macOS, watchOS, etc.
    targeted_versions: Optional[List[str]] = None
    is_targeted_attack: bool = False
    is_physical_attack: bool = False
    notes: Optional[str] = None
    raw_text: Optional[str] = None  # Original text that triggered detection


class SmartKEVDetector:
    """Smart detection of exploited vulnerabilities."""
    
    # Enhanced Apple exploitation patterns with metadata
    APPLE_PATTERNS = [
        # Direct exploitation
        (
            r"Apple is aware of a report that this issue may have been exploited",
            ExploitationSource.APPLE_DIRECT,
            ExploitationConfidence.CONFIRMED,
            {"is_exploited": True}
        ),
        (
            r"Apple is aware of a report that this issue may have been actively exploited",
            ExploitationSource.APPLE_DIRECT,
            ExploitationConfidence.CONFIRMED,
            {"is_exploited": True}
        ),
        
        # Targeted attacks
        (
            r"exploited in an extremely sophisticated attack against specific targeted individuals",
            ExploitationSource.APPLE_TARGETED,
            ExploitationConfidence.CONFIRMED,
            {"is_exploited": True, "is_targeted_attack": True}
        ),
        
        # Version-specific exploitation
        (
            r"actively exploited against versions of (iOS|iPadOS|macOS|watchOS|tvOS|visionOS) (?:released )?before (?:iOS |iPadOS |macOS |watchOS |tvOS |visionOS )?([\d\.]+)",
            ExploitationSource.APPLE_VERSION_SPECIFIC,
            ExploitationConfidence.CONFIRMED,
            {"is_exploited": True, "extract_version": True}
        ),
        
        # Physical attacks
        (
            r"A physical attack may.*Apple is aware of a report that this issue may have been exploited",
            ExploitationSource.APPLE_DIRECT,
            ExploitationConfidence.CONFIRMED,
            {"is_exploited": True, "is_physical_attack": True}
        ),
        
        # Supplementary fixes (indicates prior exploitation)
        (
            r"This is a supplementary fix for an attack that was blocked",
            ExploitationSource.APPLE_DIRECT,
            ExploitationConfidence.HIGH,
            {"is_exploited": True, "notes": "Supplementary fix for previously blocked attack"}
        ),
    ]
    
    def __init__(self, kev_catalog_path: Optional[Path] = None):
        """Initialize the detector."""
        self.kev_catalog_path = kev_catalog_path or Path("cache/kev_catalog.json")
        self.cisa_kevs: Set[str] = set()
        self.apple_exploited: Dict[str, ExploitationInfo] = {}
        self.load_cisa_kevs()
        
    def load_cisa_kevs(self) -> None:
        """Load CISA KEV catalog."""
        if self.kev_catalog_path.exists():
            try:
                with open(self.kev_catalog_path) as f:
                    data = json.load(f)
                    catalog = data.get("catalog", data)
                    
                    if "vulnerabilities" in catalog:
                        for vuln in catalog["vulnerabilities"]:
                            self.cisa_kevs.add(vuln["cveID"])
                        logger.info(f"Loaded {len(self.cisa_kevs)} CISA KEVs")
            except Exception as e:
                logger.error(f"Failed to load CISA KEV catalog: {e}")
    
    def detect_apple_exploitation(self, cve_id: str, text: str, platform: str) -> Optional[ExploitationInfo]:
        """
        Detect exploitation from Apple's security note text.
        
        Args:
            cve_id: CVE identifier
            text: Text containing impact description
            platform: Platform (iOS, macOS, etc.)
            
        Returns:
            ExploitationInfo if exploitation detected
        """
        info = ExploitationInfo(
            cve_id=cve_id,
            is_exploited=False,
            confidence=ExploitationConfidence.LOW,
            sources=[],
            affected_platforms={platform},
            raw_text=None
        )
        
        for pattern, source, confidence, metadata in self.APPLE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                info.is_exploited = metadata.get("is_exploited", False)
                info.confidence = confidence
                info.sources.append(source)
                info.raw_text = match.group(0)[:200]  # Store first 200 chars
                
                # Extract version if applicable
                if metadata.get("extract_version") and len(match.groups()) >= 2:
                    affected_os = match.group(1)
                    affected_version = match.group(2) if len(match.groups()) > 1 else None
                    if affected_version:
                        info.targeted_versions = [f"{affected_os} {affected_version}"]
                        info.affected_platforms.add(affected_os)
                
                # Set flags
                info.is_targeted_attack = metadata.get("is_targeted_attack", False)
                info.is_physical_attack = metadata.get("is_physical_attack", False)
                if metadata.get("notes"):
                    info.notes = metadata["notes"]
                
                # Don't break - collect all matching patterns
        
        return info if info.is_exploited else None
    
    def check_cross_platform_exploitation(
        self, 
        cve_id: str, 
        current_platform: str
    ) -> Optional[ExploitationInfo]:
        """
        Check if CVE is exploited on other platforms.
        
        Returns exploitation info with cross-platform warning if applicable.
        """
        # Check if we have info about this CVE from other platforms
        if cve_id in self.apple_exploited:
            existing_info = self.apple_exploited[cve_id]
            
            # If exploited on different platform
            if current_platform not in existing_info.affected_platforms:
                cross_platform_info = ExploitationInfo(
                    cve_id=cve_id,
                    is_exploited=False,  # Not confirmed on THIS platform
                    confidence=ExploitationConfidence.MEDIUM,
                    sources=[ExploitationSource.CROSS_PLATFORM],
                    affected_platforms={current_platform},
                    notes=f"Known exploited on: {', '.join(existing_info.affected_platforms)}"
                )
                return cross_platform_info
        
        return None
    
    def get_exploitation_status(
        self, 
        cve_id: str,
        apple_text: Optional[str] = None,
        platform: str = "unknown"
    ) -> ExploitationInfo:
        """
        Get comprehensive exploitation status for a CVE.
        
        Combines Apple indicators and CISA KEV catalog.
        """
        info = ExploitationInfo(
            cve_id=cve_id,
            is_exploited=False,
            confidence=ExploitationConfidence.LOW,
            sources=[],
            affected_platforms={platform}
        )
        
        # Check Apple's text if provided
        if apple_text:
            apple_info = self.detect_apple_exploitation(cve_id, apple_text, platform)
            if apple_info:
                info = apple_info
                # Store for cross-platform checks
                self.apple_exploited[cve_id] = apple_info
        
        # Check CISA KEV
        if cve_id in self.cisa_kevs:
            info.is_exploited = True
            if ExploitationSource.CISA_KEV not in info.sources:
                info.sources.append(ExploitationSource.CISA_KEV)
            # Upgrade confidence if in CISA
            if info.confidence != ExploitationConfidence.CONFIRMED:
                info.confidence = ExploitationConfidence.HIGH
        
        # Check cross-platform if not already exploited
        if not info.is_exploited:
            cross_info = self.check_cross_platform_exploitation(cve_id, platform)
            if cross_info:
                return cross_info
        
        return info
    
    def create_feed_entry(self, exploitation_info: ExploitationInfo) -> Dict:
        """
        Create a feed entry with exploitation information.
        
        Returns dict suitable for inclusion in SOFA feeds.
        """
        entry = {
            "cve": exploitation_info.cve_id,
            "exploited": exploitation_info.is_exploited,
            "exploitation_confidence": exploitation_info.confidence.value,
            "exploitation_sources": [s.value for s in exploitation_info.sources]
        }
        
        # Add optional fields
        if exploitation_info.affected_platforms:
            entry["affected_platforms"] = list(exploitation_info.affected_platforms)
        
        if exploitation_info.is_targeted_attack:
            entry["targeted_attack"] = True
            
        if exploitation_info.is_physical_attack:
            entry["physical_attack"] = True
            
        if exploitation_info.targeted_versions:
            entry["targeted_versions"] = exploitation_info.targeted_versions
            
        if exploitation_info.notes:
            entry["exploitation_notes"] = exploitation_info.notes
            
        return entry
    
    def analyze_security_release(
        self, 
        release_url: str,
        platform: str = "unknown"
    ) -> Dict[str, Dict]:
        """
        Analyze a complete security release page.
        
        Returns dict mapping CVE IDs to exploitation entries.
        """
        import requests
        
        try:
            response = requests.get(release_url)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            logger.error(f"Failed to fetch {release_url}: {e}")
            return {}
        
        soup = BeautifulSoup(html, "lxml")
        cve_pattern = re.compile(r'CVE-\d{4}-\d{4,7}')
        
        results = {}
        
        # Find all CVE sections
        for element in soup.find_all(text=cve_pattern):
            cves = cve_pattern.findall(str(element))
            
            # Get surrounding context
            parent = element.parent
            context = ""
            if parent:
                # Look for impact description
                for sibling in parent.find_next_siblings(limit=5):
                    text = sibling.get_text() if sibling else ""
                    if "Impact:" in text:
                        context = text
                        break
                
                # Also check parent's text
                if not context:
                    context = parent.get_text()
            
            for cve in cves:
                if cve not in results:
                    info = self.get_exploitation_status(cve, context, platform)
                    results[cve] = self.create_feed_entry(info)
        
        return results


def main():
    """Test the smart KEV detector."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart KEV detection')
    parser.add_argument(
        '--test-url',
        help='Test with a specific security release URL'
    )
    parser.add_argument(
        '--platform',
        default='macOS',
        help='Platform to analyze (macOS, iOS, etc.)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase verbosity'
    )
    
    args = parser.parse_args()
    
    configure_logger(max(1, args.verbose))
    
    detector = SmartKEVDetector()
    
    if args.test_url:
        logger.info(f"Analyzing {args.test_url} for {args.platform}")
        results = detector.analyze_security_release(args.test_url, args.platform)
        
        print(f"\nAnalysis Results for {args.platform}:")
        print("=" * 60)
        
        exploited_cves = {
            cve: info for cve, info in results.items() 
            if info.get("exploited") or info.get("exploitation_sources")
        }
        
        if exploited_cves:
            print(f"\nFound {len(exploited_cves)} CVEs with exploitation indicators:\n")
            for cve, info in exploited_cves.items():
                print(f"{cve}:")
                print(f"  Exploited: {info.get('exploited', False)}")
                print(f"  Confidence: {info.get('exploitation_confidence', 'unknown')}")
                print(f"  Sources: {', '.join(info.get('exploitation_sources', []))}")
                if info.get('exploitation_notes'):
                    print(f"  Notes: {info['exploitation_notes']}")
                if info.get('targeted_attack'):
                    print(f"  Type: Targeted attack")
                print()
        else:
            print("No exploitation indicators found")
    
    # Test cross-platform detection
    print("\nTesting cross-platform detection:")
    
    # Simulate iOS exploitation
    ios_info = detector.get_exploitation_status(
        "CVE-2024-44308",
        "Impact: Apple is aware of a report that this issue may have been actively exploited against versions of iOS before iOS 17.2",
        "iOS"
    )
    
    # Now check for macOS
    macos_info = detector.get_exploitation_status(
        "CVE-2024-44308",
        None,  # No Apple text for macOS
        "macOS"
    )
    
    print(f"\nCVE-2024-44308 on iOS: {ios_info.is_exploited} ({ios_info.sources})")
    print(f"CVE-2024-44308 on macOS: {macos_info.is_exploited} ({macos_info.sources})")
    if macos_info.notes:
        print(f"  Cross-platform note: {macos_info.notes}")


if __name__ == "__main__":
    main()