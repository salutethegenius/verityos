# VerityOS – Sovereign AI Operating System 🧠⚡

> **Your AI. Your Rules.**  
> VerityOS is a modular, agent-based operating system designed to bring sovereign AI autonomy to small businesses, creators, NGOs, and emerging nations. It runs offline, adapts to your workflow, and never sells your data. Powered by purpose, not hype.

---

## 🌐 What Is VerityOS?

VerityOS is a task-execution AI system built around:
- **Local-first models** (Mistral, DeepSeek, etc.)
- **Smart memory + hybrid RAG**
- **Modular agents** (like Verity, Right, Nova, Ripple)
- **No cloud required** (unless you want it)
- **Custom hardware support** via VerityLite

Designed to operate like a human team with role-specific AI agents working together.

---

## 🧠 Core Agents

| Agent    | Role                                     |
|----------|------------------------------------------|
| `Verity` | Strategic planner + wellness monitor     |
| `Right`  | Executor + system operator               |
| `Nova`   | Content researcher + RAG interface       |
| `Ripple` | Inbox + email intelligence               |
| `Minty`  | Financial monitoring                     |
| `Mango`  | DevTools and code builder                |

---

## 📦 Features

- 🧠 **Embodied memory + sentiment-aware context**
- 🛠️ **Agent-to-Agent protocol (A2A)**
- 💬 **Chat + Command interface**
- 📁 **Encrypted local memory vaults**
- 💻 **Offline-first deployment (VerityLite)**

---

## 🖥️ Local Deployment

VerityOS can run on:
- Ubuntu / macOS / Kali Linux
- Raspberry Pi (Kali or Lite)
- AWS EC2 (optional cloud deploy)
- VerityLite physical terminal (coming soon)

---

## 📂 Directory Structure
/agents/           - All modular AI agents
/tools/            - Internal CLI + helper modules
/memory_system/    - Smart memory with chunk routing
/scripts/          - Launchers, taggers, system ops
/webui/            - Optional GUI interface

---

## 🚀 How to Use

1. Clone the repo  
2. Create your environment file (`.env`)  
3. Set up your virtual environment  
4. Install dependencies  
5. Run VerityOS  
6. Inside the system, run `.help` to view available commands  

---

## 🧪 Environment Setup (`.env` Required)

Before running VerityOS, you must create a `.env` file in the project root:

```bash
touch .env
```

Paste the following into `.env`, replacing with your actual values:

```env
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX
OPENAI_MODEL=gpt-4
VERITY_MODEL=gpt-4
VERITY_PROVIDER=OpenAI
VERITY_VAULT_KEY=yourCustomEncryptionKey123!
```

> 🔒 **Never share your `.env` file.** It's excluded from Git for your protection.

---

## 🧰 Launch VerityOS

```bash
python3 -m venv verityenv
source verityenv/bin/activate
pip install -r requirements.txt
python3 agents/verity/boot.py
```

⸻

🛡️ License

This project uses a hybrid license model:
	•	Open-core: Personal, educational, nonprofit use
	•	Commercial: Requires permission or partnership via Kemis Group of Companies Inc.

⸻

🧭 Built By

Kenneth C. Moncur – Founder, Bahamian technologist, strategist, and digital sovereign.
For partnerships: kemisdigital.com

“We don’t just build AI. We build freedom.”