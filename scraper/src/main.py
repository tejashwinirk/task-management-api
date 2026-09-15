import requests
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup


START_URL = "https://books.toscrape.com/"
CACHE_DIR = Path("scraper/cache")

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/tejashwinirk/task-management-api)"
}


def fetch_or_load(url, cache_path):
    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        print("CACHE HIT")
        print(f"response_size={len(html)} bytes")
        return html

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Request failed with status {response.status_code}"
        )

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(response.text, encoding="utf-8")

    print("FETCH")
    print(f"response_size={len(response.text)} bytes")

    return response.text


# Discover the first three catalogue pages
current_url = START_URL
catalogue_pages = []
book_links = set()

for page_number in range(1, 4):

    cache_path = CACHE_DIR / f"catalogue-page-{page_number}.html"

    html = fetch_or_load(current_url, cache_path)

    soup = BeautifulSoup(html, "html.parser")

    catalogue_pages.append(current_url)

    for book in soup.select("article.product_pod h3 a"):
        href = book.get("href")

        if href:
            book_url = urljoin(current_url, href)
            book_links.add(book_url)

    if page_number < 3:
        next_link = soup.select_one("li.next a")

        if not next_link:
            raise RuntimeError("Next catalogue page link not found")

        current_url = urljoin(current_url, next_link.get("href"))


print(f"catalogue_pages={len(catalogue_pages)}")
print(f"discovered={len(book_links)}")
print(f"unique_urls={len(book_links)}")