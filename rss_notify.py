import os
import sys
import feedparser
import requests

from datetime import datetime
from zoneinfo import ZoneInfo

# DEBUG block: prove that Python sees the secret
webhook = os.getenv('SLACK_WEBHOOK_URL')
print(f"🔍 [DEBUG] SLACK_WEBHOOK_URL in Python is: {repr(webhook)}")
if not webhook:
    print("❌ ERROR: SLACK_WEBHOOK_URL is not set in Python’s environment. Exiting.")
    sys.exit(1)

# What to watch for
COMMUNITIES = [
    "Chula Vista",
    "Imperial Beach",
    "National City",
    "Bonita",
    "San Ysidro",
    "Otay Mesa",
    "Lincoln Acres",
    "South Bay",
    "South County"
]

# All your San Diego feeds
RSS_FEEDS = [
    "https://www.sandiegouniontribune.com/rss/feed",
    "https://www.sandiegoreader.com/feeds/print/",
    "https://www.nbcsandiego.com/?rss=y",
    "https://feeds.feedblitz.com/cbs8/news",
    "https://timesofsandiego.com/feed",
    "https://voiceofsandiego.org/feed",
    "https://www.countynewscenter.com/news/rss",
    "https://coronadotimes.com/feed",
    "https://sdcitytimes.com/feed",
    "https://laprensa.org/feed",
    "https://clairemonttimes.com/feed",
    "https://thecoronadonews.com/feed",
    "https://mesapress.com/feed",
    "https://sdnews.com/feed",
    "https://lgbtqsd.news/feed",
    "https://gay-sd.com/feed",
    "https://delmartimes.net/feed",
    "https://sandiegonewsdesk.com/feed",
    "https://chulavistatoday.com/feed",
    "https://triton.news/feed",
    "https://www.kpbs.org/index.rss",
    "https://fox5sandiego.com/feed"
]

# Where we keep track of what we've already posted
CACHE_DIR = '.cache'
SEEN_FILE = os.path.join(CACHE_DIR, 'seen.txt')
os.makedirs(CACHE_DIR, exist_ok=True)

if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE) as f:
        seen = set(line.strip() for line in f)
else:
    seen = set()
new_seen = set(seen)

def format_pub_date(entry):
    # Try published_parsed first
    if getattr(entry, 'published_parsed', None):
        # Build a UTC datetime
        dt_utc = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC"))
        # Convert to Pacific Time
        dt_pt  = dt_utc.astimezone(ZoneInfo("America/Los_Angeles"))
        # Format however you like; here we add "PT"
        return dt_pt.strftime('%Y-%m-%d %H:%M PT')
    # Fall back to raw strings (these may already include a timezone)
    raw = entry.get('published') or entry.get('updated') or 'Unknown date'
    return raw

def fetch_and_notify():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        print(f"Checking {feed_url} → {len(feed.entries)} entries")
        for entry in feed.entries:
            link = entry.get('link')
            title = entry.get('title', '').strip()
            summary_text = (entry.get('summary','') or '').strip().lower()
            pub_date = format_pub_date(entry)
            combined = (title + " " + summary_text).lower()
            for community in COMMUNITIES:
                if community.lower() in combined and link not in seen:
                    print(f"→ Posting for {community}: {title} (Published: {pub_date})")
                    requests.post(webhook, json={
                        "text": (
                            f":bell: *{community}* — {title}\n"
                            f"_Published: {pub_date}_\n"
                            f"{link}"
                        )
                    })
                    new_seen.add(link)
                    break

    # Persist the updated seen list
    with open(SEEN_FILE, 'w') as f:
        for url in new_seen:
            f.write(url + '\n')

if __name__ == "__main__":
    fetch_and_notify()
