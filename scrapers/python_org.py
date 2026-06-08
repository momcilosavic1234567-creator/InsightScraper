import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger("InsightScraper")

def parse_python_org_jobs(html_content):
    """
    Parses the HTML of the Python.org job board and extracts job details.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    base_url = "https://www.python.org"
    
    # Python.org jobs list container is typically <ol class="list-recent-jobs ...">
    job_cards = soup.select("ol.list-recent-jobs li")
    jobs = []
    
    logger.info(f"Python.org Parser: Found {len(job_cards)} list items to parse.")

    for idx, card in enumerate(job_cards):
        try:
            # 1. Title and Link
            title_link_elem = card.select_one("h2.listing-company span.listing-company-name a")
            if not title_link_elem:
                continue
                
            title = title_link_elem.get_text(strip=True)
            relative_link = title_link_elem.get("href", "")
            link = urljoin(base_url, relative_link)
            
            # 2. Company Name
            # The company name is text inside span.listing-company-name, after the <br> tag.
            company_span = card.select_one("h2.listing-company span.listing-company-name")
            company = "N/A"
            if company_span:
                # Get the last text node in the contents
                strings = list(company_span.stripped_strings)
                if strings:
                    # If "New" badge is present, it's at index 0, Title is at index 1, Company is the last string
                    company = strings[-1]
            
            # 3. Location
            location_elem = card.select_one("h2.listing-company span.listing-location a")
            location = location_elem.get_text(strip=True) if location_elem else "N/A"
            
            # 4. Date Posted
            posted_elem = card.select_one("span.listing-posted time")
            date_posted = posted_elem.get_text(strip=True) if posted_elem else "N/A"
            
            job_data = {
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "date_posted": date_posted,
                "source": "Python.org"
            }
            jobs.append(job_data)
        except Exception as e:
            logger.error(f"Error parsing Python.org job item at index {idx}: {e}")
            
    return jobs
