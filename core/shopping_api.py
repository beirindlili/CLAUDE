"""
Naver Shopping Search API integration module
"""
import os
import re
import time
import requests
from typing import Tuple, List, Dict, Optional
from urllib.parse import urlparse


class ShoppingAPI:
    """Naver Shopping Search API wrapper"""

    SHOPPING_SEARCH_URL = "https://openapi.naver.com/v1/search/shop.json"
    SMARTSTORE_DOMAINS = [
        'smartstore.naver.com',
        'shopping.naver.com/window-products',
        'shopping.naver.com/catalog'
    ]

    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Initialize Shopping API client

        Args:
            client_id: Naver API client ID (or from env)
            client_secret: Naver API client secret (or from env)
        """
        self.client_id = client_id or os.getenv('NAVER_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('NAVER_CLIENT_SECRET')

        if not self.client_id or not self.client_secret:
            raise ValueError("NAVER_CLIENT_ID and NAVER_CLIENT_SECRET must be set")

        self.headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }

    def _is_smartstore(self, link: str) -> bool:
        """
        Check if a product link is from SmartStore

        Args:
            link: Product URL

        Returns:
            True if SmartStore, False otherwise
        """
        try:
            parsed = urlparse(link)
            domain = parsed.netloc

            # Check if domain matches SmartStore patterns
            for smartstore_domain in self.SMARTSTORE_DOMAINS:
                if smartstore_domain in domain:
                    return True

            # Additional check for URL path patterns
            if 'smartstore' in link.lower():
                return True

            return False

        except Exception:
            return False

    def _request_with_retry(self, url: str, params: dict, max_retries: int = 3) -> Optional[dict]:
        """
        Make API request with retry logic

        Args:
            url: API endpoint URL
            params: Query parameters
            max_retries: Maximum number of retries

        Returns:
            Response JSON or None on failure
        """
        for attempt in range(max_retries):
            try:
                time.sleep(0.2)  # Rate limiting
                response = requests.get(url, params=params, headers=self.headers, timeout=30)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limit hit
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⚠️  Rate limit hit, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code in [401, 403]:
                    print(f"❌ Authentication error: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return None
                else:
                    print(f"⚠️  API error {response.status_code}: {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    return None

            except requests.exceptions.RequestException as e:
                print(f"⚠️  Request error (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))
                    continue
                return None

        return None

    def get_shopping_supply(self, keyword: str, display: int = 50) -> Tuple[int, int]:
        """
        Get shopping supply metrics (total products and SmartStore estimate)

        Args:
            keyword: Search keyword
            display: Number of results to fetch for sampling (max 100)

        Returns:
            Tuple of (total_count, smartstore_estimated_count)
        """
        params = {
            'query': keyword,
            'display': min(display, 100),  # Max 100 per API limit
            'sort': 'sim'  # Similarity sort
        }

        result = self._request_with_retry(self.SHOPPING_SEARCH_URL, params)

        if not result:
            return 0, 0

        total = result.get('total', 0)
        items = result.get('items', [])

        if not items:
            return total, 0

        # Count SmartStore items in sample
        smartstore_count = sum(1 for item in items if self._is_smartstore(item.get('link', '')))

        # Estimate total SmartStore count
        sample_size = len(items)
        smartstore_ratio = smartstore_count / sample_size if sample_size > 0 else 0
        smartstore_estimated = round(total * smartstore_ratio)

        return total, smartstore_estimated

    def search_products(self, keyword: str, display: int = 10, start: int = 1,
                       sort: str = 'sim') -> List[Dict]:
        """
        Search for products

        Args:
            keyword: Search keyword
            display: Number of results to display (max 100)
            start: Start position (1-indexed)
            sort: Sort order (sim: similarity, date: recent, asc: low price, dsc: high price)

        Returns:
            List of product items
        """
        params = {
            'query': keyword,
            'display': min(display, 100),
            'start': start,
            'sort': sort
        }

        result = self._request_with_retry(self.SHOPPING_SEARCH_URL, params)

        if result and 'items' in result:
            return result['items']

        return []
