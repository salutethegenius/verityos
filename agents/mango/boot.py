#!/usr/bin/env python3
import typer
import os
import zipfile
import shutil
from rich import print
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import json
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
from scanapi import scan_openapi, save_scan_result


app = typer.Typer()


load_dotenv()

# Mango step-by-step tutorial CLI command
@app.command()
def tutorial():
    """Launch a step-by-step tutorial explaining how Mango works."""
    print("[bold green]📘 Mango Tutorial Mode Activated[/bold green]")
    print("\nWelcome to Mango! Here's what you can do:")
    print("1. [yellow]Create an agent:[/yellow] Use [blue]mango new[/blue] to build a new agent.")
    print("2. [yellow]Wizard mode:[/yellow] Run [blue]mango wizard[/blue] for a guided setup.")
    print("3. [yellow]Simulate:[/yellow] Use [blue]mango testagent [agent_name][/blue] to preview behavior.")
    print("4. [yellow]Bundle:[/yellow] Use [blue]mango bundleagent [agent_name][/blue] to package the agent.")
    print("5. [yellow]Install:[/yellow] Install shared agents using [blue]mango installagent[/blue].")
    print("6. [yellow]Publish:[/yellow] Share your agent with [blue]mango publishagent[/blue].")
    print("7. [yellow]Agent info:[/yellow] View agent metadata using [blue]mango agentinfo [agent_name][/blue].")
    print("\n[green]Explore, build, and automate. You got this![/green]")

@app.command()
def editagent(agent_name: str):
    """Open an agent folder in nano (CLI editor)."""
    agent_dir = OUTPUT_BASE / agent_name.lower().replace(" ", "_")
    if not agent_dir.exists():
        print(f"[red]Agent not found: {agent_dir}[/red]")
        raise typer.Exit()

    os.system(f"nano {agent_dir}/boot.py")

@app.command()
def runonce(agent_name: str):
    """Run the agent’s main logic immediately (ignoring scheduler)."""
    agent_dir = OUTPUT_BASE / agent_name.lower().replace(" ", "_")
    boot_path = agent_dir / "boot.py"
    if not boot_path.exists():
        print(f"[red]❌ boot.py not found in {agent_dir}[/red]")
        raise typer.Exit()

    os.system(f"python3 {boot_path}")

@app.command()
def gentests(agent_name: str):
    """Generate a basic test file for an agent."""
    agent_dir = OUTPUT_BASE / agent_name.lower().replace(" ", "_")
    test_path = agent_dir / "test_agent.py"
    if not agent_dir.exists():
        print(f"[red]❌ Agent not found: {agent_dir}[/red]")
        raise typer.Exit()

    test_code = f'''
# test_agent.py — basic test scaffold
def test_boot_runs():
    try:
        import boot
        boot.run()
        print("✅ boot.run() executed without errors.")
    except Exception as e:
        print("❌ boot.run() failed:", e)
'''

    with open(test_path, "w") as f:
        f.write(test_code.strip() + "\n")

    print(f"[green]✅ Test file created:[/green] {test_path}")

@app.command()
def demoagent():
    """Scaffold a demo agent using preset content."""
    from datetime import datetime
    demo_name = f"demo_agent_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    agent_dir = OUTPUT_BASE / demo_name
    os.makedirs(agent_dir, exist_ok=True)

    context = {
        "agent_name": demo_name,
        "description": "This is a demo agent to test the Mango scaffold flow.",
    }

    render_template("boot.py.j2", context, agent_dir / "boot.py")
    render_template("config.yaml.j2", context, agent_dir / "config.yaml")

    with open(agent_dir / "metadata.json", "w") as f:
        json.dump({
            "agent_name": demo_name,
            "creator": "Kenneth Moncur",
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "license": "© 2025 VerityOS | KemisDigital Labs. All rights reserved.",
            "tested": False
        }, f, indent=2)

    # Generate basic unit test
    test_code = f'''
    # test_agent.py — basic unit test for {demo_name}
    def test_boot_runs():
        try:
            import boot
            boot.run()
            print("✅ boot.run() executed without errors.")
        except Exception as e:
            print("❌ boot.run() failed:", e)
    '''
    with open(agent_dir / "test_agent.py", "w") as f:
        f.write(test_code.strip() + "\n")
    print(f"[green]✅ Unit test created:[/green] {agent_dir / 'test_agent.py'}")

    print(f"[green]✅ Demo agent '{demo_name}' created at {agent_dir}[/green]")

