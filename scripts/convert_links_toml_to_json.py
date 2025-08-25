#!/usr/bin/env python3
import toml
import json
from pathlib import Path

def convert_toml_to_json():
    # Read TOML file
    toml_path = Path(__file__).parent.parent / "config" / "essential_links.toml"
    with open(toml_path, "r") as f:
        data = toml.load(f)
    
    # Write JSON file
    json_path = Path(__file__).parent.parent / "data" / "feeds" / "v1" / "essential_links.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Converted {toml_path} to {json_path}")

if __name__ == "__main__":
    convert_toml_to_json()