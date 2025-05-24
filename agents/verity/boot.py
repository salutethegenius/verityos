# VerityOS boot.py (v1.6.5 – OpenAI, Memory, Learned, System Greeting)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pytz
import subprocess
chat_mode = True
import time

# Boot timer start
boot_start = time.time()

# === System Report Import ===
from scripts.system_module import get_system_report

# Add memory imports
import yaml
import os
import time
from scripts.config_module import load_config
from dotenv import load_dotenv
from collections import Counter
import collections
import re
from datetime import datetime
import psutil # type: ignore
# === Logger Module import ===
from scripts.logger_module import init_log, write_log
# === Helper: Nassau Time ===
def get_nassau_time():
    return datetime.now(pytz.timezone("America/Nassau")).strftime("%A, %B %d, %Y – %I:%M %p")

from llm_router import query_model
import string
# === UI Modules ===
from scripts.ui_module import render_startup_summary
from scripts.agent_status_module import render_agent_statuses
from scripts.log_memory_module import setup_daily_log_and_memory_sync
from scripts.task_runner_module import execute_auto_tasks
# === Memory Core commands ===
from memory_core import build_index_from_folder, get_combined_context
# === Agent Module commands ===
from scripts.agent_module import handle_agent_commands, get_agent_report

# === Breeze News Scraper ===
from scripts.breeze_module import run_breeze_scraper
# === Builder Module commands ===
from agents.right.agent_builder import build_agent_boot
from agents.right.agent_builder import parse_command as builder_parse_command
# === Task Module commands ===
from scripts.task_module import handle_task_commands
# === Agenda Module commands ===
from scripts.agenda_module import handle_agenda_commands
# === Log Module commands ===
from scripts.log_module import handle_log_commands
# === Memory Core Module commands ===
from scripts.memory_core_module import handle_memory_core_commands
# === SOP Module commands ===
from scripts.sop_module import handle_sop_commands

# === Load environment ===



# === Help Menu ===
def get_help():
    help_items = [
        ("Core Commands", [
            (".help", "Show this help menu"),
            (".intro", "Display VerityOS startup summary"),
            (".status", "System CPU and RAM usage"),
            (".agents", "List online agents"),
            (".chatmode on/off", "Toggle chat interaction mode"),
            (".exit", "Exit VerityOS"),
        ]),
        ("Memory System", [
            (".buildindex [folder]", "Create memory index from Markdown and TXT files"),
            (".ask [question] or natural chat", "Ask or Polish Verity for insights"),
            (".sync memory", "Sync Verity memory with agent logs"),
            (".synclogs", "Manually sync all agent logs to memory"),
        ]),
        ("Notes", [
            (".note", "Add note to memory"),
        ]),
        ("Log System", [
            (".log", "Log system overview"),
            (".log help", "Show log commands"),
        ]),
        ("Agents", [
            (".agent", "Agent tools"),
            (".activate agent [name]", "Launch agent in background"),
            (".generate agent [name]", "Scaffold new agent"),
            (".simulate build [name]", "Simulate agent manifest"),
            (".build agent [name]", "Build full agent with config, boot, and script"),
            (".export agent [name]", "Export agent bundle"),
            (".check agent [name]", "Validate agent manifest"),
            (".recall agent [name]", "Show agent memory"),
            (".note agent [name] [note]", "Append note to agent"),
            (".log summary [agent]", "Agent log summary"),
        ]),
        ("Tasks", [
            (".task", "View tasks"),
            (".task create [name]", "Create new task"),
            (".assign [task] to [agent]", "Assign task to agent"),
            (".process builder_task", "Process queued builder task"),
            (".task execute [agent]", "Execute all assigned tasks"),
            (".agent tasks [agent]", "List agent tasks"),
        ]),
        ("Agenda", [
            (".agenda", "View agenda commands"),
            (".load agenda [file]", "Load tasks from file"),
            (".start agenda", "Display current agenda"),
            (".done [#]", "Mark task done"),
            (".undo [#]", "Undo completed task"),
            (".edit agenda [#] [new text]", "Edit a task line"),
            (".archive agenda", "Archive current agenda"),
            (".list archives", "List agenda archives"),
            (".load archive [name]", "Restore archived agenda"),
            (".delete archive [name]", "Remove archived agenda"),
        ]),
        ("SOPs", [
            (".sop list [agent]", "List SOPs for agent"),
            (".sop show [agent] [sop]", "View SOP details"),
        ]),
        ("System Tools", [
            (".new agent", "Create new agent (interactive)"),
        ]),
    ]

    output = ["Available Commands:\n"]
    for group_name, commands in help_items:
        output.append(f"== {group_name} ==")
        output.extend([f"{cmd:<30} {desc}" for cmd, desc in commands])
        output.append("")  # Add spacing between groups
    return "\n".join(output)

