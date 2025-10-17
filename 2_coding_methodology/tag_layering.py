"""Tag layering system: temporal, resolution, root cause categories."""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import typer
import yaml
from rich.console import Console
from rich.progress import track

app = typer.Typer()
console = Console()


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def parse_timestamp(ts: str) -> datetime:
    """Parse timestamp string to datetime."""
    try:
        # Try ISO format first
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        # Remove timezone info to make it naive
        return dt.replace(tzinfo=None)
    except:
        try:
            # Try common formats
            return datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')
        except:
            try:
                # Try simple date format
                return datetime.strptime(ts, '%Y-%m-%d')
            except:
                return datetime.now()


def assign_temporal_period(timestamp: str, periods: Dict[str, str]) -> str:
    """
    Assign temporal period based on timestamp.
    
    Args:
        timestamp: ISO timestamp string
        periods: Dictionary of period boundaries from config
        
    Returns:
        Period name (pre_launch, early_adoption, plateau, decline, post_discontinuation)
    """
    dt = parse_timestamp(timestamp)
    
    pre_launch = parse_timestamp(periods.get('pre_launch', '2023-03-01'))
    early_adoption = parse_timestamp(periods.get('early_adoption', '2023-06-30'))
    plateau = parse_timestamp(periods.get('plateau', '2024-06-30'))
    decline = parse_timestamp(periods.get('decline', '2024-12-31'))
    
    if dt < pre_launch:
        return 'pre_launch'
    elif dt < early_adoption:
        return 'early_adoption'
    elif dt < plateau:
        return 'plateau'
    elif dt < decline:
        return 'decline'
    else:
        return 'post_discontinuation'


def assign_resolution_status(row: pd.Series, config: Dict[str, Any]) -> str:
    """
    Assign resolution status based on metadata heuristics.
    
    Args:
        row: DataFrame row
        config: Configuration dictionary
        
    Returns:
        Resolution status (fixed, acknowledged_not_fixed, wontfix_explicit, 
                          abandoned, duplicate, user_error, unknown)
    """
    source = row.get('source', '')
    metadata = row.get('metadata', '{}')
    
    # Parse metadata (may be JSON string)
    if isinstance(metadata, str):
        import json
        try:
            metadata = json.loads(metadata.replace("'", '"'))
        except:
            metadata = {}
    
    # GitHub-specific resolution
    if 'github' in source:
        state = metadata.get('state', 'unknown')
        labels = metadata.get('labels', [])
        
        if isinstance(labels, str):
            labels = [labels]
        
        # Check for explicit wontfix
        if any(label.lower() in ['wontfix', "won't fix"] for label in labels):
            return 'wontfix_explicit'
        
        # Check for duplicate
        if any(label.lower() == 'duplicate' for label in labels):
            return 'duplicate'
        
        # Check if merged (PRs)
        if metadata.get('merged', False):
            return 'fixed'
        
        # Check if closed with resolution
        if state == 'closed':
            closed_at = metadata.get('closed_at')
            if closed_at:
                return 'acknowledged_not_fixed'
        
        # Check for abandoned (no activity for threshold days)
        created_at = metadata.get('created_at')
        if created_at and state == 'open':
            days_open = (datetime.now() - parse_timestamp(created_at)).days
            threshold = config.get('tagging', {}).get('resolution_heuristics', {}).get('abandoned_threshold_days', 90)
            if days_open > threshold:
                return 'abandoned'
        
        return 'unknown'
    
    # Stack Overflow-specific
    elif 'stackoverflow' in source:
        is_answered = metadata.get('is_answered', False)
        if is_answered:
            return 'fixed'
        
        # Check age
        created_at = metadata.get('timestamp') or row.get('timestamp')
        if created_at:
            days_old = (datetime.now() - parse_timestamp(created_at)).days
            if days_old > 90:
                return 'abandoned'
        
        return 'unknown'
    
    # Reddit/HN/Groups - harder to determine resolution
    else:
        # Check for high engagement as proxy for "acknowledged"
        comments = metadata.get('num_comments', 0) or metadata.get('comments_count', 0)
        if comments > 5:
            return 'acknowledged_not_fixed'
        
        return 'unknown'


