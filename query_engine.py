import datetime
import random
import logging
import config

logger = logging.getLogger(__name__)

class QueryEngine:
    """Precision search query generator optimized for cost and accuracy (v5.5 Elite)."""

    def __init__(self):
        self.sectors = list(config.SECTORS.keys())
        self.year = "2026"

    def get_daily_budget_allocation(self):
        """
        Consolidated Budget Allocation:
        Focuses on maximum city coverage using grouped queries to save credits.
        """
        # We now use the consolidated method to cover all cities with fewer requests
        queries = self.generate_consolidated_city_queries(50)
        
        # Add some tier 1 (Awards) for critical sectors
        queries += self.generate_tier_1(20)
        
        # Add some Tier 3 (Organizers)
        queries += self.generate_tier_3(10)
        
        return queries[:80] # Stay within the 80 query hard cap

    def _format_query(self, query_text, sector):
        return {
            'query': query_text.format(sector=sector, year=self.year),
            'sector': sector,
            'use_awards_cse': any(ind in query_text.lower() for ind in config.AWARD_INDICATORS)
        }

    def generate_tier_1(self, count=40):
        """Tier 1 — High Signal Award Intent."""
        templates = [
            '"{sector}" awards India {year} nominations open',
            '"{sector}" excellence awards India {year} apply now',
            '"{sector}" industry awards India {year} nominations open',
            'apply for "{sector}" excellence awards India {year}'
        ]
        pool = []
        for s in self.sectors:
            for t in templates:
                pool.append(self._format_query(t, s))
        random.shuffle(pool)
        return pool[:count]

    def generate_tier_3(self, count=35):
        """Tier 3 — Organizer-Anchored Patterns."""
        organizers = ["Economic Times", "NASSCOM", "FICCI", "CII"]
        templates = [
            '{org} "{sector}" awards {year} nominations',
            '{org} "{sector}" summit {year} registration'
        ]
        pool = []
        for s in self.sectors:
            for org in organizers:
                for t in templates:
                    pool.append(self._format_query(t.format(org=org, sector="{sector}", year="{year}"), s))
        random.shuffle(pool)
        return pool[:count]

    def generate_consolidated_city_queries(self, count=40):
        """
        ULTRA-MINIMAL: Covers all cities by grouping them into batches of 5.
        Uses only 5 high-level sectors to maintain absolute minimum credit usage.
        """
        cities = config.CITIES
        group_size = 5
        city_groups = [cities[i:i + group_size] for i in range(0, len(cities), group_size)]
        
        # Broad template to catch everything in one credit
        templates = [
            '({sector} awards OR summit OR conference) ({city_list}) India {year} "nominations open"',
            'upcoming ({sector} events OR awards) in ({city_list}) {year} register'
        ]
        
        pool = []
        # Use only a small set of the most active sectors to minimize total queries
        sampled_sectors = random.sample(self.sectors, min(len(self.sectors), 5))
        
        for s in sampled_sectors:
            for group in city_groups:
                city_list = " OR ".join(group)
                for t in templates:
                    pool.append({
                        'query': t.format(sector=s, city_list=city_list, year=self.year),
                        'sector': s,
                        'use_awards_cse': "awards" in t.lower()
                    })
        
        random.shuffle(pool)
        return pool[:count]
