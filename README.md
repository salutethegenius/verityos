VerityOS – Sovereign AI Operating System
Your AI — Your Rules

VerityOS is a closed-core, agent-first AI operating system designed for offline autonomy, sovereign deployment, and real-world task execution. Built for founders, researchers, small teams, and emerging nations, VerityOS gives you full control over your data, workflows, and AI infrastructure—without relying on cloud APIs or external platforms.

🔧 Core Features
🧠 Agent-Orchestrated Architecture
Modular agents (Verity, Right, Nova, Minty, Ripple, Breeze, etc.) with specific roles
Planner–Executor split (Verity as strategist, Right as executor)
Auto-agent generation using templates
Real-time A2A (Agent-to-Agent) communication
🗂 Hybrid Memory + RAG System
Supports long-term memory, short-term memory, and memory summarization
Embedding-based semantic search with custom chunking, rerankers, and metadata filters
.buildindex, .sync memory, and .ask commands for fast recall
💬 Command-Driven Interface
Lightweight terminal-first experience (CLI powered)
Interactive .help, .note, .task, .agents, .build agent, and more
Optional chat mode with real-time LLM interactions
⚙️ Agent Specializations
Verity: Strategist, memory monitor, planner
Right: Executor agent (task runner, system ops)
Nova: Research and content generation (blogs, posts, drafts)
Minty: Financial monitor and accounting logic
Ripple: Email intelligence agent with Gmail integration
Breeze: National news and tone monitoring agent
🔒 Privacy-First by Design
Runs offline (no API requirement)
Embeds, stores, and queries data locally
Built for sovereignty, edge devices, and airgapped environments

🛠️ Setup & Usage
Prerequisites
Python 3.10+
Ubuntu (recommended) or compatible Linux distro
16GB+ RAM for full stack
Git + pip + virtualenv
Installation
git clone https://github.com/kemis-tech/verityos.git
cd verityos
python3 -m venv verityenv
source verityenv/bin/activate
pip install -r requirements.txt

Boot Verity
cd agents/verity
python3 boot.py

Example Commands
.help                   # View all available commands
.chatmode on            # Enable chat mode
.note agent nova        # Add memory note to Nova
.build agent minty      # Generate full agent from template
.task create "Send report to Ripple"


🌍 Ideal Use Cases
Sovereign AI deployments for small nations
Offline AI for research labs or NGOs
Workflow automation without cloud dependencies
Content generation with memory awareness
Local knowledge hubs (education, media, government)

📦 Roadmap (2025)
VerityOS v1.0 (Q4 2025)
VerityLite device (plug-and-play AI hardware terminal)
Plugin ecosystem for third-party agent types
Fine-tuning pipeline and in-house model hosting
VerityHub dashboard UI (Flutter-based)

✍️ Author
Kenneth C. Moncur
Founder, Kemis Group of Companies
Builder of sovereign AI tools for The Bahamas and beyond
📧 Contact: info@kemisdigital.com
🌐 Website: https://verityos.net
💡 Support: https://ko-fi.com/verityos

⚖️ License
VerityOS is a dual-license system:
Open-core for community use
Commercial license for enterprise, government, and white-label builds
Contact us for deployment, integration, or partnership opportunities.
"In a world of black-box AI, VerityOS puts the keys back in your hands."

