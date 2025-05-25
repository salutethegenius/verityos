

# Marley: PR & Personal Content Agent

Marley is a CLI tool that helps you plan and generate personalized social media content for LinkedIn, Facebook, and Instagram with a Bahamian cultural lens.

## Features

- **Plan**: Generate multi-channel posts based on a weekly theme and tone.  
- **Selective Generation**: Choose which platforms (LinkedIn, Facebook, Instagram) to generate content for.  
- **Export**: Write your content plan to a Markdown file.  
- **Schedule**: Create Google Calendar events for your recommended posting times.  

## Setup

1. **Clone** the repo and navigate to the Marley directory:
   ```bash
   git clone https://github.com/your-org/verityos-agents.git
   cd verityos-agents/agents/marley
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements_marley.txt
   ```

3. **Configure**:
   - Copy `config.yaml` and update:
     ```yaml
     name: Marley
     signature_name: Your Full Name
     model: gpt-4o-mini
     mode: command
     memory_path: ./memory_system
     log_path: ./logs
     ```
   - Place your Google OAuth client secrets file as `credentials.json` in this directory.

4. **Alias** (optional):
   ```bash
   echo "alias marley='python /home/ubuntu/verityos/agents/marley/boot.py'" >> ~/.bashrc
   source ~/.bashrc
   ```

## Usage

Start Marley:

```bash
marley
# or
python boot.py
```

**Commands**:

- `plan`  
  Prompt for theme, tone, and channels, then generate content.  

- `export`  
  Export the last plan to a Markdown file.

- `schedule`  
  Schedule reminders in Google Calendar for your recommended times.

- `exit`  
  Quit Marley.

## Directory Structure

```
marley/
├─ boot.py
├─ config.yaml
├─ requirements_marley.txt
├─ README.md
├─ memory_system/
└─ logs/
```

## License

© VerityOS | KemisDigital Labs