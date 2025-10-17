"""Generate visualizations for analysis."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import typer
from rich.console import Console

app = typer.Typer()
console = Console()

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.dpi'] = 300


def plot_timeline_by_category(df: pd.DataFrame, output_path: Path):
    """Plot issue frequency timeline by root cause category."""
    df['date'] = pd.to_datetime(df['timestamp']).dt.to_period('M')
    
    timeline_data = df.groupby(['date', 'root_cause_category']).size().unstack(fill_value=0)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    timeline_data.plot(kind='line', ax=ax, marker='o')
    
    ax.set_title('Issue Frequency Over Time by Root Cause Category', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Number of Issues', fontsize=12)
    ax.legend(title='Root Cause', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path / 'timeline_by_category.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_resolution_heatmap(df: pd.DataFrame, output_path: Path):
    """Plot resolution rates heatmap."""
    heatmap_data = pd.crosstab(
        df['root_cause_category'],
        df['resolution_status'],
        normalize='index'
    ) * 100
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='RdYlGn', ax=ax, cbar_kws={'label': '% of Issues'})
    
    ax.set_title('Resolution Status by Root Cause Category (%)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Resolution Status', fontsize=12)
    ax.set_ylabel('Root Cause Category', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_path / 'resolution_rates_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()


def plot_root_cause_matrix(df: pd.DataFrame, output_path: Path):
    """Plot root cause frequency matrix."""
    matrix_data = df.groupby(['root_cause_category', 'temporal_period']).size().unstack(fill_value=0)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(matrix_data, annot=True, fmt='d', cmap='Blues', ax=ax, cbar_kws={'label': 'Issue Count'})
    
    ax.set_title('Root Cause Distribution Across Temporal Periods', fontsize=14, fontweight='bold')
    ax.set_xlabel('Temporal Period', fontsize=12)
    ax.set_ylabel('Root Cause Category', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_path / 'root_cause_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()


@app.command()
def generate_all(
    input_file: str = typer.Argument(..., help="Path to tagged dataset CSV"),
    output_dir: str = typer.Option("4_analysis/visualizations", help="Output directory")
):
    """Generate all visualizations."""
    console.print("[bold]Generating Visualizations...[/bold]\\n")
    
    df = pd.read_csv(input_file)
    console.print(f"Loaded {len(df):,} records\\n")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    console.print("Generating timeline plot...")
    plot_timeline_by_category(df, output_path)
    
    console.print("Generating resolution heatmap...")
    plot_resolution_heatmap(df, output_path)
    
    console.print("Generating root cause matrix...")
    plot_root_cause_matrix(df, output_path)
    
    console.print(f"\\n[green]✓[/green] Visualizations saved to {output_path}/")


if __name__ == '__main__':
    app()
