"""
Utility functions for the Naver Keyword Opportunity Scraper
"""
import csv
import math
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any


def zscore(values: List[float], x: float) -> float:
    """
    Calculate Z-score for a value in a list of values

    Args:
        values: List of float values
        x: Value to calculate Z-score for

    Returns:
        Z-score (standardized value)
    """
    if not values or len(values) < 2:
        return 0.0

    mean = statistics.mean(values)
    try:
        stdev = statistics.stdev(values)
    except statistics.StatisticsError:
        return 0.0

    if stdev == 0:
        return 0.0

    return (x - mean) / stdev


def save_csv(rows: List[Dict[str, Any]], path: str) -> None:
    """
    Save list of dictionaries to CSV file

    Args:
        rows: List of dictionaries with data
        path: Output file path
    """
    if not rows:
        print(f"⚠️  No data to save to {path}")
        return

    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Saved {len(rows)} rows to {path}")


def get_date_ranges(period_days: int) -> tuple:
    """
    Get date ranges for recent and previous periods

    Args:
        period_days: Number of days in each period

    Returns:
        Tuple of (recent_start, recent_end, prev_start, prev_end)
    """
    today = datetime.now()

    # Recent period: yesterday to (yesterday - period_days + 1)
    recent_end = today - timedelta(days=1)
    recent_start = recent_end - timedelta(days=period_days - 1)

    # Previous period: (recent_start - 1) to (recent_start - period_days)
    prev_end = recent_start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days - 1)

    return (
        recent_start.strftime('%Y-%m-%d'),
        recent_end.strftime('%Y-%m-%d'),
        prev_start.strftime('%Y-%m-%d'),
        prev_end.strftime('%Y-%m-%d')
    )


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero

    Returns:
        Result of division or default
    """
    if denominator == 0:
        return default
    return numerator / denominator
