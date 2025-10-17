"""Stack Overflow scraper for questions and answers."""

import time
from datetime import datetime
from typing import Any, Dict, List
import os

from .base_scraper import BaseScraper


class StackOverflowScraper(BaseScraper):
    """Scraper for Stack Overflow questions and answers."""
    
    def __init__(self, config: Dict[str, Any], dry_run: bool = False):
        """
        Initialize Stack Overflow scraper.
        
        Args:
            config: Configuration dictionary
            dry_run: If True, simulate scraping
        """
        super().__init__(config, dry_run)
        self.so_config = config['sources']['stackoverflow']
        self.api_base = "https://api.stackexchange.com/2.3"
        self.api_key = os.getenv(self.so_config.get('api_key_env', 'STACKEXCHANGE_KEY'))
        
    def collect(self) -> List[Dict[str, Any]]:
        """
        Collect Stack Overflow questions and answers.
        
        Returns:
            List of question/answer records
        """
        all_data = []
        
        tags = self.so_config.get('tags', ['service-weaver'])
        max_items = self.so_config.get('max_items', 1000)
        
        for tag in tags:
            self.logger.info(f"Collecting questions with tag '{tag}'...")
            
            try:
                questions = self._collect_questions(tag, max_items // len(tags))
                all_data.extend(questions)
                self.logger.info(f"Collected {len(questions)} questions for tag '{tag}'")
                
            except Exception as e:
                self.logger.error(f"Error collecting tag '{tag}': {e}")
                self.errors.append({
                    'source': 'stackoverflow',
                    'tag': tag,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        self.collected_items = all_data
        
        # Save raw data
        if all_data:
            self.save_raw_data('stackoverflow_raw', all_data)
        
        return all_data
    
    def _collect_questions(self, tag: str, max_items: int) -> List[Dict[str, Any]]:
        """
        Collect questions for a specific tag.
        
        Args:
            tag: Stack Overflow tag
            max_items: Maximum items to collect
            
        Returns:
            List of question records
        """
        if self.dry_run:
            return self._generate_mock_questions(tag, min(max_items, 20))
        
        questions = []
        page = 1
        per_page = self.so_config.get('per_page', 100)
        
        while len(questions) < max_items:
            url = f"{self.api_base}/questions"
            params = {
                'tagged': tag,
                'site': self.so_config.get('site', 'stackoverflow'),
                'page': page,
                'pagesize': per_page,
                'order': 'desc',
                'sort': 'creation',
                'filter': 'withbody'
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            try:
                response = self.make_request(url, params=params)
                data = response.json()
                
                items = data.get('items', [])
                if not items:
                    break
                
                for item in items:
                    record = self._parse_question(item, tag)
                    
                    # Language filter
                    if self.config.get('languages', {}).get('detect', True):
                        lang = self.detect_language(record['raw_text'])
                        record['metadata']['language'] = lang
                        if not self.should_include_language(lang):
                            continue
                    
                    questions.append(record)
                    
                    # Collect answers if enabled
                    if self.so_config.get('include_answers', True):
                        answers = self._collect_answers(item['question_id'])
                        for answer in answers:
                            questions.append(answer)
                
                # Check quota
                quota_remaining = data.get('quota_remaining', 0)
                if quota_remaining < 100:
                    self.logger.warning(f"Low API quota: {quota_remaining} remaining")
                
                # Check if we have more pages
                if not data.get('has_more', False):
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                self.logger.error(f"Error fetching questions: {e}")
                break
        
        return questions
    
    def _parse_question(self, item: Dict, tag: str) -> Dict[str, Any]:
        """
        Parse Stack Overflow question into standard format.
        
        Args:
            item: Raw question data from API
            tag: Tag being searched
            
        Returns:
            Standardized record
        """
        raw_text = f"{item.get('title', '')}\\n\\n{item.get('body', '')}"
        
        return {
            'source': 'stackoverflow_question',
            'data_id': f"so_q_{item['question_id']}",
            'timestamp': datetime.fromtimestamp(item['creation_date']).isoformat(),
            'raw_text': raw_text,
            'author_id': self.anonymize_author(str(item.get('owner', {}).get('user_id', ''))),
            'url': item.get('link', ''),
            'metadata': {
                'question_id': item['question_id'],
                'tag': tag,
                'score': item.get('score', 0),
                'view_count': item.get('view_count', 0),
                'answer_count': item.get('answer_count', 0),
                'is_answered': item.get('is_answered', False),
                'tags': item.get('tags', [])
            }
        }
    
    def _collect_answers(self, question_id: int) -> List[Dict[str, Any]]:
        """
        Collect answers for a question.
        
        Args:
            question_id: Stack Overflow question ID
            
        Returns:
            List of answer records
        """
        url = f"{self.api_base}/questions/{question_id}/answers"
        params = {
            'site': self.so_config.get('site', 'stackoverflow'),
            'filter': 'withbody',
            'order': 'desc',
            'sort': 'votes'
        }
        
        if self.api_key:
            params['key'] = self.api_key
        
        try:
            response = self.make_request(url, params=params)
            data = response.json()
            
            answers = []
            for item in data.get('items', []):
                record = {
                    'source': 'stackoverflow_answer',
                    'data_id': f"so_a_{item['answer_id']}",
                    'timestamp': datetime.fromtimestamp(item['creation_date']).isoformat(),
                    'raw_text': item.get('body', ''),
                    'author_id': self.anonymize_author(str(item.get('owner', {}).get('user_id', ''))),
                    'url': f"https://stackoverflow.com/a/{item['answer_id']}",
                    'metadata': {
                        'answer_id': item['answer_id'],
                        'question_id': question_id,
                        'score': item.get('score', 0),
                        'is_accepted': item.get('is_accepted', False)
                    }
                }
                answers.append(record)
            
            return answers
            
        except Exception as e:
            self.logger.warning(f"Failed to collect answers for Q{question_id}: {e}")
            return []
    
    def _generate_mock_questions(self, tag: str, count: int) -> List[Dict[str, Any]]:
        """Generate mock Stack Overflow questions for dry-run mode."""
        return [{
            'source': 'stackoverflow_question',
            'data_id': f'so_q_mock_{i}',
            'timestamp': '2023-05-01T00:00:00Z',
            'raw_text': f'Mock question {i+1} about {tag}\\n\\nHow do I use Service Weaver?',
            'author_id': self.anonymize_author(f'user{i}'),
            'url': f'https://stackoverflow.com/questions/mock{i}',
            'metadata': {
                'question_id': 1000 + i,
                'tag': tag,
                'score': i % 10,
                'view_count': 100 + i * 10,
                'answer_count': i % 3,
                'is_answered': i % 2 == 0,
                'tags': [tag, 'golang'],
                'language': 'en'
            }
        } for i in range(count)]


if __name__ == '__main__':
    import yaml
    import sys
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    dry_run = '--dry-run' in sys.argv
    
    scraper = StackOverflowScraper(config, dry_run=dry_run)
    data = scraper.collect()
    
    print(f"\\nCollection complete!")
    print(f"Total records: {len(data)}")
