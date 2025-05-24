


from pathlib import Path
import yaml

def handle_sop_commands(user_input):
    if user_input.startswith(".sop list "):
        agent_name = user_input.split(" ", 2)[2].strip()
        sops_path = Path(f"/home/ubuntu/verityos/agents/{agent_name}/sops.yaml")
        if not sops_path.exists():
            return f"📭 No SOP file found for {agent_name}."
        with open(sops_path, "r") as f:
            sops = yaml.safe_load(f)
        return f"📒 SOPs for {agent_name}:\n" + "\n".join(f"- {k}" for k in sops.keys())

    elif user_input.startswith(".sop show "):
        parts = user_input.split(" ")
        if len(parts) < 4:
            return "❌ Usage: .sop show [agent] [title]"
        agent_name = parts[2]
        title = parts[3]
        sops_path = Path(f"/home/ubuntu/verityos/agents/{agent_name}/sops.yaml")
        if not sops_path.exists():
            return f"📭 No SOP file found for {agent_name}."
        with open(sops_path, "r") as f:
            sops = yaml.safe_load(f)
        if title not in sops:
            return f"❌ SOP '{title}' not found for {agent_name}."
        sop = sops[title]
        return f"📋 {title} ({agent_name})\n- Description: {sop.get('description')}\n- Command: {sop.get('command')}"

    elif user_input == ".sop run":
        return "🚧 .sop run not implemented yet."

    return None