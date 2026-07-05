"""
Fast IT Jobs Scraper (jobz.pk) — BeautifulSoup + requests version
===================================================================
Replaces the Selenium-based scraper with plain HTTP requests + BeautifulSoup.
Since jobz.pk serves fully-rendered HTML (no JS needed to see listings or
detail pages), this avoids the overhead of a real browser entirely, and
fetches detail pages concurrently with a thread pool for a large speed-up.

Usage:
    python scrape_it_jobs_bs4.py
    python scrape_it_jobs_bs4.py --max-pages 20 --workers 16
"""

import argparse
import os
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

BASE = "https://www.jobz.pk"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
OUT_DIR = "data/raw"
os.makedirs(OUT_DIR, exist_ok=True)


def get_soup(session: requests.Session, url: str, retries: int = 3, timeout: int = 15):
    """GET a URL and return a parsed BeautifulSoup object, with basic retry logic."""
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, headers=HEADERS, timeout=timeout)
            if resp.status_code == 200:
                return BeautifulSoup(resp.text, "html.parser")
            print(f"  [warn] {url} -> HTTP {resp.status_code} (attempt {attempt})")
        except requests.RequestException as e:
            print(f"  [warn] {url} -> {e} (attempt {attempt})")
        time.sleep(1.5 * attempt)
    return None


def parse_listing_page(soup: BeautifulSoup):
    """Extract basic job rows (title, city, date, link) from a listing page."""
    listing = soup.find(class_="listings")
    if not listing:
        return []

    rows = listing.find_all(class_="row_container")[1:]  # skip header row
    page_jobs = []
    for row in rows:
        title_el = row.select_one(".cell31 a")
        city_el = row.select_one(".cell32 a")
        date_el = row.find(class_="cell33")

        page_jobs.append({
            "Job Title": title_el.get_text(strip=True) if title_el else "",
            "City": city_el.get_text(strip=True) if city_el else "",
            "Date Posted": date_el.get_text(strip=True) if date_el else "",
            "Job Link": title_el["href"] if title_el and title_el.has_attr("href") else "",
        })
    return page_jobs


def scrape_job_details(session: requests.Session, link: str) -> dict:
    """Fetch a single job detail page and extract the label/value rows + description."""
    details = {}
    if not link:
        return details

    soup = get_soup(session, link)
    if soup is None:
        return details

    detail_block = soup.find(class_="job_detail")
    if detail_block:
        for row in detail_block.find_all(class_="row_job_detail"):
            label_el = row.find(class_="job_detail_cell1")
            value_el = row.find(class_="job_detail_cell2")
            if label_el and value_el:
                key = label_el.get_text(strip=True).rstrip(":")
                if key:
                    details[key] = value_el.get_text(strip=True)

    desc_block = soup.find(id="ad-desc-cont")
    details["Description"] = desc_block.get_text(strip=True) if desc_block else ""

    return details


def scrape(max_pages: int | None, workers: int, delay: float):
    session = requests.Session()
    jobs = []
    page = 0

    while True:
        if max_pages is not None and page >= max_pages:
            print(f"Reached max_pages={max_pages}, stopping.")
            break

        url = f"{BASE}/it-employment/" if page == 0 else f"{BASE}/it-employment-{page}/"
        print(f"\nOpening Page {page + 1}: {url}")

        soup = get_soup(session, url)
        if soup is None:
            print("Failed to load page after retries. Stopping.")
            break

        page_jobs = parse_listing_page(soup)
        if not page_jobs:
            print("No jobs found. Scraping completed.")
            break

        print(f"Found {len(page_jobs)} jobs — fetching details with {workers} workers...")

        # Fetch all detail pages for this listing page concurrently
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_job = {
                executor.submit(scrape_job_details, session, job["Job Link"]): job
                for job in page_jobs
            }
            for future in as_completed(future_to_job):
                job = future_to_job[future]
                try:
                    details = future.result()
                    job.update(details)
                except Exception as e:
                    print(f"  [warn] failed to fetch details for {job['Job Link']}: {e}")

        jobs.extend(page_jobs)
        print(f"Collected {len(jobs)} jobs so far")

        # Auto-save after every page, same as the original scraper
        df = pd.DataFrame(jobs)
        df.to_csv(f"{OUT_DIR}/IT_Related_Jobs_Visiting_Links1.csv", index=False, encoding="utf-8-sig")
        df.to_excel(f"{OUT_DIR}/IT_Related_Jobs_Visiting_Links1.xlsx", index=False)

        page += 1
        time.sleep(delay)  # be polite to the server between listing pages

    print("\n===================================")
    print(f"Total Pages Scraped : {page}")
    print(f"Total Jobs Scraped  : {len(jobs)}")
    print("Data saved successfully.")
    print("===================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fast jobz.pk IT jobs scraper (requests + BeautifulSoup)")
    parser.add_argument("--max-pages", type=int, default=None, help="Stop after N listing pages (default: no limit)")
    parser.add_argument("--workers", type=int, default=10, help="Concurrent threads for detail-page fetching (default: 10)")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds to wait between listing pages (default: 1.0)")
    args = parser.parse_args()

    scrape(max_pages=args.max_pages, workers=args.workers, delay=args.delay)