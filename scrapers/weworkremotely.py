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
    job_cards = soup.select("section.jobs article li, section.jobs li")
    jobs = []
    
    logger.info(f"WeWorkRemotely Parser: Found {len(job_cards)} list items to parse.")

    for idx, card in enumerate(job_cards):
        try:
            card_classes = card.get("class") or []
            # Skip advertisement cards
            if any("feature--ad" in cls or "listing-ad" in cls for cls in card_classes):
                continue
                
            link_elem = card.select_one("a.listing-link--unlocked")
            if not link_elem:
                link_elem = card.select_one('a[href^="/remote-jobs/"]')
                if not link_elem:
                    continue

            relative_link = link_elem.get("href", "")
            link = urljoin(base_url, str(relative_link))
            
            # Title
            title_elem = card.select_one(".new-listing__header__title__text")
            if not title_elem:
                title_elem = card.select_one(".title")
                title_elem = title_elem or card.select_one("h2, h3, h4")
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            
            # Company Name
            company_elem = card.select_one(".new-listing__company-name")
            if not company_elem:
                company_elem = card.select_one(".company")
            company = company_elem.get_text(strip=True) if company_elem else "N/A"
            
            # Headquarters and Location Restrictions
            hq_elem = card.select_one(".new-listing__company-headquarters")
            hq = hq_elem.get_text(strip=True) if hq_elem else ""
            
            # Additional category tags (like 'Contract', 'Anywhere in the World')
            category_elems = card.select(".new-listing__categories__category, .listing-category, .listing-tag")
            categories = [cat.get_text(strip=True) for cat in category_elems if cat.get_text(strip=True)]
            
            location_details = []
            if hq:
                location_details.append(hq)
            if categories:
                location_details.append(", ".join(categories))
                
            location = " | ".join(location_details) if location_details else "Remote"
            
            # Date Posted
            date_elem = card.select_one(".new-listing__header__icons__date, time")
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
