import os
import sys
import feedparser
import requests

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

def fetch_and_notify():
    for feed_url in RSS_FEEDS:
        print(f"Checking feed: {feed_url} ({len(feedparser.parse(feed_url).entries)} entries)")
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            link = entry.get('link')
            text = (entry.get('title','') + ' ' + entry.get('summary','')).lower()
            for community in COMMUNITIES:
                if community.lower() in text and link not in seen:
                    print(f"→ Posting for {community}: {entry.get('title')}")
                    requests.post(webhook, json={
                        "text": f":bell: *{community}* — {entry.get('title')}\n{link}"
                    })
                    new_seen.add(link)
                    break

    # Persist the updated seen list
    with open(SEEN_FILE, 'w') as f:
        for url in new_seen:
            f.write(url + '\n')

if __name__ == "__main__":
    fetch_and_notify()
