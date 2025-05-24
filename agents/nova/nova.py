


# nova.py

import sys
sys.path.append('/home/ubuntu/verityos')

from utils.logger import log_audit

class Nova:
    def __init__(self):
        self.name = "nova"
        self.version = "1.0"
        self.role = "Agent"
        self.memory_path = "/home/ubuntu/verityos/agents/nova/memory_system"
        self.log_path = "/home/ubuntu/verityos/agents/nova/logs"

    def startup(self):
        log_audit("nova", "Boot", "Agent is now active.")
        print(f"[✔] nova v1.0 started.")

if __name__ == "__main__":
    agent = Nova()
    agent.startup()