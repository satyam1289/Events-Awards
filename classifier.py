"""
Sector Classifier - Classifies articles into sectors based on keywords
"""

import re
import logging
from typing import Dict, List, Optional
from collections import Counter
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Noise filtering
NEGATIVE_KEYWORDS = getattr(config, 'NEGATIVE_KEYWORDS', [])


class SectorClassifier:
    """Classifies articles into sectors based on keyword matching"""
    
    def __init__(self):
        # Build sector keyword patterns
        self._build_patterns()
    
    def _build_patterns(self):
        """Build regex patterns for each sector"""
        self.sector_patterns = {}
        
        for sector, keywords in config.SECTORS.items():
            # Create a pattern that matches any of the keywords
            # Use word boundaries to avoid partial matches
            patterns = []
            for keyword in keywords:
                # Escape special regex characters
                escaped_keyword = re.escape(keyword)
                # Create word boundary pattern
                pattern = r'\b' + escaped_keyword + r'\b'
                patterns.append(pattern)
            
            # Combine all keywords for this sector
            combined_pattern = '|'.join(patterns)
            self.sector_patterns[sector] = re.compile(combined_pattern, re.IGNORECASE)
    
    def classify(self, title: str, content: str) -> Dict:
        """
        Classify an article into sectors
        
        Args:
            title: Article title
            content: Article content
            
        Returns:
            Dictionary containing classification results
        """
        text = f"{title} {content}".lower()
        
        # Count keyword matches for each sector
        sector_scores = {}
        
        for sector, pattern in self.sector_patterns.items():
            matches = pattern.findall(text)
            sector_scores[sector] = len(matches)
        
        # Sort by score
        sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get top sector with guard for empty results
        if not sorted_sectors:
            return {
                'primary_sector': None,
                'sector_scores': {},
                'matched_sectors': [],
                'confidence': 0,
                'noise_found': []
            }

        top_sector = sorted_sectors[0]
        primary_sector = top_sector[0] if top_sector[1] > 0 else None
        
        # Get all sectors with matches above threshold
        threshold = 1
        matched_sectors = [
            (sector, score) 
            for sector, score in sorted_sectors 
            if score >= threshold
        ]
        
        # Check for noise
        noise_matches = []
        for kw in NEGATIVE_KEYWORDS:
            if kw in text:
                noise_matches.append(kw)
        
        # Calculate confidence
        if primary_sector and top_sector[1] > 0:
            # Simple confidence based on score ratio
            total_score = sum(sector_scores.values())
            confidence = int((top_sector[1] / total_score) * 100) if total_score > 0 else 0
            
            # Penalize confidence if noise is found
            if noise_matches:
                logger.debug(f"Noise detected: {noise_matches}")
                confidence = max(0, confidence - (len(noise_matches) * 15))
                if len(noise_matches) >= 2:
                    primary_sector = "Noise/Low Quality"
        else:
            confidence = 0
        
        return {
            'primary_sector': primary_sector,
            'sector_scores': dict(sorted_sectors),
            'matched_sectors': matched_sectors,
            'confidence': confidence,
            'noise_found': noise_matches
        }
    
    def classify_with_fallback(self, title: str, content: str) -> str:
        """
        Classify article with fallback to default sector
        
        Args:
            title: Article title
            content: Article content
            
        Returns:
            Primary sector name
        """
        result = self.classify(title, content)
        
        if result['primary_sector']:
            return result['primary_sector']
        
        # Try to infer from title only if content classification fails
        title_result = self._classify_title_only(title)
        if title_result:
            return title_result
        
        # Default fallback
        return "Unknown"
    
    def _classify_title_only(self, title: str) -> Optional[str]:
        """Classify based on title only (for fallback)"""
        text = title.lower()
        
        best_match = None
        best_score = 0
        
        for sector, pattern in self.sector_patterns.items():
            matches = pattern.findall(text)
            score = len(matches)
            
            if score > best_score:
                best_score = score
                best_match = sector
        
        return best_match if best_score > 0 else None
    
    def get_sector_keywords_matched(self, title: str, content: str) -> Dict[str, List[str]]:
        """
        Get which keywords were matched for each sector
        
        Args:
            title: Article title
            content: Article content
            
        Returns:
            Dictionary mapping sector to list of matched keywords
        """
        text = f"{title} {content}"
        matched_keywords = {}
        
        for sector, keywords in config.SECTORS.items():
            sector_matches = []
            for keyword in keywords:
                # Use word boundary matching
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    sector_matches.append(keyword)
            
            if sector_matches:
                matched_keywords[sector] = sector_matches
        
        return matched_keywords
    
    def classify_batch(self, articles: List[Dict]) -> List[Dict]:
        """
        Classify a batch of articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of articles with sector classification added
        """
        results = []
        
        for article in articles:
            title = article.get('title', '')
            content = article.get('content', article.get('description', ''))
            
            classification = self.classify(title, content)
            
            # Add classification to article
            article['sector'] = classification['primary_sector']
            article['sector_confidence'] = classification['confidence']
            article['sector_scores'] = classification['sector_scores']
            
            results.append(article)
        
        return results


def test_classifier():
    """Test the sector classifier"""
    classifier = SectorClassifier()
    
    # Test articles
    test_cases = [
        {
            'title': 'Global FinTech Summit 2026 announced in Mumbai',
            'content': 'The FinTech conference will bring together banking and finance leaders. Topics include digital payments, cryptocurrency investment, and blockchain technology.'
        },
        {
            'title': 'AI Healthcare Conference to be held in Delhi',
            'content': 'Medical professionals and AI researchers will discuss healthcare innovation. Topics include medical devices, biotech, and hospital automation.'
        },
        {
            'title': 'Startup Awards India 2026',
            'content': 'The annual startup awards will recognize innovative entrepreneurs and their ventures. Founders from across the country will participate.'
        }
    ]
    
    for i, test in enumerate(test_cases):
        result = classifier.classify(test['title'], test['content'])
        print(f"\nTest {i+1}: {test['title'][:50]}...")
        print(f"Primary sector: {result['primary_sector']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Sector scores: {result['sector_scores']}")


if __name__ == "__main__":
    test_classifier()

