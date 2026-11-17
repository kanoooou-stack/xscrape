import asyncio
import csv
import os
from pathlib import Path
from twscrape import API

async def main():
    cookies = os.environ.get("X_COOKIES", "").strip()
    if not cookies:
        print("SKIPPED: X_COOKIES secret is not set. No live X request made.")
        return
    query = os.environ.get("SEARCH_QUERY", "NVIDIA").strip() or "NVIDIA"
    api = API("xscrape-test-accounts.db")
    await api.pool.add_account_cookies("test_account", cookies)
    output = Path("x_search_results.csv")
    count = 0
    with output.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "date", "user", "text", "url"])
        async for tweet in api.search(query, limit=20, product="Latest"):
            writer.writerow([tweet.id, tweet.date, tweet.user.username, tweet.rawContent,
                             f"https://x.com/{tweet.user.username}/status/{tweet.id}"])
            count += 1
            if count >= 20:
                break
    print(f"Search finished. Saved {count} posts to {output}.")
    if count == 0:
        raise RuntimeError("No posts returned. Check X session validity or rate limits.")

asyncio.run(main())
