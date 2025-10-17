"""Double-coding tool for inter-rater reliability testing."""

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table
from sklearn.metrics import cohen_kappa_score, confusion_matrix

app = typer.Typer()
console = Console()


def load_dataset(filepath: str) -> pd.DataFrame:
    """Load dataset from CSV."""
    return pd.DataFrame(pd.read_csv(filepath))


def export_pilot_subset(
    dataset_path: str,
    output_dir: str = "2_coding_methodology/pilot_study",
    percentage: float = 0.15,
    random_seed: int = 42
) -> None:
    """
    Export a random subset for pilot double-coding study.
    
    Args:
        dataset_path: Path to full dataset CSV
        output_dir: Output directory for pilot files
        percentage: Percentage of dataset to sample (default: 15%)
        random_seed: Random seed for reproducibility
    """
    console.print(f"[bold]Exporting pilot subset ({percentage*100:.0f}%)...[/bold]")
    
    # Load dataset
    df = load_dataset(dataset_path)
    total_records = len(df)
    
    console.print(f"Total records: {total_records:,}")
    
    # Sample subset
    random.seed(random_seed)
    sample_size = int(total_records * percentage)
    sample_indices = random.sample(range(total_records), min(sample_size, total_records))
    
    pilot_df = df.iloc[sample_indices].copy()
    pilot_df = pilot_df.reset_index(drop=True)
    
    # Add columns for coding
    pilot_df['primary_code_coder1'] = ''
    pilot_df['secondary_code_coder1'] = ''
    pilot_df['confidence_coder1'] = ''
    pilot_df['notes_coder1'] = ''
    
    pilot_df['primary_code_coder2'] = ''
    pilot_df['secondary_code_coder2'] = ''
    pilot_df['confidence_coder2'] = ''
    pilot_df['notes_coder2'] = ''
    
    # Save pilot files
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Coder 1 file (only coder1 columns visible)
    coder1_columns = [
        'source', 'data_id', 'timestamp', 'raw_text', 'url',
        'primary_code_coder1', 'secondary_code_coder1', 'confidence_coder1', 'notes_coder1'
    ]
    pilot_df[coder1_columns].to_csv(output_path / 'pilot_coder1.csv', index=False)
    
    # Coder 2 file (only coder2 columns visible)
    coder2_columns = [
        'source', 'data_id', 'timestamp', 'raw_text', 'url',
        'primary_code_coder2', 'secondary_code_coder2', 'confidence_coder2', 'notes_coder2'
    ]
    pilot_df[coder2_columns].to_csv(output_path / 'pilot_coder2.csv', index=False)
    
    # Master file (for comparison later)
    pilot_df.to_csv(output_path / 'pilot_master.csv', index=False)
    
    console.print(f"[green]✓[/green] Pilot files exported to {output_path}/")
    console.print(f"  - pilot_coder1.csv ({len(pilot_df)} records)")
    console.print(f"  - pilot_coder2.csv ({len(pilot_df)} records)")
    console.print(f"  - pilot_master.csv (master file)")
    
    console.print("\\n[yellow]Next steps:[/yellow]")
    console.print("1. Send pilot_coder1.csv to Coder 1")
    console.print("2. Send pilot_coder2.csv to Coder 2")
    console.print("3. Instruct coders to fill coding columns (blind to each other)")
    console.print("4. Collect completed files and run: python -m coding.double_code_tool --calculate-kappa")


def merge_coded_files(
    coder1_file: str,
    coder2_file: str,
    output_file: str = "2_coding_methodology/pilot_study/pilot_merged.csv"
) -> pd.DataFrame:
    """
    Merge coded files from two coders.
    
    Args:
        coder1_file: Path to coder 1's completed file
        coder2_file: Path to coder 2's completed file
        output_file: Path to save merged file
        
    Returns:
        Merged DataFrame
    """
    df1 = pd.read_csv(coder1_file)
    df2 = pd.read_csv(coder2_file)
    
    # Merge on data_id
    merged = df1.merge(
        df2[['data_id', 'primary_code_coder2', 'secondary_code_coder2', 'confidence_coder2', 'notes_coder2']],
        on='data_id',
        how='inner'
    )
    
    # Save merged file
    merged.to_csv(output_file, index=False)
    console.print(f"[green]✓[/green] Merged file saved to {output_file}")
    
    return merged