@app.command()
def trashagent(agent_name: str, confirm: bool = typer.Option(False, help="Confirm trash action")):
    """Move an agent to the VerityOS trash bin instead of deleting permanently."""
    agent_folder = OUTPUT_BASE / agent_name.lower().replace(" ", "_")
    trash_base = Path("/home/ubuntu/verityos/trash")
    trash_folder = trash_base / f"{agent_name.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    registry_path = Path("/home/ubuntu/verityos/registry/agents.json")

    if not agent_folder.exists():
        print(f"[red]❌ Agent not found: {agent_folder}[/red]")
        raise typer.Exit()

    if not confirm:
        print(f"[yellow]⚠ Are you sure you want to trash '{agent_name}'? Use --confirm to proceed.[/yellow]")
        raise typer.Exit()

    trash_base.mkdir(parents=True, exist_ok=True)
    shutil.move(str(agent_folder), str(trash_folder))
    print(f"[green]🗑 Agent moved to trash: {trash_folder}[/green]")

    if registry_path.exists():
        with open(registry_path, "r") as f:
            agents = json.load(f)

        updated_agents = [a for a in agents if a.get("agent_name") != agent_name]

        with open(registry_path, "w") as f:
            json.dump(updated_agents, f, indent=2)

        print(f"[green]✅ Agent '{agent_name}' removed from registry[/green]")

TEMPLATE_DIR = Path(__file__).parent / "templates"
OUTPUT_BASE = Path("/home/ubuntu/verityos/agents")

@app.command()
def listagents():
    """List all registered agents from the local registry."""
    registry_path = Path("/home/ubuntu/verityos/registry/agents.json")
    if not registry_path.exists():
        print("[yellow]No agents registered yet.[/yellow]")
        return

    with open(registry_path, "r") as f:
        agents = json.load(f)

    print("[bold green]🔧 Installed Agents:[/bold green]")
    for agent in agents:
        if isinstance(agent, dict) and "agent_name" in agent:
            name = agent.get("agent_name", "Unnamed")
            version = agent.get("version", "0.0.0")
            creator = agent.get("creator", "Unknown")
            print(f"- {name} (v{version}) by {creator}")
        else:
            print(f"[yellow]⚠ Skipped invalid agent entry: {agent}[/yellow]")

def render_template(template_name, context, output_path):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_name)
    content = template.render(context)
    with open(output_path, "w") as f:
        f.write(content)
    print(f"[green]Created:[/green] {output_path}")

@app.command()
def importagent(from_zip: str = typer.Option(..., help="Path to agent .zip bundle")):
    """Import a zipped agent into VerityOS and register it."""
    bundle_path = Path(from_zip).resolve()
    if not bundle_path.exists():
        print(f"[red]Bundle not found: {bundle_path}[/red]")
        raise typer.Exit()

    with zipfile.ZipFile(bundle_path, 'r') as zip_ref:
        names = zip_ref.namelist()
        root_dir = names[0].split('/')[0]
        extract_path = OUTPUT_BASE / root_dir

        if extract_path.exists():
            print(f"[red]Agent folder already exists: {extract_path}[/red]")
            raise typer.Exit()

        zip_ref.extractall(OUTPUT_BASE)
        print(f"[green]✅ Extracted to: {extract_path}[/green]")

    # Validate contents
    required_files = {"boot.py", "config.yaml", "metadata.json"}
    actual_files = {f.name for f in extract_path.iterdir() if f.is_file()}
    missing = required_files - actual_files

    if missing:
        print(f"[red]❌ Missing required files in {extract_path.name}: {', '.join(missing)}[/red]")
        print("[red]Make sure your zip follows this structure:[/red]")
        print("ping.zip\n└── ping/\n    ├── boot.py\n    ├── config.yaml\n    └── metadata.json")
        # Clean up
        shutil.rmtree(extract_path)
        raise typer.Exit()

    # Enforce presence of metadata.json
    metadata_path = extract_path / "metadata.json"
    if not metadata_path.exists():
        print(f"[red]❌ metadata.json missing in {extract_path.name}[/red]")
        shutil.rmtree(extract_path)
        raise typer.Exit()

    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"[red]❌ Failed to parse metadata.json: {e}[/red]")
        shutil.rmtree(extract_path)
        raise typer.Exit()

    if metadata.get("agent_name") != root_dir:
        print(f"[red]❌ Mismatch: metadata.agent_name = '{metadata.get('agent_name')}', folder = '{root_dir}'[/red]")
        shutil.rmtree(extract_path)
        raise typer.Exit()

    registry_path = Path("/home/ubuntu/verityos/registry/agents.json")
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    if registry_path.exists():
        with open(registry_path, "r") as f:
            agents = json.load(f)
    else:
        agents = []

    metadata["path"] = str(extract_path)
    metadata["installed_at"] = datetime.utcnow().isoformat() + "Z"
    agents.append(metadata)

    with open(registry_path, "w") as f:
        json.dump(agents, f, indent=2)

    print(f"[green]📦 Agent '{metadata['agent_name']}' registered.[/green]")

