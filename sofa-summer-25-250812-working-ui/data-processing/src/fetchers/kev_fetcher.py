#!/usr/bin/env python3
"""
CISA Known Exploited Vulnerabilities (KEV) fetcher with caching.
Fetches and caches the KEV catalog from CISA.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

import httpx
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KEVEntry(BaseModel):
    """CISA KEV catalog entry."""
    cveID: str
    vendorProject: str
    product: str
    vulnerabilityName: str
    dateAdded: str
    shortDescription: str
    requiredAction: str
    dueDate: str
    notes: Optional[str] = None
    knownRansomwareCampaignUse: Optional[str] = None


class KEVCatalog(BaseModel):
    """CISA KEV catalog."""
    title: str
    catalogVersion: str
    dateReleased: str
    count: int
    vulnerabilities: List[KEVEntry]


class KEVFetcher:
    """Fetches and caches CISA KEV catalog."""
    
    KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    CACHE_FILE = "cache/kev_catalog.json"
    CACHE_DURATION = timedelta(hours=6)  # Refresh every 6 hours
    
    def __init__(self, cache_dir: Path = Path(__file__).resolve().parent.parent.parent / "data" / "cache"):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "kev_catalog.json"
        self.kev_set: Set[str] = set()
        self.catalog: Optional[KEVCatalog] = None
        
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self.cache_file.exists():
            return False
            
        try:
            with open(self.cache_file) as f:
                cache_data = json.load(f)
                
            cached_time = datetime.fromisoformat(cache_data.get("cached_at", ""))
            now = datetime.now(timezone.utc)
            
            if now - cached_time > self.CACHE_DURATION:
                logger.info("KEV cache expired")
                return False
                
            return True
            
        except Exception as e:
            logger.warning(f"Error checking cache validity: {e}")
            return False
    
    def _load_from_cache(self) -> Optional[KEVCatalog]:
        """Load KEV catalog from cache."""
        try:
            with open(self.cache_file) as f:
                cache_data = json.load(f)
                
            catalog_data = cache_data.get("catalog")
            if catalog_data:
                catalog = KEVCatalog(**catalog_data)
                self.kev_set = {v.cveID for v in catalog.vulnerabilities}
                logger.info(f"Loaded {len(self.kev_set)} KEVs from cache")
                return catalog
                
        except Exception as e:
            logger.warning(f"Error loading from cache: {e}")
            
        return None
    
    def _fetch_from_cisa(self) -> Optional[KEVCatalog]:
        """Fetch KEV catalog from CISA."""
        try:
            logger.info("Fetching KEV catalog from CISA...")
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.KEV_URL)
                response.raise_for_status()
                
            data = response.json()
            catalog = KEVCatalog(**data)
            
            # Cache the data
            cache_data = {
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "catalog": catalog.model_dump()
            }
            
            with open(self.cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)
                
            self.kev_set = {v.cveID for v in catalog.vulnerabilities}
            logger.info(f"Fetched and cached {len(self.kev_set)} KEVs")
            
            return catalog
            
        except Exception as e:
            logger.error(f"Error fetching KEV catalog: {e}")
            return None
    
    def load_kev_catalog(self) -> bool:
        """Load KEV catalog from cache or fetch if needed."""
        # Try cache first
        if self._is_cache_valid():
            self.catalog = self._load_from_cache()
            if self.catalog:
                return True
        
        # Fetch from CISA
        self.catalog = self._fetch_from_cisa()
        return self.catalog is not None
    
    def is_kev(self, cve_id: str) -> bool:
        """Check if a CVE is in the KEV catalog."""
        if not self.kev_set and not self.load_kev_catalog():
            return False
            
        return cve_id in self.kev_set
    
    def get_kev_details(self, cve_id: str) -> Optional[KEVEntry]:
        """Get details for a KEV entry."""
        if not self.catalog and not self.load_kev_catalog():
            return None
            
        for vuln in self.catalog.vulnerabilities:
            if vuln.cveID == cve_id:
                return vuln
                
        return None
    
    def get_apple_kevs(self) -> List[KEVEntry]:
        """Get all Apple-related KEVs."""
        if not self.catalog and not self.load_kev_catalog():
            return []
            
        apple_kevs = []
        for vuln in self.catalog.vulnerabilities:
            if "apple" in vuln.vendorProject.lower() or "apple" in vuln.product.lower():
                apple_kevs.append(vuln)
                
        return apple_kevs
    
    def enrich_cves_with_kev(self, cves: Dict[str, bool]) -> Dict[str, bool]:
        """
        Enrich CVE dictionary with KEV status.
        
        Args:
            cves: Dictionary of CVE IDs with exploitation status from Apple
            
        Returns:
            Updated dictionary with KEV status merged
        """
        if not self.load_kev_catalog():
            return cves
            
        enriched = cves.copy()
        
        for cve_id in enriched:
            # If Apple says it's exploited, keep that
            if enriched[cve_id]:
                continue
                
            # Check if it's in CISA KEV catalog
            if self.is_kev(cve_id):
                enriched[cve_id] = True
                logger.info(f"CVE {cve_id} found in CISA KEV catalog")
                
        return enriched


def main():
    """Test KEV fetcher."""
    fetcher = KEVFetcher()
    
    if fetcher.load_kev_catalog():
        print(f"Loaded {len(fetcher.kev_set)} KEVs")
        
        # Test some CVEs
        test_cves = ["CVE-2024-44308", "CVE-2024-44309", "CVE-2023-42890"]
        for cve in test_cves:
            if fetcher.is_kev(cve):
                details = fetcher.get_kev_details(cve)
                if details:
                    print(f"\n{cve} is in KEV:")
                    print(f"  - {details.vulnerabilityName}")
                    print(f"  - Added: {details.dateAdded}")
            else:
                print(f"{cve} is not in KEV")
        
        # Get Apple KEVs
        apple_kevs = fetcher.get_apple_kevs()
        print(f"\nFound {len(apple_kevs)} Apple-related KEVs")
        for kev in apple_kevs[:5]:  # Show first 5
            print(f"  - {kev.cveID}: {kev.vulnerabilityName}")


if __name__ == "__main__":
    main()