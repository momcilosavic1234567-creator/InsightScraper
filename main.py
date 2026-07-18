import asyncio
import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from scrapers.engine import ScraperEngine
from utils.logger import setup_logger
from utils.database import init_db, save_jobs
from utils.notifications import check_and_notify_matches

load_dotenv()

# Main Execution
async def run_pipeline():
    logger = setup_logger()
    logger.info("=========================================")
    logger.info("Starting InsightScraper ETL Pipeline...")
    logger.info("=========================================")

    # 1. Load Configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        logger.info("Configuration loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    # 2. Initialize SQLite Database
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return

    # 3. Initialize Scraper Engine
    engine = ScraperEngine(config)

    # 4. Extract & Transform
    try:
        logger.info("Starting scrape of all enabled sources...")
        scraped_data = await engine.scrape_all_sources()
        logger.info(f"Scrape completed. Total items extracted: {len(scraped_data)}")
        
        if not scraped_data:
            logger.warning("No data found to process.")
            return

        # 5. Load to DB (Save and deduplicate)
        new_jobs = save_jobs(scraped_data)
        logger.info(f"SQLite load complete. Added {len(new_jobs)} new job listings.")
        
        # 6. Fallback/Backup CSV Save (Optional but good for history)
        if new_jobs:
            os.makedirs('data', exist_ok=True)
            df = pd.DataFrame(new_jobs)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"data/results_{timestamp}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"Historical backup CSV saved to {filename}")

            # 7. Check matches and notify only for newly inserted jobs.
            check_and_notify_matches(new_jobs, config)
        else:
            logger.info("No new jobs were added. Skipping notification checks.")
        
    except Exception as e:
        logger.error(f"An error occurred during pipeline execution: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run_pipeline())