import logging
import os

def setup_logger():
    """Sets up a logger that saves to both a file and the console."""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('InsightScraper')
    logger.setLevel(logging.INFO)

    # Format for logs: Time - Name - Level - Message
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler
    fh = logging.FileHandler('logs/scraper.log')
    fh.setFormatter(formatter)

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger