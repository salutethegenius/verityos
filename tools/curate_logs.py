import os, json
from pathlib import Path

AGENTS = ["verity", "nova", "right", "breeze", "ripple", "minty"]
BASE_DIR = Path.home() / "verityos" / "fine_tuning"

for agent in AGENTS:
    raw_dir = BASE_DIR / agent / "raw_logs"
    curated_dir = BASE_DIR / agent / "curated_examples"
    curated_dir.mkdir(parents=True, exist_ok=True)

    for file in raw_dir.glob("*.json"):
        try:
            with open(file) as f:
                data = json.load(f)

            curated_samples = []

            # Example: Standard memory format with messages
            if isinstance(data, list):
                for entry in data:
                    if "user" in entry and "assistant" in entry:
                        curated_samples.append({
                            "input": entry["user"].strip(),
                            "output": entry["assistant"].strip(),
                            "intent": "auto",  # We'll refine this later
                            "agent": agent,
                            "source_file": file.name
                        })
            elif isinstance(data, dict):
                # e.g., short_term.json structure
                for k, v in data.items():
                    if isinstance(v, dict) and "event" in v:
                        curated_samples.append({
                            "input": v.get("event", "")[:500],  # truncate long text
                            "output": v.get("embedding", "N/A"),
                            "intent": "memory_embedding",
                            "agent": agent,
                            "source_file": file.name
                        })

            out_path = curated_dir / f"{file.stem}_curated.json"
            with open(out_path, "w") as f_out:
                json.dump(curated_samples, f_out, indent=2)

            print(f"✅ Curated {len(curated_samples)} samples from {file.name} for {agent}")

        except Exception as e:
            print(f"❌ Failed to process {file.name} for {agent}: {e}")