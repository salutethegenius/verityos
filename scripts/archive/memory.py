import time
import re
from collections import Counter
from pathlib import Path
from cryptography.fernet import Fernet
import os

def summarize_memory(path): return "Memory summarized"

def recall_memory(path):
    mem_file = Path(path) / "memory.txt"
    return mem_file.read_text() if mem_file.exists() else "No memory yet."

def analyze_memory(path):
    insights_path = Path("/home/ubuntu/verityos/insights")
    insights_path.mkdir(parents=True, exist_ok=True)
    mem_file = Path(path) / "memory.txt"
    if not mem_file.exists():
        return "No memory to analyze."
    content = mem_file.read_text().lower()
    words = re.findall(r'\b[a-z]{3,}\b', content)
    freq = Counter(words).most_common(5)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    summary = [f"Insight generated at {timestamp}:"] + [f"- {word}: {count} mentions" for word, count in freq]
    insight_file = insights_path / f"insight_{int(time.time())}.txt"
    insight_file.write_text("\n".join(summary))
    return "Insight saved. Use .insight to view it."

def latest_insight():
    insights_path = Path("/home/ubuntu/verityos/insights")
    files = sorted(insights_path.glob("insight_*.txt"), reverse=True)
    if not files:
        return "No insights available."
    return files[0].read_text()

def learn_manual(path, text):
    learn_path = Path(path) / "learned"
    learn_path.mkdir(parents=True, exist_ok=True)
    file_path = learn_path / f"learned_{int(time.time())}.txt"
    file_path.write_text(text)
    return f"Learned input saved: {file_path.name}"

def show_learned_memory(path):
    learn_path = Path(path) / "learned"
    if not learn_path.exists():
        return "No learned entries found."
    files = sorted(learn_path.glob("learned_*.txt"), reverse=True)
    if not files:
        return "No learned entries available."
    output = []
    for file in files[:5]:
        content = file.read_text().strip()
        output.append(f"{file.name}:\n{content}\n")
    return "\n".join(output)

def add_note(path, text):
    mem_file = Path(path) / "memory.txt"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(mem_file, "a") as f:
        f.write(f"[{timestamp}] NOTE: {text}\n")
    if "secure:" in text.lower():
        try:
            key = os.getenv("VERITY_VAULT_KEY")
            fernet = Fernet(key.encode())
            encrypted = fernet.encrypt(text.encode())
            secure_path = Path(path) / "vault"
            secure_path.mkdir(parents=True, exist_ok=True)
            note_file = secure_path / f"secure_note_{int(time.time())}.vault"
            note_file.write_bytes(encrypted)
        except Exception as e:
            return f"⚠️ Note saved to memory, but vault secure save failed: {e}"
    return "Note saved to memory."