@app.command()
def new():
    """Create a new agent scaffold using Mango."""
    print("[bold yellow]🍃 Welcome to Mango: Agent Builder[/bold yellow]")

    agent_name = typer.prompt("What should we name this agent?")

    use_plan = typer.confirm("Would you like to load your most recent reasoning plan?")
    plan_data = None
    if use_plan:
        reasoning_dir = Path("/home/ubuntu/verityos/logs/mango/reasoning")
        if not reasoning_dir.exists() or not list(reasoning_dir.glob("*.json")):
            print("[red]No reasoning plans found.[/red]")
        else:
            latest_plan = max(reasoning_dir.glob("*.json"), key=os.path.getmtime)
            with open(latest_plan, "r") as f:
                plan_data = json.load(f)
            print(f"[green]Loaded plan from:[/green] {latest_plan}")

    goal = typer.prompt("Describe what this agent should do")

    agent_dir = OUTPUT_BASE / agent_name.lower().replace(" ", "_")
    if agent_dir.exists():
        print(f"[red]Agent folder {agent_dir} already exists.[/red]")
        raise typer.Exit()

    os.makedirs(agent_dir, exist_ok=True)

    context = {
        "agent_name": agent_name,
        "description": plan_data['steps'][0] if plan_data else goal,
    }

    if plan_data:
        for input_key in plan_data.get("required_inputs", []):
            context[input_key] = typer.prompt(f"Enter value for '{input_key}'")

    # Optional: Check for last scanned API and prompt integration
    api_scan_path = Path("/home/ubuntu/verityos/logs/mango/apis/scan_result.json")
    if api_scan_path.exists():
        with open(api_scan_path, "r") as f:
            api_data = json.load(f)
        endpoints = api_data.get("endpoints", [])
        if endpoints:
            print("\n[bold magenta]📡 API Scan Detected[/bold magenta]")
            for i, ep in enumerate(endpoints):
                print(f"[{i}] {ep['method']} {ep['path']} — {ep['summary']}")
            selected = typer.prompt("Choose an endpoint by number", type=int)
            selected_ep = endpoints[selected]

            base_url = typer.prompt("Base URL for the API (e.g. https://api.example.com)")
            auth_type = typer.prompt("Auth type (none / bearer)", default="bearer")

            param_names = [p["name"] for p in selected_ep.get("parameters", [])]
            context.update({
                "function_name": selected_ep["summary"].replace(' ', '_').lower(),
                "path": selected_ep["path"],
                "method": selected_ep["method"].lower(),
                "base_url": base_url,
                "auth_type": auth_type,
                "param_list": param_names,
                "payload_params": param_names  # For now, reuse params for payload
            })

            render_template("api_client.py.j2", context, agent_dir / "api_client.py")

    # Render base files
    render_template("config.yaml.j2", context, agent_dir / "config.yaml")
    render_template("boot.py.j2", context, agent_dir / "boot.py")

    # Generate basic unit test
    test_code = f'''
    # test_agent.py — basic unit test for {agent_name}
    def test_boot_runs():
        try:
            import boot
            boot.run()
            print("✅ boot.run() executed without errors.")
        except Exception as e:
            print("❌ boot.run() failed:", e)
    '''
    with open(agent_dir / "test_agent.py", "w") as f:
        f.write(test_code.strip() + "\n")
    print(f"[green]✅ Unit test created:[/green] {agent_dir / 'test_agent.py'}")

    if plan_data and "cron" in plan_data.get("preferred_method", "").lower():
        render_template("scheduler.py.j2", context, agent_dir / "scheduler.py")
    if plan_data and any("medium" in json.dumps(step).lower() for step in plan_data["steps"]):
        render_template("medium_client.py.j2", context, agent_dir / "medium_client.py")

    print("\n[bold green]✅ Done![/bold green] Your agent scaffold is ready.")
    print(f"Check the folder: [cyan]{agent_dir}[/cyan]")

