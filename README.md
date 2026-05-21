# dna-monitor

A small script I wrote to learn how dark web threat collection actually works. It connects to a Tor-hosted forum, pulls thread titles from the index, flags the ones matching keywords I care about (credentials, carding, malware, etc), then goes back to each flagged thread to grab the author, post date, and a preview.

The point was to stop reading about Tor scraping and actually do it.

## Run it

```bash
brew install tor && brew services start tor
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

Output:
```
35 sections, 50 threads, 45 alerts
```

Raw data goes to `data/raw/forum_data.json`, flagged threads with their enriched metadata to `data/alerts/alerts.json`.

## A few things I learned the hard way

- `socks5h` matters. Without the `h`, your machine resolves the `.onion` locally and leaks the DNS lookup.
- Default Python User-Agent gets blocked on most forums. Faking Firefox works fine.
- The first onion I tried was dead, the second hid behind a DDoS queue, the third returned 403. Onions die or change addresses constantly — that alone was useful to learn.
- `data-tp-primary="on"` turned out to be how this forum tags thread links. The standard XenForo selectors returned nothing, so I saved the HTML locally and dug through it until I found the attribute that worked.
- 3-second pause between thread requests. Without it you hammer the onion and either get rate-limited or just look like a bot. With it, the second pass takes a couple of minutes but it behaves.

## What it doesn't do

Index page only — no pagination. Substring matching ("card" matches "discard"). One source. Each run overwrites the last. Content preview is 300 chars max, on purpose.

## Why I built it

I'm trying to move from fraud analysis at a bank into CTI. Wanted to build the smallest end-to-end version of dark web monitoring.

It's intentionally simple. I wanted to be able to explain every line.