from pathlib import Path
import time

def init_log(log_path):
    log_file = Path(log_path) / f"session_{int(time.time())}.log"
    log_file.touch()
    return log_file

def write_log(log_file, entry):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {entry}\n")