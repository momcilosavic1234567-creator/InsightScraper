import asyncio
import json
import logging
import os
import pandas as pd
from datetime import datetime
from scrapers.engine import ScraperEngine

# Setup logging
def setup_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/scraper_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("InsightScraper")

# Data management
def save_data(data, config, logger):
    if not data:
        logger.warning("No data found to save.")
        return

    os.makedirs('data', exist_ok=True)
    df = pd.DataFrame(data)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    filename = f"data/results_{timestamp}.csv"
    df.to_csv(filename, index=False)
    logger.info(f"✨ Data successfully saved to {filename}")

# Main Execution
async def run_pipeline():
    logger = setup_logger()
    logger.info("Starting InsightScraper Pipeline...")

    # 1. Load Configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        logger.info("Config loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    # 2. Initialize Engine
    engine = ScraperEngine(config)

    # 3. Extract & Transform
    try:
        html = await engine.fetch_page(config['target_url'])
        scraped_data = engine.parse_data(html)
        logger.info(f"Successfully scraped {len(scraped_data)} items.")
        
        # 4. Load (Save)
        save_data(scraped_data, config, logger)
        
    except Exception as e:
        logger.error(f"An error occurred during the scrape: {e}")

if __name__ == "__main__":
    asyncio.run(run_pipeline())