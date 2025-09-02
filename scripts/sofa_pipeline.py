#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich>=13.7.0",
#     "typer>=0.9.0",
#     "pydantic>=2.5.0",
#     "httpx>=0.25.0",
# ]
# ///
"""
SOFA Pipeline Orchestrator 
Simple Organized Feed for Apple Software Updates
Manages the complete SOFA data pipeline: gather → fetch → build (v1 & v2)
Uses TOML configuration files
"""

__version__ = "0.1.0"

import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

# Use tomllib for Python 3.11+, fallback to toml for older versions
try:
    import tomllib
except ImportError:
    try:
        import toml as tomllib
    except ImportError:
        tomllib = None

import typer
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree
from rich.text import Text

# Initialize Rich console
console = Console()


def detect_paths():
    """Detect correct paths based on where the script is run from"""
    cwd = Path.cwd()
    script_dir = Path(__file__).parent

    # Check if we're running from repo root (has bin/ and config/ directories)
    if (cwd / "bin").exists() and (cwd / "config").exists():
        # Running from repo root
        return {
            "base_dir": cwd,
            "bin_dir": cwd / "bin",
            "config_dir": cwd / "config",
            "data_dir": cwd / "data",
            "subprocess_cwd": cwd
        }
    # Check if we're running from scripts/ directory
    elif (cwd.parent / "bin").exists() and (cwd.parent / "config").exists():
        # Running from scripts/ directory
        repo_root = cwd.parent
        return {
            "base_dir": repo_root,
            "bin_dir": repo_root / "bin",
            "config_dir": repo_root / "config",
            "data_dir": repo_root / "data",
            "subprocess_cwd": repo_root
        }
    else:
        # Fallback: assume script is in scripts/ and repo structure exists
        repo_root = script_dir.parent
        return {
            "base_dir": repo_root,
            "bin_dir": repo_root / "bin",
            "config_dir": repo_root / "config",
            "data_dir": repo_root / "data",
            "subprocess_cwd": repo_root
        }


# Detect paths once at startup
PATHS = detect_paths()
app = typer.Typer(help=f"SOFA Pipeline Orchestrator v{__version__}")


class PipelineStage(str, Enum):
    """Pipeline stages"""
    GATHER = "gather"
    FETCH = "fetch"
    BUILD = "build"
    BULLETIN = "bulletin"  # Generate bulletin data for frontpage
    RSS = "rss"  # Generate RSS feed
    CVE = "cve"  # Optional CVE processing stage
    ALL = "all"


class GatherSource(str, Enum):
    """Data sources for gathering"""
    KEV = "kev"
    GDMF = "gdmf"
    IPSW = "ipsw"
    XPROTECT = "xprotect"
    BETA = "beta"
    UMA = "uma"


class Product(str, Enum):
    """Products for build"""
    SAFARI = "safari"
    IOS = "ios"
    MACOS = "macos"  # Fixed: was mac-os
    TVOS = "tvos"  # Fixed: was tv-os
    WATCHOS = "watchos"  # Fixed: was watch-os
    VISIONOS = "visionos"  # Fixed: was vision-os


class PipelineConfig(BaseModel):
    """Pipeline configuration model"""
    base_dir: Path = Field(default_factory=lambda: PATHS["base_dir"], description="Base directory")
    data_dir: Path = Field(default_factory=lambda: PATHS["data_dir"], description="Data directory")
    v1_dir: Path = Field(default=Path("v1"), description="v1 output directory")
    v2_dir: Path = Field(default=Path("v2"), description="v2 output directory")
    config_dir: Path = Field(default_factory=lambda: PATHS["config_dir"], description="Config directory")
    bin_dir: Path = Field(default_factory=lambda: PATHS["bin_dir"], description="Binary directory")
    
    gather_sources: List[GatherSource] = Field(
        default=[GatherSource.KEV, GatherSource.GDMF, GatherSource.IPSW, GatherSource.XPROTECT, GatherSource.BETA, GatherSource.UMA],
        description="Sources to gather"
    )
    products: List[Product] = Field(
        default=[
            Product.SAFARI, Product.IOS, Product.MACOS,
            Product.TVOS, Product.WATCHOS, Product.VISIONOS
        ],
        description="Products to build"
    )
    
    class Config:
        use_enum_values = True


class PipelineResult(BaseModel):
    """Pipeline execution result"""
    success: bool
    stage: str
    duration: float
    message: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    outputs: Dict[str, Any] = Field(default_factory=dict)


