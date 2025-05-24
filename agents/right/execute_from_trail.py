


import sys
sys.path.append('/home/ubuntu/verityos')
import os
import json
from datetime import datetime
from utils.logger import log_audit

TRAIL_DIR = "/home/ubuntu/verityos/shared/decision_trails/"

def get_latest_trail():
    files = [f for f in os.listdir(TRAIL_DIR) if f.endswith(".json")]
    if not files:
        print("No decision trails found.")
        return None

    files.sort(reverse=True)
    latest_file = files[0]
    with open(os.path.join(TRAIL_DIR, latest_file), "r") as f:
        data = json.load(f)
        return data, latest_file

def execute_from_trail():
    result = get_latest_trail()
    if result is None:
        return

    trail_data, filename = result
    task = trail_data["task"]
    recommendation = trail_data["recommendation"]
    reasoning = trail_data["reasoning"]

    print(f"🛠️ Right is executing from trail: {filename}")
    print(f"Task: {task}")
    print(f"Recommended Path: {recommendation}")
    print(f"Reasoning: {reasoning}")

    log_audit(
        agent="Right",
        action="Read Decision Trail",
        details=f"Prepared to execute: {task} (Path {recommendation})"
    )

if __name__ == "__main__":
    execute_from_trail()