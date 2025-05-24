

import os
import json
from pathlib import Path
from dotenv import load_dotenv

CONFIG_PATH = "/home/ubuntu/verityos/system.yaml"
DEFAULT_CONFIG = {
    "memory_path": "/home/ubuntu/verityos/memory_system/verity",
    "log_path": "/home/ubuntu/verityos/logs",
    "agents_path": "/home/ubuntu/verityos/agents",
    "data_path": "/home/ubuntu/verityos/data",
}

def load_config():
    from ruamel.yaml import YAML
    yaml = YAML()
    if not os.path.exists(CONFIG_PATH):
        print("⚙️ No system.yaml found, using default config.")
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_PATH, "r") as f:
            config = yaml.load(f)
        if not isinstance(config, dict):
            raise ValueError("Invalid config format.")
        return {**DEFAULT_CONFIG, **config}
    except Exception as e:
        print(f"⚠️ Failed to load config: {e}")
        return DEFAULT_CONFIG

# Load environment variables when this module is imported
load_dotenv()