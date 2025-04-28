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
    
]

def fetch_and_notify():
    if not SLACK_WEBHOOK_URL:
        print("Error: SLACK_WEBHOOK_URL is not set.")
        return
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            for community in COMMUNITIES:
                if community.lower() in title.lower() or community.lower() in summary.lower():
                    payload = {
                        "text": f":bell: *New Article Mentioning {community}*\n*{title}*\n{link}"
                    }
                    requests.post(SLACK_WEBHOOK_URL, json=payload)
                    break

if __name__ == "__main__":
    fetch_and_notify()