# === Command Logic ===

## get_agent_report is now imported from scripts.agent_module




def selftest(config):
    output = []
    passed = True

    # Check memory path
    memory_path = Path(config["memory_path"])
    if memory_path.exists():
        output.append(f"✅ Memory path exists: {memory_path}")
    else:
        output.append(f"❌ Memory path missing: {memory_path}")
        passed = False

    # Check log path
    log_path = Path(config["log_path"])
    if log_path.exists():
        output.append(f"✅ Log path exists: {log_path}")
    else:
        output.append(f"❌ Log path missing: {log_path}")
        passed = False

    # Check agents folder
    agents_path = Path("/home/ubuntu/verityos/agents")
    if agents_path.exists():
        output.append(f"✅ Agents folder exists: {agents_path}")
    else:
        output.append(f"❌ Agents folder missing: {agents_path}")
        passed = False

    # Check system.yaml
    system_path = Path("/home/ubuntu/verityos/system.yaml")
    if system_path.exists():
        output.append(f"✅ system.yaml found.")
    else:
        output.append(f"❌ system.yaml is missing.")
        passed = False

    return "\n".join(output) + ("\n\n🟢 All checks passed." if passed else "\n\n🔥 Some checks failed.")

# === OpenAI Chat with Memory Awareness ===
def chat_openai(prompt, config):
    memory_file = Path(config.get("memory_path", "/home/ubuntu/verityos/memory")) / "verity_daily_logs" / "memory.txt"
    memory_content = memory_file.read_text() if memory_file.exists() else "No memory yet."
    full_prompt = f"""
You are Verity, an AI OS assistant with task memory and insight recall.
Here is your current memory:
---
{memory_content}
---
Only respond based on what you’ve learned from the Boss. Use notes and learned data where relevant.
"""
    return query_model(full_prompt.strip())

# === Summarization Helper for Conversation History ===
def summarize_history(entries: list[str]) -> str:
    # Summarize a list of messages into a single concise bullet list
    prompt = "Summarize the following conversation history into 3 bullet points:\n" + "\n".join(entries)
    summary = query_model(prompt)
    return summary.strip()

