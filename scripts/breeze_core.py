


import os
import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_DIR = "/home/ubuntu/verityos/data/news"
LOG_DIR = "/home/ubuntu/verityos/logs/breeze"
METADATA_DIR = "metadata"

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def extract_bahamaspress_articles(base_url, output_path, metadata_path, start_page=1, end_page=1):
    """
    Extract articles from Bahamas Press paginated news pages.
    Args:
        base_url (str): Base URL of Bahamas Press (e.g., 'https://bahamaspress.com')
        output_path (str): Path to save markdown files.
        metadata_path (str): Path to save metadata JSON files.
        start_page (int): The starting page number to scrape.
        end_page (int): The ending page number to scrape (inclusive).
    Returns:
        list: Titles of articles scraped.
    """
    articles = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        total_scraped = 0
        for page_num in range(start_page, end_page + 1):
            try:
                page_url = f"{base_url}/page/{page_num}"
                page = browser.new_page()
                page.goto(page_url)
                page.wait_for_timeout(3000)
                links = page.locator("div.td-module-thumb > a[href]")
                count = links.count()
                for i in range(count):
                    try:
                        title = links.nth(i).get_attribute("title")
                        href = links.nth(i).get_attribute("href")
                        if not href:
                            continue
                        article_page = browser.new_page()
                        article_page.goto(href)
                        article_page.wait_for_timeout(2000)
                        paragraphs = article_page.locator("div.td-post-content p")
                        content = "\n".join([p.inner_text().strip() for p in paragraphs.all() if p.inner_text().strip()])
                        article_page.close()
                        if len(content.split()) < 50:
                            continue
                        pub_date = datetime.now().strftime("%Y-%m-%d")
                        author = "Unknown"
                        category = "News"
                        summary = content[:300].split(".")[0] + "..."
                        tone = "neutral"
                        slug_title = slugify(title)
                        filename = f"{pub_date}-{slug_title}"

                        md_path = os.path.join(output_path, f"{filename}.md")
                        with open(md_path, "w", encoding="utf-8") as f:
                            f.write(f"# {title}\n")
                            f.write(f"**Date:** {pub_date}  \n")
                            f.write(f"**Author:** {author}  \n")
                            f.write(f"**Source:** Bahamas Press  \n")
                            f.write(f"**Category:** {category}  \n")
                            f.write(f"**Tags:** Bahamas, press, news  \n")
                            f.write("\n---\n\n## Summary\n")
                            f.write(f"{summary}\n\n**Tone:** {tone}\n\n---\n\n## Article\n")
                            f.write(f"{content}\n\n---\n**URL:** {href}")

                        meta_path = os.path.join(metadata_path, f"{filename}.json")
                        with open(meta_path, "w", encoding="utf-8") as j:
                            json.dump({
                                "title": title,
                                "date": pub_date,
                                "author": author,
                                "category": category,
                                "tags": ["Bahamas", "press", "news"],
                                "summary": summary,
                                "tone": tone,
                                "url": href,
                                "word_count": len(content.split()),
                                "source": "Bahamas Press"
                            }, j, indent=2)
                        articles.append(title)
                        total_scraped += 1
                    except Exception as e:
                        print(f"⚠️ Error scraping article on page {page_num}, link {i+1}: {e}")
                page.close()
            except Exception as e:
                print(f"⚠️ Error scraping page {page_num}: {e}")
        browser.close()
    return articles