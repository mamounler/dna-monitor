import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

BASE_URL = "http://dna777fdlbcv24cx5ctdvydvfa277vgb6wd6w4ztem6cho3kqogi7bqd.onion"
PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0"
}

with open("config/keywords.json", "r", encoding="utf-8") as f:
    keywords = json.load(f)

response = requests.get(BASE_URL + "/", proxies=PROXIES, headers=HEADERS, timeout=60)

if response.status_code != 200:
    print(f"ERREUR : status {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

sections = soup.select("h3.node-title a")
threads = soup.select("a[data-tp-primary='on']")

data = {
    "scraped_at": datetime.now().isoformat(),
    "source": "DarkNetArmy",
    "url": BASE_URL,
    "sections": [],
    "threads": []
}

for section in sections:
    data["sections"].append({
        "title": section.get_text(strip=True),
        "url": section.get("href")
    })

for thread in threads:
    data["threads"].append({
        "title": thread.get_text(strip=True),
        "url": thread.get("href")
    })

alerts = []
for thread in data["threads"]:
    title_lower = thread["title"].lower()
    for category, config in keywords.items():
        for term in config["terms"]:
            if term.lower() in title_lower:
                alerts.append({
                    "detected_at": datetime.now().isoformat(),
                    "category": category,
                    "severity": config["severity"],
                    "keyword": term,
                    "thread_title": thread["title"],
                    "thread_url": thread["url"]
                })
                break

for i, alert in enumerate(alerts):
    full_url = BASE_URL + alert["thread_url"]
    try:
        r = requests.get(full_url, proxies=PROXIES, headers=HEADERS, timeout=60)
        if r.status_code != 200:
            continue

        s = BeautifulSoup(r.text, "html.parser")
        first_post = s.select_one("article.message")
        if not first_post:
            continue

        alert["author"] = first_post.get("data-author")

        time_tag = first_post.select_one("time")
        if time_tag:
            alert["posted_at"] = time_tag.get("datetime")

        content = first_post.select_one("div.bbWrapper")
        if content:
            text = content.get_text(strip=True, separator=" ")
            alert["content_preview"] = text[:300]

        print(f"{i+1}/{len(alerts)} {alert.get('author')}")
        time.sleep(3)
    except Exception:
        continue

with open("data/raw/forum_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

with open("data/alerts/alerts.json", "w", encoding="utf-8") as f:
    json.dump(alerts, f, indent=2, ensure_ascii=False)

print(f"\n{len(data['sections'])} sections, {len(data['threads'])} threads, {len(alerts)} alerts")