@app.command()
def reason():
    """Use LLM to reason through a user's automation goal and generate a plan."""
    print("[bold cyan]🧠 Mango Reasoning Mode Activated[/bold cyan]")
    goal = typer.prompt("What is your agent supposed to accomplish?")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[red]Missing OpenAI API key. Set OPENAI_API_KEY in environment.[/red]")
        raise typer.Exit()
    client = OpenAI(api_key=api_key)

    prompt = f"""You are an expert AI architect. Your job is to turn the following plain-English goal into a structured automation plan.

Goal: {goal}

Respond with a JSON object that includes ONLY:
- "steps": a list of strings, each being a clear step to build this agent
- "required_inputs": a list of parameter names you would ask the user to provide
- "preferred_method": a single string describing the best approach (e.g. cron + Python + requests)

Format:
{{
  "steps": ["Step 1", "Step 2", "Step 3"],
  "required_inputs": ["api_key", "post_schedule"],
  "preferred_method": "cron + Python script + REST API"
}}
"""

    print("[yellow]Thinking...[/yellow]")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful automation planner."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
        plan = response.choices[0].message.content
        parsed = json.loads(plan)

        log_dir = Path("/home/ubuntu/verityos/logs/mango/reasoning")
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"plan_{timestamp}.json"

        with open(log_file, "w") as f:
            json.dump(parsed, f, indent=2)

        print("[green]✅ Plan generated and saved![/green]")
        print(f"[cyan]View at: {log_file}[/cyan]")
    except Exception as e:
        print(f"[red]Failed to generate plan: {e}[/red]")

@app.command()
def scanapi(file: str = typer.Option(..., help="Path to OpenAPI JSON file")):
    """Scan an OpenAPI JSON file and extract endpoints."""
    print(f"[bold cyan]📡 Scanning API from file:[/bold cyan] {file}")
    result = scan_openapi(file)
    if "error" in result:
        print(f"[red]Error:[/red] {result['error']}")
        raise typer.Exit()

    output_path = save_scan_result(result)
    print(f"[green]✅ API scan saved to:[/green] {output_path}")

@app.command()
def testagent(agent_name: str):
    """Simulate running an agent without making real API calls."""
    print(f"[bold yellow]🧪 Simulating agent:[/bold yellow] {agent_name}")
    agent_path = OUTPUT_BASE / agent_name.lower().replace(" ", "_")

    boot_path = agent_path / "boot.py"
    if not boot_path.exists():
        print(f"[red]Agent boot.py not found in {agent_path}[/red]")
        raise typer.Exit()

    config_path = agent_path / "config.yaml"
    config = {}
    if config_path.exists():
        import yaml
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

    print(f"[cyan]Found agent at: {agent_path}[/cyan]")
    print(f"[blue]Note:[/blue] This simulation won't make actual HTTP requests.")
    print(f"[green]Loaded config:[/green] {config}")

    api_path = agent_path / "api_client.py"
    if api_path.exists():
        with open(api_path, "r") as f:
            api_code = f.read()
        api_code = api_code.replace("requests.post", "print").replace("requests.get", "print")
        print("\n[bold magenta]--- Simulated API Client ---[/bold magenta]")
        print(api_code)
        print("\n[bold green]🔁 Simulated API Call Output:[/bold green]")
        print("Simulated call to: [blue]https://example.com/ping[/blue]")
        print(f"Headers: {{'Authorization': 'Bearer {config.get('token', '...')}'}}")
        print("Payload: {}")
        print("Response: 200 OK — {'message': 'Ping successful'}")

    print("\n[bold magenta]--- Simulated boot.py Output ---[/bold magenta]")
    try:
        with open(boot_path, "r") as f:
            boot_code = f.read()
        print(boot_code)
    except Exception as e:
        print(f"[red]Failed to read boot.py: {e}[/red]")

    print("\n[bold cyan]🧾 Agent Summary:[/bold cyan]")
    print(f"- Name: {agent_name}")
    print(f"- Config keys: {list(config.keys())}")
    print(f"- Boot + API logic detected ✅")

