# InsightScraper



[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

HEAD
**InsightScraper** is a professional-grade automated ETL pipeline and interactive Job Application Tracker. It dynamically extracts programming job listings from multiple sources, deduplicates and stores them in a local SQLite database, filters them against alert keywords, and presents them in a premium Streamlit dashboard.

**Project Name** is a robust web scraping solution designed to extract data from targeted site. It handles dynamic content, bypasses common rate limits, and exports clean, structured data for analysis.

## ✨ Key Features

*   **Multi-Source Scraping:** Dynamically scrapes the official **Python.org Job Board** and remote programming roles from **WeWorkRemotely** using Playwright and BeautifulSoup4.
*   **Local Database Storage:** Saves jobs into a local SQLite database (`data/jobs.db`).
*   **Automatic Deduplication:** Uses unique URL constraints to filter out previously scraped listings.
*   **Interactive Application Tracker:** Persists user application states (`New`, `Favorite`, `Applied`, `Rejected`) and custom notes.
*   **Discord Webhook Notifications:** Automatically flags new jobs matching keywords of interest (e.g., *Django*, *Senior*, *Remote*) and posts details as rich embeds to a Discord channel.
*   **Premium Streamlit Dashboard:** Features a tabbed user interface:
    *   📋 **Job Explorer:** Browse cards of available jobs, filter by location/source/status, search, and update status/notes.
    *   🎯 **Application Tracker:** Edit tracking statuses and notes directly in a spreadsheet-like grid view.
    *   📊 **Insights & Analytics:** Dynamic Plotly visualizations of company distributions, sources, and application ratios.
    *   ⚙️ **Pipeline Config:** Adjust browser settings, timeouts, and Discord Webhook configurations directly inside the UI.
=======
**InsightScraper** is an automated ETL pipeline and interactive job application tracker for developers. It scrapes programming job listings from multiple sources, deduplicates and stores them in a local SQLite database, alerts you about roles matching your keywords via Discord, and presents everything in a clean Streamlit dashboard.
>>>>>>> 078e293 (Updated UI, more available jobs added using remoteok, fixed errors)

---

## Features

- **Multi-source scraping** — Pulls listings from the [Python.org Job Board](https://www.python.org/jobs/), [We Work Remotely](https://weworkremotely.com/), and [RemoteOK](https://remoteok.com/) using Playwright and BeautifulSoup4.
- **Automatic deduplication** — URL-based constraints prevent duplicate entries from accumulating across runs.
- **Application tracking** — Persists per-job statuses (`New`, `Favorite`, `Applied`, `Rejected`) and personal notes across sessions.
- **Discord notifications** — Flags new listings that match your alert keywords (e.g. *Django*, *Senior*, *Remote*) and posts them as rich embeds to a Discord channel.
- **Interactive dashboard** — A tabbed Streamlit UI with four views:
  - 📋 **Job Explorer** — Browse and filter job cards by location, source, or status; update notes inline.
  - 🎯 **Application Tracker** — Edit statuses and notes in a spreadsheet-style grid.
  - 📊 **Insights & Analytics** — Plotly charts showing company distributions, sources, and application ratios.
  - ⚙️ **Pipeline Config** — Adjust browser settings, timeouts, and notification keywords.
- **Browser behavior** — Uses User-Agent rotation but does not claim full rate-limit bypass, advanced backoff, or pacing.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.10+ |
| Scraping | Playwright, BeautifulSoup4 |
| Data & UI | Pandas, Streamlit, Plotly |
| Storage | SQLite |
| Notifications | Requests (Discord Webhooks) |
| Testing | Pytest |

---

## Project Structure

```
InsightScraper/
├── app.py              # Streamlit dashboard entry point
├── main.py             # ETL pipeline entry point
├── config.json         # Scraper and notification settings
├── requirements.txt
├── scrapers/
│   └── engine.py       # Playwright/BS4 scraping logic
├── utils/
│   ├── database.py     # SQLite init, save, and query helpers
│   ├── logger.py       # Logging setup
│   └── notifications.py# Discord webhook integration
├── data/               # SQLite database and CSV backups
├── logs/               # Pipeline run logs
└── tests/              # Pytest test suite
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/momcilosavic1234567-creator/InsightScraper.git
cd InsightScraper
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Install Playwright browser binaries

```bash
playwright install chromium
```

### 5. Configure the pipeline

Edit `config.json` to set your alert keywords. Manage your Discord webhook securely through the environment variable `DISCORD_WEBHOOK_URL` instead of storing it in `config.json`.

```json
{
  "settings": {
    "headless": true,
    "timeout": 30000,
    "notification_keywords": ["Django", "Senior", "Remote"]
  }
}
```

To enable Discord notifications, set the webhook URL in your environment:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

On Windows PowerShell:

```powershell
$env:DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
```

---

## Usage

### Run the scraper pipeline

Fetches new listings, deduplicates against the database, saves results, and triggers Discord alerts:

```bash
python main.py
```

### Launch the dashboard

```bash
streamlit run app.py
```

Then open **[http://localhost:8501](http://localhost:8501)** in your browser.

### Run the test suite

```bash
pytest
```

---

## Contributing

Contributions are welcome. To propose a change:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to your fork: `git push origin feature/your-feature`
5. Open a Pull Request

Please keep PRs focused — one feature or fix per PR makes review much easier.

---

## License

This project is licensed under the [MIT License](LICENSE).
