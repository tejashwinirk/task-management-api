import requests
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from pydantic import BaseModel, HttpUrl


START_URL = "https://books.toscrape.com/"
CACHE_DIR = Path("scraper/cache")
DETAIL_CACHE_DIR = CACHE_DIR / "details"

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/tejashwinirk/task-management-api)"
}


class BookRecord(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: HttpUrl
    fetched_at: datetime


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

def normalize_price(price_text):
    if not price_text:
        raise ValueError("Price is missing")

    cleaned = price_text.replace("£", "").replace("Â", "").strip()

    return float(cleaned)

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

    fetched_at = datetime.now(timezone.utc)

    return {
    "title": title,
    "product_url": product_url,
    "price_text": price_text,
    "price_gbp": normalize_price (price_text),
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

        current_url = urljoin(
            current_url,
            next_link.get("href")
        )


print(f"catalogue_pages={len(catalogue_pages)}")
print(f"discovered={len(book_links)}")
print(f"unique_urls={len(book_links)}")


# Fetch and extract every book detail page
raw_records = []

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

    raw_records.append(record)

    if index == 1:
        print("First raw record:")
        print(record)


valid_records = []
invalid_records = []

for record in raw_records:
    try:
        validated = BookRecord.model_validate(record)
        valid_records.append(validated)

    except Exception as error:
        invalid_records.append({
            "record": record,
            "error": str(error)
        })


OUTPUT_DIR = Path("scraper/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

books_output = OUTPUT_DIR / "books.json"
errors_output = OUTPUT_DIR / "errors.json"


books_output.write_text(
    __import__("json").dumps(
        [record.model_dump(mode="json") for record in valid_records],
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


errors_output.write_text(
    __import__("json").dumps(
        invalid_records,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


print(f"detail_pages={len(raw_records)}")
print(f"valid_records={len(valid_records)}")
print(f"invalid_records={len(invalid_records)}")
print(f"saved={books_output}")
print(f"saved={errors_output}")