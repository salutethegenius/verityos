


# right.py

import sys
sys.path.append('/home/ubuntu/verityos')

from utils.logger import log_audit

class Right:
    def __init__(self):
        self.name = "right"
        self.version = "1.0"
        self.role = "Agent"
        self.memory_path = "/home/ubuntu/verityos/agents/right/memory_system"
        self.log_path = "/home/ubuntu/verityos/agents/right/logs"

    def startup(self):
        log_audit("right", "Boot", "Agent is now active.")
        print(f"[✔] right v1.0 started.")

if __name__ == "__main__":
    agent = Right()
    agent.startup()