"""Statistical analysis: Chi-square, Cohen's Kappa, descriptive stats."""

import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table
from scipy.stats import chi2_contingency
from sklearn.metrics import cohen_kappa_score

app = typer.Typer()
console = Console()


def load_dataset(filepath: str) -> pd.DataFrame:
    """Load tagged dataset."""
    return pd.read_csv(filepath)


def compute_descriptive_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute descriptive statistics."""
    stats = {
        'total_records': len(df),
        'sources': df['source'].value_counts().to_dict(),
        'temporal_periods': df['temporal_period'].value_counts().to_dict(),
        'resolution_status': df['resolution_status'].value_counts().to_dict(),
        'root_cause_categories': df['root_cause_category'].value_counts().to_dict()
    }
    # Add primary_codes only if column exists
    if 'primary_code' in df.columns:
        stats['primary_codes'] = df['primary_code'].value_counts().head(10).to_dict()
    return stats


def chi_square_test(df: pd.DataFrame, var1: str, var2: str) -> Dict[str, Any]:
    """
    Perform chi-square test for independence.
    
    Args:
        df: DataFrame
        var1: First categorical variable
        var2: Second categorical variable
        
    Returns:
        Dictionary with test results
    """
    contingency_table = pd.crosstab(df[var1], df[var2])
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    
    return {
        'chi2': chi2,
        'p_value': p_value,
        'degrees_of_freedom': dof,
        'significant': p_value < 0.05
    }


@app.command()
def analyze(
    input_file: str = typer.Argument(..., help="Path to tagged dataset CSV"),
    output_dir: str = typer.Option("4_analysis", help="Output directory")
):
    """Run statistical analysis on tagged dataset."""
    console.print("[bold]Running Statistical Analysis...[/bold]\\n")
    
    df = load_dataset(input_file)
    console.print(f"Loaded {len(df):,} records\\n")
    
    # Descriptive stats
    stats = compute_descriptive_stats(df)
    
    console.print("[bold cyan]Descriptive Statistics:[/bold cyan]\\n")
    console.print(f"Total Records: {stats['total_records']:,}")
    console.print(f"\\nSources: {json.dumps(stats['sources'], indent=2)}")
    console.print(f"\\nTemporal Periods: {json.dumps(stats['temporal_periods'], indent=2)}")
    
    # Chi-square test: primary_code vs resolution_status
    console.print("\\n[bold cyan]Chi-Square Test: primary_code ~ resolution_status[/bold cyan]")
    chi2_result = chi_square_test(df, 'primary_code', 'resolution_status')
    console.print(f"χ² = {chi2_result['chi2']:.2f}, p = {chi2_result['p_value']:.4f}")
    if chi2_result['significant']:
        console.print("[green]✓ Significant association (p < 0.05)[/green]")
    else:
        console.print("[yellow]✗ No significant association[/yellow]")
    
    # Save results
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / 'statistical_results.json', 'w') as f:
        json.dump({
            'descriptive_stats': stats,
            'chi_square_tests': {
                'primary_code_vs_resolution': chi2_result
            }
        }, f, indent=2)
    
    console.print(f"\\n[green]✓[/green] Results saved to {output_path}/statistical_results.json")


if __name__ == '__main__':
    app()
