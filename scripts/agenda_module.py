


from pathlib import Path
import time

def handle_agenda_commands(user_input, config):
    agenda_file = Path(config["memory_path"]) / "agenda.txt"
    archive_dir = Path(config["memory_path"]) / "archives"
    archive_dir.mkdir(parents=True, exist_ok=True)

    if user_input == ".agenda":
        if not agenda_file.exists():
            return "📭 No agenda found. Use .load agenda to begin."
        with open(agenda_file, "r") as f:
            lines = [line.strip() for line in f.readlines()]
        return "🧾 Current Agenda:\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines))

    elif user_input.startswith(".load agenda "):
        try:
            filename = user_input.split(" ", 2)[2].strip()
            path = Path(filename)
            if not path.exists():
                return f"❌ File '{filename}' not found."
            agenda_file.write_text(path.read_text())
            return f"✅ Agenda loaded from {filename}"
        except:
            return "❌ Usage: .load agenda [file_path]"

    elif user_input == ".start agenda":
        if not agenda_file.exists():
            return "📭 No agenda found."
        with open(agenda_file, "r") as f:
            lines = [line.strip() for line in f.readlines()]
        return "🟢 Starting Agenda:\n" + "\n".join(f"{i+1}. {line}" for i, line in enumerate(lines))

    elif user_input.startswith(".edit agenda "):
        parts = user_input.split(" ", 3)
        if len(parts) < 4:
            return "❌ Usage: .edit agenda [line_number] [new_text]"
        line_num = int(parts[2]) - 1
        new_text = parts[3]
        lines = agenda_file.read_text().splitlines()
        if line_num < 0 or line_num >= len(lines):
            return "❌ Invalid line number."
        lines[line_num] = new_text
        agenda_file.write_text("\n".join(lines) + "\n")
        return f"✏️ Line {line_num+1} updated."

    elif user_input.startswith(".done "):
        index = int(user_input.split(" ", 1)[1]) - 1
        lines = agenda_file.read_text().splitlines()
        if index < 0 or index >= len(lines):
            return "❌ Invalid task number."
        lines[index] = f"✅ {lines[index]}"
        agenda_file.write_text("\n".join(lines) + "\n")
        return f"✅ Task {index+1} marked as done."

    elif user_input.startswith(".undo "):
        index = int(user_input.split(" ", 1)[1]) - 1
        lines = agenda_file.read_text().splitlines()
        if index < 0 or index >= len(lines):
            return "❌ Invalid task number."
        lines[index] = lines[index].replace("✅ ", "")
        agenda_file.write_text("\n".join(lines) + "\n")
        return f"🔄 Task {index+1} marked as not done."

    elif user_input == ".clear agenda":
        if agenda_file.exists():
            agenda_file.unlink()
        return "🧹 Agenda cleared."

    elif user_input == ".reset agenda":
        if agenda_file.exists():
            agenda_file.write_text("")
        return "♻️ Agenda reset."

    elif user_input == ".archive agenda":
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        archive_file = archive_dir / f"agenda_{timestamp}.txt"
        if agenda_file.exists():
            archive_file.write_text(agenda_file.read_text())
            return f"📦 Agenda archived as {archive_file.name}"
        return "❌ No agenda to archive."

    elif user_input == ".list archives":
        archives = sorted(archive_dir.glob("agenda_*.txt"))
        if not archives:
            return "📭 No archives found."
        return "📚 Agenda Archives:\n" + "\n".join(f"- {f.name}" for f in archives)

    elif user_input.startswith(".load archive "):
        filename = user_input.split(" ", 2)[2].strip()
        archive_file = archive_dir / filename
        if not archive_file.exists():
            return f"❌ Archive '{filename}' not found."
        agenda_file.write_text(archive_file.read_text())
        return f"✅ Loaded agenda from archive: {filename}"

    elif user_input.startswith(".delete archive "):
        filename = user_input.split(" ", 2)[2].strip()
        archive_file = archive_dir / filename
        if not archive_file.exists():
            return f"❌ Archive '{filename}' not found."
        archive_file.unlink()
        return f"🗑 Archive '{filename}' deleted."

    return None