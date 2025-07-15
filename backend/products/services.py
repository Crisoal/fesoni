# products/services.py
import os
import json
import logging
import requests
from typing import Dict, List, Any
from django.conf import settings
from .models import ProductSearch, ProductRecommendation

logger = logging.getLogger(__name__)

class AmazonProductService:
    def __init__(self):
        self.access_key = settings.AMAZON_ACCESS_KEY
        self.secret_key = settings.AMAZON_SECRET_KEY
        self.partner_tag = settings.AMAZON_ASSOCIATE_TAG
        self.host = "webservices.amazon.com"
        self.region = "us-east-1"
    
    def search_products(self, keywords: List[str], category: str = "All", max_results: int = 10) -> List[Dict]:
        """Search Amazon products (mock implementation)"""
        # This is a placeholder implementation
        # In production, you'd use the actual Amazon Product Advertising API
        
        mock_products = [
            {
                "product_id": "B08N5WRWNW",
                "title": "Cozy Throw Blanket - Soft Knit",
                "url": "https://amazon.com/dp/B08N5WRWNW",
                "image": "https://m.media-amazon.com/images/I/71abc123def.jpg",
                "price": 29.99,
                "rating": 4.5,
                "reviews": 1234
            },
            {
                "product_id": "B07XJ8C8F5",
                "title": "Minimalist Desk Lamp",
                "url": "https://amazon.com/dp/B07XJ8C8F5",
                "image": "https://m.media-amazon.com/images/I/71xyz789abc.jpg",
                "price": 45.99,
                "rating": 4.3,
                "reviews": 567
            }
        ]
        
        return mock_products[:max_results]

class WalmartProductService:
    def __init__(self):
        self.api_key = settings.WALMART_API_KEY
        self.base_url = "https://developer.api.walmart.com/api-proxy/service/affil/product/v2"
    
    def search_products(self, keywords: List[str], category: str = "All", max_results: int = 10) -> List[Dict]:
        """Search Walmart products (mock implementation)"""
        # This is a placeholder implementation
        # In production, you'd use the actual Walmart API
        
        mock_products = [
            {
                "product_id": "12345678",
                "title": "Bohemian Tapestry Wall Hanging",
                "url": "https://walmart.com/ip/12345678",
                "image": "https://i5.walmartimages.com/asr/sample.jpg",
                "price": 24.99,
                "rating": 4.2,
                "reviews": 890
            },
            {
                "product_id": "87654321",
                "title": "Scandinavian Style Coffee Table",
                "url": "https://walmart.com/ip/87654321",
                "image": "https://i5.walmartimages.com/asr/sample2.jpg",
                "price": 199.99,
                "rating": 4.6,
                "reviews": 234
            }
        ]
        
        return mock_products[:max_results]

class ProductService:
    def __init__(self):
        self.amazon_service = AmazonProductService()
        self.walmart_service = WalmartProductService()
    
    def search_products(self, cultural_context: Dict, product_mapping: Dict) -> List[Dict]:
        """Search products across multiple retailers"""
        try:
            # Extract search keywords from cultural context
            keywords = self._extract_search_keywords(cultural_context, product_mapping)
            
            # Search both Amazon and Walmart
            amazon_products = self.amazon_service.search_products(keywords, max_results=8)
            walmart_products = self.walmart_service.search_products(keywords, max_results=8)
            
            # Combine and score products
            all_products = []
            
            # Process Amazon products
            for product in amazon_products:
                cultural_score = self._calculate_cultural_match_score(
                    product, cultural_context, product_mapping
                )
                all_products.append({
                    **product,
                    'retailer': 'amazon',
                    'cultural_match_score': cultural_score
                })
            
            # Process Walmart products
            for product in walmart_products:
                cultural_score = self._calculate_cultural_match_score(
                    product, cultural_context, product_mapping
                )
                all_products.append({
                    **product,
                    'retailer': 'walmart',
                    'cultural_match_score': cultural_score
                })
            
            # Sort by cultural match score
            all_products.sort(key=lambda x: x['cultural_match_score'], reverse=True)
            
            return all_products[:12]  # Return top 12 products
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def _extract_search_keywords(self, cultural_context: Dict, product_mapping: Dict) -> List[str]:
        """Extract search keywords from cultural context"""
        keywords = []
        
        # Add aesthetic keywords
        keywords.extend(cultural_context.get('aesthetic_keywords', []))
        
        # Add style preferences
        keywords.extend(cultural_context.get('style_preferences', []))
        
        # Add mood descriptors
        keywords.extend(cultural_context.get('mood_descriptors', []))
        
        # Add product categories from mapping
        keywords.extend(product_mapping.get('product_categories', []))
        
        # Filter and clean keywords
        keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
        keywords = list(set(keywords))  # Remove duplicates
        
        return keywords
    
    def _calculate_cultural_match_score(self, product: Dict, cultural_context: Dict, product_mapping: Dict) -> float:
        """Calculate how well a product matches cultural preferences"""
        score = 0.0
        
        # Base score from Qloo mapping
        score += product_mapping.get('taste_score', 0.0) * 0.3
        
        # Title matching score
        title_lower = product['title'].lower()
        
        # Check aesthetic keywords
        aesthetic_keywords = cultural_context.get('aesthetic_keywords', [])
        for keyword in aesthetic_keywords:
            if keyword.lower() in title_lower:
                score += 0.2
        
        # Check style preferences
        style_preferences = cultural_context.get('style_preferences', [])
        for pref in style_preferences:
            if pref.lower() in title_lower:
                score += 0.15
        
        # Check mood descriptors
        mood_descriptors = cultural_context.get('mood_descriptors', [])
        for mood in mood_descriptors:
            if mood.lower() in title_lower:
                score += 0.1
        
        # Product rating bonus
        rating = product.get('rating', 0)
        if rating > 4.0:
            score += 0.1
        
        # Normalize score to 0-1 range
        return min(score, 1.0)