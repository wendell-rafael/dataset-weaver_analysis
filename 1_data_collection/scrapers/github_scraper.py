"""GitHub scraper for issues, PRs, and discussions."""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_scraper import BaseScraper


class GitHubScraper(BaseScraper):
    """Scraper for GitHub repository data."""
    
    def __init__(self, config: Dict[str, Any], dry_run: bool = False):
        """
        Initialize GitHub scraper.
        
        Args:
            config: Configuration dictionary
            dry_run: If True, simulate scraping
        """
        super().__init__(config, dry_run)
        self.github_config = config['sources']['github']
        self.token = self._get_token()
        self.base_url = "https://api.github.com"
        self.repo = self.github_config['repository']
        
    def _get_token(self) -> Optional[str]:
        """Get GitHub token from environment."""
        import os
        token_env = self.github_config.get('token_env', 'GITHUB_TOKEN')
        token = os.getenv(token_env)
        if not token and not self.dry_run:
            self.logger.warning("GitHub token not found. Rate limits will be strict.")
        return token
    
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers with authentication."""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'ServiceWeaverResearchBot/1.0'
        }
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        return headers
    
    def collect_issues(self) -> List[Dict[str, Any]]:
        """
        Collect GitHub issues.
        
        Returns:
            List of issue records
        """
        self.logger.info(f"Collecting issues from {self.repo}...")
        
        url = f"{self.base_url}/repos/{self.repo}/issues"
        params = {
            'state': 'all' if self.github_config.get('include_closed', True) else 'open',
            'per_page': self.github_config.get('per_page', 100),
            'page': 1
        }
        
        issues = []
        max_items = self.github_config.get('max_items', 5000)
        
        while len(issues) < max_items:
            try:
                response = self.make_request(url, headers=self._get_headers(), params=params)
                
                if self.dry_run:
                    # Mock data for dry run
                    batch = self._generate_mock_issues(min(30, max_items - len(issues)))
                else:
                    batch = response.json()
                
                if not batch:
                    break
                
                for issue in batch:
                    # Skip pull requests (they appear in issues endpoint)
                    if 'pull_request' in issue:
                        continue
                    
                    record = self._parse_issue(issue)
                    
                    # Language filter
                    if self.config.get('languages', {}).get('detect', True):
                        lang = self.detect_language(record['raw_text'])
                        record['metadata']['language'] = lang
                        if not self.should_include_language(lang):
                            continue
                    
                    issues.append(record)
                    
                self.logger.info(f"Collected {len(issues)} issues so far...")
                
                # Check for next page
                if len(batch) < params['per_page']:
                    break
                    
                params['page'] += 1
                time.sleep(self.github_config.get('rate_limit_sleep', 1))
                
            except Exception as e:
                self.logger.error(f"Error collecting issues: {e}")
                self.errors.append({
                    'endpoint': 'issues',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                break
        
        self.logger.info(f"Collected {len(issues)} total issues")
        return issues
    
    def _parse_issue(self, issue: Dict) -> Dict[str, Any]:
        """
        Parse GitHub issue into standard format.
        
        Args:
            issue: Raw issue data from API
            
        Returns:
            Standardized record
        """
        # Combine title, body, and comments
        raw_text = f"{issue.get('title', '')}\\n\\n{issue.get('body', '') or ''}"
        
        # Collect comments if enabled
        if self.github_config.get('include_comments', True):
            comments = self._collect_comments(issue.get('comments_url', ''))
            if comments:
                raw_text += "\\n\\n--- Comments ---\\n" + "\\n".join(comments)
        
        return {
            'source': 'github_issue',
            'data_id': f"gh_issue_{issue['number']}",
            'timestamp': issue['created_at'],
            'raw_text': raw_text,
            'author_id': self.anonymize_author(issue.get('user', {}).get('login', '')),
            'url': issue['html_url'],
            'metadata': {
                'number': issue['number'],
                'state': issue['state'],
                'labels': [label['name'] for label in issue.get('labels', [])],
                'created_at': issue['created_at'],
                'closed_at': issue.get('closed_at'),
                'comments_count': issue.get('comments', 0),
                'reactions': issue.get('reactions', {})
            }
        }
    
    def _collect_comments(self, comments_url: str) -> List[str]:
        """
        Collect comments for an issue.
        
        Args:
            comments_url: API URL for comments
            
        Returns:
            List of comment texts
        """
        if self.dry_run:
            return ["Mock comment 1", "Mock comment 2"]
        
        try:
            response = self.make_request(comments_url, headers=self._get_headers())
            comments = response.json()
            return [c.get('body', '') for c in comments if c.get('body')]
        except Exception as e:
            self.logger.warning(f"Failed to collect comments: {e}")
            return []
    
    def collect_pull_requests(self) -> List[Dict[str, Any]]:
        """
        Collect GitHub pull requests.
        
        Returns:
            List of PR records
        """
        self.logger.info(f"Collecting pull requests from {self.repo}...")
        
        url = f"{self.base_url}/repos/{self.repo}/pulls"
        params = {
            'state': 'all',
            'per_page': self.github_config.get('per_page', 100),
            'page': 1
        }
        
        prs = []
        max_items = self.github_config.get('max_items', 5000)
        
        while len(prs) < max_items:
            try:
                response = self.make_request(url, headers=self._get_headers(), params=params)
                
                if self.dry_run:
                    batch = self._generate_mock_prs(min(30, max_items - len(prs)))
                else:
                    batch = response.json()
                
                if not batch:
                    break
                
                for pr in batch:
                    record = self._parse_pull_request(pr)
                    
                    # Language filter
                    if self.config.get('languages', {}).get('detect', True):
                        lang = self.detect_language(record['raw_text'])
                        record['metadata']['language'] = lang
                        if not self.should_include_language(lang):
                            continue
                    
                    prs.append(record)
                    
                self.logger.info(f"Collected {len(prs)} PRs so far...")
                
                if len(batch) < params['per_page']:
                    break
                    
                params['page'] += 1
                time.sleep(self.github_config.get('rate_limit_sleep', 1))
                
            except Exception as e:
                self.logger.error(f"Error collecting PRs: {e}")
                self.errors.append({
                    'endpoint': 'pull_requests',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                break
        
        self.logger.info(f"Collected {len(prs)} total pull requests")
        return prs
    
    def _parse_pull_request(self, pr: Dict) -> Dict[str, Any]:
        """Parse GitHub PR into standard format."""
        raw_text = f"{pr.get('title', '')}\\n\\n{pr.get('body', '') or ''}"
        
        return {
            'source': 'github_pr',
            'data_id': f"gh_pr_{pr['number']}",
            'timestamp': pr['created_at'],
            'raw_text': raw_text,
            'author_id': self.anonymize_author(pr.get('user', {}).get('login', '')),
            'url': pr['html_url'],
            'metadata': {
                'number': pr['number'],
                'state': pr['state'],
                'merged': pr.get('merged', False),
                'created_at': pr['created_at'],
                'merged_at': pr.get('merged_at'),
                'comments_count': pr.get('comments', 0),
                'review_comments_count': pr.get('review_comments', 0)
            }
        }
    
    def _generate_mock_issues(self, count: int) -> List[Dict]:
        """Generate mock issues for dry-run mode."""
        return [{
            'number': i + 1,
            'title': f'Mock Issue {i+1}',
            'body': 'This is a mock issue for testing purposes.',
            'state': 'open' if i % 2 == 0 else 'closed',
            'created_at': '2023-03-01T00:00:00Z',
            'closed_at': '2023-03-15T00:00:00Z' if i % 2 == 1 else None,
            'user': {'login': f'user{i}'},
            'html_url': f'https://github.com/mock/repo/issues/{i+1}',
            'labels': [{'name': 'bug'}] if i % 3 == 0 else [],
            'comments': i % 5,
            'comments_url': f'https://api.github.com/mock/comments/{i+1}'
        } for i in range(count)]
    
    def _generate_mock_prs(self, count: int) -> List[Dict]:
        """Generate mock PRs for dry-run mode."""
        return [{
            'number': i + 1,
            'title': f'Mock PR {i+1}',
            'body': 'This is a mock pull request.',
            'state': 'open' if i % 2 == 0 else 'closed',
            'merged': i % 2 == 1,
            'created_at': '2023-03-01T00:00:00Z',
            'merged_at': '2023-03-10T00:00:00Z' if i % 2 == 1 else None,
            'user': {'login': f'user{i}'},
            'html_url': f'https://github.com/mock/repo/pull/{i+1}',
            'comments': i % 3,
            'review_comments': i % 4
        } for i in range(count)]
    
    def collect(self) -> List[Dict[str, Any]]:
        """
        Main collection method.
        
        Returns:
            All collected records (issues + PRs)
        """
        all_data = []
        
        if 'issues' in self.github_config.get('endpoints', ['issues']):
            all_data.extend(self.collect_issues())
        
        if 'pull_requests' in self.github_config.get('endpoints', ['issues']):
            all_data.extend(self.collect_pull_requests())
        
        self.collected_items = all_data
        
        # Save raw data
        if all_data:
            self.save_raw_data('github_raw', all_data)
        
        return all_data


if __name__ == '__main__':
    import yaml
    import sys
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Check for dry-run flag
    dry_run = '--dry-run' in sys.argv
    
    scraper = GitHubScraper(config, dry_run=dry_run)
    data = scraper.collect()
    
    print(f"\\nCollection complete!")
    print(f"Total records: {len(data)}")
    print(f"Errors: {len(scraper.errors)}")
