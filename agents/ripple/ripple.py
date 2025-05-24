# ripple.py

import sys
sys.path.append('/home/ubuntu/verityos')

from utils.logger import log_audit

class Ripple:
    def __init__(self):
        self.name = "ripple"
        self.version = "1.0"
        self.role = "Agent"
        self.memory_path = "/home/ubuntu/verityos/agents/ripple/memory_system"
        self.log_path = "/home/ubuntu/verityos/agents/ripple/logs"

    def startup(self):
        import os

        def ensure_dirs():
            paths = [
                "/home/ubuntu/verityos/memory_system/ripple/",
                "/home/ubuntu/verityos/logs/ripple/",
                "/home/ubuntu/verityos/messages/ripple/"
            ]
            for path in paths:
                os.makedirs(path, exist_ok=True)

        ensure_dirs()
        log_audit("ripple", "Boot", "Agent is now active.")
        print(f"[✔] ripple v1.0 started.")

if __name__ == "__main__":
    agent = Ripple()
    agent.startup()