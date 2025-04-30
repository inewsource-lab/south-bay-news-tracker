import os
import sys
import feedparser
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# DEBUG: confirm we see the North County webhook in Python
webhook = os.getenv('SLACK_WEBHOOK_NORTH')
print(f"🔍 [DEBUG] SLACK_WEBHOOK_NORTH in Python is: {repr(webhook)}")
if not webhook:
    print("❌ ERROR: SLACK_WEBHOOK_NORTH is not set. Exiting.")
    sys.exit(1)

# All North County San Diego communities: incorporated, unincorporated, and CDPs
COMMUNITIES = [
    "Oceanside",
    "Vista",
    "Carlsbad",
    "Encinitas",
    "Solana Beach",
    "Del Mar",
    "San Marcos",
    "Escondido",
    "Poway",
    "Fallbrook",
    "Bonsall",
    "Rainbow",
    "Valley Center",
    "Pauma Valley",
    "Pala",
    "Rancho Santa Fe",
    "Ramona",
    "Julian",
    "Cardiff-by-the-Sea",
    "Carmel Valley"
]

# North County–focused RSS feeds
RSS_FEEDS = [
    "https://thecoastnews.com/feed/",
    "https://www.northcoastcurrent.com/category/latest-news/feed/",
    "https://timesofsandiego.com/feed",
    "https://voiceofsandiego.org/feed",
    "https://www.sandiegouniontribune.com/rss/feed",
    "https://www.nbcsandiego.com/?rss=y",
    "https://feeds.feedblitz.com/cbs8/news",
    "https://fox5sandiego.com/feed",
    "https://www.kpbs.org/index.rss",
    "https://www.countynewscenter.com/news/rss"
]

# Cache setup to avoid duplicates
CACHE_DIR = '.cache_north'
SEEN_FILE = os.path.join(CACHE_DIR, 'seen.txt')
import os.path as _op
os.makedirs(CACHE_DIR, exist_ok=True)

if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE) as f:
        seen = set(line.strip() for line in f)
else:
    seen = set()
new_seen = set(seen)

def format_pub_date(entry):
    if getattr(entry, 'published_parsed', None):
        dt_utc = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC"))
        dt_pt  = dt_utc.astimezone(ZoneInfo("America/Los_Angeles"))
        return dt_pt.strftime('%Y-%m-%d %H:%M PT')
    return entry.get('published') or entry.get('updated') or 'Unknown date'

def fetch_and_notify():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        print(f"Checking {feed_url}: {len(feed.entries)} entries")
        for entry in feed.entries:
            link = entry.get('link')
            title = entry.get('title', '').strip()
            pub_date = format_pub_date(entry)
            text_blob = (title + " " + (entry.get('summary','') or '')).lower()
            for community in COMMUNITIES:
                if community.lower() in text_blob and link not in seen:
                    print(f"→ Posting {community}: {title}")
                    requests.post(webhook, json={
                        "text": (
                            f":bell: *{community}* — {title}\n"
                            f"_Published: {pub_date}_\n"
                            f"{link}"
                        )
                    })
                    new_seen.add(link)
                    break

    # Persist updated seen list
    with open(SEEN_FILE, 'w') as f:
        for url in new_seen:
            f.write(url + '\n')

if __name__ == "__main__":
    fetch_and_notify()
