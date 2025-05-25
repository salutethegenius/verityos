


# mango.py

import sys
sys.path.append('/home/ubuntu/verityos')

from utils.logger import log_audit

class Mango:
    def __init__(self):
        self.name = "mango"
        self.version = "1.0"
        self.role = "Assistant"
        self.memory_path = "/home/ubuntu/verityos/agents/mango/memory_system"
        self.log_path = "/home/ubuntu/verityos/agents/mango/logs"

    def startup(self):
        log_audit("mango", "Boot", "Agent is now active.")
        print(f"[✔] mango v1.0 started.")

if __name__ == "__main__":
    agent = Mango()
    agent.startup()