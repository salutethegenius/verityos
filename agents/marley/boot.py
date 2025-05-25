#!/usr/bin/env python3
import os
import sys
import yaml
import openai
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Store last generated plan for export
last_plan = {}

# Load environment
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

CAL_SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Paths
config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
log_path = os.path.join(os.path.dirname(__file__), "logs")
memory_path = os.path.join(os.path.dirname(__file__), "memory_system")

# Ensure directories exist
os.makedirs(log_path, exist_ok=True)
os.makedirs(memory_path, exist_ok=True)

# Load config
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

name = config.get("name", "Marley")

def log(entry: str):
    from datetime import datetime
    timestamp = datetime.utcnow().isoformat()
    with open(os.path.join(log_path, "latest.log"), "a") as lf:
        lf.write(f"{timestamp} {entry}\n")

def get_local_insights():
    # Stub: replace with real data later
    return {
        "holidays": ["Federal Monuments Day"],
        "landmarks": ["Nassau Harbour", "Harbour Island"],
        "idioms": ["yinna", "ting-a-ling"]
    }

def generate_marketing_posts(theme: str, tone: str):
    insights = get_local_insights()
    base = (
        f"Theme: {theme}\n"
        f"Tone: {tone}\n"
        f"Use Bahamian context: holidays {insights['holidays']}, "
        f"landmarks {insights['landmarks']}, idioms {insights['idioms']}.\n"
    )
    # LinkedIn
    li_prompt = base + "Write a 100-word professional LinkedIn post."
    li_resp = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":li_prompt}]
    )
    li = li_resp.choices[0].message.content.strip()

    # Facebook
    fb = []
    for i in range(1):
        fb_prompt = base + f"Write Facebook post #{i+1}, 40 words, conversational."
        fb_resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":fb_prompt}]
        )
        fb.append(fb_resp.choices[0].message.content.strip())

    # Instagram
    ig = []
    for i in range(1):
        ig_prompt = base + f"Write Instagram caption #{i+1}, 25 words plus 5 hashtags."
        ig_resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":ig_prompt}]
        )
        ig.append(ig_resp.choices[0].message.content.strip())

    # Image prompts
    img_prompts = [
        f"A vibrant scene of Bahamian {insights['landmarks'][i % len(insights['landmarks'])]} in {theme}, photo-realistic"
        for i in range(1)
    ]

    # Timing suggestions (static for now)
    times = {
        "LinkedIn": "Tue 10 AM",
        "Facebook": ["Wed 7 PM"],
        "Instagram": ["Mon 8 AM"]
    }

    return li, fb, ig, img_prompts, times