def calculate_cohen_kappa(
    coder1_file: str,
    coder2_file: str,
    output_dir: str = "2_coding_methodology/pilot_study"
) -> Dict[str, Any]:
    """
    Calculate Cohen's Kappa for inter-rater reliability.
    
    Args:
        coder1_file: Path to coder 1's completed file
        coder2_file: Path to coder 2's completed file
        output_dir: Output directory for results
        
    Returns:
        Dictionary with kappa statistics
    """
    console.print("[bold]Calculating Cohen's Kappa...[/bold]\\n")
    
    # Merge coded files
    merged = merge_coded_files(coder1_file, coder2_file, f"{output_dir}/pilot_merged.csv")
    
    # Extract primary codes
    coder1_codes = merged['primary_code_coder1'].fillna('').tolist()
    coder2_codes = merged['primary_code_coder2'].fillna('').tolist()
    
    # Remove empty codes
    valid_pairs = [(c1, c2) for c1, c2 in zip(coder1_codes, coder2_codes) if c1 and c2]
    
    if not valid_pairs:
        console.print("[red]Error:[/red] No valid coded pairs found.")
        return {}
    
    coder1_valid = [p[0] for p in valid_pairs]
    coder2_valid = [p[1] for p in valid_pairs]
    
    # Calculate kappa
    kappa = cohen_kappa_score(coder1_valid, coder2_valid)
    
    # Calculate agreement stats
    total_pairs = len(valid_pairs)
    agreements = sum(1 for c1, c2 in valid_pairs if c1 == c2)
    agreement_rate = agreements / total_pairs
    
    # Interpret kappa
    if kappa < 0:
        interpretation = "Poor (less than chance)"
    elif kappa < 0.20:
        interpretation = "Slight"
    elif kappa < 0.40:
        interpretation = "Fair"
    elif kappa < 0.60:
        interpretation = "Moderate"
    elif kappa < 0.80:
        interpretation = "Substantial"
    else:
        interpretation = "Almost Perfect"
    
    # Display results
    console.print("[bold green]Inter-Rater Reliability Results[/bold green]\\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Cohen's Kappa", f"{kappa:.3f}")
    table.add_row("Interpretation", interpretation)
    table.add_row("Raw Agreement", f"{agreement_rate:.1%} ({agreements}/{total_pairs})")
    table.add_row("Coded Pairs", str(total_pairs))
    
    console.print(table)
    
    # Check if kappa meets threshold
    target_kappa = 0.70
    if kappa >= target_kappa:
        console.print(f"\\n[green]✓ Kappa ≥ {target_kappa} - Acceptable reliability![/green]")
    else:
        console.print(f"\\n[red]✗ Kappa < {target_kappa} - Reliability below target.[/red]")
        console.print("[yellow]Recommended actions:[/yellow]")
        console.print("  1. Review disagreements")
        console.print("  2. Clarify codebook definitions")
        console.print("  3. Discuss edge cases")
        console.print("  4. Re-code problematic records")
    
    # Confusion matrix
    console.print("\\n[bold]Confusion Matrix (top disagreements):[/bold]\\n")
    
    unique_codes = sorted(set(coder1_valid + coder2_valid))
    cm = confusion_matrix(coder1_valid, coder2_valid, labels=unique_codes)
    
    # Find top disagreements
    disagreements = []
    for i, code1 in enumerate(unique_codes):
        for j, code2 in enumerate(unique_codes):
            if i != j and cm[i][j] > 0:
                disagreements.append((code1, code2, cm[i][j]))
    
    disagreements.sort(key=lambda x: x[2], reverse=True)
    
    if disagreements:
        dis_table = Table(show_header=True, header_style="bold magenta")
        dis_table.add_column("Coder 1", style="cyan")
        dis_table.add_column("Coder 2", style="yellow")
        dis_table.add_column("Count", style="red")
        
        for code1, code2, count in disagreements[:10]:
            dis_table.add_row(code1, code2, str(count))
        
        console.print(dis_table)
    else:
        console.print("[green]No disagreements found![/green]")
    
    # Save results
    results = {
        'cohen_kappa': kappa,
        'interpretation': interpretation,
        'agreement_rate': agreement_rate,
        'total_agreements': agreements,
        'total_pairs': total_pairs,
        'top_disagreements': disagreements[:10]
    }
    
    results_path = Path(output_dir) / 'cohen_kappa_results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    console.print(f"\\n[green]✓[/green] Results saved to {results_path}")
    
    # Export disagreements for review
    disagreement_records = merged[
        merged['primary_code_coder1'] != merged['primary_code_coder2']
    ].copy()
    
    if not disagreement_records.empty:
        dis_path = Path(output_dir) / 'disagreements_to_review.csv'
        disagreement_records.to_csv(dis_path, index=False)
        console.print(f"[green]✓[/green] Disagreements saved to {dis_path} ({len(disagreement_records)} records)")
    
    return results


@app.command()
def export_pilot(
    dataset: str = typer.Argument(..., help="Path to full dataset CSV"),
    percentage: float = typer.Option(0.15, help="Percentage to sample (0.0-1.0)"),
    output_dir: str = typer.Option("2_coding_methodology/pilot_study", help="Output directory"),
    seed: int = typer.Option(42, help="Random seed")
):
    """Export a pilot subset for double-coding."""
    export_pilot_subset(dataset, output_dir, percentage, seed)


@app.command()
def calculate_kappa(
    coder1: str = typer.Argument(..., help="Path to coder 1's completed CSV"),
    coder2: str = typer.Argument(..., help="Path to coder 2's completed CSV"),
    output_dir: str = typer.Option("2_coding_methodology/pilot_study", help="Output directory")
):
    """Calculate Cohen's Kappa from two coded files."""
    calculate_cohen_kappa(coder1, coder2, output_dir)


if __name__ == '__main__':
    app()
