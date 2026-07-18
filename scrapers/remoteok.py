import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger("InsightScraper")


def parse_remoteok_jobs(html_content):
    """Parse RemoteOK job cards from HTML."""
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    base_url = "https://remoteok.com"
    job_cards = soup.select(".job.list, .job")
    jobs = []

    logger.info(f"RemoteOK Parser: Found {len(job_cards)} job items to parse.")

    for index, card in enumerate(job_cards):
        try:
            link_elem = card.select_one("a.preventLink")
            if not link_elem:
                continue

            href = link_elem.get("href", "")
            if isinstance(href, (list, tuple)):
                href = href[0] if href else ""
            if not href:
                continue

            link = urljoin(base_url, str(href))
            title = card.select_one("h2")
            title_text = title.get_text(" ", strip=True) if title else "N/A"

            company_elem = card.select_one(".company")
            company = company_elem.get_text(" ", strip=True) if company_elem else "N/A"

            location_elem = card.select_one(".location")
            location = location_elem.get_text(" ", strip=True) if location_elem else "Remote"

            date_elem = card.select_one(".date")
            date_text = date_elem.get_text(" ", strip=True) if date_elem else "N/A"

            jobs.append(
                {
                    "title": title_text,
                    "company": company,
                    "location": location,
                    "link": link,
                    "date_posted": date_text,
                    "source": "RemoteOK",
                }
            )
        except Exception as exc:
            logger.error(f"Error parsing RemoteOK job item at index {index}: {exc}")

    return jobs
