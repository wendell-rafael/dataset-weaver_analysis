"""Tests for tag layering system."""

import pytest
import pandas as pd
from coding.tag_layering import assign_temporal_period, assign_root_cause_category


def test_assign_temporal_period():
    """Test temporal period assignment."""
    periods = {
        'pre_launch': '2023-03-01',
        'early_adoption': '2023-06-30',
        'plateau': '2024-06-30',
        'decline': '2024-12-31'
    }
    
    assert assign_temporal_period('2023-02-01T00:00:00Z', periods) == 'pre_launch'
    assert assign_temporal_period('2023-04-01T00:00:00Z', periods) == 'early_adoption'
    assert assign_temporal_period('2024-01-01T00:00:00Z', periods) == 'plateau'
    assert assign_temporal_period('2024-11-01T00:00:00Z', periods) == 'decline'
    assert assign_temporal_period('2025-01-01T00:00:00Z', periods) == 'post_discontinuation'


def test_assign_root_cause_category():
    """Test root cause category assignment."""
    assert assign_root_cause_category('DESIGN_ARCHITECTURE.RPC_PROBLEM') == 'architectural_limitation'
    assert assign_root_cause_category('COMMUNITY_ADOPTION.LACK_ENGAGEMENT') == 'community_mismatch'
    assert assign_root_cause_category('PERFORMANCE_SCALE.OVERHEAD') == 'technical_debt'
    assert assign_root_cause_category('USABILITY_DX.LEARNING_CURVE') == 'resource_constraint'
    assert assign_root_cause_category('') == 'unclear'
