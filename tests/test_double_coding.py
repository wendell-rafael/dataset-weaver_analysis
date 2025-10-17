"""Tests for double-coding tool."""

import pytest
import pandas as pd
from coding.double_code_tool import export_pilot_subset, calculate_cohen_kappa
import tempfile
import os


def test_export_pilot_subset(tmp_path):
    """Test exporting pilot subset."""
    # Create mock dataset
    data = {
        'source': ['github_issue'] * 100,
        'data_id': [f'id_{i}' for i in range(100)],
        'timestamp': ['2023-03-01T00:00:00Z'] * 100,
        'raw_text': [f'Text {i}' for i in range(100)],
        'url': [f'https://example.com/{i}' for i in range(100)]
    }
    df = pd.DataFrame(data)
    
    dataset_path = tmp_path / 'dataset.csv'
    df.to_csv(dataset_path, index=False)
    
    output_dir = tmp_path / 'pilot'
    
    # Export subset
    export_pilot_subset(str(dataset_path), str(output_dir), percentage=0.15, random_seed=42)
    
    # Check files exist
    assert (output_dir / 'pilot_coder1.csv').exists()
    assert (output_dir / 'pilot_coder2.csv').exists()
    assert (output_dir / 'pilot_master.csv').exists()
    
    # Check subset size
    coder1_df = pd.read_csv(output_dir / 'pilot_coder1.csv')
    assert len(coder1_df) == 15  # 15% of 100


def test_cohen_kappa_perfect_agreement():
    """Test Cohen's Kappa with perfect agreement."""
    from sklearn.metrics import cohen_kappa_score
    
    codes1 = ['A', 'B', 'C', 'A', 'B']
    codes2 = ['A', 'B', 'C', 'A', 'B']
    
    kappa = cohen_kappa_score(codes1, codes2)
    
    assert kappa == 1.0  # Perfect agreement


def test_cohen_kappa_no_agreement():
    """Test Cohen's Kappa with no agreement."""
    from sklearn.metrics import cohen_kappa_score
    
    codes1 = ['A', 'A', 'A', 'A', 'A']
    codes2 = ['B', 'B', 'B', 'B', 'B']
    
    kappa = cohen_kappa_score(codes1, codes2)
    
    assert kappa < 0.5  # Poor agreement
