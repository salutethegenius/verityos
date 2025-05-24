

import os
from datetime import datetime

AUDIT_LOG_PATH = "/home/ubuntu/verityos/logs/auditlog.md"

def log_audit(agent: str, action: str, details: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"""### {timestamp} — Agent: {agent}
Action: {action}
Details: {details}

---
"""
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    with open(AUDIT_LOG_PATH, "a") as log_file:
        log_file.write(log_entry)