def get_calendar_service():
    creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    if not os.path.exists(creds_path):
        print(f"⚠️ credentials.json not found at {creds_path}.")
        print("   Please place your OAuth client secrets file here.")
        return None

    token_path = os.path.join(os.path.dirname(__file__), 'token_calendar.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, CAL_SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, CAL_SCOPES)
        # Use out-of-band (OOB) for terminal-based auth
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        # Console-based auth flow
        auth_url, _ = flow.authorization_url(access_type='offline', prompt='consent')
        print("🔗 Please go to this URL to authorize:\n" + auth_url)
        code = input("Enter the authorization code here: ").strip()
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open(token_path, 'w') as tf:
            tf.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def run_command():
    print(f"🔁 Booting {name} (mode: command)")
    print(f"📂 Memory: {memory_path} | Logs: {log_path}")
    print("🧠 Available commands: plan, export, schedule, exit")

    while True:
        task = input("🧠 Marley > ").strip()
        if task.lower() == "exit":
            print("👋 Goodbye!")
            sys.exit(0)
        elif task.lower() == "plan":
            theme = input("🧠 Marley > What’s our theme this week? ").strip()
            tone = input("🧠 Marley > What tone (e.g. inspirational, educational)? ").strip()
            # Ask which channels to generate
            print("🧠 Marley > Which channels to generate? (comma-separated numbers)")
            print("   1) All, 2) LinkedIn, 3) Facebook, 4) Instagram")
            choices = input("Enter choice(s): ").strip().split(",")
            choices = [c.strip() for c in choices]
            generate_all = '1' in choices or 'all' in [c.lower() for c in choices]
            do_li = generate_all or '2' in choices
            do_fb = generate_all or '3' in choices
            do_ig = generate_all or '4' in choices
            print("🔍 Gathering local insights and generating content...")
            li, fb_posts, ig_caps, images, times = generate_marketing_posts(theme, tone)

            global last_plan
            last_plan = {
                "theme": theme,
                "tone": tone,
                "linkedin": li,
                "facebook": fb_posts,
                "instagram": ig_caps,
                "images": images,
                "times": times
            }

            # If none selected, default to all channels and restore all times
            if not (do_li or do_fb or do_ig):
                do_li = do_fb = do_ig = True
                last_plan["times"] = times
            else:
                # Filter recommended times based on channel selection
                filtered_times = {}
                if do_li:
                    filtered_times["LinkedIn"] = times["LinkedIn"]
                if do_fb:
                    filtered_times["Facebook"] = times["Facebook"]
                if do_ig:
                    filtered_times["Instagram"] = times["Instagram"]
                last_plan["times"] = filtered_times

            if do_li:
                print("\n--- LinkedIn (100 words) ---")
                print(li)
            if do_fb:
                print("\n--- Facebook Post ---")
                print(f"1. {fb_posts[0]}")
            if do_ig:
                print("\n--- Instagram Caption ---")
                print(f"1. {ig_caps[0]}")
            print("\n--- Image Prompt ---")
            print(f"1. {images[0]}")
            print("\n--- Recommended Times ---")
            for channel, slot in last_plan["times"].items():
                if isinstance(slot, list):
                    print(f"{channel}: {', '.join(slot)}")
                else:
                    print(f"{channel}: {slot}")
        elif task.lower() == "export":
            if not last_plan:
                print("⚠️ No plan available to export. Run 'plan' first.")
            else:
                filename = f"marley_plan_{last_plan['theme'].replace(' ', '_')}.md"
                with open(os.path.join(os.getcwd(), filename), "w") as md:
                    md.write(f"# Marley Content Plan: {last_plan['theme']} ({last_plan['tone']})\n\n")
                    # Conditionally export channels
                    if "LinkedIn" in last_plan["times"]:
                        md.write("## LinkedIn (100 words)\n")
                        md.write(last_plan["linkedin"] + "\n\n")
                    if "Facebook" in last_plan["times"]:
                        md.write("## Facebook\n")
                        for idx, p in enumerate(last_plan["facebook"], 1):
                            md.write(f"{idx}. {p}\n")
                        md.write("\n")
                    if "Instagram" in last_plan["times"]:
                        md.write("## Instagram\n")
                        for idx, c in enumerate(last_plan["instagram"], 1):
                            md.write(f"{idx}. {c}\n")
                        md.write("\n")
                    # Always include images
                    md.write("## Image Prompts\n")
                    for idx, ip in enumerate(last_plan["images"], 1):
                        md.write(f"{idx}. {ip}\n")
                    md.write("\n")
                    # Recommended Times for selected channels
                    md.write("## Recommended Times\n")
                    for channel, slot in last_plan["times"].items():
                        if isinstance(slot, list):
                            md.write(f"{channel}: {', '.join(slot)}\n")
                        else:
                            md.write(f"{channel}: {slot}\n")
                print(f"✅ Exported plan to {filename}")
        elif task.lower() == "schedule":
            if not last_plan:
                print("⚠️ No plan available. Run 'plan' first.")
            else:
                service = get_calendar_service()
                if service is None:
                    continue
                now = datetime.utcnow().date()
                # map abbreviations to weekday numbers
                weekdays = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
                for channel, times in last_plan['times'].items():
                    slots = times if isinstance(times, list) else [times]
                    for slot in slots:
                        day_abbr, time_str = slot.split(" ", 1)
                        # convert time_str "10 AM" or "7 PM" into 24-hour hour integer
                        hr, ampm = time_str.split()
                        hour = int(hr) % 12
                        if ampm.upper() == "PM":
                            hour += 12

                        # compute next date for this weekday
                        target_wd = weekdays.get(day_abbr[:3], now.weekday())
                        days_ahead = (target_wd - now.weekday() + 7) % 7
                        if days_ahead == 0:
                            days_ahead = 7
                        event_date = now + timedelta(days=days_ahead)
                        event_start = f"{event_date.isoformat()}T{hour:02d}:00:00"
                        event = {
                            'summary': f"Post {channel}: {last_plan['theme']}",
                            'start': {'dateTime': event_start, 'timeZone': 'America/Nassau'},
                            'end':   {'dateTime': event_start, 'timeZone': 'America/Nassau'},
                            'description': last_plan.get(channel.lower(), '')
                        }
                        service.events().insert(calendarId='primary', body=event).execute()
                print("✅ Scheduled calendar events for your content plan.")
        else:
            print("⚠️ Unknown command. Available: plan, export, schedule, exit")

if __name__ == "__main__":
    run_command()
