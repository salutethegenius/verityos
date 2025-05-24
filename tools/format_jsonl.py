import json
from pathlib import Path

agent = "verity"
base_path = Path.home() / "verityos" / "fine_tuning" / agent
curated_dir = base_path / "curated_examples"
jsonl_dir = base_path / "jsonl_ready"
jsonl_dir.mkdir(parents=True, exist_ok=True)

merged = []

for file in curated_dir.glob("*.json"):
    try:
        with open(file) as f:
            samples = json.load(f)
            for s in samples:
                merged.append({
                    "instruction": s["input"],
                    "output": s["output"],
                    "intent": s.get("intent", "unknown"),
                    "agent": s.get("agent", agent)
                })
    except Exception as e:
        print(f"❌ Error processing {file.name}: {e}")

out_path = jsonl_dir / f"{agent}_ft_data.jsonl"

with open(out_path, "w") as f_out:
    for item in merged:
        f_out.write(json.dumps(item) + "\n")

print(f"✅ Saved {len(merged)} samples to {out_path}")