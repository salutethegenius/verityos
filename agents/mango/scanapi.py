# scanapi.py - Mango’s API parser module

import json
import os
from pathlib import Path

def scan_openapi(file_path):
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}

    try:
        with open(file_path, 'r') as f:
            raw = json.load(f)
    except Exception as e:
        return {"error": f"Invalid JSON format: {e}"}

    paths = raw.get("paths", {})
    parsed_endpoints = []

    for path, methods in paths.items():
        for method, details in methods.items():
            entry = {
                "path": path,
                "method": method.upper(),
                "summary": details.get("summary", "No summary"),
                "parameters": [],
                "requestBody": details.get("requestBody", {}).get("content", {})
            }

            for param in details.get("parameters", []):
                entry["parameters"].append({
                    "name": param.get("name"),
                    "in": param.get("in"),
                    "required": param.get("required"),
                    "type": param.get("schema", {}).get("type")
                })

            parsed_endpoints.append(entry)

    return {"endpoints": parsed_endpoints, "total": len(parsed_endpoints)}

def save_scan_result(data, filename="scan_result.json"):
    out_path = Path("/home/ubuntu/verityos/logs/mango/apis/")
    out_path.mkdir(parents=True, exist_ok=True)
    with open(out_path / filename, "w") as f:
        json.dump(data, f, indent=2)
    return str(out_path / filename)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Path to OpenAPI JSON file", required=True)
    args = parser.parse_args()

    result = scan_openapi(args.file)
    if "error" in result:
        print("Error:", result["error"])
    else:
        path = save_scan_result(result)
        print(f"✅ API scan saved to {path}")
        