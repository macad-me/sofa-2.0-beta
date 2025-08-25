#!/usr/bin/env python3
"""
KEV (Known Exploited Vulnerability) Policy for SOFA feeds.

This module defines how we handle exploitation information to avoid
unnecessary alarms while providing useful security information.

Key principles:
1. Only mark as "actively_exploited" if confirmed on THAT platform
2. Use "exploitation_warning" for cross-platform concerns
3. Provide detailed metadata so users can make informed decisions
"""

from dataclasses import dataclass
from enum import Enum
from typing import Set, Optional, List


class ExploitationLevel(str, Enum):
    """Exploitation severity levels for feed entries."""
    
    ACTIVELY_EXPLOITED = "actively_exploited"  # Confirmed exploited on THIS platform
    EXPLOITATION_WARNING = "exploitation_warning"  # Exploited on OTHER platform
    TARGETED_ATTACK = "targeted_attack"  # Sophisticated targeted attack
    PHYSICAL_ATTACK = "physical_attack"  # Requires physical access
    NO_EXPLOITATION = "no_exploitation"  # No known exploitation


@dataclass
class KEVPolicy:
    """Policy for handling KEV information in feeds."""
    
    platform: str  # Current platform (macOS, iOS, etc.)
    
    def should_mark_as_exploited(
        self,
        cve_platforms: Set[str],
        is_cisa_kev: bool,
        apple_categories: List[str]
    ) -> bool:
        """
        Determine if CVE should be marked as actively exploited.
        
        Only returns True if:
        1. Apple confirms exploitation on THIS platform, OR
        2. In CISA KEV AND affects this platform
        """
        # Check if exploited on this specific platform
        if self.platform in cve_platforms:
            return True
            
        # For CISA KEVs, only mark if it actually affects this platform
        # (CISA doesn't always specify platform)
        if is_cisa_kev and self.platform in cve_platforms:
            return True
            
        return False
    
    def get_exploitation_level(
        self,
        cve_platforms: Set[str],
        is_cisa_kev: bool,
        apple_categories: List[str]
    ) -> ExploitationLevel:
        """
        Get appropriate exploitation level for display.
        """
        # Actively exploited on this platform
        if self.should_mark_as_exploited(cve_platforms, is_cisa_kev, apple_categories):
            # Check for special types
            if "TARGETED_ATTACK" in apple_categories:
                return ExploitationLevel.TARGETED_ATTACK
            elif "PHYSICAL_ATTACK_EXPLOITED" in apple_categories:
                return ExploitationLevel.PHYSICAL_ATTACK
            else:
                return ExploitationLevel.ACTIVELY_EXPLOITED
        
        # Exploited on other platforms - provide warning
        elif cve_platforms and self.platform not in cve_platforms:
            return ExploitationLevel.EXPLOITATION_WARNING
            
        return ExploitationLevel.NO_EXPLOITATION
    
    def create_exploitation_note(
        self,
        cve_platforms: Set[str],
        apple_categories: List[str]
    ) -> Optional[str]:
        """
        Create human-readable exploitation note.
        """
        level = self.get_exploitation_level(
            cve_platforms,
            False,  # Don't need CISA for note
            apple_categories
        )
        
        if level == ExploitationLevel.EXPLOITATION_WARNING:
            # Create helpful cross-platform warning
            other_platforms = cve_platforms - {self.platform}
            if other_platforms:
                platforms_str = ", ".join(sorted(other_platforms))
                return f"Known exploited on: {platforms_str}"
                
        elif level == ExploitationLevel.TARGETED_ATTACK:
            return "Exploited in sophisticated targeted attacks"
            
        elif level == ExploitationLevel.PHYSICAL_ATTACK:
            return "Requires physical device access for exploitation"
            
        return None