@app.command()
def updateagent(agent_name: str):
    """Update or regenerate files for an existing agent."""
    print(f"[bold blue]🔧 Updating agent:[/bold blue] {agent_name}")
    agent_dir = OUTPUT_BASE / agent_name.lower().replace(" ", "_")

    if not agent_dir.exists():
        print(f"[red]Agent folder not found: {agent_dir}[/red]")
        raise typer.Exit()

    context = {"agent_name": agent_name}
    config_path = agent_dir / "config.yaml"
    if config_path.exists():
        import yaml
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        context.update(config_data)

    api_path = agent_dir / "api_client.py"
    if api_path.exists() and typer.confirm("Regenerate api_client.py?"):
        render_template("api_client.py.j2", context, api_path)

    boot_path = agent_dir / "boot.py"
    if boot_path.exists() and typer.confirm("Regenerate boot.py?"):
        render_template("boot.py.j2", context, boot_path)

    config_bak = agent_dir / "config.yaml.bak"
    if config_path.exists():
        config_path.rename(config_bak)
        print(f"[yellow]Backed up old config to:[/yellow] {config_bak}")
        render_template("config.yaml.j2", context, config_path)

    print(f"[green]✅ Agent {agent_name} updated![/green]")




# Bundle agent command (updated: verify, optional files, enhanced README)
@app.command()
def bundleagent(agent_name: str):
    """Bundle an agent into a distributable zip with metadata and license."""
    from datetime import datetime

    agent_dir = OUTPUT_BASE / agent_name.lower().replace(" ", "_")
    if not agent_dir.exists():
        print(f"[red]Agent not found: {agent_dir}[/red]")
        raise typer.Exit()

    # Verify agent integrity before bundling
    print(f"[bold cyan]🔍 Verifying agent before bundling...[/bold cyan]")
    try:
        verifyagent(agent_name)
    except SystemExit:
        print("[red]❌ Verification failed. Bundle aborted.[/red]")
        raise typer.Exit()

    version = typer.prompt("Enter version", default="1.0.0")
    creator = typer.prompt("Enter creator name")

    # Set up bundle directory
    bundle_dir = Path("/home/ubuntu/verityos/bundles") / agent_name
    bundle_dir.mkdir(parents=True, exist_ok=True)

    files_to_include = ["boot.py", "api_client.py", "config.yaml", "scheduler.py", "medium_client.py", "test_agent.py"]
    for file_name in files_to_include:
        src = agent_dir / file_name
        dst = bundle_dir / file_name
        if src.exists():
            with open(src, "r") as f:
                content = f.read()
            if file_name.endswith(".py"):
                content = f"# © 2025 VerityOS | KemisDigital Labs. All rights reserved.\n{content}"
            with open(dst, "w") as f:
                f.write(content)

    # Create README
    readme_path = bundle_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write(f"# Agent: {agent_name}\n")
        f.write(f"Created by: {creator}\n")
        f.write(f"Version: {version}\n")
        f.write(f"Packaged: {datetime.utcnow().isoformat()} UTC\n")
        f.write("\nThis agent was created using VerityOS and Mango.\n")
        f.write("\n## Files Included:\n")
        for file_name in files_to_include:
            if (bundle_dir / file_name).exists():
                f.write(f"- {file_name}\n")
        f.write("\n## Running the Agent:\n")
        f.write("Run this agent using:\n")
        f.write("```bash\npython3 boot.py\n```\n")

    # Create metadata.json
    metadata = {
        "agent_name": agent_name,
        "version": version,
        "creator": creator,
        "license": "© 2025 VerityOS | KemisDigital Labs. All rights reserved.",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "tested": False
    }
    with open(bundle_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Zip it
    zip_path = bundle_dir.with_suffix(".zip")
    shutil.make_archive(str(zip_path).replace(".zip", ""), 'zip', bundle_dir)
    print(f"[green]✅ Agent bundled to: {zip_path}[/green]")

# Publish agent command: publish a bundled agent to the VerityOS marketplace
@app.command()
def publishagent(agent_name: str):
    """Publish a bundled agent to the VerityOS marketplace."""
    bundle_zip = Path(f"/home/ubuntu/verityos/bundles/{agent_name}.zip")
    if not bundle_zip.exists():
        print(f"[red]❌ Bundle not found for agent '{agent_name}': {bundle_zip}[/red]")
        raise typer.Exit()

    market_dir = Path("/home/ubuntu/verityos/marketplace")
    market_dir.mkdir(parents=True, exist_ok=True)

    target = market_dir / f"{agent_name}.zip"
    shutil.copy(bundle_zip, target)

    print(f"[green]✅ Published {agent_name} to marketplace[/green]")
    print(f"[blue]Location:[/blue] {target}")

@app.command()
def demo():
    """Create a demo agent scaffold named 'hello_agent'."""
    agent_name = "hello_agent"
    agent_dir = OUTPUT_BASE / agent_name

    if agent_dir.exists():
        print(f"[red]Demo agent folder {agent_dir} already exists.[/red]")
        raise typer.Exit()

    os.makedirs(agent_dir, exist_ok=True)

    context = {
        "agent_name": agent_name,
        "description": "A simple demo agent that says hello.",
    }

    render_template("boot.py.j2", context, agent_dir / "boot.py")
    render_template("config.yaml.j2", context, agent_dir / "config.yaml")
    render_template("scheduler.py.j2", context, agent_dir / "scheduler.py")

    print(f"[green]✅ Demo agent '{agent_name}' created at {agent_dir}[/green]")


# Agent integrity verification command
@app.command()
def verifyagent(agent_name: str):
    """Perform integrity check on an installed agent."""
    print(f"[bold cyan]🔍 Verifying agent: {agent_name}[/bold cyan]")
    agent_dir = OUTPUT_BASE / agent_name.lower().replace(" ", "_")

    if not agent_dir.exists():
        print(f"[red]Agent folder not found: {agent_dir}[/red]")
        raise typer.Exit()

    # Check for required files
    required_files = ["boot.py", "config.yaml", "metadata.json"]
    missing = [f for f in required_files if not (agent_dir / f).exists()]
    if missing:
        print(f"[red]❌ Missing required files: {', '.join(missing)}[/red]")
        raise typer.Exit()
    else:
        print("[green]✅ All required files found[/green]")

    # Validate metadata.json
    metadata_path = agent_dir / "metadata.json"
    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"[red]❌ Failed to read metadata.json: {e}[/red]")
        raise typer.Exit()

    if metadata.get("agent_name") != agent_name:
        print(f"[red]❌ metadata.agent_name = {metadata.get('agent_name')} does not match folder name[/red]")
    else:
        print("[green]✅ metadata.agent_name matches folder name[/green]")

    if not metadata.get("version"):
        print("[red]❌ metadata.version is missing[/red]")
    else:
        print(f"[green]✅ version = {metadata['version']}[/green]")

    # Check config.yaml
    import yaml
    config_path = agent_dir / "config.yaml"
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        print("[green]✅ config.yaml loaded successfully[/green]")
        print(f"[cyan]Config keys:[/cyan] {list(config.keys())}")
    except Exception as e:
        print(f"[red]❌ Failed to load config.yaml: {e}[/red]")

    # Optional: api_client.py
    if not (agent_dir / "api_client.py").exists():
        print("[yellow]⚠ api_client.py not found (optional)[/yellow]")
    else:
        print("[green]✅ api_client.py found[/green]")

    print(f"[bold green]✅ Agent {agent_name} passed verification[/bold green]")


