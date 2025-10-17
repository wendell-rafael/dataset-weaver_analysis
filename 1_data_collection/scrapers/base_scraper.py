"""Base scraper utilities and common functions."""

import hashlib
import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('collection.log'),
        logging.StreamHandler()
    ]
)


class BaseScraper:
    """Base class for all scrapers with common functionality."""
    
    def __init__(self, config: Dict[str, Any], dry_run: bool = False):
        """
        Initialize base scraper.
        
        Args:
            config: Configuration dictionary
            dry_run: If True, simulate scraping without API calls
        """
        self.config = config
        self.dry_run = dry_run
        self.logger = logging.getLogger(self.__class__.__name__)
        self.salt = os.getenv(config.get('anonymization', {}).get('salt_env_var', 'AW_SALT'), 'default_salt')
        self.collected_items: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        
    def anonymize_author(self, author_id: str) -> str:
        """
        Anonymize author ID using salted hash.
        
        Args:
            author_id: Original author identifier
            
        Returns:
            Anonymized hash
        """
        if not author_id:
            return "anonymous"
        content = f"{author_id}{self.salt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def make_request(self, url: str, headers: Optional[Dict] = None, 
                    params: Optional[Dict] = None) -> requests.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            url: Request URL
            headers: Request headers
            params: Query parameters
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: On request failure
        """
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would request: {url}")
            return self._mock_response()
            
        self.logger.debug(f"Requesting: {url}")
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        # Respect rate limits
        if 'X-RateLimit-Remaining' in response.headers:
            remaining = int(response.headers['X-RateLimit-Remaining'])
            if remaining < 10:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                sleep_time = max(reset_time - time.time(), 60)
                self.logger.warning(f"Rate limit low ({remaining}), sleeping {sleep_time}s")
                time.sleep(sleep_time)
                
        return response
    
    def _mock_response(self) -> requests.Response:
        """Generate mock response for dry-run mode."""
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"mock": true, "data": []}'
        return response
    
    def save_raw_data(self, filename: str, data: List[Dict[str, Any]]) -> Path:
        """
        Save raw data to CSV/JSON.
        
        Args:
            filename: Output filename
            data: List of data records
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime(self.config.get('output', {}).get('timestamp_format', '%Y%m%d_%H%M%S'))
        output_dir = Path(self.config.get('output', {}).get('raw_data_dir', '1_data_collection/raw_datasets'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / f"{filename}_{timestamp}.csv"
        
        import pandas as pd
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        
        self.logger.info(f"Saved {len(data)} records to {filepath}")
        return filepath
    
    def log_collection_stats(self) -> Dict[str, Any]:
        """
        Generate collection statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            'source': self.__class__.__name__,
            'collected': len(self.collected_items),
            'errors': len(self.errors),
            'timestamp': datetime.now().isoformat()
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text.
        
        Args:
            text: Input text
            
        Returns:
            Language code (e.g., 'en', 'unknown')
        """
        try:
            from langdetect import detect
            return detect(text)
        except Exception:
            return self.config.get('languages', {}).get('fallback', 'unknown')
    
    def should_include_language(self, lang: str) -> bool:
        """
        Check if language should be included based on config.
        
        Args:
            lang: Language code
            
        Returns:
            True if should be included
        """
        include_langs = self.config.get('languages', {}).get('include', ['en'])
        return lang in include_langs or not include_langs
    
    def collect(self) -> List[Dict[str, Any]]:
        """
        Main collection method. Must be implemented by subclasses.
        
        Returns:
            List of collected records
        """
        raise NotImplementedError("Subclasses must implement collect()")
