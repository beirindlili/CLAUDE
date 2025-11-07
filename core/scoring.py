"""
Opportunity scoring module
"""
import math
from typing import Dict, List
from core.utils import clamp


class OpportunityScorer:
    """Calculate opportunity scores for keywords"""

    def __init__(self, search_wow_weight: float = 0.6, blog_wow_weight: float = 0.4):
        """
        Initialize scorer with weights

        Args:
            search_wow_weight: Weight for search trend wow (default 0.6)
            blog_wow_weight: Weight for blog wow (default 0.4)
        """
        self.search_wow_weight = search_wow_weight
        self.blog_wow_weight = blog_wow_weight

    def compute_momentum(self, search_wow: float, blog_wow: float = 0.0) -> float:
        """
        Calculate momentum score from search and blog trends

        Args:
            search_wow: Search week-over-week change
            blog_wow: Blog week-over-week change (optional)

        Returns:
            Momentum score
        """
        momentum = (self.search_wow_weight * search_wow +
                   self.blog_wow_weight * blog_wow)

        # Clamp momentum to prevent extreme negative values
        momentum = clamp(momentum, -0.9, float('inf'))

        return momentum

    def compute_score(self, demand_z: float, momentum: float, smartstore_count: int) -> float:
        """
        Calculate opportunity score

        Formula: demand_z * (1 / log1p(smartstore_count)) * (1 + momentum)

        Args:
            demand_z: Demand Z-score (standardized search volume)
            momentum: Momentum score (from WoW changes)
            smartstore_count: Estimated SmartStore product count

        Returns:
            Opportunity score
        """
        # Prevent division by zero with log1p (log(1+x))
        supply_penalty = 1.0 / math.log1p(max(smartstore_count, 1))

        # Momentum multiplier (1 + momentum)
        momentum_multiplier = 1.0 + momentum

        # Final score
        score = demand_z * supply_penalty * momentum_multiplier

        return score

    def rank_keywords(self, keyword_data: List[Dict]) -> List[Dict]:
        """
        Rank keywords by opportunity score

        Args:
            keyword_data: List of keyword dictionaries with metrics

        Returns:
            Sorted list of keywords (descending by opportunity_score)
        """
        # Sort by opportunity_score (descending), then by smartstore_est (ascending)
        ranked = sorted(
            keyword_data,
            key=lambda x: (-x.get('opportunity_score', 0), x.get('smartstore_est', float('inf')))
        )

        return ranked

    def calculate_all_scores(self, keywords_data: List[Dict], with_blog: bool = False) -> List[Dict]:
        """
        Calculate momentum and opportunity scores for all keywords

        Args:
            keywords_data: List of keyword dictionaries with metrics
            with_blog: Whether to include blog metrics

        Returns:
            Updated list with momentum and opportunity_score fields
        """
        for kw_data in keywords_data:
            # Calculate momentum
            search_wow = kw_data.get('search_wow', 0.0)
            blog_wow = kw_data.get('blog_wow', 0.0) if with_blog else 0.0

            momentum = self.compute_momentum(search_wow, blog_wow)
            kw_data['momentum'] = round(momentum, 4)

            # Calculate opportunity score
            demand_z = kw_data.get('demand_z', 0.0)
            smartstore_est = kw_data.get('smartstore_est', 0)

            opportunity_score = self.compute_score(demand_z, momentum, smartstore_est)
            kw_data['opportunity_score'] = round(opportunity_score, 4)

        return keywords_data