def assign_root_cause_category(primary_code: str, secondary_code: str = '') -> str:
    """
    Assign root cause category based on primary/secondary codes.
    
    Args:
        primary_code: Primary thematic code
        secondary_code: Secondary thematic code (optional)
        
    Returns:
        Root cause category (architectural_limitation, resource_constraint, 
                            community_mismatch, technical_debt, unclear)
    """
    if not primary_code or primary_code == '':
        return 'unclear'
    
    primary_upper = primary_code.upper()
    
    # Architectural limitation
    if 'DESIGN_ARCHITECTURE' in primary_upper:
        return 'architectural_limitation'
    
    # Community mismatch
    if 'COMMUNITY_ADOPTION' in primary_upper:
        return 'community_mismatch'
    
    # Technical debt (performance/scale + ecosystem issues)
    if 'PERFORMANCE_SCALE' in primary_upper or 'ECOSYSTEM_INTEROP' in primary_upper:
        return 'technical_debt'
    
    # Resource constraint (inferred from slow responses, DX issues)
    if 'USABILITY_DX' in primary_upper:
        return 'resource_constraint'  # Insufficient investment in DX
    
    # Check secondary code as well
    if secondary_code:
        secondary_upper = secondary_code.upper()
        if 'ECOSYSTEM' in secondary_upper:
            return 'technical_debt'
    
    return 'unclear'


def generate_tag_reasoning(row: pd.Series, temporal: str, resolution: str, root_cause: str) -> str:
    """
    Generate reasoning text for tag assignments.
    
    Args:
        row: DataFrame row
        temporal: Temporal period assigned
        resolution: Resolution status assigned
        root_cause: Root cause category assigned
        
    Returns:
        Reasoning string (1-2 sentences)
    """
    reasons = []
    
    # Temporal reasoning
    timestamp = row.get('timestamp', 'unknown')
    reasons.append(f"Temporal: {temporal} based on {timestamp[:10]}")
    
    # Resolution reasoning
    source = row.get('source', '')
    if 'github' in source:
        metadata = row.get('metadata', {})
        if isinstance(metadata, str):
            import json
            try:
                metadata = json.loads(metadata.replace("'", '"'))
            except:
                metadata = {}
        
        state = metadata.get('state', 'unknown')
        labels = metadata.get('labels', [])
        reasons.append(f"Resolution: {resolution} (state={state}, labels={labels})")
    else:
        reasons.append(f"Resolution: {resolution} (heuristic)")
    
    # Root cause reasoning
    primary_code = row.get('primary_code', '')
    reasons.append(f"Root cause: {root_cause} (code={primary_code})")
    
    return ". ".join(reasons)


@app.command()
def apply_tags(
    input_file: str = typer.Argument(..., help="Path to coded dataset CSV"),
    output_file: str = typer.Option("3_processed_data/tagged_dataset.csv", help="Output path"),
    config_path: str = typer.Option("config.yaml", help="Config file path")
):
    """
    Apply tag layering system to coded dataset.
    
    Adds columns:
    - temporal_period
    - resolution_status
    - root_cause_category
    - tag_reasoning
    """
    console.print("[bold]Applying tag layering system...[/bold]\\n")
    
    # Load config
    config = load_config(config_path)
    
    # Load coded dataset
    df = pd.read_csv(input_file)
    console.print(f"Loaded {len(df):,} records from {input_file}")
    
    # Apply tags
    temporal_periods = config.get('tagging', {}).get('temporal_periods', {})
    
    df['temporal_period'] = ''
    df['resolution_status'] = ''
    df['root_cause_category'] = ''
    df['tag_reasoning'] = ''
    
    for idx in track(range(len(df)), description="Tagging records..."):
        row = df.iloc[idx]
        
        # Temporal period
        temporal = assign_temporal_period(row.get('timestamp', ''), temporal_periods)
        df.at[idx, 'temporal_period'] = temporal
        
        # Resolution status
        resolution = assign_resolution_status(row, config)
        df.at[idx, 'resolution_status'] = resolution
        
        # Root cause category
        root_cause = assign_root_cause_category(
            row.get('primary_code', ''),
            row.get('secondary_code', '')
        )
        df.at[idx, 'root_cause_category'] = root_cause
        
        # Reasoning
        reasoning = generate_tag_reasoning(row, temporal, resolution, root_cause)
        df.at[idx, 'tag_reasoning'] = reasoning
    
    # Save tagged dataset
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    console.print(f"\\n[green]✓[/green] Tagged dataset saved to {output_path}")
    
    # Display summary statistics
    console.print("\\n[bold]Tagging Summary:[/bold]\\n")
    
    console.print("[cyan]Temporal Periods:[/cyan]")
    print(df['temporal_period'].value_counts().to_string())
    
    console.print("\\n[cyan]Resolution Status:[/cyan]")
    print(df['resolution_status'].value_counts().to_string())
    
    console.print("\\n[cyan]Root Cause Categories:[/cyan]")
    print(df['root_cause_category'].value_counts().to_string())


if __name__ == '__main__':
    app()
