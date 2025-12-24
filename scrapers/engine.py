import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class ScraperEngine:
    def __init__(self, config):
        self.config = config
        self.results = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    async def fetch_page(self, url):
        settings = self.config.get('settings', {})
        headless = settings.get('headless', True)
        timeout = settings.get('timeout', 60000)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context(user_agent=self.headers["User-Agent"])
            page = await context.new_page()
            
            try:
                print(f"Navigating to {url}...")
                await page.goto(url, wait_until="networkidle", timeout=timeout)
                content = await page.content()
                await browser.close()
                return content
            except Exception as e:
                print(f"Error: {e}")
                await browser.close()
                raise e

    def parse_data(self, html_content):
        if not html_content:
            return []
        
        # Get selectors from config
        selectors = self.config.get('selectors', {})
        soup = BeautifulSoup(html_content, "html.parser")
        items = []

        # use the job_card selector from config.json
        cards = soup.select(selectors.get('job_card', '.job-card'))

        for card in cards:
            data = {
                "title": card.select_one(selectors.get('title')).get_text(strip=True) if card.select_one(selectors.get('title')) else "N/A",
                "company": card.select_one(selectors.get('company')).get_text(strip=True) if card.select_one(selectors.get('company')) else "N/A",
                "location": card.select_one(selectors.get('location')).get_text(strip=True) if card.select_one(selectors.get('location')) else "N/A"
            }
            items.append(data)
        
        return items