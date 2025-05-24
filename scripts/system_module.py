


import psutil

def get_system_report():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    return f"CPU Usage: {cpu}% | RAM Usage: {ram.percent}% of {round(ram.total / 1e9, 2)} GB"