import os
import feedparser
import requests

SLACK_WEBHOOK_URL = os.getenv('https://hooks.slack.com/services/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')
COMMUNITIES = [
    "Chula Vista",
    "Imperial Beach",
    "National City",
    "Bonita",
    "San Ysidro",
    "Otay Mesa",
    "Lincoln Acres"
]
RSS_FEEDS = [
    "https://www.sandiegouniontribune.com/rss/feed",
    "https://www.sandiegoreader.com/feeds/print/",
    "https://www.nbcsandiego.com/?rss=y",
    "https://feeds.feedblitz.com/cbs8/news",
    "https://timesofsandiego.com/feed",
    "https://voiceofsandiego.org/feed",
    "https://www.countynewscenter.com/news/rss",
    "https://coronadotimes.com/feed",
    "https://sdcitytimes.com/feed,"
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
    "https://fox5sandiego.com/feed",
    
CACHE_DIR = '.cache'
SEEN_FILE = os.path.join(CACHE_DIR, 'seen.txt')
os.makedirs(CACHE_DIR, exist_ok=True)

# Load seen URLs
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE) as f:
        seen = set(line.strip() for line in f)
else:
    seen = set()

new_seen = set(seen)

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        link = entry.get('link')
        title = entry.get('title', '')
        summary = entry.get('summary', '')
        for community in COMMUNITIES:
            if community.lower() in (title + summary).lower():
                if link not in seen:
                    # post to Slack
                    requests.post(SLACK_WEBHOOK_URL, json={
                        "text": f":bell: *{community}* — {title}\n{link}"
                    })
                    new_seen.add(link)
                break

# Save updated seen list
with open(SEEN_FILE, 'w') as f:
    for url in new_seen:
        f.write(url + '\n')
