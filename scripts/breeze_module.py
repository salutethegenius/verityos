from playwright.sync_api import sync_playwright
import os
from datetime import datetime
import json
import re
import argparse
import hashlib
from pathlib import Path
from urllib.parse import urljoin
from scripts.breeze_core import extract_bahamaspress_articles
from scripts.breeze_core_gov import extract_bahamasgov_articles

def run_breeze_scraper(target=None):
    # Define the base directory for data output
    BASE_DIR = "/home/ubuntu/verityos/data/news"
    LOG_DIR = "/home/ubuntu/verityos/logs/breeze"
    METADATA_DIR = "metadata"

    SITES = {
        "1": ("Bahamas Press", "https://www.bahamaspress.com", "bahamaspress"),
        "2": ("Bahamas Gov News", "https://www.bahamas.gov.bs/wps/portal/public/gov/government/news", "bahamasgov")
    }

    if target and target in SITES:
        choice = target
    else:
        print("🌬️  Breeze is online and ready to collect national tone data.")
        print("Select a website to scrape:\n")
        print("1. Bahamas Press        (https://www.bahamaspress.com)")
        print("2. Bahamas Gov News     (https://www.bahamas.gov.bs/wps/portal/public/gov/government/news)")
        choice = input("> ").strip()

    parser = argparse.ArgumentParser()
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--max-pages", type=int, default=5)
    args, _ = parser.parse_known_args()

    if choice in SITES:
        site_name, base_url, slug = SITES[choice]
    else:
        print("Invalid choice. Exiting.")
        return

    print(f"\n🛰️  Starting scrape for: {site_name} ({base_url})\n")

    output_path = os.path.join(BASE_DIR, slug)
    metadata_path = os.path.join(output_path, METADATA_DIR)
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(metadata_path, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

    def slugify(text):
        return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

    if slug == "bahamaspress" or "bahamaspress.com" in base_url:
        titles = extract_bahamaspress_articles(base_url, output_path, metadata_path, args.start_page, args.start_page + args.max_pages - 1)
        with open(os.path.join(LOG_DIR, "run.log"), "a") as log:
            log.write(f"{datetime.now()}: Scraped {len(titles)} articles from {site_name}\n")
        print(f"\n✅ Completed. {len(titles)} articles saved.\n")

    elif slug == "bahamasgov" or "bahamas.gov.bs" in base_url:
        titles = extract_bahamasgov_articles(base_url, output_path, metadata_path, args.start_page, args.start_page + args.max_pages - 1)
        with open(os.path.join(LOG_DIR, "run.log"), "a") as log:
            log.write(f"{datetime.now()}: Scraped {len(titles)} articles from {site_name}\n")
        print(f"\n✅ Completed. {len(titles)} articles saved.\n")