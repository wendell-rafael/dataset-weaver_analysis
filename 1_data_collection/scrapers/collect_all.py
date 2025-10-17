"""Orchestrator to run all scrapers and generate collection report."""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Handle both relative and absolute imports
try:
    from .github_scraper import GitHubScraper
    from .reddit_scraper import RedditScraper
    from .stackoverflow_scraper import StackOverflowScraper
    from .hackernews_scraper import HackerNewsScraper
    from .google_groups_scraper import GoogleGroupsScraper
except ImportError:
    # Running as script - add current directory to path
    sys.path.insert(0, str(Path(__file__).parent))
    from github_scraper import GitHubScraper
    from reddit_scraper import RedditScraper
    from stackoverflow_scraper import StackOverflowScraper
    from hackernews_scraper import HackerNewsScraper
    from google_groups_scraper import GoogleGroupsScraper


console = Console()


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def run_scraper(scraper_class, config: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """
    Run a scraper and collect stats.
    
    Args:
        scraper_class: Scraper class to instantiate
        config: Configuration dictionary
        dry_run: Dry-run mode
        
    Returns:
        Dictionary with collection stats
    """
    scraper_name = scraper_class.__name__
    console.print(f"\\n[bold blue]Running {scraper_name}...[/bold blue]")
    
    start_time = time.time()
    
    try:
        scraper = scraper_class(config, dry_run=dry_run)
        data = scraper.collect()
        
        elapsed = time.time() - start_time
        
        stats = {
            'scraper': scraper_name,
            'status': 'success',
            'records_collected': len(data),
            'errors': len(scraper.errors),
            'elapsed_seconds': round(elapsed, 2),
            'error_details': scraper.errors[:5]  # Keep first 5 errors
        }
        
        console.print(f"[green]✓[/green] Collected {len(data)} records in {elapsed:.2f}s")
        
        return stats
        
    except Exception as e:
        elapsed = time.time() - start_time
        console.print(f"[red]✗[/red] Failed: {e}")
        
        return {
            'scraper': scraper_name,
            'status': 'failed',
            'records_collected': 0,
            'errors': 1,
            'elapsed_seconds': round(elapsed, 2),
            'error_details': [{'error': str(e), 'timestamp': datetime.now().isoformat()}]
        }


def generate_report(stats_list: List[Dict[str, Any]], config: Dict[str, Any], 
                   dry_run: bool = False) -> str:
    """
    Generate collection report in Markdown.
    
    Args:
        stats_list: List of scraper statistics
        config: Configuration dictionary
        dry_run: Dry-run mode
        
    Returns:
        Markdown report content
    """
    total_records = sum(s['records_collected'] for s in stats_list)
    total_errors = sum(s['errors'] for s in stats_list)
    total_time = sum(s['elapsed_seconds'] for s in stats_list)
    
    report = f"""# Service Weaver Data Collection Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Dataset Version:** {config.get('dataset_version', 'v1.0')}  
**Mode:** {'DRY RUN' if dry_run else 'PRODUCTION'}  
**Date Range:** {config['date_range']['start']} to {config['date_range']['end']}

## Summary

- **Total Records Collected:** {total_records:,}
- **Total Errors:** {total_errors}
- **Total Execution Time:** {total_time:.2f}s

## Collection Details

| Source | Status | Records | Errors | Time (s) |
|--------|--------|---------|--------|----------|
"""
    
    for stats in stats_list:
        status_icon = '✓' if stats['status'] == 'success' else '✗'
        report += f"| {stats['scraper']} | {status_icon} {stats['status']} | {stats['records_collected']:,} | {stats['errors']} | {stats['elapsed_seconds']:.2f} |\n"
    
    report += f"""
## Configuration Used

```yaml
date_range:
  start: {config['date_range']['start']}
  end: {config['date_range']['end']}

sources:
"""
    
    for source, source_config in config.get('sources', {}).items():
        if source_config.get('enabled', True):
            report += f"  {source}: enabled\n"
    
    report += "```\n\n"
    
    # Add error details if any
    if total_errors > 0:
        report += "## Error Details\n\n"
        for stats in stats_list:
            if stats['errors'] > 0:
                report += f"### {stats['scraper']}\n\n"
                for error in stats['error_details']:
                    report += f"- **{error.get('timestamp', 'N/A')}:** {error.get('error', 'Unknown error')}\\n"
                report += "\n"
    
    report += """## Next Steps

1. Review error details and re-run failed scrapers if needed
2. Run deduplication: `make deduplicate`
3. Begin thematic coding: `make pilot_code`
4. Generate preliminary statistics: `make analyze`

---
*Generated by Service Weaver Analysis Pipeline*
"""
    
    return report


def main():
    """Main orchestrator function."""
    console.print("[bold]Service Weaver Data Collection Pipeline[/bold]\\n")
    
    # Parse arguments
    config_path = 'config.yaml'
    dry_run = '--dry-run' in sys.argv
    
    if '--config' in sys.argv:
        idx = sys.argv.index('--config')
        config_path = sys.argv[idx + 1]
    
    # Load config
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Config file '{config_path}' not found.")
        console.print("Run 'make setup' to create from example.")
        sys.exit(1)
    
    if dry_run:
        console.print("[yellow]⚠ Running in DRY-RUN mode (no actual API calls)[/yellow]\\n")
    
    # Determine which scrapers to run
    sources = config.get('sources', {})
    scrapers = []
    
    if sources.get('github', {}).get('enabled', True):
        scrapers.append(GitHubScraper)
    
    if sources.get('stackoverflow', {}).get('enabled', True):
        scrapers.append(StackOverflowScraper)
    
    if sources.get('reddit', {}).get('enabled', True):
        scrapers.append(RedditScraper)
    
    if sources.get('hackernews', {}).get('enabled', True):
        scrapers.append(HackerNewsScraper)
    
    if sources.get('google_groups', {}).get('enabled', False):
        scrapers.append(GoogleGroupsScraper)
    
    if not scrapers:
        console.print("[red]No scrapers enabled in config.[/red]")
        sys.exit(1)
    
    # Run scrapers
    stats_list = []
    
    for scraper_class in scrapers:
        stats = run_scraper(scraper_class, config, dry_run=dry_run)
        stats_list.append(stats)
    
    # Generate report
    console.print("\\n[bold blue]Generating collection report...[/bold blue]")
    report = generate_report(stats_list, config, dry_run=dry_run)
    
    # Save report
    report_path = Path('1_data_collection/collection_report.md')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    
    console.print(f"[green]✓[/green] Report saved to {report_path}")
    
    # Save stats as JSON
    stats_path = Path('1_data_collection/collection_stats.json')
    stats_path.write_text(json.dumps(stats_list, indent=2), encoding='utf-8')
    
    console.print(f"[green]✓[/green] Stats saved to {stats_path}")
    
    # Summary
    total_records = sum(s['records_collected'] for s in stats_list)
    total_errors = sum(s['errors'] for s in stats_list)
    
    console.print(f"\\n[bold green]Collection Complete![/bold green]")
    console.print(f"Total records: {total_records:,}")
    console.print(f"Total errors: {total_errors}")
    
    if total_errors > 0:
        console.print(f"\\n[yellow]⚠ Some errors occurred. Check {report_path} for details.[/yellow]")


if __name__ == '__main__':
    main()
