

# chat_router.py — VerityOS Chat Mode Handler

import collections
import string
from scripts.command_router import route_command
from scripts.chat_utils import summarize_history, inject_long_term_memory
from scripts.init_system import write_log
from scripts.memory_core_module import handle_memory_core_commands

def run_chat(config, log_file):
    """
    Main chat loop: handles both dot-commands and natural language chat.
    """
    conversation_history = collections.deque(maxlen=10)
    chat_mode = config.get("chatmode", "off") == "on"

    while True:
        user_input = input("\n🧠 Boss > ").strip()
        write_log(log_file, f"INPUT: {user_input}")

        # Handle prefixed commands when chat mode is off or dot-command starts
        if user_input.startswith(".") or not chat_mode:
            result = route_command(user_input, config)

            if result == "exit":
                print("Exiting VerityOS.")
                break
            if result == "chatmode_on":
                chat_mode = True
                print("💬 Chat Mode activated.")
                continue
            if result == "chatmode_off":
                chat_mode = False
                print("🔒 Chat Mode deactivated.")
                continue

            if result:
                print(result)
                write_log(log_file, f"COMMAND: {result}")
            else:
                print("⚠️ Unknown command. Use .help")

        # Natural language chat input
        else:
            # Record user input
            conversation_history.append(("User", user_input))

            # Summarize older history when buffer is full
            if len(conversation_history) == conversation_history.maxlen:
                old_entries = [f"{s}: {m}" for s, m in list(conversation_history)[:5]]
                summary = summarize_history(old_entries)
                for _ in range(5):
                    conversation_history.popleft()
                conversation_history.append(("System", summary))

            # Build history context
            history_text = "\n".join([f"{s}: {m}" for s, m in conversation_history])

            # Inject long-term memory if requested
            if "earlier you said" in user_input.lower():
                memory_context = inject_long_term_memory("verity", user_input)
                history_text += "\nMemory Recall:\n" + memory_context

            # Construct and execute the .ask command
            command = f".ask verity {history_text}\nUser: {user_input}"
            result = handle_memory_core_commands(command)

            if result:
                print(f"Verity > {result}")
                conversation_history.append(("Verity", result))
                write_log(log_file, f"CHAT: {result}")
            else:
                print("Verity > 🤖 I’m not sure what to do with that. Try rephrasing.")