#!/usr/bin/env python3
"""
Component normalizer for CVE categorization.

Maps detailed Apple component names to standardized categories to prevent
endless component proliferation and provide meaningful groupings.
"""

import re
from typing import Optional, Dict, Set


class ComponentNormalizer:
    """Normalize component names to standard categories."""
    
    # Main categories for grouping components
    CATEGORIES = {
        "WebKit": {
            "patterns": [r"webkit", r"javascriptcore", r"web\s*content", r"web\s*inspector", r"safari\s*pdf"],
            "keywords": ["webkit", "javascript", "webrtc", "web content", "web inspector"]
        },
        "Kernel": {
            "patterns": [r"kernel", r"xnu", r"mach", r"bsd"],
            "keywords": ["kernel", "xnu", "mach", "bsd kernel"]
        },
        "Networking": {
            "patterns": [r"network", r"cfnetwork", r"curl", r"wi-?fi", r"bluetooth", r"bonjour"],
            "keywords": ["network", "cfnetwork", "curl", "wifi", "bluetooth", "bonjour", "airplay", "airdrop"]
        },
        "Security": {
            "patterns": [r"security", r"sandbox", r"gatekeeper", r"codesign", r"keychain", r"filevault"],
            "keywords": ["security", "sandbox", "gatekeeper", "codesigning", "keychain", "applemobilefileintegrity", "amfi"]
        },
        "Media": {
            "patterns": [r"core\s*media", r"audio", r"video", r"av\s*foundation", r"image\s*io", r"core\s*image"],
            "keywords": ["coremedia", "coreaudio", "avfoundation", "imageio", "coreimage", "photos", "camera"]
        },
        "Graphics": {
            "patterns": [r"graphics", r"metal", r"core\s*graphics", r"opengl", r"gpu", r"display"],
            "keywords": ["coregraphics", "metal", "gpu", "opengl", "display", "windowserver"]
        },
        "System Services": {
            "patterns": [r"launchd", r"systemconfig", r"directory\s*service", r"spotlight", r"time\s*machine"],
            "keywords": ["launchd", "systemconfiguration", "directoryservice", "spotlight", "timemachine", "coreservices"]
        },
        "File System": {
            "patterns": [r"file\s*system", r"apfs", r"hfs", r"disk", r"storage", r"archive"],
            "keywords": ["filesystem", "apfs", "hfs", "diskarbitration", "diskimages", "archive utility", "sharedfilelist"]
        },
        "Drivers": {
            "patterns": [r"driver", r"kext", r"iokit", r"usb", r"thunderbolt", r"pci"],
            "keywords": ["driver", "kext", "iokit", "usb", "thunderbolt", "intel", "amd", "broadcom"]
        },
        "Applications": {
            "patterns": [r"mail", r"messages", r"facetime", r"safari(?!\s*pdf)", r"finder", r"notes", r"calendar"],
            "keywords": ["mail", "messages", "facetime", "safari", "finder", "notes", "calendar", "reminders", "shortcuts"]
        },
        "Accessibility": {
            "patterns": [r"accessibility", r"voiceover", r"assistive", r"speech"],
            "keywords": ["accessibility", "voiceover", "assistive", "speech", "siri"]
        },
        "Virtualization": {
            "patterns": [r"virtualization", r"hypervisor", r"rosetta", r"boot\s*camp"],
            "keywords": ["virtualization", "hypervisor", "rosetta", "bootcamp"]
        },
        "Package Management": {
            "patterns": [r"installer", r"package", r"software\s*update", r"app\s*store"],
            "keywords": ["installer", "packagekit", "softwareupdate", "appstore"]
        },
        "Developer Tools": {
            "patterns": [r"xcode", r"instruments", r"dtrace", r"lldb", r"swift"],
            "keywords": ["xcode", "instruments", "dtrace", "lldb", "swift", "modelio", "model i/o"]
        },
        "Privacy": {
            "patterns": [r"privacy", r"tcc", r"transparency", r"location\s*services", r"contacts"],
            "keywords": ["privacy", "tcc", "transparency", "location", "contacts", "calendar access"]
        }
    }
    
    # Fallback for uncategorized components
    DEFAULT_CATEGORY = "System"
    
    def __init__(self):
        """Initialize the normalizer with compiled patterns."""
        self.compiled_patterns = {}
        for category, config in self.CATEGORIES.items():
            patterns = [re.compile(pattern, re.IGNORECASE) for pattern in config["patterns"]]
            self.compiled_patterns[category] = {
                "patterns": patterns,
                "keywords": set(k.lower() for k in config["keywords"])
            }
    
    def normalize(self, component: str) -> str:
        """
        Normalize a component name to a standard category.
        
        Args:
            component: Raw component name from Apple security page
            
        Returns:
            Normalized category name
        """
        if not component:
            return self.DEFAULT_CATEGORY
        
        component_lower = component.lower().strip()
        
        # Direct match first (fastest)
        for category, config in self.compiled_patterns.items():
            if component_lower in config["keywords"]:
                return category
        
        # Pattern matching
        for category, config in self.compiled_patterns.items():
            for pattern in config["patterns"]:
                if pattern.search(component_lower):
                    return category
        
        # Special cases and heuristics
        if self._is_driver_component(component_lower):
            return "Drivers"
        elif self._is_app_component(component_lower):
            return "Applications"
        elif self._is_framework_component(component_lower):
            return "System Services"
        
        # Default fallback
        return self.DEFAULT_CATEGORY
    
    def _is_driver_component(self, component: str) -> bool:
        """Check if component appears to be a driver."""
        driver_suffixes = ["driver", "kext", ".kext", "controller"]
        vendor_prefixes = ["intel", "amd", "nvidia", "broadcom", "qualcomm"]
        
        for suffix in driver_suffixes:
            if component.endswith(suffix):
                return True
        
        for prefix in vendor_prefixes:
            if component.startswith(prefix):
                return True
        
        return False
    
    def _is_app_component(self, component: str) -> bool:
        """Check if component appears to be an application."""
        app_suffixes = [".app", "app", "application"]
        
        for suffix in app_suffixes:
            if component.endswith(suffix):
                return True
        
        return False
    
    def _is_framework_component(self, component: str) -> bool:
        """Check if component appears to be a framework."""
        framework_patterns = ["framework", ".framework", "kit", "core", "foundation"]
        
        for pattern in framework_patterns:
            if pattern in component.lower():
                return True
        
        return False
    
    def get_category_stats(self, components: Dict[str, int]) -> Dict[str, Dict]:
        """
        Get statistics for component categories.
        
        Args:
            components: Dict of component names to counts
            
        Returns:
            Dictionary with category statistics
        """
        category_stats = {}
        unmapped = []
        
        for component, count in components.items():
            category = self.normalize(component)
            
            if category not in category_stats:
                category_stats[category] = {
                    "count": 0,
                    "components": []
                }
            
            category_stats[category]["count"] += count
            category_stats[category]["components"].append(component)
            
            if category == self.DEFAULT_CATEGORY:
                unmapped.append(component)
        
        # Sort by count
        sorted_stats = dict(sorted(category_stats.items(), 
                                 key=lambda x: x[1]["count"], 
                                 reverse=True))
        
        # Add unmapped list for debugging
        if unmapped:
            sorted_stats["_unmapped"] = unmapped
        
        return sorted_stats
    
    def suggest_category(self, component: str) -> Dict[str, str]:
        """
        Suggest a category for a component with reasoning.
        
        Useful for debugging and improving mappings.
        """
        result = {
            "component": component,
            "category": self.normalize(component),
            "reason": ""
        }
        
        component_lower = component.lower().strip()
        
        # Check what matched
        for category, config in self.compiled_patterns.items():
            if component_lower in config["keywords"]:
                result["reason"] = f"Keyword match: '{component_lower}' in {category}"
                break
            
            for pattern in config["patterns"]:
                if pattern.search(component_lower):
                    result["reason"] = f"Pattern match: '{pattern.pattern}' in {category}"
                    break
        
        if not result["reason"]:
            if result["category"] != self.DEFAULT_CATEGORY:
                result["reason"] = "Heuristic match"
            else:
                result["reason"] = "No match found, using default"
        
        return result


