from pathlib import Path
import time

def handle_task_commands(user_input, config):
    memory_path = Path(config["memory_path"])
    log_path = Path(config["log_path"])

    if user_input.startswith(".task create "):
        task_name = user_input.split(" ", 2)[2].strip()
        task_dir = memory_path / "tasks"
        task_dir.mkdir(parents=True, exist_ok=True)
        task_path = task_dir / f"{task_name}.txt"
        if task_path.exists():
            return f"⚠️ Task '{task_name}' already exists."
        description = input(f"✍️ Enter description for task '{task_name}':\n> ")
        task_path.write_text(description)
        return f"✅ Task '{task_name}' saved."

    elif user_input == ".task list":
        task_dir = memory_path / "tasks"
        if not task_dir.exists():
            return "📭 No tasks available."
        tasks = [f.stem for f in task_dir.glob("*.txt")]
        return "🗂 Tasks:\n" + "\n".join(f"- {t}" for t in tasks)

    elif user_input.startswith(".task show "):
        task_name = user_input.split(" ", 2)[2].strip()
        task_path = memory_path / "tasks" / f"{task_name}.txt"
        if not task_path.exists():
            return f"❌ Task '{task_name}' not found."
        return f"📋 {task_name}:\n" + task_path.read_text()

    elif user_input.startswith(".task delete "):
        task_name = user_input.split(" ", 2)[2].strip()
        task_path = memory_path / "tasks" / f"{task_name}.txt"
        if not task_path.exists():
            return f"❌ Task '{task_name}' not found."
        task_path.unlink()
        return f"🗑 Task '{task_name}' deleted."

    elif user_input.startswith(".assign "):
        try:
            parts = user_input[len(".assign "):].split(" to ")
            task_name = parts[0].strip()
            agent_name = parts[1].strip()
            task_file = memory_path / "tasks" / f"{task_name}.txt"
            agent_manifest = memory_path / "agents" / f"{agent_name}.yaml"
            if not task_file.exists():
                return f"❌ Task '{task_name}' not found."
            if not agent_manifest.exists():
                return f"❌ Agent '{agent_name}' not found."
            assignment_file = memory_path / "agents" / f"{agent_name}_tasks.txt"
            with open(assignment_file, "a") as af:
                af.write(task_name + "\n")
            return f"✅ Task '{task_name}' assigned to {agent_name}."
        except:
            return "❌ Usage: .assign [task_name] to [agent_name]"

    elif user_input.startswith(".unassign "):
        try:
            parts = user_input[len(".unassign "):].split(" from ")
            task_name = parts[0].strip()
            agent_name = parts[1].strip()
            assignment_file = memory_path / "agents" / f"{agent_name}_tasks.txt"
            if not assignment_file.exists():
                return f"❌ No assignments found for {agent_name}."
            with open(assignment_file, "r") as f:
                tasks = [line.strip() for line in f.readlines() if line.strip()]
            if task_name not in tasks:
                return f"❌ Task '{task_name}' not found for {agent_name}."
            tasks.remove(task_name)
            with open(assignment_file, "w") as f:
                f.write("\n".join(tasks) + ("\n" if tasks else ""))
            return f"🗑 Task '{task_name}' unassigned from {agent_name}."
        except:
            return "❌ Usage: .unassign [task_name] from [agent_name]"

    elif user_input.startswith(".agent tasks "):
        agent_name = user_input.split(" ", 2)[2].strip()
        assignment_file = memory_path / "agents" / f"{agent_name}_tasks.txt"
        if not assignment_file.exists():
            return f"📭 No tasks assigned to {agent_name}."
        with open(assignment_file, "r") as f:
            tasks = [line.strip() for line in f.readlines() if line.strip()]
        return f"🗂 Tasks for {agent_name}:\n" + "\n".join(f"- {t}" for t in tasks)

    elif user_input.startswith(".assign builder_task "):
        task = user_input.split(" ", 2)[2].strip()
        task_dir = memory_path / "tasks"
        task_dir.mkdir(parents=True, exist_ok=True)
        task_log = task_dir / "builder_tasks.txt"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(task_log, "a") as f:
            f.write(f"[{timestamp}] {task}\n")
        return f"✅ Task assigned and saved to builder_tasks.txt"

    elif user_input == ".process builder_task":
        task_log = memory_path / "tasks" / "builder_tasks.txt"
        if not task_log.exists():
            return "📭 No builder tasks found."
        with open(task_log, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        if not lines:
            return "📭 No builder tasks in the queue."
        current_task = lines[0]
        with open(task_log, "w") as f:
            f.write("\n".join(lines[1:]))
        return f"📋 Processing: {current_task}\n✅ Task dequeued and ready for simulation."

    # Task execution logic could be moved here too (if not already modularized)
    return None