# Install agent from marketplace with --force support
@app.command()
def installagent(agent_name: str, force: bool = typer.Option(False, help="Force overwrite if agent already exists")):
    """Install an agent from the VerityOS marketplace."""
    market_path = Path(f"/home/ubuntu/verityos/marketplace/{agent_name}.zip")
    if not market_path.exists():
        print(f"[red]❌ Agent not found in marketplace: {market_path}[/red]")
        raise typer.Exit()

    print(f"[bold cyan]📥 Installing agent '{agent_name}' from marketplace...[/bold cyan]")

    # Check if agent already exists
    extract_path = OUTPUT_BASE / agent_name.lower().replace(" ", "_")
    if extract_path.exists():
        if not force:
            print(f"[red]❌ Agent '{agent_name}' already exists. Use --force to overwrite.[/red]")
            raise typer.Exit()
        else:
            shutil.rmtree(extract_path)
            print(f"[yellow]⚠ Removed existing agent folder: {extract_path}[/yellow]")

    importagent(from_zip=str(market_path))


# Sprint 10: Uninstall agent command
@app.command()
def uninstallagent(agent_name: str, confirm: bool = typer.Option(False, help="Confirm uninstallation")):
    """Uninstall an agent from the system and remove it from registry."""
    agent_folder = OUTPUT_BASE / agent_name.lower().replace(" ", "_")
    registry_path = Path("/home/ubuntu/verityos/registry/agents.json")

    if not agent_folder.exists():
        print(f"[red]❌ Agent not found: {agent_folder}[/red]")
        raise typer.Exit()

    if not confirm:
        print(f"[yellow]⚠ Are you sure you want to uninstall '{agent_name}'? Use --confirm to proceed.[/yellow]")
        raise typer.Exit()

    shutil.rmtree(agent_folder)
    print(f"[green]✅ Agent folder removed: {agent_folder}[/green]")

    if registry_path.exists():
        with open(registry_path, "r") as f:
            agents = json.load(f)

        updated_agents = [a for a in agents if a.get("agent_name") != agent_name]

        with open(registry_path, "w") as f:
            json.dump(updated_agents, f, indent=2)

        print(f"[green]✅ Agent '{agent_name}' removed from registry[/green]")


