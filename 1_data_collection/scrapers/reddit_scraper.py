"""Reddit scraper for posts and comments."""

import time
from datetime import datetime
from typing import Any, Dict, List

from .base_scraper import BaseScraper


class RedditScraper(BaseScraper):
    """Scraper for Reddit posts and comments."""
    
    def __init__(self, config: Dict[str, Any], dry_run: bool = False):
        """
        Initialize Reddit scraper.
        
        Args:
            config: Configuration dictionary
            dry_run: If True, simulate scraping
        """
        super().__init__(config, dry_run)
        self.reddit_config = config['sources']['reddit']
        self.reddit = self._init_reddit_client()
        
    def _init_reddit_client(self):
        """Initialize Reddit API client (PRAW)."""
        if self.dry_run:
            return None
        
        import os
        import praw
        
        client_id = os.getenv(self.reddit_config.get('client_id_env', 'REDDIT_CLIENT_ID'))
        client_secret = os.getenv(self.reddit_config.get('client_secret_env', 'REDDIT_CLIENT_SECRET'))
        user_agent = self.reddit_config.get('user_agent', 'ServiceWeaverResearchBot/1.0')
        
        if not client_id or not client_secret:
            self.logger.warning("Reddit credentials not found. Using dry-run mode.")
            return None
        
        return praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    
    def collect(self) -> List[Dict[str, Any]]:
        """
        Collect Reddit posts and comments.
        
        Returns:
            List of post/comment records
        """
        all_data = []
        
        subreddits = self.reddit_config.get('subreddits', ['golang', 'microservices'])
        keywords = self.reddit_config.get('keywords', ['service weaver', 'serviceweaver'])
        max_items_per_sub = self.reddit_config.get('max_items_per_sub', 500)
        
        for subreddit_name in subreddits:
            self.logger.info(f"Collecting from r/{subreddit_name}...")
            
            try:
                posts = self._collect_from_subreddit(
                    subreddit_name, 
                    keywords, 
                    max_items_per_sub
                )
                all_data.extend(posts)
                self.logger.info(f"Collected {len(posts)} posts from r/{subreddit_name}")
                
            except Exception as e:
                self.logger.error(f"Error collecting from r/{subreddit_name}: {e}")
                self.errors.append({
                    'source': 'reddit',
                    'subreddit': subreddit_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        self.collected_items = all_data
        
        # Save raw data
        if all_data:
            self.save_raw_data('reddit_raw', all_data)
        
        return all_data
    
    def _collect_from_subreddit(self, subreddit_name: str, 
                                keywords: List[str], 
                                max_items: int) -> List[Dict[str, Any]]:
        """
        Collect posts from a specific subreddit.
        
        Args:
            subreddit_name: Name of subreddit
            keywords: Keywords to search for
            max_items: Maximum items to collect
            
        Returns:
            List of post records
        """
        if self.dry_run or not self.reddit:
            return self._generate_mock_posts(subreddit_name, min(max_items, 20))
        
        posts = []
        subreddit = self.reddit.subreddit(subreddit_name)
        
        # Search for each keyword
        for keyword in keywords:
            try:
                search_results = subreddit.search(
                    keyword, 
                    limit=max_items // len(keywords),
                    time_filter='all',
                    sort='relevance'
                )
                
                for submission in search_results:
                    record = self._parse_submission(submission, subreddit_name)
                    
                    # Language filter
                    if self.config.get('languages', {}).get('detect', True):
                        lang = self.detect_language(record['raw_text'])
                        record['metadata']['language'] = lang
                        if not self.should_include_language(lang):
                            continue
                    
                    posts.append(record)
                    
                    if len(posts) >= max_items:
                        break
                
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                self.logger.warning(f"Error searching '{keyword}': {e}")
                continue
        
        return posts
    
    def _parse_submission(self, submission, subreddit_name: str) -> Dict[str, Any]:
        """
        Parse Reddit submission into standard format.
        
        Args:
            submission: PRAW submission object
            subreddit_name: Name of subreddit
            
        Returns:
            Standardized record
        """
        # Combine title, selftext, and top comments
        raw_text = f"{submission.title}\\n\\n{submission.selftext}"
        
        # Collect top comments
        try:
            submission.comments.replace_more(limit=0)
            top_comments = submission.comments.list()[:10]
            if top_comments:
                comment_texts = [c.body for c in top_comments if hasattr(c, 'body')]
                raw_text += "\\n\\n--- Top Comments ---\\n" + "\\n".join(comment_texts)
        except Exception as e:
            self.logger.warning(f"Failed to load comments: {e}")
        
        return {
            'source': 'reddit',
            'data_id': f"reddit_{submission.id}",
            'timestamp': datetime.fromtimestamp(submission.created_utc).isoformat(),
            'raw_text': raw_text,
            'author_id': self.anonymize_author(str(submission.author) if submission.author else 'deleted'),
            'url': f"https://reddit.com{submission.permalink}",
            'metadata': {
                'subreddit': subreddit_name,
                'score': submission.score,
                'upvote_ratio': submission.upvote_ratio,
                'num_comments': submission.num_comments,
                'flair': submission.link_flair_text,
                'created_utc': submission.created_utc
            }
        }
    
    def _generate_mock_posts(self, subreddit_name: str, count: int) -> List[Dict[str, Any]]:
        """Generate mock Reddit posts for dry-run mode."""
        return [{
            'source': 'reddit',
            'data_id': f'reddit_mock_{i}',
            'timestamp': '2023-06-01T00:00:00Z',
            'raw_text': f'Mock Reddit post {i+1} about Service Weaver\\n\\nThis is a test post.',
            'author_id': self.anonymize_author(f'user{i}'),
            'url': f'https://reddit.com/r/{subreddit_name}/mock_{i}',
            'metadata': {
                'subreddit': subreddit_name,
                'score': 10 + i,
                'upvote_ratio': 0.85,
                'num_comments': i % 10,
                'flair': 'Discussion' if i % 2 == 0 else 'Question',
                'language': 'en'
            }
        } for i in range(count)]


if __name__ == '__main__':
    import yaml
    import sys
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    dry_run = '--dry-run' in sys.argv
    
    scraper = RedditScraper(config, dry_run=dry_run)
    data = scraper.collect()
    
    print(f"\\nCollection complete!")
    print(f"Total records: {len(data)}")
