import sqlite3
import pytest
from scrapers.engine import ScraperEngine
from scrapers.python_org import parse_python_org_jobs
from scrapers.remoteok import parse_remoteok_jobs
from scrapers.weworkremotely import parse_weworkremotely_jobs
from utils.database import init_db, save_jobs

@pytest.fixture
def mock_config():
    """provides a sample config for testing."""
    return {
        "selectors": {
            "job_card": ".test-card",
            "title": ".test-title",
            "company": ".test-company",
            "location": ".test-location"
        }
    }

@pytest.fixture
def sample_html():
    """provides a fake piece of HTML to test the parser."""
    return """
    <html>
        <body>
            <div class="test-card">
                <div class="test-title">Software Engineer</div>
                <div class="test-company">Tech Corp</div>
                <div class="test-location">New York</div>
            </div>
            <div class="test-card">
                <div class="test-title">Data Scientist</div>
                <div class="test-company">Data Inc</div>
                <div class="test-location">Remote</div>
            </div>
        </body>
    </html>
    """

def test_parse_data_correctly_extracts_fields(mock_config, sample_html):
    """test if the engine correctly extracts data from HTML using selectors."""
    engine = ScraperEngine(mock_config)
    results = engine.parse_data(sample_html)

    assert len(results) == 2
    assert results[0]['title'] == "Software Engineer"
    assert results[0]['company'] == "Tech Corp"
    assert results[1]['location'] == "Remote"

def test_parse_data_handles_missing_fields(mock_config):
    """Test if the engine handles messy HTML where some info is missing."""
    broken_html = '<div class="test-card"><div class="test-title">Lonely Job</div></div>'
    engine = ScraperEngine(mock_config)
    results = engine.parse_data(broken_html)

    assert results[0]['title'] == "Lonely Job"
    assert results[0]['company'] == "N/A"

def test_python_org_parser():
    """Test that python_org parser correctly extracts fields from Python.org HTML."""
    sample_python_org_html = """
    <ol class="list-recent-jobs">
        <li>
            <h2 class="listing-company">
                <span class="listing-company-name">
                    <span class="listing-new">New</span>
                    <a href="/jobs/8089/">Founding ML/Data Scientist</a><br>
                    MyDataValue
                </span>
                <span class="listing-location">
                    <a href="/jobs/location/remote/">Remote - London UK</a>
                </span>
            </h2>
            <span class="listing-posted">
                Posted: <time datetime="2026-06-03">03 June 2026</time>
            </span>
        </li>
    </ol>
    """
    results = parse_python_org_jobs(sample_python_org_html)
    assert len(results) == 1
    assert results[0]["title"] == "Founding ML/Data Scientist"
    assert results[0]["company"] == "MyDataValue"
    assert results[0]["location"] == "Remote - London UK"
    assert results[0]["link"] == "https://www.python.org/jobs/8089/"
    assert results[0]["date_posted"] == "03 June 2026"
    assert results[0]["source"] == "Python.org"

def test_weworkremotely_parser():
    """Test that weworkremotely parser correctly extracts fields from WeWorkRemotely HTML."""
    sample_wwr_html = """
    <section class="jobs">
        <article>
            <ul>
                <li class="new-listing-container feature">
                    <a class="listing-link--unlocked" href="/remote-jobs/a-team-senior-independent-ai-engineer-architect">
                        <div class="new-listing">
                            <h3 class="new-listing__header__title">
                                <span class="new-listing__header__title__text">Senior AI Architect</span>
                            </h3>
                            <div class="new-listing__header__icons">
                                <p class="new-listing__header__icons__date">New</p>
                            </div>
                            <p class="new-listing__company-name">A.Team</p>
                            <p class="new-listing__company-headquarters">NYC and TLV</p>
                            <div class="new-listing__categories">
                                <p class="new-listing__categories__category">Contract</p>
                                <p class="new-listing__categories__category">Anywhere in the World</p>
                            </div>
                        </div>
                    </a>
                </li>
                <li class="feature feature--ad">
                    <a class="listing-ad-url" href="/promoted">Promoted Ad</a>
                </li>
            </ul>
        </article>
    </section>
    """
    results = parse_weworkremotely_jobs(sample_wwr_html)
    assert len(results) == 1  # The ad should be skipped!
    assert results[0]["title"] == "Senior AI Architect"
    assert results[0]["company"] == "A.Team"
    assert results[0]["location"] == "NYC and TLV | Contract, Anywhere in the World"
    assert results[0]["link"] == "https://weworkremotely.com/remote-jobs/a-team-senior-independent-ai-engineer-architect"
    assert results[0]["date_posted"] == "Today"
    assert results[0]["source"] == "WeWorkRemotely"


def test_remoteok_parser():
    """Test that RemoteOK parser extracts title, company, location, and link from sample HTML."""
    sample_remoteok_html = """
    <div class="job list">
        <a class="preventLink" href="/remote-jobs/123-senior-python-engineer">
            <h2>Senior Python Engineer</h2>
        </a>
        <div class="company">Insight Labs</div>
        <div class="location">Remote - Europe</div>
        <div class="date">2 days ago</div>
    </div>
    """
    results = parse_remoteok_jobs(sample_remoteok_html)
    assert len(results) == 1
    assert results[0]["title"] == "Senior Python Engineer"
    assert results[0]["company"] == "Insight Labs"
    assert results[0]["location"] == "Remote - Europe"
    assert results[0]["link"] == "https://remoteok.com/remote-jobs/123-senior-python-engineer"
    assert results[0]["date_posted"] == "2 days ago"
    assert results[0]["source"] == "RemoteOK"


def test_database_init_migrates_missing_columns_and_skips_empty_links(tmp_path):
    """Older database schemas should be migrated and empty links should be ignored."""
    db_path = tmp_path / "jobs.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            link TEXT UNIQUE NOT NULL,
            date_posted TEXT,
            source TEXT NOT NULL,
            scraped_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

    init_db(db_path)

    conn = sqlite3.connect(db_path)
    columns = [row[1] for row in conn.execute("PRAGMA table_info(jobs)")]
    conn.close()

    assert "status" in columns
    assert "notes" in columns

    new_jobs = save_jobs([
        {"title": "Valid", "company": "Acme", "location": "Remote", "link": "https://example.com/job/1", "source": "RemoteOK"},
        {"title": "Missing Link", "company": "Acme", "location": "Remote", "link": "", "source": "RemoteOK"},
    ], db_path)

    assert len(new_jobs) == 1
    assert new_jobs[0]["title"] == "Valid"