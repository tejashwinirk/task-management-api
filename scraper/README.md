# A9 — The Polite Scraper

A polite Python scraper for the **Books to Scrape** sandbox website.

## Target Classification

**Site:** Books to Scrape
**URL:** https://books.toscrape.com/

**Classification:** Sandbox / test website for practicing web scraping.

**Why this target is appropriate:**
Books to Scrape is explicitly presented as a sandbox website for scraping practice. It provides publicly accessible catalogue and book-detail pages without requiring login or access to private information.

**Amount of data:**
Only the first 3 catalogue pages are processed. These pages contain 60 unique books in total.

**Data to be collected:**

For each book:

* Title
* Product URL
* Price
* Availability
* Rating
* Description
* Source page
* Fetch timestamp
* Normalized numeric price in GBP

## robots.txt Check

The scraper requested:

`https://books.toscrape.com/robots.txt`

The result was **404 Not Found**.

This check was performed once before scraping.

## Installation

From the repository root:

```bash
python -m venv venv
```

Activate the virtual environment.

On Git Bash:

```bash
source venv/Scripts/activate
```

Install dependencies:

```bash
pip install -r scraper/requirements.txt
```

## Run

From the repository root, run:

```bash
python scraper/src/main.py
```

The scraper discovers the first three catalogue pages, collects the 60 book URLs, fetches and caches book-detail pages, extracts the required fields, validates the normalized records, and writes the output files.

## Output

The scraper produces:

```text
scraper/output/books.json
scraper/output/errors.json
scraper/output/run-report.json
```

### `books.json`

Contains validated book records.

Each valid record contains:

* `title`
* `product_url`
* `price_text`
* `price_gbp`
* `availability_text`
* `rating_text`
* `description`
* `source_page`
* `fetched_at`

### `errors.json`

Contains records that failed Pydantic validation.

### `run-report.json`

Contains:

* Start time
* Finish time
* Duration
* Pages fetched
* Cache hits
* Valid records
* Invalid records
* Failed pages

## Pipeline

The scraper follows this pipeline:

```text
Fetch
  ↓
Extract
  ↓
Normalize
  ↓
Validate
  ↓
Store
  ↓
Report
```

## Politeness Rules

The scraper follows these rules:

* Uses a descriptive `User-Agent`.
* Uses a 10-second request timeout.
* Waits at least 0.5 seconds between real HTTP requests.
* Does not wait when loading from the local cache.
* Caches catalogue and detail-page HTML to avoid unnecessary repeat requests.
* Retries once for timeout/request errors and HTTP 5xx responses.
* Does not retry HTTP 403 or 404 responses.
* Processes only the first three catalogue pages.
* Does not require login or access private information.

## Failure Handling

A failed detail page does not stop the entire run.

The scraper records the failed URL and error in the run report while continuing with the remaining pages.

A test with a fake book URL demonstrated that the scraper can skip a failed page while still producing 60 valid book records.

## Validation

Records are validated using Pydantic.

The normalized `price_gbp` field must be numeric, and product/source URLs are validated as HTTPS URLs.

## Caching

Downloaded HTML is stored locally under:

```text
scraper/cache/
```

The cache is ignored by Git and is **not published to GitHub**.

This prevents hundreds of cached HTML files from unnecessarily increasing the repository size.

## Limitation

This scraper intentionally processes only the first three catalogue pages of Books to Scrape.

It is designed as an internship exercise demonstrating respectful scraping, extraction, normalization, validation, caching, and failure handling rather than as a general-purpose crawler.

## Browser Cost Comparison

This implementation uses direct HTTP requests with Requests and Beautiful Soup because the target pages expose the required book information directly in HTML.

A browser automation approach would add browser startup and rendering overhead without being necessary for this target.

For a JavaScript-heavy website where content is unavailable in the initial HTML, browser automation could become appropriate.

## Ethics Note

This project is intended for the Books to Scrape sandbox.

I will not reuse this scraper on another website without first checking that site's robots.txt, terms, access rules, and applicable policies.

The scraper avoids private information, authentication-protected areas, and unnecessary request volume.
