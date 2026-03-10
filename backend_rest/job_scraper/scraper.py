# job_scraper/scraper.py

import requests
import urllib.parse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random

SCRAPE_DO_TOKEN = "9ad7dd6fdf0b41b79890cc484d5218ea7ef605bea67"  # 🔴 Put your real token here

ua = UserAgent()


def get_html_with_scrape_do(target_url):
    """
    VIVA:
    Sends target URL to scrape.do proxy.
    Retries 3 times if request fails or times out.
    render=true executes JavaScript before returning HTML.
    """
    encoded_url = urllib.parse.quote(target_url)

    proxy_url = (
        f"http://api.scrape.do/"
        f"?url={encoded_url}"
        f"&token={SCRAPE_DO_TOKEN}"
        f"&super=true"
        f"&render=true"
        f"&renderTimeout=12000"
    )

    headers = {"User-Agent": ua.random}

    # VIVA: Retry 3 times if request fails or times out
    for attempt in range(3):
        try:
            print(f"[Scraper] Attempt {attempt + 1}...")
            response = requests.get(proxy_url, headers=headers, timeout=120)
            response.raise_for_status()
            return response.text

        except requests.exceptions.Timeout:
            print(f"Attempt {attempt + 1} timed out. Retrying...")
            time.sleep(3)
            continue

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    print("All 3 attempts failed.")
    return None


def scrape_internshala_jobs(query="python", location="india"):
    """
    VIVA:
    Main scraping function.
    1. Build URL
    2. Fetch HTML via scrape.do
    3. Parse with BeautifulSoup
    4. Extract job data from each card
    5. Return list of job dicts

    Real HTML Structure found by inspection:
    <div class="internship_meta">                   ← parent card
        <h3 class="job-internship-name">            ← title
        <p class="company-name">                    ← company
        <div class="individual_internship_job">     ← details
            <p class="locations">                   ← location
            <span class="desktop">                  ← salary
            row_items[-1] span                      ← experience
    """

    # Step 1: Build URL
    base_url = f"https://internshala.com/jobs/{query}-jobs-in-{location}"
    print(f"[Scraper] Fetching: {base_url}")

    # Step 2: Fetch HTML
    html = get_html_with_scrape_do(base_url)
    if not html:
        print("[Scraper] Failed to fetch HTML.")
        return []

    # Step 3: Parse HTML
    soup = BeautifulSoup(html, "lxml")

    jobs = []

    # Step 4: Find all job cards
    job_cards = soup.find_all("div", class_="individual_internship_job")
    print(f"[Scraper] Found {len(job_cards)} job cards")

    # Step 5: Extract data from each card
    for card in job_cards:
        try:
            # Go UP to parent div to get title + company
            # VIVA: find_parent() traverses UP the HTML tree
            parent = card.find_parent("div", class_="internship_meta")

            # ── Job Title ─────────────────────────────────
            title_tag = parent.find("h3", class_="job-internship-name") if parent else None
            title = title_tag.text.strip() if title_tag else "N/A"

            # ── Company Name ──────────────────────────────
            company_tag = parent.find("p", class_="company-name") if parent else None
            company = company_tag.text.strip() if company_tag else "N/A"

            # ── Location ──────────────────────────────────
            location_tag = card.find("p", class_="locations")
            location_text = location_tag.text.strip() if location_tag else "N/A"

            # ── Salary ────────────────────────────────────
            salary_tag = card.find("span", class_="desktop")
            salary = salary_tag.text.strip() if salary_tag else "Not Disclosed"

            # ── Experience ────────────────────────────────
            row_items = card.find_all("div", class_="row-1-item")
            experience = "N/A"
            if len(row_items) >= 1:
                exp_span = row_items[-1].find("span")
                experience = exp_span.text.strip() if exp_span else "N/A"

            # ── Job URL ───────────────────────────────────
            link_tag = parent.find("a", class_="job-title-href") if parent else None
            job_url = (
                "https://internshala.com" + link_tag["href"]
                if link_tag else "N/A"
            )

            job = {
                "title": title,
                "company": company,
                "location": location_text,
                "salary": salary,
                "experience": experience,
                "posted_on": "N/A",
                "job_url": job_url,
                "source": "Internshala",
            }

            jobs.append(job)
            print(f"[Scraper] ✅ {title} at {company}")

        except Exception as e:
            print(f"[Scraper] Error parsing card: {e}")
            continue

        time.sleep(random.uniform(0.5, 1))

    print(f"[Scraper] Successfully scraped {len(jobs)} jobs")
    return jobs