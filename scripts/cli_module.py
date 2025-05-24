

import sys

def handle_cli_args(config):
    args = sys.argv[1:]
    if not args:
        return

    if "--query" in args:
        idx = args.index("--query")
        query = args[idx + 1] if len(args) > idx + 1 else None
        if query:
            print(f"🧠 Verity (query mode): {query}")
            # Insert future query routing here
        else:
            print("⚠️  Missing query argument after --query")
        sys.exit(0)

    if "--help" in args or "-h" in args:
        print("""Available CLI Flags:
  --query [text]   Run a one-off query with Verity
  --help           Show this help message
""")
        sys.exit(0)