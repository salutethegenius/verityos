# Ripple: Email Intelligence Agent

Ripple is a terminal-based email assistant that integrates with Gmail and OpenAI to help you:

- Curate your important senders (`known_senders` / `bad_senders`)
- Fetch unread messages in batches of 10
- Page through your inbox (`fetch`, `next`, `previous`)
- Generate AI‑powered drafts (`draft <n>`) with your custom signature
- Send replies (`send <n>`)
- Manage and blacklist senders interactively (`senders`, `remove <n>`)
- Archive messages (`archive`)

## Setup

1. **Clone** the repo:
   ```bash
   git clone https://github.com/your-org/verityos-agents.git
   cd verityos-agents/agents/ripple
   ```

2. **Install dependencies** (assumes Python 3.10+):
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure**:
   - Create `.env` with:
     ```
     OPENAI_API_KEY=your_openai_key
     ```
   - Edit `config.yaml` to add your:
     ```yaml
     name: Your Name
     signature_name: Your Full Name
     known_senders:
       - alice@example.com
       - bob@company.com
     bad_senders: []
     setup_phase: 0
     ```

4. **Authorize**:
   ```bash
   python boot.py
   ```
   On first run, you’ll be prompted to blacklist any initial senders and restart.

## Usage

```bash
# In the ripple directory
python boot.py --mode=command

# Or, if aliased:
ripple
```

### Commands

- `fetch`      Fetch next 10 unread emails
- `next`       Fetch the next 10 unread emails
- `previous`   Go back to the previous fetched batch
- `draft <n>`  Generate an AI draft for the nth message
- `send <n>`   Send the generated draft
- `archive`    Mark current batch as read
- `senders`    Review known senders list
- `remove <n>` Blacklist sender(s) by number
- `nextsenders` / `prevsenders` Page through senders
- `senders save` Exit senders management
- `exit`       Quit Ripple

## Development

- Code is in `boot.py`
- Config in `config.yaml`
- Logs in the `logs/` directory
- Memory in the `memory_system/` directory

## License

© VerityOS | KemisDigital Labs
