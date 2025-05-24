# Ripple Agent 2.0 Roadmap
# - Break into modules: /commands/, /services/gmail_service.py, /ui/reporting.py
# - Convert to class-based: RippleAgent with fetch, summarize, save_draft, send_reply, report
# - Schedule background tasks via cron or daemon
# - Wire into VerityOS commands using .delegate or .ripple.*
from __future__ import print_function
import os
import os.path
import base64
import json
import sys
from datetime import datetime
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def clear_drafts():
    drafts_path = "/home/ubuntu/verityos/messages/ripple/drafts/"
    if not os.path.exists(drafts_path):
        print("📭 No drafts directory found.")
        return
    removed = 0
    for file in os.listdir(drafts_path):
        if file.endswith(".json"):
            os.remove(os.path.join(drafts_path, file))
            removed += 1
    print(f"🧽 Cleared {removed} drafts.")

def list_drafts():
    drafts_path = "/home/ubuntu/verityos/messages/ripple/drafts/"
    if not os.path.exists(drafts_path):
        print("📭 No drafts directory found.")
        return

    draft_files = [f for f in os.listdir(drafts_path) if f.endswith(".json")]
    if not draft_files:
        print("📭 No pending drafts found.")
        return

    print("📌 Pending Drafts:")
    for file in draft_files:
        with open(os.path.join(drafts_path, file), "r") as f:
            data = json.load(f)
            print(f"\nID: {file.replace('.json', '')}")
            print(f"From: {data.get('from', 'Unknown')}")
            print(f"Subject: {data.get('subject', 'No Subject')}")

def read_draft(msg_id):
    draft_path = f"/home/ubuntu/verityos/messages/ripple/drafts/{msg_id}.json"
    if not os.path.exists(draft_path):
        print(f"❌ No draft found with ID: {msg_id}")
        return

    with open(draft_path, "r") as f:
        draft = json.load(f)
        print(f"\n📄 Draft Preview: {msg_id}")
        print(f"From: {draft.get('from', 'Unknown')}")
        print(f"Subject: {draft.get('subject', 'No Subject')}")
        print(f"Suggested Reply:\n{draft.get('reply', '[No reply found]')}")

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def ripple_report():
    log_path = "/home/ubuntu/verityos/logs/ripple/daily.log"
    important = 0
    junk = 0
    not_important = 0
    replied = 0
    pending = 0
    total = 0

    try:
        with open(log_path, "r") as f:
            for line in f:
                if "Saved draft and logged important email" in line:
                    important += 1
                elif "Category: Junk" in line:
                    junk += 1
                elif "Category: Not Important" in line:
                    not_important += 1
                elif "Replied to" in line:
                    replied += 1
        total = important + junk + not_important
        pending = important - replied

        print("\n📊 Ripple Daily Report")
        print(f"Emails received: {total}")
        print(f"Important: {important}")
        print(f"Junk: {junk}")
        print(f"Not Important: {not_important}")
        print(f"Replied: {replied}")
        print(f"Pending Approval: {pending}")
    except FileNotFoundError:
        print("⚠️ No log found for today.")

def authenticate_gmail():
    creds = None
    cred_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def approve_reply(msg_id):
    draft_path = f"/home/ubuntu/verityos/messages/ripple/drafts/{msg_id}.json"
    if not os.path.exists(draft_path):
        print(f"❌ No draft found for message ID: {msg_id}")
        return

    with open(draft_path, 'r') as f:
        draft = json.load(f)

    reply_text = draft.get("reply", "")
    subject = "Re: " + draft.get("subject", "No Subject")

    service = authenticate_gmail()
    message = EmailMessage()
    message.set_content(reply_text)
    message["To"] = draft["from"]
    message["Subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw}

    service.users().messages().send(userId="me", body=body).execute()
    print(f"✅ Reply sent to: {draft['from']}")

    log_path = "/home/ubuntu/verityos/logs/ripple/daily.log"
    with open(log_path, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] Replied to: {draft['from']} - {subject}\n")

if len(sys.argv) > 2 and sys.argv[1] == "readdraft":
    read_draft(sys.argv[2])
    exit()
if len(sys.argv) > 1 and sys.argv[1] == "report":
    ripple_report()
    exit()
if len(sys.argv) > 2 and sys.argv[1] == "approve":
    approve_reply(sys.argv[2])
    exit()
if len(sys.argv) > 1 and sys.argv[1] == "listdrafts":
    list_drafts()
    exit()
if len(sys.argv) > 1 and sys.argv[1] == "cleardrafts":
    clear_drafts()
    exit()

def fetch_unread(service, max_results=5):
    results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=max_results).execute()
    messages = results.get('messages', [])
    return messages

