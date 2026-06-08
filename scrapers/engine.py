import asyncio
import logging
import random
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from scrapers.python_org import parse_python_org_jobs
from scrapers.weworkremotely import parse_weworkremotely_jobs

logger = logging.getLogger("InsightScraper")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

class ScraperEngine:
    def __init__(self, config):
        self.config = config
        self.results = []

    async def fetch_page(self, url):
        """Fetches the page content of the given URL using Playwright."""
        settings = self.config.get('settings', {})
        headless = settings.get('headless', True)
        timeout = settings.get('timeout', 30000)
        user_agent = random.choice(USER_AGENTS)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context(user_agent=user_agent)
            page = await context.new_page()
            
            try:
                logger.info(f"Navigating to {url}...")
                # Using 'domcontentloaded' is much more resilient and faster than 'networkidle'
                await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                # Give it a short pause to ensure any basic dynamic scripts load
                await page.wait_for_timeout(1000)
                content = await page.content()
                await browser.close()
                return content
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                await browser.close()
                raise e

    def parse_data(self, html_content, source_name="Generic"):
        """
        Parses HTML content based on source name or falls back to CSS selectors config
        for backward compatibility.
        """
        if not html_content:
            return []

        # If source is explicit, route to specific parser
        if source_name == "Python.org":
            return parse_python_org_jobs(html_content)
        elif source_name == "WeWorkRemotely":
            return parse_weworkremotely_jobs(html_content)

        # Backward compatibility fallback using config selectors (for existing tests)
        selectors = self.config.get('selectors', {})
        if not selectors or 'job_card' not in selectors:
            # Try to autodetect or return empty
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        items = []
        cards = soup.select(selectors.get('job_card', '.job-card'))

        for card in cards:
            data = {
                "title": card.select_one(selectors.get('title')).get_text(strip=True) if card.select_one(selectors.get('title')) else "N/A",
                "company": card.select_one(selectors.get('company')).get_text(strip=True) if card.select_one(selectors.get('company')) else "N/A",
                "location": card.select_one(selectors.get('location')).get_text(strip=True) if card.select_one(selectors.get('location')) else "N/A",
                "link": card.select_one('a')['href'] if card.select_one('a') else "",
                "source": "Generic"
            }
            items.append(data)
        
        return items

    async def scrape_all_sources(self):
        """Scrapes all enabled sources in the configuration and returns aggregated jobs."""
        sources = self.config.get("sources", [])
        if not sources:
            logger.warning("No scraping sources defined in config.json")
            return []

        all_jobs = []
        for src in sources:
            if not src.get("enabled", True):
                logger.info(f"Skipping disabled source: {src.get('name')}")
                continue

            name = src.get("name")
            url = src.get("url")
            logger.info(f"Scraping source '{name}' from {url}...")
            
            try:
                html = await self.fetch_page(url)
                jobs = self.parse_data(html, source_name=name)
                logger.info(f"Successfully scraped {len(jobs)} jobs from {name}")
                all_jobs.extend(jobs)
            except Exception as e:
                logger.error(f"Failed to scrape source {name}: {e}")

        return all_jobs