# === Command Parser ===
def parse_command(user_input, config):
    config.setdefault("chatmode", "on")
    config.setdefault("memory_path", "/home/ubuntu/verityos/memory")
    config.setdefault("log_path", "/home/ubuntu/verityos/logs")
    # === Breeze Scraper Command ===
    if user_input.startswith(".breeze"):
        parts = user_input.split()
        if len(parts) == 2 and parts[1] in ["press", "gov"]:
            run_breeze_scraper(parts[1])
            return f"✅ Breeze scraper launched for: {parts[1]}"
        else:
            return "Usage: .breeze [press|gov]"

    # === Agent Module Delegation ===
    result = handle_agent_commands(user_input, config)
    if result is not None:
        return result
    # === Task Module Delegation ===
    result = handle_task_commands(user_input, config)
    if result is not None:
        return result
    # === Agenda Module Delegation ===
    result = handle_agenda_commands(user_input, config)
    if result is not None:
        return result
    # === Log Module Delegation ===
    result = handle_log_commands(user_input, config)
    if result is not None:
        return result
    # === Memory Core Module Delegation ===
    result = handle_memory_core_commands(user_input)
    if result is not None:
        return result
    # === SOP Management Commands ===
    result = handle_sop_commands(user_input)
    if result is not None:
        return result
    # === Generate Agent Structure Command ===
    elif user_input.startswith(".generate agent "):
        agent_name = user_input.split(" ", 2)[2].strip()
        base_path = Path(f"/home/ubuntu/verityos/agents/{agent_name}")
        memory_path = Path(f"/home/ubuntu/verityos/memory/{agent_name}")
        log_path = Path(config["log_path"]).parent / agent_name

        # Create directories
        base_path.mkdir(parents=True, exist_ok=True)
        memory_path.mkdir(parents=True, exist_ok=True)
        log_path.mkdir(parents=True, exist_ok=True)

        # Create boot.py
        boot_path = base_path / "boot.py"
        if not boot_path.exists():
            boot_code = f'''# {agent_name} boot.py generated by VerityOS
print("🔧 {agent_name} booted. Ready to serve Boss.")
'''
            boot_path.write_text(boot_code)

        # Create sops.yaml
        sops_path = base_path / "sops.yaml"
        if not sops_path.exists():
            sops_path.write_text("# Add SOPs here for task routines\n")

        # Create memory.txt
        mem_txt = memory_path / "memory.txt"
        if not mem_txt.exists():
            mem_txt.touch()

        # Create README
        readme_path = base_path / "README.md"
        if not readme_path.exists():
            readme_path.write_text(f"# {agent_name}\nThis agent is part of VerityOS.")

        return f"✅ Generated agent scaffold for '{agent_name}'."
    # === Role Memory Features ===
    if user_input.startswith(".role summary "):
        agent_name = user_input.split(" ", 2)[2].strip()
        manifest_path = Path(config["memory_path"]) / "agents" / f"{agent_name}.yaml"
        if not manifest_path.exists():
            return f"❌ Agent '{agent_name}' not found."
        with open(manifest_path, "r") as f:
            lines = f.readlines()
        key_lines = [line.strip() for line in lines if any(k in line for k in ["name:", "role:", "version:", "mode:", "model:"])]
        return f"🧠 {agent_name} Summary:\n" + "\n".join(key_lines)

    elif user_input.startswith(".log summary "):
        agent_name = user_input.split(" ", 2)[2].strip()
        log_dir = Path(config["log_path"]).parent / agent_name
        if not log_dir.exists():
            return f"📭 No logs found for agent '{agent_name}'."
        files = sorted(log_dir.glob("*.log"), reverse=True)
        if not files:
            return f"📭 No logs available for '{agent_name}'."
        return files[0].read_text()[:1000]

    elif user_input.startswith(".recall agent "):
        agent_name = user_input.split(" ", 2)[2].strip()
        mem_file = Path(config["memory_path"]).parent / agent_name / "memory.txt"
        if not mem_file.exists():
            return f"📭 No memory found for agent '{agent_name}'."
        return mem_file.read_text()

    elif user_input.startswith(".check agent "):
        agent_name = user_input.split(" ", 2)[2].strip()
        manifest_path = Path(config["memory_path"]) / "agents" / f"{agent_name}.yaml"
        if not manifest_path.exists():
            return f"❌ Manifest for agent '{agent_name}' not found."
        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)
        required_keys = ["name", "role", "version", "mode", "model", "persona"]
        missing = [k for k in required_keys if k not in manifest]
        if missing:
            return f"⚠️ Missing fields in manifest: {', '.join(missing)}"
        return f"✅ Manifest for '{agent_name}' is valid."

    elif user_input.startswith(".export agent "):
        import shutil
        from zipfile import ZipFile
        agent_name = user_input.split(" ", 2)[2].strip()
        agent_dir = Path(config["memory_path"]).parent / agent_name
        if not agent_dir.exists():
            return f"❌ No memory found for agent '{agent_name}'."
        manifest_file = Path(config["memory_path"]) / "agents" / f"{agent_name}.yaml"
        logs_dir = Path(config["log_path"]).parent / agent_name
        export_path = Path(config["memory_path"]) / f"{agent_name}_export.zip"
        with ZipFile(export_path, "w") as zipf:
            if manifest_file.exists():
                zipf.write(manifest_file, arcname=manifest_file.name)
            if agent_dir.exists():
                for file in agent_dir.rglob("*"):
                    if file.is_file():
                        zipf.write(file, arcname=f"{agent_name}/" + file.relative_to(agent_dir).as_posix())
            if logs_dir.exists():
                for file in logs_dir.rglob("*"):
                    if file.is_file():
                        zipf.write(file, arcname=f"{agent_name}/logs/" + file.name)
        return f"📦 Agent '{agent_name}' exported to: {export_path}"

    elif user_input.startswith(".note agent "):
        try:
            parts = user_input.split(" ", 3)
            agent_name = parts[2].strip()
            note = parts[3].strip()
            mem_file = Path(config["memory_path"]).parent / agent_name / "memory.txt"
            mem_file.parent.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(mem_file, "a") as f:
                f.write(f"[{timestamp}] NOTE: {note}\n")
            # Also append to agent log
            log_file = Path(config["log_path"]).parent / agent_name / "latest.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, "a") as lf:
                lf.write(f"[{timestamp}] NOTE: {note}\n")
            return f"📝 Note added to {agent_name}'s memory."
        except:
            return "❌ Usage: .note agent [agent_name] [note]"

    if user_input == ".new agent":
        print("🧠 Let's create a new agent.")
        name = input("Agent name: ").strip()
        role = input("Agent role: ").strip()
        version = input("Agent version (e.g. 1.0): ").strip()
        model = input("Model (e.g. gpt-4, mistral): ").strip()
        mode = input("Mode (command/chat/dual): ").strip()

        manifest = {
            "name": name,
            "role": role,
            "version": version,
            "model": model,
            "mode": mode,
            "persona": f"You are {name}, a {role} created to serve the Boss within VerityOS.\nYou act with clarity, purpose, and integrity.",
            "memory_path": f"/home/ubuntu/verityos/memory/{name.lower()}",
            "log_path": f"/home/ubuntu/verityos/logs/{name.lower()}",
            "sops_path": f"/home/ubuntu/verityos/agents/{name.lower()}/sops.yaml",
            "chatmode": "off"
        }

        agents_dir = Path(config["memory_path"]) / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = agents_dir / f"{name.lower()}.yaml"

        with open(manifest_path, "w") as f:
            yaml.dump(manifest, f)

        return f"✅ Agent '{name}' created at: {manifest_path}"
    if user_input == ".exit": return "exit"
    elif user_input == ".help": return get_help()
    elif user_input == ".chatmode on": return "chatmode_on"
    elif user_input == ".chatmode off": return "chatmode_off"
    elif user_input == ".status": return get_system_report()
    elif user_input == ".agents": return get_agent_report(config)

    # The following commands are deprecated and removed: .show knowledge map, .summarize embedded, .show summary, .link memory, .show links
    elif user_input == ".sync memory":
        from glob import glob
        memory_file = Path(config["memory_path"]) / "verity" / "memory.txt"
        log_root = Path(config["log_path"]).parent
        agent_dirs = [p for p in log_root.glob("*") if p.is_dir() and p.name != "verity"]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(memory_file, "a") as mf:
            mf.write(f"\n[{timestamp}] Memory Sync Started\n")
            for agent_dir in agent_dirs:
                log_file = agent_dir / "latest.log"
                if log_file.exists():
                    content = log_file.read_text().strip()
                    if content:
                        mf.write(f"\n[{agent_dir.name}] {content}\n")
        return "🧠 Verity memory synced with agent logs + insights generated."
    elif user_input == ".synclogs":
        memory_file = Path(config["memory_path"]) / "verity" / "memory.txt"
        log_root = Path(config["log_path"]).parent
        agent_dirs = [p for p in log_root.glob("*") if p.is_dir() and p.name != "verity"]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(memory_file, "a") as mf:
            mf.write(f"\n[{timestamp}] Manual Log Sync Started\n")
            for agent_dir in agent_dirs:
                log_file = agent_dir / "latest.log"
                if log_file.exists():
                    content = log_file.read_text().strip()
                    if content:
                        mf.write(f"\n[{agent_dir.name}] {content}\n")
        return "📎 Logs manually synced to memory + insights updated."
    elif user_input.startswith(".show agent "):
        agent_name = user_input.split(" ", 2)[2].strip()
        if agent_name.lower() == "verity":
            agent_path = Path("/home/ubuntu/verityos/agents/verity/config.yaml")
        else:
            agent_path = Path(config["memory_path"]) / "agents" / f"{agent_name}.yaml"
        if not agent_path.exists():
            return f"❌ Agent '{agent_name}' not found."
        return agent_path.read_text()
    # === Simulate Build Command ===
    elif user_input.startswith(".activate agent "):
        import subprocess
        agent_name = user_input.split(" ", 2)[2].strip()
        boot_path = Path(f"/home/ubuntu/verityos/agents/{agent_name}/boot.py")
        if not boot_path.exists():
            return f"❌ Agent '{agent_name}' has no boot.py."
        subprocess.Popen(["python3", str(boot_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"✅ Agent '{agent_name}' launched in background."
    elif user_input.startswith(".simulate build "):
        agent_name = user_input.split(" ", 2)[2].strip()
        config_path = Path(f"/home/ubuntu/verityos/agents/{agent_name}/config.yaml")
        config_path.parent.mkdir(parents=True, exist_ok=True)

        default_manifest = {
            "name": agent_name,
            "role": "Executor AI",
            "version": "1.0",
            "model": "gpt-3.5",
            "mode": "command",
            "persona": f"You are {agent_name}, a loyal agent for Boss. Follow all instructions and keep logs.",
            "auto_task": True
        }

        import yaml
        with open(config_path, "w") as f:
            yaml.dump(default_manifest, f)

        return f"🧪 Simulated and created default config.yaml for agent '{agent_name}'."
    # === Build Agent Command ===
    elif user_input.startswith(".build agent "):
        return builder_parse_command(user_input)
    # .send message and .check inbox commands have been remov fed.

    # (Agenda-related command blocks have been delegated to handle_agenda_commands.)
    elif user_input == ".reset config":
        config["chatmode"] = "on"
        config["memory_path"] = "/home/ubuntu/verityos/memory"
        config["log_path"] = "/home/ubuntu/verityos/logs"
        with open("/home/ubuntu/verityos/agents/verity/config.yaml", "w") as f:
            yaml.dump(config, f)
        return "🔄 Config reset to defaults and saved."
    else:
        return None

# === Main Loop ===

def get_exit_summary(memory_path, log_path, config):
    now = get_nassau_time()
    return (
        f"🟢 VerityOS Ready\n"
        f"📅 {now}\n"
        f"🧠 Memory: {memory_path}\n"
        f"📂 Logs: {log_path}\n"
        f"{get_system_report()}\n"
        f"{get_agent_report(config)}"
    )

def start_verity_os():
    global chat_mode
    fastboot = "--fastboot" in sys.argv
    config = load_config()
    if not isinstance(config, dict):
        print(f"DEBUG: config type is {type(config)} — value: {config}")
        raise TypeError("❌ VerityOS Error: config is not a dictionary.")
    config.setdefault("memory_path", "/home/ubuntu/verityos/memory")
    config.setdefault("log_path", "/home/ubuntu/verityos/logs")
    # Ensure chatmode key exists
    config.setdefault("chatmode", "on")
    from scripts.index_watch_module import start_index_watcher
    index_watch_folder = Path("/home/ubuntu/verityos/data/markdown")
    index_watch_folder.mkdir(parents=True, exist_ok=True)
    start_index_watcher(index_watch_folder, build_index_from_folder)
    memory_path = Path(config["memory_path"])
    log_path = Path(config["log_path"])
    memory_path.mkdir(parents=True, exist_ok=True)
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = init_log(log_path)

    # Render and display startup UI
    print(render_startup_summary(config, boot_start))
    agent_count = render_agent_statuses()
    print(f"📡 {agent_count} agents online.")
    print()  # Adds the space
    print("Verity > Hello Boss, How can I help you?\n")
    print("🧠 Boss > ", end="")
    user_input = input().strip()
    if user_input == ".exit":
        print("Exiting VerityOS.")
        return
    chat_mode_original = config.get("chatmode", "on")
    config["chatmode"] = "off"
    result = parse_command(user_input, config)
    config["chatmode"] = chat_mode_original
    if result and result != "exit":
        print(result)

    print("🧠 Boss > ", end="")
    user_input = input().strip()
    if user_input == ".exit":
        print("Exiting VerityOS.")
        return
    chat_mode_original = config.get("chatmode", "on")
    config["chatmode"] = "off"
    result = parse_command(user_input, config)
    config["chatmode"] = chat_mode_original
    if result and result != "exit":
        print(result)

    # === Daily Log Tracker & Agent Sync, Auto-Tasks (skip if fastboot) ===
    if not fastboot:
        setup_daily_log_and_memory_sync(config)
        print("⏱ Daily log and memory sync complete.")

        execute_auto_tasks(config, log_file)
        print("⏱ Auto-tasks executed.")

    # === Launch Ripple Agent ===
    ripple_path = Path("/home/ubuntu/verityos/agents/ripple/ripple.py")
    if ripple_path.exists():
        import subprocess
        subprocess.Popen(["python3", str(ripple_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # (Agent status lines are displayed above at login)

    from scripts.chat_module import handle_chat_interaction
    conversation_history = collections.deque(maxlen=10)

    # (Initial two startup commands collected above. Removed old input handling block.)

    while True:
        user_input = input("\n🧠 Boss > ").strip()
        write_log(log_file, f"INPUT: {user_input}")

        if user_input.startswith(".") or (chat_mode and user_input.strip().startswith(".")):
            result = parse_command(user_input, config)
            if result == "exit":
                print("Exiting VerityOS.")
                break
            elif result == "chatmode_on":
                chat_mode = True
                print("💬 Chat Mode activated.")
            elif result == "chatmode_off":
                chat_mode = False
                print("🔒 Chat Mode deactivated.")
            elif result is not None:
                print(result)
                write_log(log_file, f"COMMAND: {result}")
            else:
                print("⚠️ Unknown command. Use .help to list options.")
        else:
            if chat_mode:
                result = handle_chat_interaction(user_input, conversation_history, config, log_file)
                print(f"Verity > {result}")
            else:
                print("Verity > Not a command. Use .help or enable .chatmode on")
    print(f"⏱ VerityOS booted in {round(time.time() - boot_start, 2)} seconds.")
    return get_exit_summary(memory_path, log_path, config)

import sys
if __name__ == "__main__":
    try:
        config = load_config()
        config.setdefault("memory_path", "/home/ubuntu/verityos/memory")
        config.setdefault("log_path", "/home/ubuntu/verityos/logs")
        config.setdefault("chatmode", "on")

        if len(sys.argv) > 2 and sys.argv[1] == "--query":
            if sys.argv[2] == ".status":
                print(get_system_report())
            elif sys.argv[2] == ".agents":
                print(get_agent_report(config))
            elif sys.argv[2] == ".help":
                print(get_help())
            else:
                print("⚠️ Unknown query")

        elif len(sys.argv) > 2 and sys.argv[1] == "--command":
            user_input = " ".join(sys.argv[2:]).strip()
            result = parse_command(user_input, config)

            if result == "chatmode_on":
                config["chatmode"] = "on"
                with open("/home/ubuntu/verityos/agents/verity/config.yaml", "w") as f:
                    yaml.dump(config, f)
                print("✅ Chat mode enabled")

            elif result == "chatmode_off":
                config["chatmode"] = "off"
                with open("/home/ubuntu/verityos/agents/verity/config.yaml", "w") as f:
                    yaml.dump(config, f)
                print("✅ Chat mode disabled")

            elif user_input == ".intro":
                print(parse_command(".intro", config))

            elif user_input == ".help":
                print(get_help())

            elif user_input == ".status":
                print(get_system_report())

            elif user_input == ".agents":
                print(get_agent_report(config))

            elif user_input == ".selftest":
                print(selftest(config))

            elif user_input == ".new agent":
                # This is handled in parse_command (interactive mode), so for CLI we can error or call parse_command
                result = parse_command(user_input, config)
                print(result if result else "⚠️ Unknown command")

            else:
                if config.get("chatmode") == "on":
                    response = chat_openai(user_input, config)
                    print(response)
                else:
                    print("⚠️ Unknown command")
        else:
            start_verity_os()

    except Exception as e:
        print(f"🔥 VerityOS Error: {type(e).__name__}: {e}")