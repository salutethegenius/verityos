# Minty: Financial Visibility Agent

Minty helps you connect to Stripe (and future QuickBooks) to fetch, categorize, and snapshot your transactions directly from the terminal.

---

## Features

- **Fetch** new transactions (Stripe charges & refunds) since last run, with caching  
- **Map** transactions into categories based on your `category_map`  
- **Snapshot** month-to-date totals for each category  
- **Report** a simple Monthly P&L summary in dollars  
- **Easy CLI**: interact with small set of intuitive commands  

---

## Setup

1. **Clone** the repo and switch to the Minty directory:  
   ```bash
   git clone https://github.com/your-org/verityos-agents.git
   cd verityos-agents/agents/minty
   ```
2. **Install dependencies**:  
   ```bash
   pip install -r requirements_minty.txt
   ```
3. **Configure** the `config.yaml` file:  
   ```yaml
   name: Minty
   mode: command
   stripe_api_key: sk_test_yourkey
   category_map:
     charge: Revenue
     refund: Refunds
   memory_path: ./memory_system
   log_path: ./logs
   ```
4. (Optional) **Alias** for convenience:  
   ```bash
   echo "alias minty='python /home/ubuntu/verityos/agents/minty/boot.py --integration stripe'" >> ~/.bashrc
   source ~/.bashrc
   ```
5. **Run** Minty:  
   ```bash
   python boot.py --integration stripe
   # or, if aliased:
   minty
   ```

---

## Usage

On startup, Minty will display:
```
🔁 Booting Minty (mode: command)
📂 Memory: ./memory_system | Logs: ./logs
🧠 Available commands: fetch, map, snapshot, report, exit
```

**Commands:**

- `fetch`      Fetch new Stripe transactions since last run  
- `map`        Assign each fetched transaction to a category  
- `snapshot`   Compute a month-to-date snapshot of category totals  
- `report`     Print a Monthly P&L summary in dollars  
- `exit`       Quit the agent  

Each command logs its output in `logs/latest.log`.

---

## Directory Structure

```
minty/
├─ boot.py            # Main entrypoint
├─ config.yaml        # API keys & settings
├─ requirements_minty.txt
├─ memory_system/     # Cached transactions
└─ logs/              # latest.log and history
```

---

## Extending

- **QuickBooks**: add a `QuickBooksConnector` and swap integrations.  
- **Additional Integrations**: Xero, Wave, etc. follow the same pattern.  
- **Dashboard**: hook snapshots into a web UI or BI tool.

---

MIT © Your Company