class SOFAPipeline:
    """SOFA Pipeline orchestrator"""
    
    def __init__(self, config: PipelineConfig = None, enable_logging: bool = True):
        # Load from pipeline.toml if no config provided
        if config is None:
            config = self.load_from_toml()
        self.config = config
        self.results: List[PipelineResult] = []
        
        # Setup logging
        if enable_logging:
            self.setup_logging()
            self.logger = logging.getLogger("sofa_pipeline")
        else:
            self.logger = None
    
    def setup_logging(self) -> None:
        """Setup detailed logging to file"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"sofa_pipeline_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                # Don't add console handler to keep UI clean
            ]
        )
        
        console.print(f"📝 Logging to: {log_file}", style="dim")
    
    def log(self, message: str, level: str = "info") -> None:
        """Log message if logger is available"""
        if self.logger:
            getattr(self.logger, level.lower())(message)
    
    def load_from_toml(self) -> PipelineConfig:
        """Load configuration from pipeline.toml (if exists) or use defaults"""
        toml_path = Path("pipeline.toml")
        if toml_path.exists() and tomllib:
            try:
                if hasattr(tomllib, 'loads'):
                    # toml library (older Python versions)
                    with open(toml_path, "r") as f:
                        toml_config = tomllib.load(f)
                else:
                    # tomllib library (Python 3.11+)
                    with open(toml_path, "rb") as f:
                        toml_config = tomllib.load(f)
                
                # Only override specific fields if present in TOML
                config = PipelineConfig()
                
                # Override base paths if specified
                if "pipeline" in toml_config:
                    if "base_dir" in toml_config["pipeline"]:
                        config.base_dir = Path(toml_config["pipeline"]["base_dir"])
                    if "data_dir" in toml_config["pipeline"]:
                        config.data_dir = Path(toml_config["pipeline"]["data_dir"])
                
                # Override sources if specified
                if "gather" in toml_config and "sources" in toml_config["gather"]:
                    config.gather_sources = [GatherSource(s) for s in toml_config["gather"]["sources"]]
                
                # Override products if specified
                if "products" in toml_config:
                    config.products = [Product(p) for p in toml_config["products"]]
                
                return config
                
            except Exception as e:
                self.log(f"Error loading TOML config: {e}, using defaults", "warning")
        
        return PipelineConfig()  # Return default config
        
    def setup_directories(self) -> None:
        """Create necessary directories"""
        with console.status("[bold green]Setting up directories..."):
            # Create standard data directories for rust-build compatibility
            for dir_path in [
                self.config.data_dir,
                self.config.data_dir / "feeds" / "v1",  # v1 feeds directory
                self.config.data_dir / "feeds" / "v2",  # v2 feeds directory
                self.config.data_dir / "resources",  # for all gathered and fetched data
                self.config.data_dir / "cache",  # for HTML cache
                self.config.config_dir,
                self.config.bin_dir,
            ]:
                dir_path.mkdir(parents=True, exist_ok=True)
        
        console.print("✅ Directories created", style="green")
    
    # Binary copying removed - pipeline now uses binaries in place
    
    def run_gather(self) -> PipelineResult:
        """Run gather stage"""
        start_time = datetime.now()
        errors = []
        outputs = {}
        
        console.rule("Gather")
        
        # Use data/resources directory for gathered data (updated naming)
        output_dir = self.config.data_dir / "resources"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Gathering data...", 
                total=len(self.config.gather_sources)
            )
            
            for source in self.config.gather_sources:
                progress.update(task, description=f"Gathering {source}...")
                
                # Use sofa-gather binary
                binary = self.config.bin_dir / "sofa-gather"
                if not binary.exists():
                    self.log(f"Binary not found: sofa-gather at {binary}", "error")
                    errors.append(f"{source}: Binary sofa-gather not found at {binary}")
                    continue
                
                cmd = [str(binary), source.value]
                
                # Add output dir if not using default
                if output_dir != Path("data/resources"):
                    cmd.extend(["--output", str(output_dir / f"{source.value}_catalog.json")])
                
                # Add --insecure flag for GDMF if needed
                if source == GatherSource.GDMF:
                    # Check if we should use insecure mode
                    apple_root = self.config.config_dir / "AppleRoot.pem"
                    if not apple_root.exists():
                        cmd.append("--insecure")
                        self.log("Using --insecure for GDMF (no AppleRoot.pem found)", "warning")
                
                self.log(f"Running gather command: {' '.join(cmd)}")
                
                try:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=300, cwd=PATHS["subprocess_cwd"]
                    )
                    
                    self.log(f"Gather {source} result - return code: {result.returncode}")
                    if result.stdout:
                        self.log(f"Gather {source} stdout: {result.stdout}")
                    if result.stderr:
                        self.log(f"Gather {source} stderr: {result.stderr}")
                    
                    if result.returncode == 0:
                        outputs[source] = "✅"
                    else:
                        outputs[source] = "❌"
                        error_msg = f"{source}: return code {result.returncode}"
                        if result.stderr:
                            error_msg += f", stderr: {result.stderr[:500]}"
                        if result.stdout:
                            error_msg += f", stdout: {result.stdout[:500]}"
                        errors.append(error_msg)
                except Exception as e:
                    outputs[source] = "❌"
                    error_msg = f"{source}: Exception: {str(e)}"
                    errors.append(error_msg)
                    self.log(error_msg, "error")
                
                progress.advance(task)
        
        duration = (datetime.now() - start_time).total_seconds()
        success = len(errors) == 0
        
        # Display results table
        table = Table(title="Gather Results")
        table.add_column("Source", style="cyan")
        table.add_column("Status", style="green")
        
        for source, status in outputs.items():
            table.add_row(source, status)
        
        console.print(table)
        
        return PipelineResult(
            success=success,
            stage="gather",
            duration=duration,
            errors=errors,
            outputs=outputs
        )
    
    def run_fetch(self, detect_changes: bool = False, detect_cache_changes: bool = False) -> PipelineResult:
        """Run fetch stage with optional change detection
        
        Args:
            detect_changes: Show which releases/CVEs changed
            detect_cache_changes: Show which HTML files changed with URLs
        """
        start_time = datetime.now()
        console.rule("Fetch")
        
        with console.status("[bold green]Fetching Apple security pages..."):
            # Output to data/resources directory (updated naming)
            output_dir = self.config.data_dir / "resources"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Use data/resources for KEV
            kev_file = output_dir / "kev_catalog.json"
            
            # Use sofa-fetch binary
            binary = self.config.bin_dir / "sofa-fetch"
            if not binary.exists():
                binary = Path("bin/sofa-fetch")
            
            cmd = [
                str(binary),
                "--output", str(output_dir / "apple_security_releases.json"),
                "--kev-file", str(kev_file),
                "--cache-dir", str(self.config.data_dir / "cache" / "html"),
                "--preserve-html"
            ]
            
            # Add change detection if requested
            if detect_changes:
                cmd.append("--detect-changes")
                console.print("🔍 Release/CVE change detection enabled", style="cyan")
            
            if detect_cache_changes:
                cmd.append("--detect-cache-changes")
                console.print("🔍 Cache file change detection enabled", style="cyan")
            
            # Config is now embedded in the binary, no need for external config
            
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=600, cwd=PATHS["subprocess_cwd"]
                )
                
                if result.returncode == 0:
                    # Count releases
                    output_file = output_dir / "apple_security_releases.json"
                    if output_file.exists():
                        with open(output_file) as f:
                            data = json.load(f)
                            release_count = len(data.get("releases", []))
                            console.print(f"✅ Fetched {release_count} releases", style="green")
                            
                            return PipelineResult(
                                success=True,
                                stage="fetch",
                                duration=(datetime.now() - start_time).total_seconds(),
                                outputs={"releases": release_count}
                            )
                
                error_msg = f"fetch failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f", stderr: {result.stderr[:500]}"
                if result.stdout:
                    error_msg += f", stdout: {result.stdout[:500]}"
                
                return PipelineResult(
                    success=False,
                    stage="fetch",
                    duration=(datetime.now() - start_time).total_seconds(),
                    errors=[error_msg]
                )
                
            except Exception as e:
                return PipelineResult(
                    success=False,
                    stage="fetch",
                    duration=(datetime.now() - start_time).total_seconds(),
                    errors=[str(e)]
                )
    
    def run_build(self, version: str, use_legacy_v1: bool = False) -> PipelineResult:
        """Run build stage
        
        Args:
            version: Feed version to build (v1 or v2)
            use_legacy_v1: Use Python legacy builder for v1 feeds instead of sofa-build
        """
        start_time = datetime.now()
        errors = []
        outputs = {}
        
        console.rule(f"[bold blue]Stage: Build {version}{' (Legacy Python)' if use_legacy_v1 and version == 'v1' else ''}")
        output_dir = self.config.data_dir / "feeds" / version
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Building {version} feeds...", 
                total=len(self.config.products)
            )
            
            # Use sofa-build all --legacy for v1 if requested
            if use_legacy_v1 and version == "v1":
                progress.update(task, description=f"Building all v1 feeds with legacy mode...")
                
                binary = self.config.bin_dir / "sofa-build"
                if not binary.exists():
                    binary = Path("bin/sofa-build")
                
                # Build all products at once with --legacy flag
                cmd = [
                    str(binary),
                    "all",  # Build all products
                    "-i", str(self.config.data_dir / "resources"),
                    "-o", str(output_dir),  # Output directory
                    "--type", "v1",
                    "--legacy"  # Use legacy builder
                ]
                
                try:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=600, cwd=PATHS["subprocess_cwd"]
                    )
                    
                    if result.returncode == 0:
                        # Check which files were created
                        for product in self.config.products:
                            feed_file = output_dir / f"{product.value}_data_feed.json"
                            if feed_file.exists():
                                outputs[product] = "✅"
                            else:
                                outputs[product] = "❌"
                                errors.append(f"{product}: Output file not created")
                    else:
                        for product in self.config.products:
                            outputs[product] = "❌"
                        error_msg = f"Legacy builder failed: return code {result.returncode}"
                        if result.stderr:
                            error_msg += f", stderr: {result.stderr[:500]}"
                        if result.stdout:
                            error_msg += f", stdout: {result.stdout[:500]}"
                        errors.append(error_msg)
                except Exception as e:
                    for product in self.config.products:
                        outputs[product] = "❌"
                    errors.append(f"Legacy builder exception: {str(e)}")
                
                for _ in self.config.products:
                    progress.advance(task)
            else:
                # Use sofa-build for all products
                for product in self.config.products:
                    progress.update(task, description=f"Building {product} {version}...")
                    
                    # sofa-build uses default data directories
                    binary = self.config.bin_dir / "sofa-build"
                    if not binary.exists():
                        binary = Path("bin/sofa-build")
                    
                    # Build command with product subcommand
                    output_file = output_dir / f"{product.value}_data_feed.json"
                    
                    # ALL products now use the same consistent flags
                    cmd = [
                        str(binary),
                        product.value,  # Product subcommand
                        "-i", str(self.config.data_dir / "resources"),  # Input directory
                        "-f", str(output_file),  # -f for file output (consistent for all)
                        "--type", version  # Feed type v1 or v2 (consistent for all)
                    ]
                    
                    try:
                        result = subprocess.run(
                            cmd, capture_output=True, text=True, timeout=300, cwd=PATHS["subprocess_cwd"]
                        )
                        
                        if result.returncode == 0:
                            # Check output file exists
                            feed_file = output_dir / f"{product.value}_data_feed.json"
                            
                            if feed_file.exists():
                                outputs[product] = "✅"
                            else:
                                outputs[product] = "❌"
                                errors.append(f"{product}: Output file not created")
                        else:
                            outputs[product] = "❌"
                            error_msg = f"{product}: return code {result.returncode}"
                            if result.stderr:
                                error_msg += f", stderr: {result.stderr[:500]}"
                            if result.stdout:
                                error_msg += f", stdout: {result.stdout[:500]}"
                            errors.append(error_msg)
                            
                    except Exception as e:
                        outputs[product] = "❌"
                        errors.append(f"{product}: Exception: {str(e)}")
                    
                    progress.advance(task)
        
        # Display results table
        table = Table(title=f"Build {version} Results")
        table.add_column("Product", style="cyan")
        table.add_column("Status", style="green")
        
        for product, status in outputs.items():
            table.add_row(product, status)
        
        console.print(table)
        
        return PipelineResult(
            success=len(errors) == 0,
            stage=f"build_{version}",
            duration=(datetime.now() - start_time).total_seconds(),
            errors=errors,
            outputs=outputs
        )
    
    def run_bulletin(self) -> PipelineResult:
        """Generate bulletin data for frontpage display"""
        start_time = datetime.now()
        console.rule("[bold magenta]Bulletin Generation")
        
        with console.status("[bold magenta]Generating bulletin data..."):
            # Use sofa-build binary with bulletin subcommand
            binary = self.config.bin_dir / "sofa-build"
            if not binary.exists():
                binary = Path("bin/sofa-build")
            
            if not binary.exists():
                error_msg = "sofa-build binary not found"
                console.print(f"❌ {error_msg}", style="red")
                return PipelineResult(
                    success=False,
                    stage="bulletin",
                    duration=0,
                    errors=[error_msg]
                )
            
            # Output to data/resources directory
            output_dir = self.config.data_dir / "resources"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "bulletin_data.json"
            
            cmd = [
                str(binary),
                "bulletin",
                "-i", str(self.config.data_dir / "resources"),
                "-b", str(output_file)
            ]
            
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=60, cwd=PATHS["subprocess_cwd"]
                )
                
                if result.returncode == 0:
                    if output_file.exists():
                        size = output_file.stat().st_size
                        console.print(f"✅ Bulletin generated ({size:,} bytes)", style="green")
                        
                        # Parse and show summary
                        with open(output_file) as f:
                            bulletin = json.load(f)
                            
                        # Display latest releases
                        table = Table(title="Latest Releases")
                        table.add_column("OS", style="cyan")
                        table.add_column("Version", style="yellow")
                        table.add_column("CVEs Fixed", style="green")
                        table.add_column("Exploited", style="red")
                        
                        latest = bulletin.get("latest_releases", {})
                        for os_name, info in latest.items():
                            if info.get("version"):
                                table.add_row(
                                    os_name.upper(),
                                    info.get("version", ""),
                                    str(info.get("total_cve_count", 0)),
                                    str(info.get("actively_exploited_count", 0))
                                )
                        
                        console.print(table)
                        
                        return PipelineResult(
                            success=True,
                            stage="bulletin",
                            duration=(datetime.now() - start_time).total_seconds(),
                            outputs={"bulletin": str(output_file)}
                        )
                    else:
                        error_msg = "Bulletin file not created"
                        return PipelineResult(
                            success=False,
                            stage="bulletin",
                            duration=(datetime.now() - start_time).total_seconds(),
                            errors=[error_msg]
                        )
                else:
                    error_msg = f"bulletin failed: {result.stderr[:500] if result.stderr else result.stdout[:500]}"
                    return PipelineResult(
                        success=False,
                        stage="bulletin",
                        duration=(datetime.now() - start_time).total_seconds(),
                        errors=[error_msg]
                    )
                    
            except Exception as e:
                return PipelineResult(
                    success=False,
                    stage="bulletin",
                    duration=(datetime.now() - start_time).total_seconds(),
                    errors=[str(e)]
                )
    
    def run_rss(self) -> PipelineResult:
        """Generate RSS feed from Apple security releases"""
        start_time = datetime.now()
        console.rule("[bold purple]RSS Feed Generation")
        
        with console.status("[bold purple]Generating RSS feed..."):
            # Use the Python RSS generator script with uv
            rss_script = Path("scripts/generate_rss.py")
            
            if not rss_script.exists():
                error_msg = "RSS generator script not found at scripts/generate_rss.py"
                console.print(f"❌ {error_msg}", style="red")
                return PipelineResult(
                    success=False,
                    stage="rss",
                    duration=0,
                    errors=[error_msg]
                )
            
            # Output locations
            v1_dir = self.config.data_dir / "feeds" / "v1"
            v1_dir.mkdir(parents=True, exist_ok=True)
            rss_file = v1_dir / "rss_feed.xml"
            
            # Run the script directly since it has uv shebang
            cmd = [
                str(rss_script),
                "--output", str(rss_file),
                "--data-dir", str(self.config.data_dir / "resources"),
                "--include-xprotect"  # Include XProtect updates by default
            ]
            
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=30, cwd=PATHS["subprocess_cwd"]
                )
                
                if result.returncode == 0:
                    if rss_file.exists():
                        size = rss_file.stat().st_size
                        console.print(f"✅ RSS feed generated ({size:,} bytes)", style="green")
                        console.print(f"   📡 Feed location: {rss_file}", style="dim")
                        console.print(f"   🔗 Feed URL: https://sofafeed.macadmins.io/v1/rss_feed.xml", style="dim")
                        
                        # Parse output to show counts
                        output_lines = result.stdout.split('\n')
                        for line in output_lines:
                            if 'Total items:' in line or 'Security updates:' in line or 'XProtect updates:' in line:
                                console.print(f"   {line.strip()}", style="dim")
                        
                        return PipelineResult(
                            success=True,
                            stage="rss",
                            duration=(datetime.now() - start_time).total_seconds(),
                            outputs={"rss_feed": str(rss_file)}
                        )
                    else:
                        error_msg = "RSS feed file not created"
                        return PipelineResult(
                            success=False,
                            stage="rss",
                            duration=(datetime.now() - start_time).total_seconds(),
                            errors=[error_msg]
                        )
                else:
                    error_msg = f"RSS generation failed: {result.stderr[:500] if result.stderr else result.stdout[:500]}"
                    console.print(f"❌ {error_msg}", style="red")
                    return PipelineResult(
                        success=False,
                        stage="rss",
                        duration=(datetime.now() - start_time).total_seconds(),
                        errors=[error_msg]
                    )
                    
            except Exception as e:
                return PipelineResult(
                    success=False,
                    stage="rss",
                    duration=(datetime.now() - start_time).total_seconds(),
                    errors=[str(e)]
                )
    
    def run_cve_pipeline(self, full_mode: bool = False) -> PipelineResult:
        """Run CVE processing pipeline (extract, enrich, index)
        
        Args:
            full_mode: If True, use full enrichment (requires API key). Default is light mode.
        """
        start_time = datetime.now()
        errors = []
        outputs = {}
        
        console.rule("[bold cyan]CVE Processing Pipeline")
        
        # Step 1: Extract CVEs
        console.print("📤 Extracting CVEs from Apple security releases...")
        binary = self.config.bin_dir / "sofa-cve"
        if not binary.exists():
            binary = Path("bin/sofa-cve")
        
        if not binary.exists():
            error_msg = "sofa-cve binary not found"
            console.print(f"❌ {error_msg}", style="red")
            return PipelineResult(
                success=False,
                stage="cve",
                duration=0,
                errors=[error_msg]
            )
        
        # Extract CVEs
        cmd = [str(binary), "extract"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=PATHS["subprocess_cwd"], env=os.environ.copy())
            if result.returncode == 0:
                console.print("✅ CVE extraction complete", style="green")
                outputs["extract"] = "✅"
            else:
                error_msg = f"CVE extract failed: {result.stderr[:500] if result.stderr else result.stdout[:500]}"
                errors.append(error_msg)
                outputs["extract"] = "❌"
        except Exception as e:
            errors.append(f"CVE extract exception: {str(e)}")
            outputs["extract"] = "❌"
        
        # Step 2: Enrich CVEs (default to --light mode, use full if requested)
        if "extract" in outputs and outputs["extract"] == "✅":
            if full_mode:
                console.print("🔍 Enriching CVEs with full vulnerability data (requires API key)...")
                cmd = [str(binary), "enrich", "--resume"]
                timeout = 1800  # 30 min for full enrichment
            else:
                console.print("⚡ Enriching CVEs with lightweight data (fast mode)...")
                cmd = [str(binary), "enrich", "--light"]
                timeout = 300  # 5 min for light enrichment
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=PATHS["subprocess_cwd"], env=os.environ.copy())
                if result.returncode == 0:
                    mode_text = "full" if full_mode else "lightweight"
                    console.print(f"✅ CVE {mode_text} enrichment complete", style="green")
                    outputs["enrich"] = "✅"
                else:
                    error_msg = f"CVE enrich failed: {result.stderr[:500] if result.stderr else result.stdout[:500]}"
                    errors.append(error_msg)
                    outputs["enrich"] = "❌"
            except Exception as e:
                errors.append(f"CVE enrich exception: {str(e)}")
                outputs["enrich"] = "❌"
        
        # Step 3: Index CVEs (always run after extract)
        if "extract" in outputs and outputs["extract"] == "✅":
            console.print("📑 Indexing CVE data...")
            cmd = [str(binary), "index"]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=PATHS["subprocess_cwd"], env=os.environ.copy())
                if result.returncode == 0:
                    console.print("✅ CVE indexing complete", style="green")
                    outputs["index"] = "✅"
                    
                    # Check for output files
                    if outputs.get("enrich") == "✅":
                        cve_file = self.config.data_dir / "feeds" / "cve_enriched.ndjson"
                    else:
                        # Without enrichment, we have the extracted data
                        cve_file = self.config.data_dir / "resources" / "apple_cves_with_context.ndjson"
                    
                    if cve_file.exists():
                        size = cve_file.stat().st_size
                        console.print(f"📊 Created {cve_file.name} ({size:,} bytes)", style="dim")
                else:
                    error_msg = f"CVE index failed: {result.stderr[:500] if result.stderr else result.stdout[:500]}"
                    errors.append(error_msg)
                    outputs["index"] = "❌"
            except Exception as e:
                errors.append(f"CVE index exception: {str(e)}")
                outputs["index"] = "❌"
        
        # Display results table
        table = Table(title="CVE Processing Results")
        table.add_column("Stage", style="cyan")
        table.add_column("Status", style="green")
        
        for stage, status in outputs.items():
            table.add_row(stage, status)
        
        console.print(table)
        
        return PipelineResult(
            success=len(errors) == 0,
            stage="cve",
            duration=(datetime.now() - start_time).total_seconds(),
            errors=errors,
            outputs=outputs
        )
    
    def verify_results(self) -> None:
        """Verify and display results"""
        console.rule("Verify")
        
        # Create results tree
        tree = Tree("📁 Pipeline Output")
        
        # Check data directory
        data_tree = tree.add("📂 data/")
        
        # Check resources directory (main data location)
        resources_tree = data_tree.add("📂 resources/")
        for file in ["kev_catalog.json", "gdmf_cached.json", "ipsw.json", "xprotect.json"]:
            path = self.config.data_dir / "resources" / file
            if path.exists():
                size = path.stat().st_size
                resources_tree.add(f"✅ {file} ({size:,} bytes)")
            else:
                resources_tree.add(f"❌ {file}")
        
        # Check for fetched data in resources
        fetch_file = self.config.data_dir / "resources" / "apple_security_releases.json"
        if fetch_file.exists():
            size = fetch_file.stat().st_size
            resources_tree.add(f"✅ apple_security_releases.json ({size:,} bytes)")
        else:
            resources_tree.add("❌ apple_security_releases.json")
        
        # Check feeds directory
        feeds_tree = data_tree.add("📂 feeds/")
        
        # Check v1 feeds (all products)
        v1_tree = feeds_tree.add("📂 v1/")
        for product in ["safari", "ios", "macos", "tvos", "watchos", "visionos"]:
            feed_file = self.config.data_dir / "feeds" / "v1" / f"{product}_data_feed.json"
            if feed_file.exists():
                size = feed_file.stat().st_size
                v1_tree.add(f"✅ {product}_data_feed.json ({size:,} bytes)")
            else:
                v1_tree.add(f"❌ {product}_data_feed.json")
        
        # Check v2 feeds (all products)
        v2_tree = feeds_tree.add("📂 v2/")
        for product in ["safari", "ios", "macos", "tvos", "watchos", "visionos"]:
            feed_file = self.config.data_dir / "feeds" / "v2" / f"{product}_data_feed.json"
            if feed_file.exists():
                size = feed_file.stat().st_size
                v2_tree.add(f"✅ {product}_data_feed.json ({size:,} bytes)")
            else:
                v2_tree.add(f"❌ {product}_data_feed.json")
        
        console.print(tree)
    
    def auto_setup(self) -> bool:
        """Auto-setup missing configs and essential files"""
        console.print("🔧 Auto-setting up missing components...")
        
        # Starter pack should already be extracted in pre-flight
        # Now just create any missing configs
        console.print("  📝 Creating TOML configs")
        # Create config directory
        self.config.config_dir.mkdir(exist_ok=True, parents=True)
        
        # Config files are no longer needed - binaries have embedded defaults
        # But we'll check for AppleRoot.pem for GDMF
        apple_root = self.config.config_dir / "AppleRoot.pem"
        if not apple_root.exists():
            console.print("  ⚠️  No AppleRoot.pem found - GDMF will use --insecure flag", style="yellow")
        
        # Models directory check
        models_dir = self.config.data_dir / "models"
        if not models_dir.exists():
            console.print("  ⚠️  Models directory missing - assembly may have incomplete device support", style="yellow")
        
        # Check for supported_devices.json
        supported_devices = self.config.data_dir / "models" / "supported_devices.json"
        if not supported_devices.exists():
            console.print("  ⚠️  supported_devices.json missing - device lists will be incomplete", style="yellow")
        
        # Copy additional existing data if available
        self.copy_existing_data()
        
        console.print("✅ Auto-setup completed", style="green")
        return True
    
    def copy_existing_data(self) -> None:
        """Copy existing data files if available"""
        import shutil as sh
        
        # No longer need to copy data - binaries use standard paths
        
        

    def get_binary_path(self, binary_name: str) -> Path:
        """Get the path to a binary from configured bin directory"""
        bin_path = self.config.bin_dir / binary_name
        return bin_path
    
    def print_binary_info(self) -> None:
        """Print information about binaries being used"""
        console.rule("[bold cyan]Binary Information")
        
        # Check for our binaries
        binaries = ["sofa-gather", "sofa-fetch", "sofa-build", "sofa-cve"]
        
        console.print("[bold]Binary paths and timestamps:[/bold]")
        for binary_name in binaries:
            bin_path = self.config.bin_dir / binary_name
            
            if bin_path.exists():
                stat = bin_path.stat()
                mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                size = stat.st_size
                console.print(f"  ✅ {binary_name}: {bin_path} [{size:,} bytes, {mod_time}]", style="green")
            else:
                console.print(f"  ❌ {binary_name}: NOT FOUND", style="red")
        
        console.print("")
    
    def validate_config(self) -> bool:
        """Validate pipeline configuration"""
        console.rule("[bold yellow]Config Validation")
        errors = []
        
        # Check binaries exist in configured bin directory
        binaries = ["sofa-gather", "sofa-fetch", "sofa-build", "sofa-cve"]
        for binary in binaries:
            bin_path = self.config.bin_dir / binary
            if not bin_path.exists():
                errors.append(f"Missing binary: {binary} (checked {self.config.bin_dir}/)")
        
        # Config files are no longer required - binaries have embedded defaults
        # But check for optional AppleRoot.pem
        apple_root = self.config.config_dir / "AppleRoot.pem"
        if not apple_root.exists():
            console.print("  ℹ️  AppleRoot.pem not found - GDMF will use --insecure mode", style="dim")
        
        # Check data directories exist
        required_dirs = [
            (self.config.data_dir / "resources", "Resources directory"),
            (self.config.data_dir / "cache", "Cache directory")
        ]
        for dir_path, description in required_dirs:
            if not dir_path.exists():
                # These will be created, just note it
                console.print(f"  ℹ️  {description} will be created: {dir_path}", style="dim")
        
        # Check for models data
        models_dir = self.config.data_dir / "models"
        supported_devices = models_dir / "supported_devices.json"
        if not supported_devices.exists():
            console.print("  ⚠️  supported_devices.json missing - device lists incomplete", style="yellow")
        
        if errors:
            console.print("❌ Configuration validation failed:", style="red")
            for error in errors:
                console.print(f"  - {error}", style="red")
            return False
        
        console.print("✅ Configuration validated", style="green")
        return True

    def run(self, stages: List[PipelineStage], skip_gather: bool = False, skip_fetch: bool = False, 
            detect_changes: bool = False, detect_cache_changes: bool = False, full_cve: bool = False,
            use_legacy_v1: bool = False) -> None:
        """Run the pipeline
        
        Args:
            stages: List of pipeline stages to run
            skip_gather: Skip gather stage if True
            skip_fetch: Skip fetch stage if True
            detect_changes: Enable change detection for fetch
            detect_cache_changes: Enable cache change detection for fetch
            full_cve: Run full CVE pipeline instead of light mode
            use_legacy_v1: Use Python legacy builder for v1 feeds
        """
        console.print(Panel.fit(
            "[bold blue]SOFA Pipeline Orchestrator[/bold blue]\n"
            "[dim]gather → fetch → build[/dim]",
            border_style="blue"
        ))
        
        # Print binary information first
        self.print_binary_info()
        
        # Stage 1: Pre-flight - Extract starter pack if needed BEFORE validation
        console.rule("[bold yellow]Pre-flight Setup")
        
        # No starter pack needed - binaries have embedded defaults
        console.print("✅ Using embedded defaults in binaries", style="green")
        console.print(f"🔍 Detected paths: bin={PATHS['bin_dir']}, config={PATHS['config_dir']}, data={PATHS['data_dir']}", style="cyan")
        
        # Stage 2: Setup directories
        self.setup_directories()
        
        # Skip binary copying - use binaries as they exist
        console.print("✅ Binaries used in place", style="green")
        
        # Stage 3: Config validation
        console.rule("[bold yellow]Configuration Validation")
        
        console.print("🔍 Validating configuration...")
        if not self.validate_config():
            console.print("⚠️  Configuration incomplete, running auto-setup...", style="yellow")
            self.auto_setup()
            
            console.print("🔍 Re-validating after setup...")
            if not self.validate_config():
                console.print("❌ Pipeline configuration still invalid after auto-setup", style="red")
                sys.exit(1)
        
        console.print("✅ Configuration ready", style="green")
        
        # Run stages
        if PipelineStage.ALL in stages or PipelineStage.GATHER in stages:
            if not skip_gather:
                result = self.run_gather()
                self.results.append(result)
            else:
                console.print("⏭️  Skipping gather stage", style="yellow")
        
        if PipelineStage.ALL in stages or PipelineStage.FETCH in stages:
            if not skip_fetch:
                result = self.run_fetch(detect_changes, detect_cache_changes)
                self.results.append(result)
            else:
                console.print("⏭️  Skipping fetch stage", style="yellow")
        
        # Build stage (creates both v1 and v2)
        if PipelineStage.ALL in stages or PipelineStage.BUILD in stages:
            result = self.run_build("v1", use_legacy_v1=use_legacy_v1)
            self.results.append(result)
            result = self.run_build("v2")
            self.results.append(result)
        
        # Bulletin generation for frontpage
        if PipelineStage.ALL in stages or PipelineStage.BULLETIN in stages:
            result = self.run_bulletin()
            self.results.append(result)
        
        # RSS feed generation
        if PipelineStage.ALL in stages or PipelineStage.RSS in stages:
            result = self.run_rss()
            self.results.append(result)
        
        # Optional CVE processing (default is light mode, use --full-cve for full)
        if PipelineStage.CVE in stages:
            result = self.run_cve_pipeline(full_mode=full_cve)
            self.results.append(result)
        
        # Verify results
        self.verify_results()
        
        # Summary
        console.rule("[bold green]Summary")
        
        total_duration = sum(r.duration for r in self.results)
        success_count = sum(1 for r in self.results if r.success)
        
        summary_table = Table(title="Execution Summary")
        summary_table.add_column("Stage", style="cyan")
        summary_table.add_column("Status", style="green")
        summary_table.add_column("Duration", style="yellow")
        
        for result in self.results:
            status = "✅ Success" if result.success else "❌ Failed"
            summary_table.add_row(
                result.stage,
                status,
                f"{result.duration:.1f}s"
            )
        
        console.print(summary_table)
        
        # Show detailed errors for failed stages
        failed_results = [r for r in self.results if not r.success]
        if failed_results:
            console.rule("[bold red]Failed Stage Details")
            for result in failed_results:
                console.print(f"[bold red]{result.stage} failed:[/bold red]")
                for error in result.errors:
                    console.print(f"  • {error}", style="red")
                console.print("")
        
        if success_count == len(self.results):
            console.print(
                f"\n✅ [bold green]Pipeline completed successfully in {total_duration:.1f}s[/bold green]"
            )
        else:
            console.print(
                f"\n⚠️  [bold yellow]Pipeline completed with {len(self.results) - success_count} failures in {total_duration:.1f}s[/bold yellow]"
            )


@app.command(short_help="Run the SOFA pipeline (use 'run --help' for examples)")
def run(
    stages: List[PipelineStage] = typer.Option(
        [PipelineStage.ALL],
        "--stage",
        "-s",
        help="Stages to run (gather, fetch, build, bulletin, rss, cve, all)"
    ),
    base_dir: Path = typer.Option(
        Path("."),
        "--base-dir",
        "-b",
        help="Base directory for pipeline"
    ),
    skip_gather: bool = typer.Option(
        False,
        "--skip-gather",
        help="Skip gather stage"
    ),
    skip_fetch: bool = typer.Option(
        False,
        "--skip-fetch",
        help="Skip fetch stage"
    ),
    detect_changes: bool = typer.Option(
        False,
        "--detect-changes",
        help="Show which releases/CVEs changed"
    ),
    detect_cache_changes: bool = typer.Option(
        False,
        "--detect-cache-changes",
        help="Show which HTML files changed with URLs"
    ),
    full_cve: bool = typer.Option(
        False,
        "--full-cve",
        help="Use full CVE enrichment (requires API key)"
    ),
    use_legacy_v1: bool = typer.Option(
        False,
        "--use-legacy-v1",
        help="Use legacy builder for v1 feeds via sofa-build all --legacy"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Verbose output"
    ),
):
    """Run the SOFA pipeline with specified stages.
    
    \b
    AVAILABLE STAGES:
    ─────────────────
    gather   : Fetch Apple Security Updates RSS feed
    fetch    : Process releases and download security notes
    build    : Generate SOFA v1 and v2 data feeds
    bulletin : Create security bulletin with recent releases
    rss      : Generate RSS feed from processed data
    cve      : Build CVE database with vulnerability details
    all      : Run entire pipeline (default)
    
    \b
    USAGE EXAMPLES:
    ───────────────
    Run entire pipeline:
      ./scripts/sofa_pipeline.py run
    
    Run single stage:
      ./scripts/sofa_pipeline.py run --stage gather
      ./scripts/sofa_pipeline.py run --stage fetch
      ./scripts/sofa_pipeline.py run --stage build
    
    Run multiple stages:
      ./scripts/sofa_pipeline.py run --stage gather --stage fetch
      ./scripts/sofa_pipeline.py run --stage build --stage bulletin --stage rss
    
    Skip stages:
      ./scripts/sofa_pipeline.py run --skip-gather --skip-fetch
    
    Detect changes:
      ./scripts/sofa_pipeline.py run --stage fetch --detect-changes
      ./scripts/sofa_pipeline.py run --stage fetch --detect-cache-changes
    
    Build CVE database:
      ./scripts/sofa_pipeline.py run --stage cve                # Light mode
      ./scripts/sofa_pipeline.py run --stage cve --full-cve      # Full enrichment
    
    Use legacy v1 builder:
      ./scripts/sofa_pipeline.py run --stage build --use-legacy-v1
    """
    config = PipelineConfig(base_dir=base_dir)
    pipeline = SOFAPipeline(config)
    pipeline.run(stages, skip_gather, skip_fetch, detect_changes, detect_cache_changes, full_cve, use_legacy_v1)


@app.command()
def clean(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be cleaned without actually cleaning"
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompts"
    ),
):
    """Clean all pipeline outputs using each tool's clean command"""
    console.print("🧹 Cleaning pipeline outputs...\n")
    
    config = PipelineConfig()
    pipeline = SOFAPipeline(config, enable_logging=False)
    
    # Tools to clean in order
    tools = [
        ("sofa-fetch", "Fetch outputs"),
        ("sofa-gather", "Gather outputs"),
        ("sofa-build", "Build outputs"),
        ("sofa-cve", "CVE outputs"),
    ]
    
    success_count = 0
    error_count = 0
    
    for tool_name, description in tools:
        console.print(f"[cyan]Cleaning {description}...[/cyan]")
        
        # Build command
        cmd = [str(pipeline.get_binary_path(tool_name)), "clean"]
        
        # Special case for fetch - use --all to clean cache too
        if tool_name == "sofa-fetch":
            cmd.append("--all")
            
        if dry_run:
            cmd.append("--dry-run")
        
        try:
            # For non-dry-run, we need to handle the confirmation
            if not dry_run and yes:
                # Auto-confirm with 'y'
                result = subprocess.run(
                    cmd,
                    input="y\n",
                    text=True,
                    capture_output=True,
                    cwd=pipeline.config.base_dir
                )
            else:
                # Let the tool handle its own prompting
                result = subprocess.run(
                    cmd,
                    cwd=pipeline.config.base_dir
                )
            
            if result.returncode == 0:
                console.print(f"  ✅ {description} cleaned successfully", style="green")
                success_count += 1
            else:
                console.print(f"  ❌ Failed to clean {description}", style="red")
                error_count += 1
                
        except FileNotFoundError:
            console.print(f"  ⚠️  {tool_name} not found, skipping", style="yellow")
        except Exception as e:
            console.print(f"  ❌ Error cleaning {description}: {e}", style="red")
            error_count += 1
    
    # Summary
    console.print(f"\n[bold]Clean Summary:[/bold]")
    console.print(f"  ✅ Success: {success_count} tools")
    if error_count > 0:
        console.print(f"  ❌ Errors: {error_count} tools", style="red")


