import asyncio
import random
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class ScraperEngine:
    def __init__(self):
        self.results = []
        # modern user-agent to avoid immediate blocking
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    async def fetch_page(self, url):
        """
        Launches a headless browser, navigates to the URL, 
        and returns the HTML content.
        """
        async with async_playwright() as p:
            # Launch browser (headless=True for speed, False to watch it work)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self.headers["User-Agent"])
            page = await context.new_page()

            print(f"🔍 Navigating to: {url}")
            
            try:
                # go to URL and wait until network is idle (important for JS sites)
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # human-like behavior: scroll down a bit
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(random.uniform(1, 3)) 

                content = await page.content()
                await browser.close()
                return content
            
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                await browser.close()
                return None

    def parse_jobs(self, html_content):
        """
        Uses BeautifulSoup to extract specific data points from the HTML.
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        job_listings = []

        # NOTE: You will update these selectors based on the target website
        # This example looks for common 'card' structures
        cards = soup.select(".job-card, .result, [data-testid='job-card']")

        for card in cards:
            data = {
                "title": card.select_one("h2, .title").get_text(strip=True) if card.select_one("h2, .title") else "N/A",
                "company": card.select_one(".company, .companyName").get_text(strip=True) if card.select_one(".company") else "N/A",
                "location": card.select_one(".location").get_text(strip=True) if card.select_one(".location") else "Remote",
                "link": card.select_one("a")["href"] if card.select_one("a") else "N/A"
            }
            job_listings.append(data)

        return job_listings

    async def run(self, target_url):
        html = await self.fetch_page(target_url)
        jobs = self.parse_jobs(html)
        print(f"Successfully scraped {len(jobs)} jobs.")
        return jobs

# To test the engine locally:
if __name__ == "__main__":
    test_url = "https://www.google.com/search?q=software+engineer+jobs" # Replace with your target
    engine = ScraperEngine()
    asyncio.run(engine.run(test_url))