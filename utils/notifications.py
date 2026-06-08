import logging
import requests

logger = logging.getLogger("InsightScraper")

def send_discord_notification(webhook_url, job):
    """Sends a formatted embed message for a matching job to the specified Discord Webhook URL."""
    if not webhook_url:
        return
        
    title = job.get("title", "N/A")
    company = job.get("company", "N/A")
    location = job.get("location", "N/A")
    link = job.get("link", "#")
    source = job.get("source", "Unknown")
    date_posted = job.get("date_posted", "N/A")
    
    payload = {
        "embeds": [
            {
                "title": f"💼 New Job Match: {title}",
                "description": f"A new job matching your keywords has been posted on **{source}**.",
                "url": link,
                "color": 5814783,  # Beautiful deep blue color
                "fields": [
                    {"name": "🏢 Company", "value": company, "inline": True},
                    {"name": "📍 Location", "value": location, "inline": True},
                    {"name": "📅 Date Posted", "value": date_posted, "inline": True},
                    {"name": "🔍 Source", "value": source, "inline": True}
                ],
                "footer": {
                    "text": "InsightScraper automated notification system"
                }
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 204:
            logger.info(f"Discord notification sent successfully for job: '{title}' at '{company}'")
        else:
            logger.error(f"Failed to send Discord notification: Status {response.status_code}, Response: {response.text}")
    except Exception as e:
        logger.error(f"Error sending Discord notification: {e}")

def check_and_notify_matches(new_jobs, config):
    """
    Checks newly scraped jobs against target keywords.
    If a job matches, triggers a notification to Discord (if configured).
    """
    settings = config.get("settings", {})
    webhook_url = settings.get("discord_webhook_url", "")
    
    # If no webhook url is configured, do not bother filtering or logging notifications
    if not webhook_url:
        return
        
    keywords = settings.get("notification_keywords", [])
    if not keywords:
        logger.warning("Discord Webhook is configured, but notification_keywords is empty.")
        return

    logger.info(f"Filtering {len(new_jobs)} new jobs for notification keywords: {keywords}")
    
    for job in new_jobs:
        title = job.get("title", "").lower()
        company = job.get("company", "").lower()
        location = job.get("location", "").lower()
        
        # Check if any keyword matches title, company, or location
        is_match = False
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in title or kw_lower in company or kw_lower in location:
                is_match = True
                break
                
        if is_match:
            logger.info(f"🎯 Match found: '{job.get('title')}' at '{job.get('company')}'")
            send_discord_notification(webhook_url, job)
