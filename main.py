import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

BASE_URL = "http://dna777fdlbcv24cx5ctdvydvfa277vgb6wd6w4ztem6cho3kqogi7bqd.onion"
SECTION = "/forums/hacking-cracking-tutorials-courses-methods.45/"
NB_PAGES = 5

PROXIES = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0"
}


def fetch(url):
    r = requests.get(url, proxies=PROXIES, headers=HEADERS, timeout=60)
    if r.status_code != 200:
        return None
    return BeautifulSoup(r.text, "html.parser")


def is_internal(url):
    if not url:
        return False
    if url.startswith("/"):
        return True
    if url.startswith(BASE_URL):
        return True
    return False


with open("config/keywords.json", "r", encoding="utf-8") as f:
    keywords = json.load(f)

data = {
    "scraped_at": datetime.now().isoformat(),
    "source": "DarkNetArmy",
    "url": BASE_URL,
    "threads": []
}

home = fetch(BASE_URL + "/")
if home:
    for s in home.select("h3.node-title a"):
        if is_internal(s.get("href")):
            data.setdefault("sections", []).append({
                "title": s.get_text(strip=True),
                "url": s.get("href")
            })

for page in range(1, NB_PAGES + 1):
    if page == 1:
        url = BASE_URL + SECTION
    else:
        url = BASE_URL + SECTION + f"page-{page}"

    print(f"Page {page} : {url}")
    soup = fetch(url)
    if not soup:
        continue

    for t in soup.select("a[data-tp-primary='on']"):
        href = t.get("href")
        if not is_internal(href):
            continue
        data["threads"].append({
            "title": t.get_text(strip=True),
            "url": href,
            "found_on_page": page
        })

    time.sleep(3)

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
        soup = fetch(full_url)
        if not soup:
            continue

        first_post = soup.select_one("article.message")
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


with open("data/alerts/alerts.json", "w", encoding="utf-8") as f:
    json.dump(alerts, f, indent=2, ensure_ascii=False)

print(f"\n{len(data['threads'])} threads, {len(alerts)} alerts")