def get_message_summary(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    headers = msg['payload']['headers']
    summary = {h['name']: h['value'] for h in headers if h['name'] in ['From', 'Subject']}
    has_attachment = any(part.get('filename') for part in msg.get('payload', {}).get('parts', []) if part.get('filename'))
    summary['has_attachment'] = has_attachment
    return summary


if __name__ == '__main__':
    service = authenticate_gmail()
    unread = fetch_unread(service)

    if not unread:
        print("📭 No unread emails found.")
    else:
        print(f"📥 Found {len(unread)} unread emails:\n")
        for msg in unread:
            summary = get_message_summary(service, msg['id'])
            print(f"From: {summary.get('From', 'Unknown')}")
            print(f"Subject: {summary.get('Subject', 'No Subject')}")
            if summary.get("has_attachment"):
                print("📎 Attachment detected")
            subject = summary.get('Subject', 'No Subject').lower()
            if any(keyword in subject for keyword in ['invoice', 'project', 'client', 'meeting']):
                category = 'Important'
            elif any(keyword in subject for keyword in ['unsubscribe', 'promo', 'newsletter']):
                category = 'Junk'
            else:
                category = 'Not Important'
            print(f"Category: {category}")
            if category == 'Important':
                suggested_reply = (
                    "Hi, thank you for reaching out. I’ve received your message and will get back to you shortly."
                )
                print(f"Suggested Reply:\n{suggested_reply}")
                # Ensure directories
                os.makedirs('/home/ubuntu/verityos/messages/ripple/drafts/', exist_ok=True)
                os.makedirs('/home/ubuntu/verityos/memory_system/ripple/', exist_ok=True)
                os.makedirs('/home/ubuntu/verityos/logs/ripple/', exist_ok=True)

                # Save draft JSON with numeric filename (sequential)
                draft_dir = "/home/ubuntu/verityos/messages/ripple/drafts/"
                os.makedirs(draft_dir, exist_ok=True)
                existing_drafts = [f for f in os.listdir(draft_dir) if f.endswith(".json")]
                next_id = str(len(existing_drafts) + 1)
                filename = f"{next_id}.json"
                draft_path = os.path.join(draft_dir, filename)
                with open(draft_path, 'w') as f:
                    json.dump({
                        'from': summary.get('From', 'Unknown'),
                        'subject': summary.get('Subject', 'No Subject'),
                        'reply': suggested_reply
                    }, f, indent=2)
                print(f"📝 Draft saved as: {filename}")

                # Append to memory.txt
                memory_path = "/home/ubuntu/verityos/memory_system/ripple/memory.txt"
                with open(memory_path, 'a') as f:
                    f.write(f"Email from {summary.get('From', 'Unknown')} with subject \"{summary.get('Subject', 'No Subject')}\" categorized as Important.\n")

                # Log to daily.log
                log_path = "/home/ubuntu/verityos/logs/ripple/daily.log"
                with open(log_path, 'a') as f:
                    f.write(f"[{datetime.now().isoformat()}] Saved draft and logged important email: {summary.get('Subject', 'No Subject')}\n")
            print("-" * 40)

    # Notify Verity if drafts are pending
    drafts_path = "/home/ubuntu/verityos/messages/ripple/drafts/"
    if os.path.exists(drafts_path):
        pending = [f for f in os.listdir(drafts_path) if f.endswith(".json")]
        if pending:
            print(f"\n🧠 Verity Notification: Ripple has {len(pending)} message(s) awaiting approval.")