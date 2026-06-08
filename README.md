# 🚀 InsightScraper

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

**InsightScraper** is a professional-grade automated ETL pipeline and interactive Job Application Tracker. It dynamically extracts programming job listings from multiple sources, deduplicates and stores them in a local SQLite database, filters them against alert keywords, and presents them in a premium Streamlit dashboard.

**Project Name** is a robust web scraping solution designed to extract [Type of Data] from [Target Site]. It handles dynamic content, bypasses common rate limits, and exports clean, structured data for analysis.

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

---

## 🛠️ Tech Stack

*   **Core:** Python 3.10+
*   **Scraping:** Playwright, BeautifulSoup4
*   **Data Science & UI:** Pandas, Streamlit, Plotly
*   **Storage:** SQLite
*   **Notifications:** Requests (Discord Webhook Integration)
*   **Testing:** Pytest

---

## ⚙️ Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/momcilosavic1234567-creator/InsightScraper.git
    cd InsightScraper
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv .venv
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Upgrade Pip and Install Requirements:**
    ```bash
    python -m pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    ```

4.  **Install Playwright Browser Dependencies:**
    ```bash
    playwright install chromium
    ```

---

## 🚀 How to Run

### Run Scraper Pipeline (ETL)
Execute the main scraper script to fetch, parse, deduplicate, save, and check notification triggers:
```bash
python main.py
```

### Launch the Streamlit Dashboard
Run the web application to explorer jobs, update application notes, and analyze hiring trends:
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your web browser.

### Run Unit Tests
Run pytest to verify parsing engines and configurations:
```bash
pytest
```

---

## 🤝 Contributing

Contributions are welcome! If you would like to submit improvements or suggest new sources:
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
