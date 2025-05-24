


import sys
sys.path.append('/home/ubuntu/verityos')

import sys
from scripts.builder_module import parse_command

def main():
    if len(sys.argv) < 3 or sys.argv[1] != ".build" or sys.argv[2] != "agent":
        print("Usage: .build agent <AgentName>")
        return

    agent_name = sys.argv[3] if len(sys.argv) > 3 else None
    if not agent_name:
        print("❌ Please provide an agent name.")
        return

    result = parse_command(f".build agent {agent_name.lower()}")
    print(result)

if __name__ == "__main__":
    main()