import asyncio
import os
import pandas as pd
from datetime import datetime
from scrapers.engine import ScraperEngine

async def main():
    # 1. configuration
    TARGET_URL = os.getenv("TARGET_URL", "https://www.google.com/search?q=software+engineer+jobs") # Update this
    DATA_DIR = "data"
    TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M")

    # Ensure the data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created directory: {DATA_DIR}")
    
    # 2. Initialize and Run Scraper
    print("Starting Scrapper...")
    engine = ScraperEngine()
    raw_data = await engine.run(TARGET_URL)

    if not raw_data:
        print(" No data collected. Check your selectors or internet connection.")
        return
    
    # 3. Process with Pandas
    df = pd.DataFrame(raw_data)

    # Basic cleaning: remove duplicates or empty rows
    df.drop_duplicates(inplace=True)

    # 4. Save to CSV and JSON
    csv_path = os.path.join(DATA_DIR, f"jobs_{TIMESTAMP}.csv")
    json_path = os.path.join(DATA_DIR, f"jobs_{TIMESTAMP}.json")

    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient="records", indent=True)

    print(f" Success! Saved {len(df)} records to:")
    print(f" - CSV: {csv_path}")
    print(f" - JSON: {json_path}")

if __name__ == "__main__":
    asyncio.run(main())