"""Tests for GitHub scraper."""

import pytest
from unittest.mock import Mock, patch
from scrapers.github_scraper import GitHubScraper


@pytest.fixture
def config():
    return {
        'sources': {
            'github': {
                'enabled': True,
                'repository': 'ServiceWeaver/weaver',
                'token_env': 'GITHUB_TOKEN',
                'endpoints': ['issues'],
                'per_page': 100,
                'max_items': 10,
                'rate_limit_sleep': 0,
                'include_closed': True,
                'include_comments': False
            }
        },
        'anonymization': {
            'salt_env_var': 'AW_SALT'
        },
        'languages': {
            'include': ['en'],
            'detect': False
        },
        'output': {
            'raw_data_dir': 'test_output',
            'timestamp_format': '%Y%m%d_%H%M%S'
        }
    }


def test_github_scraper_init(config):
    """Test GitHubScraper initialization."""
    scraper = GitHubScraper(config, dry_run=True)
    assert scraper.repo == 'ServiceWeaver/weaver'
    assert scraper.dry_run is True


def test_github_scraper_dry_run(config):
    """Test dry-run mode generates mock data."""
    scraper = GitHubScraper(config, dry_run=True)
    issues = scraper.collect_issues()
    
    assert len(issues) > 0
    assert all('github_issue' in issue['source'] for issue in issues)


def test_anonymize_author(config):
    """Test author anonymization."""
    scraper = GitHubScraper(config, dry_run=True)
    
    author1 = scraper.anonymize_author('user123')
    author2 = scraper.anonymize_author('user123')
    author3 = scraper.anonymize_author('user456')
    
    # Same input = same hash
    assert author1 == author2
    # Different input = different hash
    assert author1 != author3
    # Hash length is 16
    assert len(author1) == 16


def test_parse_issue(config):
    """Test issue parsing."""
    scraper = GitHubScraper(config, dry_run=True)
    
    mock_issue = {
        'number': 123,
        'title': 'Test Issue',
        'body': 'This is a test',
        'state': 'open',
        'created_at': '2023-03-01T00:00:00Z',
        'closed_at': None,
        'user': {'login': 'testuser'},
        'html_url': 'https://github.com/test/repo/issues/123',
        'labels': [{'name': 'bug'}],
        'comments': 0,
        'comments_url': 'https://api.github.com/test'
    }
    
    record = scraper._parse_issue(mock_issue)
    
    assert record['source'] == 'github_issue'
    assert record['data_id'] == 'gh_issue_123'
    assert 'Test Issue' in record['raw_text']
    assert record['metadata']['state'] == 'open'