# Agent info command: show detailed metadata and config for a given agent
@app.command()
def agentinfo(agent_name: str):
    """Display detailed metadata and configuration for an agent."""
    agent_dir = OUTPUT_BASE / agent_name.lower().replace(" ", "_")
    metadata_path = agent_dir / "metadata.json"
    config_path = agent_dir / "config.yaml"

    if not agent_dir.exists():
        print(f"[red]❌ Agent folder not found: {agent_dir}[/red]")
        raise typer.Exit()

    print(f"[bold cyan]ℹ Agent Info: {agent_name}[/bold cyan]")

    # Read metadata.json once
    metadata = {}
    if metadata_path.exists():
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        except Exception as e:
            print(f"[red]Failed to read metadata.json: {e}[/red]")
    else:
        print("[yellow]⚠ No metadata.json found[/yellow]")

    # Sprint 17: Show agent file sizes
    print("\n[green]📦 File Sizes:[/green]")
    for file in agent_dir.iterdir():
        if file.is_file():
            size_kb = round(file.stat().st_size / 1024, 2)
            print(f"- {file.name}: {size_kb} KB")

    if metadata:
        print("\n[green]📄 metadata.json:[/green]")
        for k, v in metadata.items():
            print(f"- [blue]{k}[/blue]: {v}")
        # Print creator/license/version again in highlighted format
        if "creator" in metadata:
            print(f"- [blue]creator[/blue]: {metadata['creator']}")
        if "license" in metadata:
            print(f"- [blue]license[/blue]: {metadata['license']}")
        if "version" in metadata:
            print(f"- [blue]version[/blue]: {metadata['version']}")

    if config_path.exists():
        print("\n[green]⚙ config.yaml:[/green]")
        try:
            import yaml
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                for k, v in config.items():
                    print(f"- [blue]{k}[/blue]: {v}")
        except Exception as e:
            print(f"[red]Failed to read config.yaml: {e}[/red]")
    else:
        print("[yellow]⚠ No config.yaml found[/yellow]")

    # Show code stats: lines of code in each .py file in the agent folder
    print("\n[green]📊 Code Stats:[/green]")
    for file in agent_dir.glob("*.py"):
        try:
            with open(file, "r") as f:
                lines = f.readlines()
            num_lines = len(lines)
            print(f"- {file.name}: {num_lines} lines")
        except Exception as e:
            print(f"[yellow]⚠ Failed to read {file.name}: {e}[/yellow]")

    # Sprint 19: Show command count
    if "config" in locals() and isinstance(config, dict) and "commands" in config:
        print("\n[green]📘 Command Summary:[/green]")
        print(f"- Total commands: {len(config['commands'])}")

    # Sprint 20: Show tested status
    if "tested" in metadata:
        print(f"\n[green]🧪 Testing Status:[/green]")
        print(f"- tested: {metadata['tested']}")

    # Sprint 21: Show license
    # (Removed duplicate license/version/creator printout)
    if "license" in metadata:
        print(f"\n[green]📜 License:[/green]")
        # Already printed above, skip duplicate
    else:
        print("\n[green]📜 License:[/green]\n- Not specified")

    # Sprint 22: Show creation timestamp
    if "created_at" in metadata:
        print(f"\n[green]📅 Created At:[/green]")
        print(f"- {metadata['created_at']}")

    # Sprint 23: Show README.md contents
    readme_path = agent_dir / "README.md"
    if readme_path.exists():
        print(f"\n[green]📖 README.md Preview:[/green]")
        try:
            with open(readme_path, "r") as f:
                lines = f.readlines()
                preview = "".join(lines[:10])  # Show first 10 lines
                print(preview.strip())
        except Exception as e:
            print(f"[red]Failed to read README.md: {e}[/red]")
    else:
        print("\n[green]📖 README.md Preview:[/green]\n- Not found")

