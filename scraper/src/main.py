import requests
from pathlib import Path

PAGE_URL = "https://books.toscrape.com/"
CACHE_PATH = Path("scraper/cache/catalogue-page-1.html")

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/tejashwinirk/task-management-api)"
}


if CACHE_PATH.exists():
    html = CACHE_PATH.read_text(encoding="utf-8")
    print("CACHE HIT")
    print(f"response_size={len(html)} bytes")
else:
    response = requests.get(
        PAGE_URL,
        headers=HEADERS,
        timeout=10
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Request failed with status {response.status_code}"
        )

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(response.text, encoding="utf-8")

    html = response.text

    print("FETCH")
    print(f"response_size={len(html)} bytes")