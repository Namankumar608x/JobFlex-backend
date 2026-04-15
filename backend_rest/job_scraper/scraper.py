import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import random

SCRAPE_DO_TOKEN = os.getenv("scrape_do_token")
ua = UserAgent()


def get_html_with_scrape_do(target_url):
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
    base_url = f"https://internshala.com/jobs/{query}-jobs-in-{location}"
    print(f"[Internshala] Fetching: {base_url}")

    html = get_html_with_scrape_do(base_url)
    if not html:
        print("[Internshala] Failed to fetch HTML.")
        return []

    soup = BeautifulSoup(html, "lxml")
    jobs = []

    job_cards = soup.find_all("div", class_="individual_internship_job")
    print(f"[Internshala] Found {len(job_cards)} job cards")

    for card in job_cards:
        try:
            parent = card.find_parent("div", class_="internship_meta")

            title_tag = parent.find("h3", class_="job-internship-name") if parent else None
            title = title_tag.text.strip() if title_tag else "N/A"

            company_tag = parent.find("p", class_="company-name") if parent else None
            company = company_tag.text.strip() if company_tag else "N/A"

            location_tag = card.find("p", class_="locations")
            location_text = location_tag.text.strip() if location_tag else "N/A"

            salary_tag = card.find("span", class_="desktop")
            salary = salary_tag.text.strip() if salary_tag else "Not Disclosed"

            row_items = card.find_all("div", class_="row-1-item")
            experience = "N/A"
            if len(row_items) >= 1:
                exp_span = row_items[-1].find("span")
                experience = exp_span.text.strip() if exp_span else "N/A"

            link_tag = parent.find("a", class_="job-title-href") if parent else None
            job_url = (
                "https://internshala.com" + link_tag["href"]
                if link_tag else "N/A"
            )

            jobs.append({
                "title": title,
                "company": company,
                "location": location_text,
                "salary": salary,
                "experience": experience,
                "posted_on": "N/A",
                "job_url": job_url,
                "source": "Internshala",
            })
            print(f"[Internshala] ✅ {title} at {company}")

        except Exception as e:
            print(f"[Internshala] Error parsing card: {e}")
            continue

        time.sleep(random.uniform(0.5, 1))

    print(f"[Internshala] Successfully scraped {len(jobs)} jobs")
    return jobs



def scrape_remoteok_jobs(query="python"):
    """
    VIVA:
    RemoteOK provides a free public REST API.
    No scraping needed - just a simple GET request.
    Returns JSON directly with all job data.

    API URL: https://remoteok.com/api?tag=QUERY
    Response: List of job dicts
        - position  → job title
        - company   → company name
        - location  → job location
        - salary_min/max → salary range
        - tags      → skill tags
        - url       → job URL
        - date      → posted date
    """

    url = f"https://remoteok.com/api?tag={urllib.parse.quote(query)}"
    print(f"[RemoteOK] Fetching: {url}")

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as e:
        print(f"[RemoteOK] Request failed: {e}")
        return []

    except ValueError:
        print("[RemoteOK] Failed to parse JSON response")
        return []

    raw_jobs = data[1:] if len(data) > 1 else []
    print(f"[RemoteOK] Found {len(raw_jobs)} jobs")

    jobs = []
    for job in raw_jobs:
        try:
           
            salary_min = job.get("salary_min", 0)
            salary_max = job.get("salary_max", 0)

            if salary_min and salary_max:
                salary = f"${salary_min:,} - ${salary_max:,}"
            elif salary_min:
                salary = f"${salary_min:,}+"
            else:
                salary = "Not Disclosed"

       
            tags = job.get("tags", [])
            tags_str = ", ".join(tags[:5]) if tags else "N/A"  # max 5 tags

            jobs.append({
                "title": job.get("position", "N/A"),
                "company": job.get("company", "N/A"),
                "location": job.get("location", "Remote") or "Remote",
                "salary": salary,
                "experience": tags_str, 
                "posted_on": job.get("date", "N/A"),
                "job_url": job.get("url", "N/A"),
                "source": "RemoteOK",
            })
            print(f"[RemoteOK] ✅ {job.get('position')} at {job.get('company')}")

        except Exception as e:
            print(f"[RemoteOK] Error parsing job: {e}")
            continue

    print(f"[RemoteOK] Successfully fetched {len(jobs)} jobs")
    return jobs