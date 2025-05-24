


from pathlib import Path
from datetime import date
import time
from scripts.system_module import get_system_report
from scripts.agent_status_module import render_agent_statuses as get_agent_report

def setup_daily_log_and_memory_sync(config):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    daily_log_file = Path(config["log_path"]) / f"daily_{date.today()}.md"
    if not daily_log_file.exists():
        with open(daily_log_file, "w") as f:
            f.write(f"# 📅 Daily Log – {date.today()}\n\n")
            f.write("## System Check\n")
            f.write(f"{get_system_report()}\n\n")
            f.write("## Agent Check\n")
            f.write(f"{get_agent_report(config)}\n\n")

        memory_file = Path(config["memory_path"]) / "verity" / "memory.txt"
        log_root = Path(config["log_path"]).parent
        agent_dirs = [p for p in log_root.glob("*") if p.is_dir() and p.name != "verity"]
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(memory_file, "a") as mf:
            mf.write(f"\n[{timestamp}] Daily Memory Sync Started\n")
            for agent_dir in agent_dirs:
                log_file = agent_dir / "latest.log"
                if log_file.exists():
                    content = log_file.read_text().strip()
                    if content:
                        mf.write(f"\n[{agent_dir.name}] {content}\n")

        with open(daily_log_file, "a") as f:
            f.write("## Memory Sync Log\n")
            f.write(f"{timestamp} – Daily memory sync complete.\n")

        print(f"\n🗒️ Daily Log Created: {daily_log_file}")
        print(f"🧠 Memory sync complete at {timestamp}.")
        print("🧠 Boss > ", end="", flush=True)