# Mango agent migration utility: add missing metadata.json to legacy agents
@app.command()
def migrateagents():
    """Add metadata.json to older agents missing them."""
    from datetime import datetime

    base_path = Path("/home/ubuntu/verityos/agents")
    for agent_folder in base_path.iterdir():
        if agent_folder.is_dir():
            metadata_file = agent_folder / "metadata.json"
            boot_file = agent_folder / "boot.py"
            config_file = agent_folder / "config.yaml"

            if metadata_file.exists():
                continue

            agent_name = agent_folder.name
            metadata = {
                "agent_name": agent_name,
                "creator": "Unknown",
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat() + "Z",
                "license": "© 2025 VerityOS | KemisDigital Labs. All rights reserved.",
                "tested": False
            }
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            print(f"[green]🩺 Migrated:[/green] {agent_name} — metadata.json created")





@app.command()
def wizard():
    """Interactive CLI wizard to guide new users through agent creation."""
    print("[bold green]🧙 Welcome to Mango Wizard Mode[/bold green]")

    agent_name = typer.prompt("What should we name this agent?")
    goal = typer.prompt("What should this agent do?")
    schedule = typer.prompt("How often should it run? (e.g., every day at 9AM)")
    api_integration = typer.confirm("Does this agent need to use an API?")
    api_path = ""
    if api_integration:
        api_path = typer.prompt("If you have an OpenAPI file, provide the path (or leave blank)")

    print("\n[cyan]--- Summary ---[/cyan]")
    print(f"Agent Name: {agent_name}")
    print(f"Goal: {goal}")
    print(f"Schedule: {schedule}")
    print(f"API Integration: {'Yes' if api_integration else 'No'}")
    if api_path:
        print(f"API File: {api_path}")

    if not typer.confirm("Proceed with agent creation?"):
        print("[red]Aborted.[/red]")
        raise typer.Exit()

    # Simulate loading the plan
    from datetime import datetime
    agent_dir = OUTPUT_BASE / agent_name.lower().replace(" ", "_")
    os.makedirs(agent_dir, exist_ok=True)

    context = {
        "agent_name": agent_name,
        "description": goal,
        "schedule": schedule
    }

    if api_path and os.path.exists(api_path):
        from scanapi import scan_openapi, save_scan_result
        print("[cyan]Scanning API...[/cyan]")
        result = scan_openapi(api_path)
        context.update({
            "function_name": result["endpoints"][0]["summary"].replace(" ", "_").lower(),
            "path": result["endpoints"][0]["path"],
            "method": result["endpoints"][0]["method"].lower(),
            "base_url": typer.prompt("Base URL for the API"),
            "auth_type": typer.prompt("Auth type (none / bearer)", default="bearer"),
            "param_list": [],
            "payload_params": []
        })
        render_template("api_client.py.j2", context, agent_dir / "api_client.py")

    render_template("boot.py.j2", context, agent_dir / "boot.py")
    render_template("config.yaml.j2", context, agent_dir / "config.yaml")
    render_template("scheduler.py.j2", context, agent_dir / "scheduler.py")

    metadata = {
        "agent_name": agent_name,
        "creator": os.getenv("USER") or os.getenv("USERNAME") or "Unknown",
        "version": "1.0.0",
        "license": "© 2025 VerityOS | KemisDigital Labs. All rights reserved.",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "tested": False
    }
    with open(agent_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"[green]✅ Wizard agent '{agent_name}' created at {agent_dir}[/green]")


# Default greeting and Easter egg handler
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        print("[bold cyan]🍋 Welcome to Mango — Your AI Agent Builder[/bold cyan]\n")
        print("👋 Hi there! Here are some things you can try:")
        print("- [green]mango new[/green] – Create a new agent from scratch")
        print("- [green]mango wizard[/green] – Launch the guided setup wizard")
        print("- [green]mango demoagent[/green] – Generate a sample agent instantly")
        print("- [green]mango tutorial[/green] – Learn how Mango works")
        print("- [green]mango listagents[/green] – View installed agents")
        print("- [green]mango credits[/green] – View the Mango CLI creators\n")
        print("[yellow]🟡 Tip:[/yellow] Try '[bold green]mango new[/bold green]' to get started or '[bold green]mango wizard[/bold green]' for a guided experience.\n")
        raise typer.Exit()

# Credits/Easter egg command
@app.command()
def credits():
    """Show credits for Mango."""
    print("[bold yellow]✨ Mango CLI ✨[/bold yellow]")
    print("Developed by: Kenneth Moncur")
    print("Powered by: VerityOS and KemisDigital Labs")
    print("License: © 2025 VerityOS | KemisDigital Labs. All rights reserved.")
    print("Easter Egg: You found the 🍍 secret!")

# Ensure CLI entry point is at the very end, after all commands are registered
if __name__ == "__main__":
    app()