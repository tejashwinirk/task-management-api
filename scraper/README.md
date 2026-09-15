# A9 — The Polite Scraper

## Target Classification

**Site:** Books to Scrape
**URL:** https://books.toscrape.com/

**Classification:** Sandbox / test website for practicing web scraping.

**Why this target is appropriate:**
Books to Scrape is explicitly presented as a sandbox website for scraping practice. It provides publicly accessible catalogue and book-detail pages without requiring login or access to private information.

**Amount of data:**
Only the first 3 catalogue pages will be processed. These pages contain 60 unique books in total.

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

A normalized numeric price in GBP will also be produced.

**robots.txt check:**
Requested `https://books.toscrape.com/robots.txt` once. The result was Not Found (404).

**Important:**
I will not reuse this code on another site without checking its rules and terms first.
