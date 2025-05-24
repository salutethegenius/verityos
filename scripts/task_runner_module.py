from pathlib import Path
from scripts.logger_module import write_log

def execute_auto_tasks(config, log_file):
    if config.get("auto_task") == True:
        tasks_path = Path(f"/home/ubuntu/verityos/agents/{config['agent_name']}/tasks")
        completed_path = tasks_path / "completed"
        tasks_path.mkdir(parents=True, exist_ok=True)
        completed_path.mkdir(parents=True, exist_ok=True)
        for task_file in tasks_path.glob("*.task"):
            task_content = task_file.read_text().strip()
            print(f"\n📝 Auto-Task: {task_file.name}\n{task_content}")
            write_log(log_file, f"TASK: {task_file.name}\n{task_content}")
            task_file.rename(completed_path / task_file.name)
        print("✅ Auto-task execution completed.\n")