@app.command()
def info():
    """Show pipeline information"""
    info_panel = Panel.fit(
        "[bold]SOFA Pipeline Information[/bold]\n\n"
        "[cyan]Stages:[/cyan]\n"
        "  • Gather - Collect data from external sources\n"
        "  • Fetch - Scrape Apple security pages\n"
        "  • Build - Generate v1 and v2 feeds for all products\n"
        "  • Bulletin - Generate bulletin data for frontpage display\n"
        "  • RSS - Generate RSS feed for Apple security updates\n"
        "  • CVE - Extract, enrich, and index CVE data (optional)\n\n"
        "[cyan]Sources:[/cyan]\n"
        "  • KEV - CISA Known Exploited Vulnerabilities\n"
        "  • GDMF - Apple Global Device Management Feed\n"
        "  • IPSW - iOS firmware information\n"
        "  • XProtect - Apple XProtect definitions\n"
        "  • Beta - Apple Beta feeds\n"
        "  • UMA - Unified Mac Analytics catalog\n\n"
        "[cyan]Products:[/cyan]\n"
        "  • Safari - Safari browser feeds\n"
        "  • iOS - iOS and iPadOS feeds\n"
        "  • macOS - macOS feeds\n"
        "  • tvOS - Apple TV feeds\n"
        "  • watchOS - Apple Watch feeds\n"
        "  • visionOS - Vision Pro feeds\n\n"
        "[cyan]Utilities:[/cyan]\n"
        "  • check-models - Check for drift between models and resources\n"
        "  • clean - Clean all pipeline outputs\n"
        "  • build-cve-database - Build CVE database",
        border_style="blue"
    )
    console.print(info_panel)


