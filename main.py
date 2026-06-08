import asyncio
import json
import logging
import os
import pandas as pd
from datetime import datetime
from scrapers.engine import ScraperEngine
from utils.logger import setup_logger
from utils.database import init_db, save_jobs
from utils.notifications import check_and_notify_matches

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
        new_jobs_count = save_jobs(scraped_data)
        logger.info(f"SQLite load complete. Added {new_jobs_count} new job listings.")
        
        # 6. Fallback/Backup CSV Save (Optional but good for history)
        if new_jobs_count > 0:
            os.makedirs('data', exist_ok=True)
            df = pd.DataFrame(scraped_data)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"data/results_{timestamp}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"Historical backup CSV saved to {filename}")

            # 7. Check matches and notify via Discord Webhook
            # Find the new jobs just scraped (we check the last 'new_jobs_count' scraped elements)
            # Or filter the scraped data list: only notify if it was newly inserted.
            # To be simple and robust: we can check the scraped items that were newly inserted.
            # We can find out which jobs were newly inserted by checking if their links match.
            # Since WeWorkRemotely / python.org jobs are processed in order, we can pass all scraped_data
            # and let the notification system process them, or check against database.
            # Let's filter scraped_data to only those that are newly inserted by checking the DB or just notifying matches
            # from the whole scrape (which is fine, but to avoid spamming, we can notify on newly inserted ones).
            # A simple way to get new jobs is to query the DB for jobs created in the last 1 minute:
            from utils.database import get_all_jobs
            df_jobs = get_all_jobs()
            if not df_jobs.empty:
                # Find jobs with scraped_at close to now, or just status='New'
                new_db_jobs = df_jobs[df_jobs['status'] == 'New'].to_dict(orient='records')
                # We can notify for these new_db_jobs
                check_and_notify_matches(new_db_jobs, config)
        else:
            logger.info("No new jobs were added. Skipping notification checks.")
        
    except Exception as e:
        logger.error(f"An error occurred during pipeline execution: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(run_pipeline())