import json
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl

from pathlib import Path
from urllib.parse import urljoin


START_URL = "https://books.toscrape.com/"

CACHE_DIR = Path("scraper/cache")
DETAIL_CACHE_DIR = CACHE_DIR / "details"
OUTPUT_DIR = Path("scraper/output")

HEADERS = {
    "User-Agent": (
        "FlyRankInternship-A9/1.0 "
        "(+https://github.com/tejashwinirk/task-management-api)"
    )
}

REQUEST_DELAY = 0.5


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


# --------------------------------------------------
# Run statistics
# --------------------------------------------------

run_started_at = datetime.now(timezone.utc)

pages_fetched = 0
cache_hits = 0


def fetch_or_load(url, cache_path):
    global pages_fetched
    global cache_hits

    if cache_path.exists():

        html = cache_path.read_text(
            encoding="utf-8"
        )

        cache_hits += 1

        print("CACHE HIT")
        print(
            f"response_size={len(html)} bytes"
        )

        return html

    time.sleep(REQUEST_DELAY)

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

    except requests.RequestException as error:

        print(
            f"REQUEST ERROR: {error}"
        )

        print("RETRY")

        time.sleep(REQUEST_DELAY)

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

    if response.status_code in {
        500,
        502,
        503,
        504
    }:

        print(
            f"RETRY status={response.status_code}"
        )

        time.sleep(REQUEST_DELAY)

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

    if response.status_code != 200:

        raise RuntimeError(
            f"Request failed with status "
            f"{response.status_code}"
        )

    cache_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cache_path.write_text(
        response.text,
        encoding="utf-8"
    )

    pages_fetched += 1

    print("FETCH")

    print(
        f"response_size={len(response.text)} bytes"
    )

    return response.text


def normalize_price(price_text):

    if not price_text:

        raise ValueError(
            "Price is missing"
        )

    cleaned = (
        price_text
        .replace("£", "")
        .replace("Â", "")
        .strip()
    )

    return float(cleaned)


def extract_book_details(
    html,
    product_url,
    source_page
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    title_element = soup.select_one(
        "div.product_main h1"
    )

    price_element = soup.select_one(
        "div.product_main p.price_color"
    )

    availability_element = soup.select_one(
        "div.product_main p.instock.availability"
    )

    rating_element = soup.select_one(
        "div.product_main p.star-rating"
    )

    description_element = soup.select_one(
        "#product_description + p"
    )

    # Make sure this is actually
    # a valid book detail page.

    if not title_element:

        raise ValueError(
            "Book title not found; "
            "page is not a valid book detail page"
        )

    if not price_element:

        raise ValueError(
            "Book price not found; "
            "page is not a valid book detail page"
        )

    if not availability_element:

        raise ValueError(
            "Book availability not found; "
            "page is not a valid book detail page"
        )

    if not rating_element:

        raise ValueError(
            "Book rating not found; "
            "page is not a valid book detail page"
        )

    title = title_element.get_text(
        strip=True
    )

    price_text = price_element.get_text(
        strip=True
    )

    availability_text = (
        availability_element.get_text(
            " ",
            strip=True
        )
    )

    rating_classes = rating_element.get(
        "class",
        []
    )

    rating_text = next(
        (
            item
            for item in rating_classes
            if item in {
                "One",
                "Two",
                "Three",
                "Four",
                "Five"
            }
        ),
        None
    )

    if not rating_text:

        raise ValueError(
            "Valid book rating not found"
        )

    description = (
        description_element.get_text(
            " ",
            strip=True
        )
        if description_element
        else None
    )

    fetched_at = datetime.now(
        timezone.utc
    )

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "price_gbp": normalize_price(
            price_text
        ),
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }


# --------------------------------------------------
# Discover the first three catalogue pages
# --------------------------------------------------

current_url = START_URL

catalogue_pages = []

book_links = set()

book_sources = {}


