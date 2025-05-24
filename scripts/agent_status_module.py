# agent_status_module.py
from pathlib import Path
import yaml

def render_agent_statuses(agent_root="/home/ubuntu/verityos/agents"):
    count = 0
    for agent_dir in sorted(Path(agent_root).iterdir(), key=lambda p: p.name.lower()):
        cfg = Path(agent_dir) / "config.yaml"
        if cfg.exists():
            count += 1
    return count

get_agent_report = render_agent_statuses