@app.command()
def check_models(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed differences"
    ),
):
    """Check for drift between models and resources directories"""
    console.print("🔍 Checking for drift between models and resources directories...\n")
    
    config = PipelineConfig()
    pipeline = SOFAPipeline(config, enable_logging=False)
    
    # Use sofa-build check-models command
    binary = pipeline.get_binary_path("sofa-build")
    cmd = [str(binary), "check-models"]
    
    if verbose:
        cmd.append("--verbose")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=pipeline.config.base_dir
        )
        
        # Print the output from the command
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(result.stderr, style="red")
        
        # Exit with the same code as the command
        if result.returncode != 0:
            sys.exit(result.returncode)
            
    except FileNotFoundError:
        console.print("❌ sofa-build not found. Please build the project first.", style="red")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Error running check-models: {e}", style="red")
        sys.exit(1)


@app.command()
def build_cve_database(
    full: bool = typer.Option(
        False,
        "--full",
        help="Use full enrichment with external API (requires VULNCHECK_API_KEY)"
    ),
):
    """Build CVE database using sofa-cve pipeline (default: light mode)"""
    # Create pipeline and run CVE stages directly
    config = PipelineConfig()
    pipeline = SOFAPipeline(config)
    
    # Run the CVE processing pipeline
    console.rule("[bold cyan]CVE Database Builder")
    if full:
        console.print("🔍 Running with full enrichment (requires API key)", style="yellow")
    else:
        console.print("⚡ Running in light mode (fast, requires API key)", style="green")
    
    result = pipeline.run_cve_pipeline(full_mode=full)
    
    if result.success:
        console.print("\n✅ CVE database built successfully!", style="green")
        
        # Show where the files were created  
        enriched_file = config.data_dir / "feeds" / "cve_enriched.ndjson"
        extracted_file = config.data_dir / "resources" / "apple_cves_with_context.ndjson"
        
        if enriched_file.exists():
            size = enriched_file.stat().st_size
            console.print(f"📊 Enriched output: {enriched_file} ({size:,} bytes)", style="dim")
        elif extracted_file.exists():
            size = extracted_file.stat().st_size
            console.print(f"📊 Extracted output: {extracted_file} ({size:,} bytes)", style="dim")
    else:
        console.print("\n❌ Failed to build CVE database", style="red")
        for error in result.errors:
            console.print(f"  • {error}", style="red")


@app.command()
def version():
    """Display the SOFA Pipeline version"""
    console.print(f"[bold blue]SOFA Pipeline Orchestrator[/bold blue] v{__version__}")


if __name__ == "__main__":
    app()