for page_number in range(1, 4):

    cache_path = (
        CACHE_DIR
        / f"catalogue-page-{page_number}.html"
    )

    html = fetch_or_load(
        current_url,
        cache_path
    )

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    catalogue_pages.append(
        current_url
    )

    for book in soup.select(
        "article.product_pod h3 a"
    ):

        href = book.get("href")

        if href:

            book_url = urljoin(
                current_url,
                href
            )

            book_links.add(
                book_url
            )

            book_sources[
                book_url
            ] = current_url

    if page_number < 3:

        next_link = soup.select_one(
            "li.next a"
        )

        if not next_link:

            raise RuntimeError(
                "Next catalogue page link not found"
            )

        current_url = urljoin(
            current_url,
            next_link.get("href")
        )


print(
    f"catalogue_pages={len(catalogue_pages)}"
)

print(
    f"discovered={len(book_links)}"
)

print(
    f"unique_urls={len(book_links)}"
)


# --------------------------------------------------
# Temporary broken-page test
# --------------------------------------------------

book_links.add(
    "https://books.toscrape.com/"
    "catalogue/fake-book-for-testing/"
    "index.html"
)


# --------------------------------------------------
# Fetch and extract every book detail page
# --------------------------------------------------

raw_records = []

failed_pages = []


for index, product_url in enumerate(
    sorted(book_links),
    start=1
):

    detail_cache_path = (
        DETAIL_CACHE_DIR
        / f"book-{index}.html"
    )

    source_page = book_sources.get(
        product_url,
        START_URL
    )

    try:

        html = fetch_or_load(
            product_url,
            detail_cache_path
        )

        record = extract_book_details(
            html,
            product_url,
            source_page
        )

        raw_records.append(
            record
        )

        if index == 1:

            print(
                "First raw record:"
            )

            print(record)

    except Exception as error:

        print(
            f"FAILED page={product_url}"
        )

        print(
            f"error={error}"
        )

        failed_pages.append(
            {
                "url": product_url,
                "error": str(error)
            }
        )


print(
    f"detail_pages={len(raw_records)}"
)


# --------------------------------------------------
# Validate records with Pydantic
# --------------------------------------------------

valid_records = []

invalid_records = []


for record in raw_records:

    try:

        validated = (
            BookRecord.model_validate(
                record
            )
        )

        valid_records.append(
            validated
        )

    except Exception as error:

        invalid_records.append(
            {
                "record": record,
                "error": str(error)
            }
        )


# --------------------------------------------------
# Save output
# --------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


books_output = (
    OUTPUT_DIR
    / "books.json"
)

errors_output = (
    OUTPUT_DIR
    / "errors.json"
)

report_output = (
    OUTPUT_DIR
    / "run-report.json"
)


books_output.write_text(
    json.dumps(
        [
            record.model_dump(
                mode="json"
            )
            for record in valid_records
        ],
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


errors_output.write_text(
    json.dumps(
        invalid_records,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


# --------------------------------------------------
# Create run report
# --------------------------------------------------

run_finished_at = datetime.now(
    timezone.utc
)

duration_seconds = (
    run_finished_at - run_started_at
).total_seconds()


run_report = {
    "started_at": run_started_at.isoformat(),
    "finished_at": run_finished_at.isoformat(),
    "duration_seconds": duration_seconds,
    "pages_fetched": pages_fetched,
    "cache_hits": cache_hits,
    "valid_records": len(valid_records),
    "invalid_records": len(invalid_records),
    "failed_pages": failed_pages
}


report_output.write_text(
    json.dumps(
        run_report,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


# --------------------------------------------------
# Final output
# --------------------------------------------------

print(
    f"valid_records={len(valid_records)}"
)

print(
    f"invalid_records={len(invalid_records)}"
)

print(
    f"failed_pages={len(failed_pages)}"
)

print(
    f"pages_fetched={pages_fetched}"
)

print(
    f"cache_hits={cache_hits}"
)

print(
    f"duration_seconds={duration_seconds}"
)

print(
    f"saved={books_output}"
)

print(
    f"saved={errors_output}"
)

print(
    f"saved={report_output}"
)