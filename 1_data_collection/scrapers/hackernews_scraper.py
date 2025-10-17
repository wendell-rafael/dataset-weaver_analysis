"""Hacker News scraper for posts and comments."""

import time
from datetime import datetime
from typing import Any, Dict, List

from .base_scraper import BaseScraper


class HackerNewsScraper(BaseScraper):
    """Scraper for Hacker News posts and comments."""
    
    def __init__(self, config: Dict[str, Any], dry_run: bool = False):
        """
        Initialize Hacker News scraper.
        
        Args:
            config: Configuration dictionary
            dry_run: If True, simulate scraping
        """
        super().__init__(config, dry_run)
        self.hn_config = config['sources']['hackernews']
        self.api_base = self.hn_config.get('api_base', 'https://hacker-news.firebaseio.com/v0')
        
    def collect(self) -> List[Dict[str, Any]]:
        """
        Collect Hacker News posts and comments.
        
        Returns:
            List of post/comment records
        """
        all_data = []
        
        keywords = self.hn_config.get('keywords', ['service weaver', 'serviceweaver'])
        max_items = self.hn_config.get('max_items', 500)
        
        self.logger.info("Collecting from Hacker News...")
        
        if self.dry_run:
            all_data = self._generate_mock_posts(min(max_items, 20))
        else:
            # Search using Algolia HN Search API
            for keyword in keywords:
                try:
                    posts = self._search_stories(keyword, max_items // len(keywords))
                    all_data.extend(posts)
                    self.logger.info(f"Collected {len(posts)} stories for '{keyword}'")
                except Exception as e:
                    self.logger.error(f"Error searching '{keyword}': {e}")
                    self.errors.append({
                        'source': 'hackernews',
                        'keyword': keyword,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        self.collected_items = all_data
        
        # Save raw data
        if all_data:
            self.save_raw_data('hackernews_raw', all_data)
        
        return all_data
    
    def _search_stories(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """
        Search Hacker News stories using Algolia API.
        
        Args:
            query: Search query
            max_items: Maximum items to collect
            
        Returns:
            List of story records
        """
        stories = []
        page = 0
        
        # Use Algolia HN Search API
        algolia_base = "https://hn.algolia.com/api/v1"
        
        while len(stories) < max_items:
            url = f"{algolia_base}/search"
            params = {
                'query': query,
                'tags': 'story',
                'page': page,
                'hitsPerPage': 50
            }
            
            try:
                response = self.make_request(url, params=params)
                data = response.json()
                
                hits = data.get('hits', [])
                if not hits:
                    break
                
                for hit in hits:
                    record = self._parse_story(hit)
                    
                    # Language filter
                    if self.config.get('languages', {}).get('detect', True):
                        lang = self.detect_language(record['raw_text'])
                        record['metadata']['language'] = lang
                        if not self.should_include_language(lang):
                            continue
                    
                    stories.append(record)
                    
                    # Collect top comments
                    if hit.get('num_comments', 0) > 0:
                        comments = self._collect_comments(hit['objectID'])
                        stories.extend(comments)
                
                # Check if we have more pages
                if page >= data.get('nbPages', 0) - 1:
                    break
                
                page += 1
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"Error fetching stories: {e}")
                break
        
        return stories
    
    def _parse_story(self, hit: Dict) -> Dict[str, Any]:
        """
        Parse Hacker News story into standard format.
        
        Args:
            hit: Raw story data from Algolia API
            
        Returns:
            Standardized record
        """
        title = hit.get('title', '')
        text = hit.get('story_text', '') or hit.get('text', '') or ''
        url_from_story = hit.get('url', '')
        
        raw_text = f"{title}\\n\\n{text}"
        if url_from_story:
            raw_text += f"\\n\\nURL: {url_from_story}"
        
        return {
            'source': 'hackernews_story',
            'data_id': f"hn_story_{hit['objectID']}",
            'timestamp': hit.get('created_at', ''),
            'raw_text': raw_text,
            'author_id': self.anonymize_author(hit.get('author', '')),
            'url': f"https://news.ycombinator.com/item?id={hit['objectID']}",
            'metadata': {
                'story_id': hit['objectID'],
                'points': hit.get('points', 0),
                'num_comments': hit.get('num_comments', 0),
                'external_url': url_from_story
            }
        }
    
    def _collect_comments(self, story_id: str) -> List[Dict[str, Any]]:
        """
        Collect comments for a story.
        
        Args:
            story_id: Hacker News story ID
            
        Returns:
            List of comment records
        """
        comments = []
        
        try:
            # Get story item with kids (comments)
            url = f"{self.api_base}/item/{story_id}.json"
            response = self.make_request(url)
            story = response.json()
            
            # Get top-level comments
            kids = story.get('kids', [])[:10]  # Limit to top 10
            
            for kid_id in kids:
                try:
                    comment_url = f"{self.api_base}/item/{kid_id}.json"
                    comment_response = self.make_request(comment_url)
                    comment = comment_response.json()
                    
                    if comment.get('text'):
                        record = {
                            'source': 'hackernews_comment',
                            'data_id': f"hn_comment_{kid_id}",
                            'timestamp': datetime.fromtimestamp(comment.get('time', 0)).isoformat(),
                            'raw_text': comment.get('text', ''),
                            'author_id': self.anonymize_author(comment.get('by', '')),
                            'url': f"https://news.ycombinator.com/item?id={kid_id}",
                            'metadata': {
                                'comment_id': kid_id,
                                'story_id': story_id,
                                'parent': comment.get('parent')
                            }
                        }
                        comments.append(record)
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    self.logger.warning(f"Failed to fetch comment {kid_id}: {e}")
                    continue
        
        except Exception as e:
            self.logger.warning(f"Failed to collect comments for story {story_id}: {e}")
        
        return comments
    
    def _generate_mock_posts(self, count: int) -> List[Dict[str, Any]]:
        """Generate mock Hacker News posts for dry-run mode."""
        return [{
            'source': 'hackernews_story',
            'data_id': f'hn_story_mock_{i}',
            'timestamp': '2023-07-01T00:00:00Z',
            'raw_text': f'Mock HN story {i+1}: Service Weaver Discussion\\n\\nThis is a test story.',
            'author_id': self.anonymize_author(f'user{i}'),
            'url': f'https://news.ycombinator.com/item?id=mock{i}',
            'metadata': {
                'story_id': f'mock{i}',
                'points': 50 + i * 5,
                'num_comments': i % 20,
                'external_url': f'https://example.com/article{i}',
                'language': 'en'
            }
        } for i in range(count)]


if __name__ == '__main__':
    import yaml
    import sys
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    dry_run = '--dry-run' in sys.argv
    
    scraper = HackerNewsScraper(config, dry_run=dry_run)
    data = scraper.collect()
    
    print(f"\\nCollection complete!")
    print(f"Total records: {len(data)}")
