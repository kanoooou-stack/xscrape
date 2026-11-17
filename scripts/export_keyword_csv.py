"""Export X keyword search results to CSV. Requires X_COOKIES secret."""
import asyncio
import csv
import os
import sys
from pathlib import Path

from twscrape import API

async def main():
    query = os.environ.get("SEARCH_QUERY", "NVIDIA").strip()
    cookies = os.environ.get("X_COOKIES", "").strip()
    if not cookies:
        print("X_COOKIES is not configured. No X login attempted.")
        print("The xscrape package is installed, but live keyword search requires an authenticated X session.")
        return
    api = API("search_accounts.db")
    # Only cookies are used for authentication. No password is stored.
    await api.pool.add_account("search_user", "unused", "unused@example.invalid", "unused", cookies=cookies)
    rows = []
    async for tweet in api.search(query, limit=20, product="Latest"):
        rows.append({"id": str(tweet.id), "date": str(tweet.date), "username": tweet.user.username if tweet.user else "", "text": tweet.rawContent, "url": f"https://x.com/i/status/{tweet.id}"})
    Path("output").mkdir(exist_ok=True)
    with open("output/x_search.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "username", "text", "url"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Exported {len(rows)} posts to output/x_search.csv")

if __name__ == "__main__":
    asyncio.run(main())
