import requests
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime, timezone


START_URL = "https://books.toscrape.com/"
CACHE_DIR = Path("scraper/cache")
DETAIL_CACHE_DIR = CACHE_DIR / "details"

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


def extract_book_details(html, product_url, source_page):
    soup = BeautifulSoup(html, "html.parser")

    title_element = soup.select_one("div.product_main h1")
    price_element = soup.select_one("div.product_main p.price_color")
    availability_element = soup.select_one(
        "div.product_main p.instock.availability"
    )
    rating_element = soup.select_one(
        "div.product_main p.star-rating"
    )
    description_element = soup.select_one(
        "#product_description + p"
    )

    title = title_element.get_text(strip=True) if title_element else None
    price_text = price_element.get_text(strip=True) if price_element else None
    availability_text = (
        availability_element.get_text(" ", strip=True)
        if availability_element
        else None
    )

    rating_text = None
    if rating_element:
        rating_classes = rating_element.get("class", [])
        rating_text = next(
            (
                item
                for item in rating_classes
                if item in {"One", "Two", "Three", "Four", "Five"}
            ),
            None
        )

    description = (
        description_element.get_text(" ", strip=True)
        if description_element
        else None
    )

    fetched_at = datetime.now(timezone.utc).isoformat()

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }


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


# Fetch and extract every book detail page
records = []

for index, product_url in enumerate(sorted(book_links), start=1):

    detail_cache_path = DETAIL_CACHE_DIR / f"book-{index}.html"

    html = fetch_or_load(
        product_url,
        detail_cache_path
    )

    record = extract_book_details(
        html,
        product_url,
        START_URL
    )

    records.append(record)

    if index == 1:
        print("First raw record:")
        print(record)


print(f"detail_pages={len(records)}")