# /// script
# dependencies = ["requests"]
# ///

import json
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Tuple, Dict, Any

import requests


CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / "gdmf_cached.json"
LOG_FILE = CACHE_DIR / "gdmf_log.json"
CONFIG_DIR = Path("config")
PEM_FILE = CONFIG_DIR / "AppleRoot.pem"
GDMF_URL = "https://gdmf.apple.com/v2/pmv"
USER_AGENT = "macadmins-sofa"


def _canonical_json(data: Any) -> bytes:
    try:
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    except Exception:
        return b""


def compute_hash(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data)).hexdigest()


def check_cache_file(path: Path) -> Tuple[Dict[str, Any], str]:
    if not path.exists():
        return {}, ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, compute_hash(data)
    except Exception as e:
        print(f"Cache read error: {e}")
        return {}, ""


def update_cache(path: Path, data: Dict[str, Any], etag: str) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
        # Write simple etag sidecar
        with open(str(path) + ".etag", "w", encoding="utf-8") as f:
            f.write(etag)
    except Exception as e:
        print(f"Cache write error: {e}")


def write_gdmf_log(path: Path, status_code: int, data: Dict[str, Any], max_entries: int) -> None:
    entry = {
        "ts": int(time.time()),
        "status": status_code,
        "size": len(_canonical_json(data)),
        "keys": list(data.keys())[:10] if isinstance(data, dict) else [],
    }
    logs = []
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                logs = json.load(f)
            if not isinstance(logs, list):
                logs = []
    except Exception as e:
        print(f"Log read error: {e}")
        logs = []
    logs.append(entry)
    logs = logs[-max_entries:]
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Log write error: {e}")


def fetch_gdmf_data() -> Dict[str, Any]:
    """Fetches latest GDMF data using AppleRoot.pem in config/; falls back to cache on failure."""
    live_data: Dict[str, Any] = {}
    cache_file_path: Path = CACHE_FILE
    log_file_path: Path = LOG_FILE
    max_log_entries = 10

    cached_data, cached_etag = check_cache_file(cache_file_path)
    if cached_data:
        print("Validated local cached GDMF data.")
    else:
        cached_data = {}

    headers = {"User-Agent": USER_AGENT}

    pem_path = PEM_FILE.resolve()
    if not pem_path.exists():
        print(f"⚠️  PEM not found at {pem_path}. Request will likely fail TLS verification.")

    try:
        response = requests.get(GDMF_URL, headers=headers, verify=str(pem_path))
        response.raise_for_status()
        live_data = response.json()
        if live_data:
            live_etag = compute_hash(live_data)
            if live_etag != cached_etag:
                update_cache(cache_file_path, live_data, live_etag)
                print("Using live gathered GDMF data and updating cache.")
            else:
                print("Live gathered GDMF data is identical to cached data. No update needed.")
            write_gdmf_log(log_file_path, response.status_code, live_data, max_log_entries)
    except requests.RequestException as gdmf_fetch_err:
        print(f"Request failed: {gdmf_fetch_err}")

    if not live_data:
        print("Attempting to use cached GDMF data due to live fetch failure.")
        status = response.status_code if "response" in locals() and hasattr(response, "status_code") else 666
        if cached_data:
            write_gdmf_log(log_file_path, status, cached_data, max_log_entries)
            live_data = cached_data
        else:
            print("No cached GDMF data available.")
            write_gdmf_log(log_file_path, status, {}, max_log_entries)
    return live_data


def main() -> int:
    print("🔍 Testing GDMF fetch with config/AppleRoot.pem...")
    print(f"Working directory: {Path.cwd()}")
    print(f"Config directory: {CONFIG_DIR.resolve()}")
    print(f"PEM exists: {PEM_FILE.exists()} at {PEM_FILE.resolve()}")
    print(f"Cache path: {CACHE_FILE.resolve()}")

    # Show the key insight: where we are vs where the PEM is
    print(f"")
    print(f"🔍 Path Analysis:")
    print(f"  Current working dir: {Path.cwd()}")
    print(f"  Looking for PEM at:  {PEM_FILE.resolve()}")
    print(f"  PEM actually at:     {Path('../config/AppleRoot.pem').resolve()}")
    print(f"  PEM accessible:      {Path('../config/AppleRoot.pem').exists()}")

    # Check if gather.toml exists and show its certificate path
    gather_toml = Path("../config/gather.toml")
    if gather_toml.exists():
        print(f"gather.toml exists at: {gather_toml.resolve()}")
        try:
            with open(gather_toml, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if 'apple_root_cert' in line:
                        print(f"gather.toml certificate config: {line.strip()}")
        except Exception as e:
            print(f"Error reading gather.toml: {e}")
    else:
        print("gather.toml not found")

    data = fetch_gdmf_data()
    ok = isinstance(data, dict) and bool(data)
    print(f"Result: {'SUCCESS' if ok else 'FAILURE'} - keys: {list(data.keys())[:10] if isinstance(data, dict) else 'n/a'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

