"""Best-effort discovery of publicly indexed X posts (not X native search)."""
import csv
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

query = os.environ.get("SEARCH_QUERY", "NVIDIA").strip() or "NVIDIA"
search_query = f'site:x.com/ status {query}'
sources = [
    ("Bing RSS", "https://www.bing.com/search?" + urllib.parse.urlencode({"q": search_query, "format": "rss"})),
    ("Bing RSS alternative", "https://www.bing.com/search?" + urllib.parse.urlencode({"q": f'site:twitter.com/ status {query}', "format": "rss"})),
]
pattern = re.compile(r'https?://(?:www\.)?(?:x\.com|twitter\.com)/[^/\s]+/status/\d+')
rows, seen = [], set()
for name, url in sources:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as response:
            data = response.read()
        root = ET.fromstring(data)
        items = root.findall(".//item")
        print(f"{name}: {len(items)} indexed results")
        for item in items:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            description = item.findtext("description", "")
            match = pattern.search(link)
            if match and match.group(0) not in seen:
                seen.add(match.group(0))
                rows.append([title, description, match.group(0)])
    except Exception as exc:
        print(f"{name}: unavailable ({type(exc).__name__}: {exc})")

Path("output").mkdir(exist_ok=True)
with open("output/public_x_index.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["search_title", "search_snippet", "post_url"])
    writer.writerows(rows)
print(f"Public X post URLs found: {len(rows)}")
if not rows:
    print("No matching indexed X posts. This does not mean X has no matching posts.")
