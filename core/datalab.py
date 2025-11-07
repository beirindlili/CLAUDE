"""
Naver DataLab API integration module
"""
import os
import time
import requests
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class DataLabAPI:
    """Naver DataLab API wrapper"""

    SEARCH_TREND_URL = "https://openapi.naver.com/v1/datalab/search"
    SHOPPING_INSIGHT_URL = "https://openapi.naver.com/v1/datalab/shopping/category/keywords"

    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Initialize DataLab API client

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
            'X-Naver-Client-Secret': self.client_secret,
            'Content-Type': 'application/json'
        }

    def _request_with_retry(self, url: str, json_data: dict, max_retries: int = 3) -> Optional[dict]:
        """
        Make API request with retry logic

        Args:
            url: API endpoint URL
            json_data: Request JSON data
            max_retries: Maximum number of retries

        Returns:
            Response JSON or None on failure
        """
        for attempt in range(max_retries):
            try:
                time.sleep(0.3)  # Rate limiting
                response = requests.post(url, json=json_data, headers=self.headers, timeout=30)

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

    def get_search_trend(self, keyword: str, start_date: str, end_date: str,
                        time_unit: str = "date", device: str = "", gender: str = "",
                        ages: List[str] = None) -> List[Dict]:
        """
        Get search trend data for a keyword

        Args:
            keyword: Search keyword
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            time_unit: Time unit (date, week, month)
            device: Device filter (pc, mo, or empty for all)
            gender: Gender filter (m, f, or empty for all)
            ages: Age groups (1-12, 13-18, 19-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60+)

        Returns:
            List of trend data points: [{'period': 'YYYY-MM-DD', 'ratio': float}, ...]
        """
        keyword_group = {
            "groupName": keyword,
            "keywords": [keyword]
        }

        if device:
            keyword_group["device"] = device
        if gender:
            keyword_group["gender"] = gender
        if ages:
            keyword_group["ages"] = ages

        request_body = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": time_unit,
            "keywordGroups": [keyword_group]
        }

        result = self._request_with_retry(self.SEARCH_TREND_URL, request_body)

        if result and 'results' in result and len(result['results']) > 0:
            return result['results'][0].get('data', [])

        return []

    def compare_recent_prev(self, keyword: str, recent_start: str, recent_end: str,
                           prev_start: str, prev_end: str) -> Tuple[float, float, float]:
        """
        Compare recent vs previous period search trends

        Args:
            keyword: Search keyword
            recent_start: Recent period start date
            recent_end: Recent period end date
            prev_start: Previous period start date
            prev_end: Previous period end date

        Returns:
            Tuple of (recent_avg, prev_avg, wow)
        """
        try:
            # Get recent period data
            recent_data = self.get_search_trend(keyword, recent_start, recent_end)

            # Get previous period data
            prev_data = self.get_search_trend(keyword, prev_start, prev_end)

            # Calculate averages
            recent_avg = sum(d['ratio'] for d in recent_data) / len(recent_data) if recent_data else 0.0
            prev_avg = sum(d['ratio'] for d in prev_data) / len(prev_data) if prev_data else 0.0

            # Calculate week-over-week (or period-over-period) change
            epsilon = 1.0  # Prevent division by zero
            wow = (recent_avg - prev_avg) / max(prev_avg, epsilon)

            return recent_avg, prev_avg, wow
        except Exception as e:
            # DataLab API not available or error occurred
            # Return zeros to continue without trend data
            return 0.0, 0.0, 0.0

    def get_shopping_keywords(self, category: str, start_date: str, end_date: str,
                             time_unit: str = "date", device: str = "", gender: str = "",
                             ages: List[str] = None) -> List[str]:
        """
        Get popular shopping keywords for a category (optional feature)

        Args:
            category: Shopping category code
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            time_unit: Time unit
            device: Device filter
            gender: Gender filter
            ages: Age groups

        Returns:
            List of popular keywords
        """
        request_body = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": time_unit,
            "category": [category]
        }

        if device:
            request_body["device"] = device
        if gender:
            request_body["gender"] = gender
        if ages:
            request_body["ages"] = ages

        result = self._request_with_retry(self.SHOPPING_INSIGHT_URL, request_body)

        keywords = []
        if result and 'results' in result:
            for item in result['results']:
                if 'data' in item:
                    for data_point in item['data']:
                        if 'keyword' in data_point:
                            keywords.append(data_point['keyword'])

        return list(set(keywords))  # Remove duplicates
