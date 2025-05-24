from pathlib import Path
import time
import re

def handle_log_commands(user_input, config):
    log_dir = Path(config["log_path"]) / "verity"
    archive_dir = log_dir / "archive"
    agent_tasks_log = log_dir / "agent_tasks.log"

    if user_input == ".log tail verity/agent_tasks.log":
        if not agent_tasks_log.exists():
            return "📭 No log found at verity/agent_tasks.log"
        lines = agent_tasks_log.read_text().splitlines()[-20:]
        return "\n".join(lines)

    elif user_input == ".log clear verity/agent_tasks.log":
        if agent_tasks_log.exists():
            agent_tasks_log.write_text("")
            return "🧹 Cleared verity/agent_tasks.log"
        return "📭 Log file does not exist."

    elif user_input == ".log rotate verity/agent_tasks.log":
        if not agent_tasks_log.exists():
            return "📭 No log file to rotate."
        archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        rotated_file = archive_dir / f"agent_tasks_{timestamp}.log"
        rotated_file.write_text(agent_tasks_log.read_text())
        agent_tasks_log.write_text("")
        return f"🔁 Log rotated and saved as {rotated_file.name}"

    elif user_input.startswith(".log grep "):
        keyword = user_input.split(" ", 2)[2].strip().lower()
        if not agent_tasks_log.exists():
            return "📭 Log file not found."
        matched = [line for line in agent_tasks_log.read_text().splitlines() if keyword in line.lower()]
        if not matched:
            return f"🔎 No matches found for '{keyword}'"
        return "\n".join(matched)

    elif user_input.startswith(".log summary "):
        agent_name = user_input.split(" ", 2)[2].strip().lower()
        if not agent_tasks_log.exists():
            return "📭 No Verity agent log found."
        lines = agent_tasks_log.read_text().splitlines()
        filtered = [line for line in lines if agent_name in line.lower()]
        if not filtered:
            return f"📭 No entries for agent '{agent_name}'"
        return f"🧾 Summary for {agent_name}:\n" + "\n".join(filtered[-10:])

    elif user_input == ".log export":
        dst = Path("/mnt/data/verity_agent_tasks_export.log")
        if not agent_tasks_log.exists():
            return "📭 No log to export."
        dst.write_text(agent_tasks_log.read_text())
        return "📤 Log exported to /mnt/data/verity_agent_tasks_export.log"

    elif user_input == ".log stats":
        if not agent_tasks_log.exists():
            return "📭 agent_tasks.log not found."
        lines = agent_tasks_log.read_text().splitlines()
        agent_counts = {}
        for line in lines:
            match = re.search(r"\[(.*?)\]", line)
            if match:
                timestamped = line.split("] ", 1)[-1]
                if "task log" in timestamped:
                    agent = timestamped.split(" ")[0]
                    agent_counts[agent] = agent_counts.get(agent, 0) + 1
        if not agent_counts:
            return "📭 No task entries found in log."
        report = "\n".join([f"🔹 {agent}: {count} task log(s)" for agent, count in agent_counts.items()])
        return "📊 Log Stats:\n" + report

    return None