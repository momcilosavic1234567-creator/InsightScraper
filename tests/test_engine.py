import pytest
from scrapers.engine import ScraperEngine

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
    """test if the engine correctly extracts data from HTML."""
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