# ui_module.py

from datetime import datetime
import pytz, psutil
from pathlib import Path
import time

from scripts.system_module import get_system_report

def render_banner():
    return r"""

##     ##  #######   ######  
##     ## ##     ## ##    ## 
##     ## ##     ## ##       
##     ## ##     ##  ######  
 ##   ##  ##     ##       ## 
  ## ##   ##     ## ##    ## 
   ###     #######   ######  
  
    Your AI — Your Rules!
"""

def render_startup_summary(config, boot_start):
    now = datetime.now(pytz.timezone("America/Nassau")).strftime("%A, %B %d, %Y – %I:%M %p")
    lines = [
      render_banner(),
      "========================================",
      "\033[96mVerityOS Startup Summary:\033[0m",
      "========================================",
      f"Date:         {now}",
      f"Memory Path:  {config['memory_path']}",
      f"Logs Path:    {config['log_path']}",
      f"Chat Mode:    {config.get('chatmode', 'on').upper()}",
      "----------------------------------------",
      f"System Check: {get_system_report() or 'Unavailable'}",
      # Agent‐status can be delegated to another helper
    ]
    lines.append(f"\033[92m⏱ Boot Duration: {round(time.time() - boot_start, 2)} seconds\033[0m")
    return "\n".join(lines)