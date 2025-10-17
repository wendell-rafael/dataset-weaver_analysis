"""Pytest configuration and fixtures."""

import pytest
import os


@pytest.fixture(scope="session")
def test_config():
    """Sample config for testing."""
    return {
        'sources': {
            'github': {
                'enabled': True,
                'repository': 'ServiceWeaver/weaver',
                'token_env': 'GITHUB_TOKEN',
                'per_page': 10,
                'max_items': 10
            }
        },
        'anonymization': {
            'salt_env_var': 'TEST_SALT'
        },
        'tagging': {
            'temporal_periods': {
                'pre_launch': '2023-03-01',
                'early_adoption': '2023-06-30',
                'plateau': '2024-06-30',
                'decline': '2024-12-31'
            }
        }
    }


@pytest.fixture(autouse=True)
def set_test_env():
    """Set test environment variables."""
    os.environ['TEST_SALT'] = 'test_salt_12345'
    os.environ['AW_SALT'] = 'test_salt_12345'
