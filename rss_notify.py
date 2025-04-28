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
    "https://www.sandiegouniontribune.com/rss/feed?sectionName=sd-local-regional",
    "https://www.sandiegoreader.com/feeds/print/"
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
