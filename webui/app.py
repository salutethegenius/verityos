from flask import Flask, request, send_from_directory
import subprocess
import os

app = Flask(__name__)

CONFIG_PATH = "/home/ubuntu/verityos/agents/verity/config.yaml"

DEFAULT_CONFIG = """
memory_path: /home/ubuntu/verityos/memory/memory.txt
model: mistral-2b
agent_name: verity
chatmode: off
vault_enabled: true
"""

if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'w') as f:
        f.write(DEFAULT_CONFIG.strip() + "\n")

BOOT_PATH = "/home/ubuntu/verityos/agents/verity/boot.py"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()
    cmd = data['command'].strip()
    print(f"🔹 Received command: {cmd}")

    try:
        if not os.path.exists(CONFIG_PATH):
            return "❌ config.yaml is missing at: " + CONFIG_PATH

        if cmd.startswith('.query'):
            arg = cmd.replace('.query', '').strip()
            result = subprocess.run(['python3', BOOT_PATH, '--query', arg], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd.startswith('.note'):
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd.startswith('.learn'):
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd == '.learned':
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd == '.recall':
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd == '.summarize':
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd == '.insight':
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd == '.train':
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd.startswith('.vault '):
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd == '.analyze memory':
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd == '.chatmode on':
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd == '.chatmode off':
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd.startswith('.agents') or cmd.startswith('.status'):
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd == '.help':
            result = subprocess.run(['python3', BOOT_PATH, '--command', '.help'], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd == '.intro':
            result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)
            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        elif cmd == '.exit':
            return "👋 Shutting down session (manual exit)"

        else:
            with open(CONFIG_PATH, 'r') as f:
                config_lines = f.read().splitlines()
            chat_mode_line = next((line for line in config_lines if line.startswith('chatmode:')), 'chatmode: off')
            chat_mode = chat_mode_line.split(':')[-1].strip().lower()

            if chat_mode == "on" and not cmd.startswith('.'):
                result = subprocess.run(['python3', BOOT_PATH, '--query', cmd], capture_output=True, text=True)
            else:
                result = subprocess.run(['python3', BOOT_PATH, '--command', cmd], capture_output=True, text=True)

            print(f"🔧 Executing: {' '.join(result.args)}")
            print(f"📤 Output:\n{result.stdout}\n📥 Errors:\n{result.stderr}")

        output = result.stdout.strip() if result.stdout else ""
        errors = result.stderr.strip() if result.stderr else ""
        return output or errors or "✅ Executed (no response returned)"
    
    except Exception as e:
        return f"❌ Error running command: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
