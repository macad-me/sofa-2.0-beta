#!/usr/bin/env python3
"""
Pydantic models for SOFA feed data structures.
Ensures strict validation and backward compatibility with original formats.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict


class OSType(str, Enum):
    """Supported OS types."""
    MACOS = "macOS"
    IOS = "iOS"
    IPADOS = "iPadOS"
    WATCHOS = "watchOS"
    TVOS = "tvOS"
    VISIONOS = "visionOS"
    SAFARI = "Safari"


class RetentionMode(str, Enum):
    """Retention policy modes."""
    ALL = "all"
    LAST_N_MAJOR = "last_n_major"


class RetentionPolicy(BaseModel):
    """Retention policy configuration."""
    mode: RetentionMode
    last_n: Optional[int] = None
    allow_pins_outside_window: bool = False


class DeviceModel(BaseModel):
    """Device model information."""
    MarketingName: str
    SupportedOS: List[str]
    OSVersions: List[int]


class XProtectInfo(BaseModel):
    """XProtect component information."""
    model_config = ConfigDict(extra="allow")
    
    ReleaseDate: str
    
    @field_validator("ReleaseDate")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Ensure date is in ISO format."""
        if v and v != "Unknown":
            try:
                # Parse and reformat to ensure ISO format
                if "T" not in v:
                    dt = datetime.strptime(v, "%Y-%m-%d")
                    return dt.isoformat() + "Z"
            except:
                pass
        return v


class InstallationApp(BaseModel):
    """Installation application info (UMA/IPSW)."""
    title: Optional[str] = None
    version: Optional[str] = None
    build: Optional[str] = None
    apple_slug: Optional[str] = None
    url: Optional[str] = None
    macos_ipsw_url: Optional[str] = None
    macos_ipsw_build: Optional[str] = None
    macos_ipsw_version: Optional[str] = None
    macos_ipsw_apple_slug: Optional[str] = None


class SecurityRelease(BaseModel):
    """Security release information."""
    UpdateName: str
    ProductName: str
    ProductVersion: str
    ReleaseDate: str
    ReleaseType: str = "OS"  # OS, RSR_x, Config, Remediator, Plug-in
    SecurityInfo: Optional[str] = None
    SupportedDevices: List[str] = Field(default_factory=list)
    CVEs: Dict[str, bool] = Field(default_factory=dict)
    ActivelyExploitedCVEs: List[str] = Field(default_factory=list)
    UniqueCVEsCount: int = 0
    DaysSincePreviousRelease: Optional[int] = None
    
    @field_validator("ReleaseDate")
    @classmethod
    def format_release_date(cls, v: str) -> str:
        """Ensure release date is in ISO format."""
        if not v or v == "Unknown":
            return v
        
        if "T" in v and v.endswith("Z"):
            return v  # Already in ISO format
        
        # Handle various date formats
        formats = ["%Y-%m-%d", "%d %b %Y", "%B %d, %Y"]
        for fmt in formats:
            try:
                dt = datetime.strptime(v, fmt)
                return dt.isoformat() + "Z"
            except ValueError:
                continue
        
        return v  # Return as-is if no format matches


class LatestVersion(BaseModel):
    """Latest version information for an OS."""
    ProductVersion: str
    Build: str
    ReleaseDate: str
    ExpirationDate: str = ""
    SupportedDevices: List[str] = Field(default_factory=list)
    SecurityInfo: Optional[str] = None
    CVEs: Dict[str, bool] = Field(default_factory=dict)
    ActivelyExploitedCVEs: List[str] = Field(default_factory=list)
    UniqueCVEsCount: int = 0
    
    @field_validator("ReleaseDate", "ExpirationDate")
    @classmethod
    def format_dates(cls, v: str) -> str:
        """Format dates to ISO format."""
        if not v or v in ("Unknown", ""):
            return v
        
        if v == "Preinstalled":
            return "2021-10-25T00:00:00Z"
        
        if "T" in v and v.endswith("Z"):
            return v
        
        formats = ["%Y-%m-%d", "%d %b %Y", "%B %d, %Y"]
        for fmt in formats:
            try:
                dt = datetime.strptime(v, fmt)
                return dt.isoformat() + "Z"
            except ValueError:
                continue
        
        return v


class SupportedModel(BaseModel):
    """Supported model information."""
    Model: str
    URL: str
    Identifiers: Dict[str, str]


class OSVersion(BaseModel):
    """OS version with all associated data."""
    OSVersion: str  # e.g., "Sequoia 15", "18"
    Latest: Optional[LatestVersion] = None
    SecurityReleases: List[SecurityRelease] = Field(default_factory=list)
    SupportedModels: List[SupportedModel] = Field(default_factory=list)


class MacOSFeed(BaseModel):
    """Complete macOS feed structure."""
    UpdateHash: str
    OSVersions: List[OSVersion]
    XProtectPayloads: Optional[Dict[str, Any]] = None
    XProtectPlistConfigData: Optional[Dict[str, Any]] = None
    Models: Optional[Dict[str, DeviceModel]] = None
    InstallationApps: Optional[Dict[str, Any]] = None


class IOSFeed(BaseModel):
    """Complete iOS/iPadOS/tvOS/watchOS/visionOS feed structure."""
    UpdateHash: str
    OSVersions: List[OSVersion]


class GDMFAsset(BaseModel):
    """GDMF asset information."""
    ProductVersion: str
    Build: str
    PostingDate: str
    ExpirationDate: Optional[str] = ""
    SupportedDevices: List[str] = Field(default_factory=list)


class GDMFData(BaseModel):
    """GDMF data structure."""
    PublicAssetSets: Dict[str, List[GDMFAsset]] = Field(default_factory=dict)
    AssetSets: Dict[str, List[GDMFAsset]] = Field(default_factory=dict)


class CachedData(BaseModel):
    """Cached data with etag."""
    etag: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None


class RSSFeedEntry(BaseModel):
    """RSS feed entry for updates."""
    UpdateName: str
    ProductName: str
    ProductVersion: str
    ReleaseType: str
    ReleaseDate: str
    UniqueCVEsCount: Optional[int] = None
    DaysSincePreviousRelease: Optional[int] = None


class TimestampData(BaseModel):
    """Timestamp tracking for feeds."""
    LastCheck: str
    UpdateHash: str