import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger("InsightScraper")

def parse_weworkremotely_jobs(html_content):
    """
    Parses WeWorkRemotely programming category jobs from HTML.
    """
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "html.parser")
    base_url = "https://weworkremotely.com"
    
    # Selecting the list items in WeWorkRemotely
    job_cards = soup.select("section.jobs article ul li")
    jobs = []
    
    logger.info(f"WeWorkRemotely Parser: Found {len(job_cards)} list items to parse.")

    for idx, card in enumerate(job_cards):
        try:
            # Skip advertisement cards
            if "feature--ad" in card.get("class", []):
                continue
                
            # Each valid job card has a link with class 'listing-link--unlocked'
            link_elem = card.select_one("a.listing-link--unlocked")
            if not link_elem:
                # If there's no unlocking link, try any link inside that goes to remote-jobs
                link_elem = card.select_one('a[href^="/remote-jobs/"]')
                if not link_elem:
                    continue

            relative_link = link_elem.get("href", "")
            link = urljoin(base_url, relative_link)
            
            # Title
            title_elem = card.select_one(".new-listing__header__title__text")
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            
            # Company Name
            company_elem = card.select_one(".new-listing__company-name")
            company = company_elem.get_text(strip=True) if company_elem else "N/A"
            
            # Headquarters and Location Restrictions
            hq_elem = card.select_one(".new-listing__company-headquarters")
            hq = hq_elem.get_text(strip=True) if hq_elem else ""
            
            # Additional category tags (like 'Contract', 'Anywhere in the World')
            category_elems = card.select(".new-listing__categories__category")
            categories = [cat.get_text(strip=True) for cat in category_elems]
            
            location_details = []
            if hq:
                location_details.append(hq)
            if categories:
                # We can add all categories or specifically the region/contract type
                location_details.append(", ".join(categories))
                
            location = " | ".join(location_details) if location_details else "Remote"
            
            # Date Posted
            date_elem = card.select_one(".new-listing__header__icons__date")
            date_posted = "N/A"
            if date_elem:
                date_posted = date_elem.get_text(strip=True)
                if not date_posted or date_posted.lower() == "new":
                    date_posted = "Today"
                    
            job_data = {
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "date_posted": date_posted,
                "source": "WeWorkRemotely"
            }
            jobs.append(job_data)
        except Exception as e:
            logger.error(f"Error parsing WeWorkRemotely job item at index {idx}: {e}")
            
    return jobs
