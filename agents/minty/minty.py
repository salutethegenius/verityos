


# minty.py

import sys
sys.path.append('/home/ubuntu/verityos')

from utils.logger import log_audit

class Minty:
    def __init__(self):
        self.name = "minty"
        self.version = "1.0"
        self.role = "Agent"
        self.memory_path = "/home/ubuntu/verityos/agents/minty/memory_system"
        self.log_path = "/home/ubuntu/verityos/agents/minty/logs"

    def startup(self):
        log_audit("minty", "Boot", "Agent is now active.")
        print(f"[✔] minty v1.0 started.")

if __name__ == "__main__":
    agent = Minty()
    agent.startup()