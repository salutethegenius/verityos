def start_index_watcher(folder_path, index_function):
    import threading
    from pathlib import Path
    import time

    def watcher(folder_to_watch):
        last_seen = set(Path(folder_to_watch).glob("*.md")) | set(Path(folder_to_watch).glob("*.txt"))
        while True:
            current_files = set(Path(folder_to_watch).glob("*.md")) | set(Path(folder_to_watch).glob("*.txt"))
            added_files = current_files - last_seen
            removed_files = last_seen - current_files
            if added_files or removed_files:
                if added_files:
                    print(f"\n📂 New file(s) detected: {[f.name for f in added_files]}")
                if removed_files:
                    print(f"\n🗑️ File(s) removed: {[f.name for f in removed_files]}")
                print("🔄 Rebuilding index...")
                index_function(folder_to_watch)
                print("✅ Index rebuilt.")
                print("🧠 Boss > ", end="", flush=True)
                last_seen = current_files
            time.sleep(15)

    threading.Thread(target=watcher, args=(folder_path,), daemon=True).start()