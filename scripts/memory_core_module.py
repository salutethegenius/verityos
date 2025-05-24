import sys
sys.path.append("/home/ubuntu/verityos/scripts")
from memory_core import build_index_from_folder, get_combined_context
from llm_router import query_model
import os
import json
import os

print(f"🔑 OpenAI Key (short preview): {os.getenv('OPENAI_API_KEY', '❌ Not Set')[:8]}...")

def get_agent_index(agent_name):
    index_path = f"/home/ubuntu/verityos/memory_system/{agent_name}/long_term_index.json"
    if not os.path.exists(index_path):
        print(f"⚠️ No index found for agent '{agent_name}' at {index_path}")
        return []

    try:
        with open(index_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading index for agent '{agent_name}': {e}")
        return []

import datetime

def handle_memory_core_commands(user_input):
    from pathlib import Path

    if user_input.startswith(".buildindex "):
        parts = user_input.split(" ")
        folder_path = parts[1].strip()
        agent = parts[2].strip() if len(parts) > 2 else "verity"
        try:
            chunks = build_index_from_folder(folder_path)
            if not chunks:
                return f"⚠️ No chunks were returned from folder: {folder_path}. Check file formats or content."
            print(f"✅ Chunking complete: {len(chunks)} total chunks.")

            agent_dir = Path(f"/home/ubuntu/verityos/memory_system/{agent}")
            agent_dir.mkdir(parents=True, exist_ok=True)
            json_path = agent_dir / "long_term_index.json"
            with open(json_path, "w") as f:
                json.dump(chunks, f, indent=2)

            print(f"✅ Memory index saved: {json_path}")
            print("✅ All files processed and indexed successfully.")
            return f"📚 Indexed {len(chunks)} chunks for '{agent}' from: {folder_path}"
        except Exception as e:
            return f"❌ Failed to build index: {e}"

    elif user_input.startswith(".autodigest"):
        parts = user_input.split(" ")
        agent = parts[1].strip() if len(parts) > 1 else "verity"
        today = datetime.date.today().isoformat()
        log_path = f"/home/ubuntu/verityos/logs/{agent}/daily.log"
        digest_path = f"/home/ubuntu/verityos/memory_system/{agent}/daily_digest/{today}.md"
        os.makedirs(os.path.dirname(digest_path), exist_ok=True)
        try:
            if not os.path.exists(log_path):
                with open(log_path, "w") as f:
                    f.write("📝 No entries yet. Starting new log.\n")
            with open(log_path, "r") as log_file:
                content = log_file.read()
            summary_prompt = f"Summarize this daily log:\n\n{content}"
            summary = query_model(summary_prompt)
            with open(digest_path, "w") as f:
                f.write(summary)
            return f"🧠 Digest saved to {digest_path}"
        except Exception as e:
            return f"❌ Failed to create digest: {e}"

    elif user_input.startswith(".logmemory "):
        parts = user_input.split(" ", 2)
        if len(parts) < 3:
            return "❌ Usage: .logmemory [agent] \"event description\""
        agent = parts[1].strip()
        event = parts[2].strip().strip('"')
        short_term_path = f"/home/ubuntu/verityos/memory_system/{agent}/short_term.json"
        os.makedirs(os.path.dirname(short_term_path), exist_ok=True)
        try:
            if os.path.exists(short_term_path):
                with open(short_term_path, "r") as f:
                    data = json.load(f)
            else:
                data = []
            data.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "event": event
            })
            with open(short_term_path, "w") as f:
                json.dump(data, f, indent=2)
            return f"📝 Logged to {short_term_path}"
        except Exception as e:
            return f"❌ Failed to log memory: {e}"

    elif user_input.startswith(".recall "):
        agent = user_input.split(" ")[1].strip()
        short_term_path = f"/home/ubuntu/verityos/memory_system/{agent}/short_term.json"
        if not os.path.exists(short_term_path):
            return f"❌ No short-term memory found for agent '{agent}'"
        try:
            with open(short_term_path, "r") as f:
                data = json.load(f)
            return json.dumps(data[-5:], indent=2)  # show last 5 entries
        except Exception as e:
            return f"❌ Error reading short-term memory: {e}"

    elif user_input.startswith(".ask "):
        question = user_input[len(".ask "):].strip()
        if " " in question:
            agent, actual_question = question.split(" ", 1)
            indexed_chunks = get_agent_index(agent.lower())
            if not indexed_chunks:
                # fallback to global context
                print(f"⚠️ No memory for '{agent}', using global context.")
                context = get_combined_context(actual_question)
            else:
                from memory_core import get_query_embedding
                query_embedding = get_query_embedding(actual_question)
                from reranker_module import rank_chunks
                top_chunks = rank_chunks(query_embedding, indexed_chunks)
                context = "\n".join([chunk["text"] for chunk in top_chunks])
                question = actual_question
        else:
            context = get_combined_context(question)
            agent = "verity"
            actual_question = question
        full_prompt = f"{context}\n\nAnswer this question based on the information above:\n{question}"
        try:
            response = query_model(full_prompt)
            # Log the question to short-term memory
            log_path = f"/home/ubuntu/verityos/memory_system/{agent}/short_term.json"
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    data = json.load(f)
            else:
                data = []
            data.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "event": f".ask → {actual_question}"
            })
            with open(log_path, "w") as f:
                json.dump(data, f, indent=2)
            return f"{response}\n\n[💡 Tip: Use `.polish {agent} {actual_question}` for a detailed version]"
        except Exception as e:
            return f"❌ Failed to generate response: {e}"

    elif user_input.startswith(".polish "):
        parts = user_input.split(" ", 2)
        if len(parts) < 3:
            return "❌ Usage: .polish [agent] [question]"
        agent, question = parts[1], parts[2]
        indexed_chunks = get_agent_index(agent.lower())
        if not indexed_chunks:
            return f"❌ No memory index found for agent '{agent}'"
        try:
            from memory_core import get_query_embedding
            query_embedding = get_query_embedding(question)
            from reranker_module import rank_chunks
            top_chunks = rank_chunks(query_embedding, indexed_chunks)
            context = "\n\n".join([chunk["text"] for chunk in top_chunks])
            polish_prompt = (
                "Format the following information into a clear, concise markdown summary. "
                "Use headers, bullet points, and group related information:\n\n" + context
            )
            return query_model(polish_prompt)
        except Exception as e:
            return f"❌ Failed to polish memory: {e}"

    elif user_input.startswith(".forget "):
        parts = user_input.split(" ", 2)
        if len(parts) < 3:
            return "❌ Usage: .forget [agent] [keyword]"
        agent, keyword = parts[1], parts[2].lower()
        index_path = f"/home/ubuntu/verityos/memory_system/{agent}/long_term_index.json"
        if not os.path.exists(index_path):
            return f"❌ No memory index found for agent '{agent}'"
        try:
            with open(index_path, "r") as f:
                chunks = json.load(f)
            new_chunks = [c for c in chunks if keyword not in c["text"].lower()]
            with open(index_path, "w") as f:
                json.dump(new_chunks, f, indent=2)
            removed = len(chunks) - len(new_chunks)
            return f"🧽 Removed {removed} memory chunks containing '{keyword}'"
        except Exception as e:
            return f"❌ Failed to forget: {e}"

    elif user_input.startswith(".pushmemory "):
        agent = user_input.split(" ")[1].strip()
        short_path = f"/home/ubuntu/verityos/memory_system/{agent}/short_term.json"
        index_path = f"/home/ubuntu/verityos/memory_system/{agent}/long_term_index.json"
        if not os.path.exists(short_path):
            return f"❌ No short-term memory found for agent '{agent}'"
        try:
            from memory_core import get_query_embedding
            with open(short_path, "r") as f:
                short_data = json.load(f)
            long_data = []
            if os.path.exists(index_path):
                try:
                    with open(index_path, "r") as f:
                        long_data = json.load(f)
                except Exception as e:
                    print(f"⚠️ Warning: Failed to parse existing long-term index. Starting fresh. Error: {e}")
                    long_data = []
            for entry in short_data:
                long_data.append({
                    "text": entry["event"],
                    "embedding": get_query_embedding(entry["event"]).tolist(),
                    "source": "short_term_push",
                    "timestamp": entry["timestamp"]
                })
            with open(index_path, "w") as f:
                json.dump(long_data, f, indent=2)
            return f"📦 Pushed {len(short_data)} entries to long-term memory"
        except Exception as e:
            return f"❌ Failed to push memory: {e}"

    elif user_input.startswith(".reviewlog "):
        agent = user_input.split(" ")[1].strip()
        log_path = f"/home/ubuntu/verityos/memory_system/{agent}/short_term.json"
        if not os.path.exists(log_path):
            return f"❌ No short-term memory found for agent '{agent}'"
        try:
            with open(log_path, "r") as f:
                data = json.load(f)
            return json.dumps(data, indent=2)
        except Exception as e:
            return f"❌ Failed to read log: {e}"

    elif user_input.startswith(".handoff ") or user_input.startswith(".delegate "):
        parts = user_input.split(" ", 2)
        if len(parts) < 3:
            return "❌ Usage: .handoff/.delegate [agent] [message/task]"
        agent, message = parts[1], parts[2]
        try:
            script_path = f"/home/ubuntu/verityos/agents/{agent}/boot.py"
            if not os.path.exists(script_path):
                return f"❌ Agent '{agent}' not found at expected path: {script_path}"
            import subprocess
            result = subprocess.run(["python3", script_path, message], capture_output=True, text=True)
            if result.returncode != 0:
                return f"❌ Error running {agent}: {result.stderr}"
            return f"📨 Response from {agent}:\n{result.stdout.strip()}"
        except Exception as e:
            return f"❌ Failed to delegate to '{agent}': {e}"

    return None