#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich>=13.7.0",
#     "typer>=0.9.0",
# ]
# ///
"""
SOFA Pipeline - Simplified Version
Works reliably from processing folder or repo root.
No complex path detection, no TOML parsing, just direct binary calls.
"""

__version__ = "0.2.0"

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List
import typer

from rich.console import Console
from rich.panel import Panel

console = Console()

def run_stage(stage: str, description: str) -> bool:
    """Run a single pipeline stage and return success"""
    console.print(f"\n🎯 STAGE: {stage.upper()} - {description}")
    
    start_time = datetime.now()
    
    if stage == "gather":
        # Run sofa-gather all with continue-on-error
        cmd = ["./bin/sofa-gather", "all", "--continue-on-error"]
        
    elif stage == "fetch":
        # Run sofa-fetch with explicit paths
        cmd = [
            "./bin/sofa-fetch",
            "--output", "data/resources/apple_security_releases.json",
            "--kev-file", "data/resources/kev_catalog.json", 
            "--cache-dir", "data/cache/html",
            "--preserve-html"
        ]
        
    elif stage == "build":
        # Run all builds in sequence
        products = ["safari", "ios", "macos", "tvos", "watchos", "visionos"]
        
        # Create feed directories
        Path("data/feeds/v1").mkdir(parents=True, exist_ok=True)
        Path("data/feeds/v2").mkdir(parents=True, exist_ok=True)
        
        # Build v1 feeds
        console.print("🔧 Building v1 feeds...")
        for product in products:
            cmd = [
                "./bin/sofa-build", product,
                "-i", "data/resources",
                "-f", f"data/feeds/v1/{product}_data_feed.json",
                "--type", "v1"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                console.print(f"  ✅ {product} v1 completed")
            else:
                console.print(f"  ❌ {product} v1 failed: {result.stderr[:200]}")
                
        # Build v2 feeds  
        console.print("🔧 Building v2 feeds...")
        for product in products:
            cmd = [
                "./bin/sofa-build", product,
                "-i", "data/resources", 
                "-f", f"data/feeds/v2/{product}_data_feed.json",
                "--type", "v2"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                console.print(f"  ✅ {product} v2 completed")
            else:
                console.print(f"  ❌ {product} v2 failed: {result.stderr[:200]}")
                
        return True
        
    elif stage == "bulletin":
        # Generate bulletin data
        cmd = [
            "./bin/sofa-build", "bulletin",
            "-i", "data/resources",
            "-b", "data/resources/bulletin_data.json"
        ]
        
    elif stage == "rss":
        # Generate RSS feed
        Path("data/feeds/v1").mkdir(parents=True, exist_ok=True)
        cmd = [
            "./scripts/generate_rss.py",
            "--data-dir", "data/resources",
            "--output", "data/feeds/v1/rss_feed.xml",
            "--include-xprotect",
            "--include-beta",
            "--verbose"
        ]
        
    else:
        console.print(f"❌ Unknown stage: {stage}")
        return False
        
    # Run the command (except build which is handled above)
    if stage != "build":
        console.print(f"🚀 Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                duration = (datetime.now() - start_time).total_seconds()
                console.print(f"✅ {stage.upper()} completed in {duration:.1f}s")
                
                # Show relevant output
                if result.stdout and any(keyword in result.stdout.lower() for keyword in ["✓", "success", "completed", "generated"]):
                    console.print("📋 Key output:")
                    for line in result.stdout.split('\n')[-10:]:
                        if line.strip():
                            console.print(f"  {line}")
                            
                return True
            else:
                console.print(f"❌ {stage.upper()} failed (exit code {result.returncode})")
                if result.stderr:
                    console.print(f"Error: {result.stderr[:500]}")
                if result.stdout:
                    console.print(f"Output: {result.stdout[:500]}")
                return False
                
        except subprocess.TimeoutExpired:
            console.print(f"❌ {stage.upper()} timed out")
            return False
        except Exception as e:
            console.print(f"❌ {stage.upper()} exception: {e}")
            return False

app = typer.Typer(help=f"SOFA Pipeline Simplified v{__version__}")

@app.command()
def run(
    stage: str = typer.Argument("all", help="Stage to run: gather, fetch, build, bulletin, rss, all")
):
    """Run SOFA pipeline stage(s) with simple, reliable approach"""
    
    console.print(Panel.fit(
        "[bold blue]SOFA Pipeline Simplified[/bold blue]\n"
        "[dim]Direct binary calls, no complex path detection[/dim]",
        border_style="blue"
    ))
    
    # Verify we're in the right place
    if not Path("bin").exists() or not Path("config").exists():
        console.print("❌ Must run from processing folder or repo root (needs bin/ and config/)", style="red")
        console.print(f"📍 Current directory: {Path.cwd()}")
        console.print("📊 Available directories:")
        for item in Path.cwd().iterdir():
            if item.is_dir():
                console.print(f"  - {item.name}/")
        sys.exit(1)
        
    # Show environment
    console.print(f"📍 Working from: {Path.cwd()}")
    console.print("📊 Environment check:")
    console.print(f"  - bin/ exists: {Path('bin').exists()}")
    console.print(f"  - config/ exists: {Path('config').exists()}")
    console.print(f"  - data/ exists: {Path('data').exists()}")
    
    # Create necessary directories
    Path("data/resources").mkdir(parents=True, exist_ok=True)
    Path("data/cache").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # Stages to run
    if stage == "all":
        stages = ["gather", "fetch", "build", "bulletin", "rss"]
    else:
        stages = [stage]
        
    success_count = 0
    
    for stage_name in stages:
        stage_descriptions = {
            "gather": "Collect data from all sources",
            "fetch": "Process Apple security releases",
            "build": "Generate v1 and v2 feeds", 
            "bulletin": "Create bulletin data",
            "rss": "Generate RSS feed"
        }
        
        if run_stage(stage_name, stage_descriptions.get(stage_name, "")):
            success_count += 1
        else:
            console.print(f"\n❌ Pipeline failed at stage: {stage_name}", style="red")
            if stage == "all":
                console.print("Continuing with remaining stages...", style="yellow")
            else:
                sys.exit(1)
                
    # Summary
    console.print(f"\n📊 Pipeline Summary:")
    console.print(f"  ✅ Successful stages: {success_count}/{len(stages)}")
    
    if success_count == len(stages):
        console.print("🎉 All stages completed successfully!", style="green")
    else:
        console.print(f"⚠️ {len(stages) - success_count} stage(s) failed", style="yellow")
        
@app.command()
def check():
    """Check environment and show file status"""
    console.print("🔍 Environment Check")
    console.print("==================")
    
    console.print(f"📍 Current directory: {Path.cwd()}")
    console.print(f"📊 Directory structure:")
    
    dirs_to_check = ["bin", "config", "data", "scripts", "logs"]
    for dir_name in dirs_to_check:
        dir_path = Path(dir_name)
        if dir_path.exists():
            console.print(f"  ✅ {dir_name}/")
            if dir_name == "bin":
                binaries = list(dir_path.glob("sofa-*"))
                console.print(f"     - {len(binaries)} binaries")
            elif dir_name == "data":
                if (dir_path / "resources").exists():
                    resources = list((dir_path / "resources").glob("*.json"))
                    console.print(f"     - resources: {len(resources)} files")
        else:
            console.print(f"  ❌ {dir_name}/")
            
if __name__ == "__main__":
    app()