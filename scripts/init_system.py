

import time
from pathlib import Path
import pytz
import psutil
from scripts.config_module import load_config
from scripts.agent_module import get_agent_report

def init_log(logDir: Path) -> Path:
    logDir.mkdir(parents=True, exist_ok=True)
    log_file = logDir / f"session_{int(time.time())}.log"
    log_file.touch()
    return log_file

def write_log(log_file: Path, entry: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {entry}\n")

def initialize_system():
    # Load configuration
    config = load_config()
    # Prepare memory and log directories
    memory_path = Path(config["memory_path"])
    logs_path = Path(config["log_path"])
    memory_path.mkdir(parents=True, exist_ok=True)
    logs_path.mkdir(parents=True, exist_ok=True)
    # Initialize log file
    log_file = init_log(logs_path)
    # Print startup summary
    now = time.strftime("%A, %B %d, %Y – %I:%M %p", time.localtime())
    print("🟢 VerityOS is online and ready.")
    print(f"📅 Date: {now}")
    print(f"🧠 Memory Path: {memory_path}")
    print(f"📂 Logs Path: {logs_path}")
    print(f"🔐 Chat Mode: {config.get('chatmode','OFF').upper()}\n")
    print(f"✅ System Check: CPU Usage: {psutil.cpu_percent(interval=1)}% | RAM Usage: {psutil.virtual_memory().percent}%")
    print(f"✅ Agent Check: {get_agent_report(config)}")
    print("\n🤖 Hello Boss. Verity is standing by.")
    return config, log_file