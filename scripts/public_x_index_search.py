"""Search publicly indexed X post URLs without X credentials. Not X's native search."""
import csv, os, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
query=os.environ.get("SEARCH_QUERY","NVIDIA").strip() or "NVIDIA"
q=f'site:x.com/*/status/ {query}'
url="https://www.bing.com/search?"+urllib.parse.urlencode({"q":q,"format":"rss"})
req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; ResearchFeed/1.0)"})
with urllib.request.urlopen(req,timeout=25) as response:
    data=response.read()
root=ET.fromstring(data)
rows=[]
seen=set()
for item in root.findall(".//item"):
    title=item.findtext("title","")
    link=item.findtext("link","")
    desc=item.findtext("description","")
    match=re.search(r'https?://(?:www\\.)?(?:x\\.com|twitter\\.com)/[^/]+/status/\\d+',link)
    if not match: continue
    post=match.group(0)
    if post in seen: continue
    seen.add(post)
    rows.append([title,desc,post])
Path("output").mkdir(exist_ok=True)
with open("output/public_x_index.csv","w",newline="",encoding="utf-8-sig") as f:
    writer=csv.writer(f)
    writer.writerow(["search_title","search_snippet","post_url"])
    writer.writerows(rows)
print(f"Indexed X post URLs found: {len(rows)}")
if not rows:
    raise SystemExit("No public X post URLs found. Search engine may not expose results.")