def main():
    """Test the component normalizer."""
    import json
    
    normalizer = ComponentNormalizer()
    
    # Test components
    test_components = [
        "WebKit",
        "WebKit PDF",
        "JavaScriptCore",
        "Kernel",
        "XNU",
        "Safari",
        "Safari Private Browsing",
        "CoreMedia",
        "CoreMedia Playback",
        "PackageKit",
        "AppleMobileFileIntegrity",
        "Intel Graphics Driver",
        "AMD Display Driver",
        "Disk Images",
        "DiskArbitration",
        "Archive Utility",
        "Shortcuts",
        "Model I/O",
        "libxpc",
        "dyld",
        "Unknown Component XYZ"
    ]
    
    print("Component Normalization Test")
    print("=" * 60)
    
    for component in test_components:
        category = normalizer.normalize(component)
        print(f"{component:30} → {category}")
    
    print("\n" + "=" * 60)
    print("Category Statistics")
    print("=" * 60)
    
    # Simulate component counts
    component_counts = {comp: 1 for comp in test_components}
    stats = normalizer.get_category_stats(component_counts)
    
    for category, data in stats.items():
        if category != "_unmapped":
            print(f"\n{category}: {data['count']} CVEs")
            print(f"  Components: {', '.join(data['components'][:5])}")
            if len(data['components']) > 5:
                print(f"  ... and {len(data['components']) - 5} more")


if __name__ == "__main__":
    main()