class FeedEnrichmentPolicy:
    """Policy for enriching feeds with KEV data."""
    
    @staticmethod
    def enrich_release_entry(
        release: dict,
        platform: str,
        exploitation_data: dict
    ) -> dict:
        """
        Enrich a release entry with KEV data following sensible policies.
        
        Returns enriched release with:
        - actively_exploited_cves: Only CVEs confirmed on THIS platform
        - exploitation_warnings: CVEs exploited on OTHER platforms
        - exploitation_metadata: Detailed info for transparency
        """
        policy = KEVPolicy(platform=platform)
        
        # Categories of CVEs
        actively_exploited = []
        exploitation_warnings = []
        targeted_attacks = []
        physical_attacks = []
        
        # Process each CVE
        for cve in release.get("cves", []):
            if cve not in exploitation_data:
                continue
                
            cve_data = exploitation_data[cve]
            cve_platforms = set(cve_data.get("platforms", []))
            is_cisa = cve_data.get("in_cisa_kev", False)
            categories = cve_data.get("categories", [])
            
            level = policy.get_exploitation_level(
                cve_platforms,
                is_cisa,
                categories
            )
            
            if level == ExploitationLevel.ACTIVELY_EXPLOITED:
                actively_exploited.append(cve)
            elif level == ExploitationLevel.EXPLOITATION_WARNING:
                note = policy.create_exploitation_note(cve_platforms, categories)
                exploitation_warnings.append({
                    "cve": cve,
                    "note": note
                })
            elif level == ExploitationLevel.TARGETED_ATTACK:
                targeted_attacks.append(cve)
                actively_exploited.append(cve)  # Also mark as exploited
            elif level == ExploitationLevel.PHYSICAL_ATTACK:
                physical_attacks.append(cve)
                actively_exploited.append(cve)  # Also mark as exploited
        
        # Add to release
        enriched = release.copy()
        
        # Primary field - only platform-specific exploits
        enriched["actively_exploited_cves"] = actively_exploited
        enriched["actively_exploited_count"] = len(actively_exploited)
        
        # Additional context fields
        if exploitation_warnings:
            enriched["exploitation_warnings"] = exploitation_warnings
            
        if targeted_attacks:
            enriched["targeted_attack_cves"] = targeted_attacks
            
        if physical_attacks:
            enriched["physical_attack_cves"] = physical_attacks
        
        # Calculate rates
        total_cves = len(release.get("cves", []))
        if total_cves > 0:
            enriched["exploitation_rate"] = round(
                len(actively_exploited) / total_cves * 100, 1
            )
            if exploitation_warnings:
                enriched["warning_rate"] = round(
                    len(exploitation_warnings) / total_cves * 100, 1
                )
        else:
            enriched["exploitation_rate"] = 0.0
            
        return enriched


def main():
    """Test the KEV policy."""
    
    # Example: CVE exploited on iOS but we're checking for macOS
    policy = KEVPolicy(platform="macOS")
    
    # Test cases
    test_cases = [
        {
            "cve": "CVE-2024-44308",
            "platforms": {"iOS", "iPadOS"},
            "is_cisa": True,
            "categories": ["ACTIVELY_EXPLOITED"]
        },
        {
            "cve": "CVE-2025-24201",
            "platforms": {"macOS"},
            "is_cisa": False,
            "categories": ["TARGETED_ATTACK", "EXPLOITED"]
        },
        {
            "cve": "CVE-2025-24200",
            "platforms": {"iOS"},
            "is_cisa": True,
            "categories": ["PHYSICAL_ATTACK_EXPLOITED"]
        }
    ]
    
    print("KEV Policy Test Results:")
    print("=" * 60)
    print(f"Platform: {policy.platform}\n")
    
    for test in test_cases:
        print(f"{test['cve']}:")
        print(f"  Platforms: {test['platforms']}")
        print(f"  CISA KEV: {test['is_cisa']}")
        
        should_mark = policy.should_mark_as_exploited(
            test["platforms"],
            test["is_cisa"],
            test["categories"]
        )
        level = policy.get_exploitation_level(
            test["platforms"],
            test["is_cisa"],
            test["categories"]
        )
        note = policy.create_exploitation_note(
            test["platforms"],
            test["categories"]
        )
        
        print(f"  Should mark as exploited: {should_mark}")
        print(f"  Exploitation level: {level.value}")
        if note:
            print(f"  Note: {note}")
        print()


if __name__ == "__main__":
    main()