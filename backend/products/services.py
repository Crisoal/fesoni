# products/services.py
import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from django.conf import settings
from .models import ProductSearch, ProductRecommendation

logger = logging.getLogger(__name__)

class RapidAPIAmazonService:
    def __init__(self):
        self.api_key = settings.RAPIDAPI_KEY
        self.host = "axesso-axesso-amazon-data-service-v1.p.rapidapi.com"
        self.search_url = f"https://{self.host}/amz/amazon-search-by-keyword-asin"
        self.details_url = f"https://{self.host}/amz/amazon-lookup-product"
        self.headers = {
            'x-rapidapi-host': self.host,
            'x-rapidapi-key': self.api_key
        }
    
    def search_products(self, keywords: List[str], max_results: int = 10) -> List[Dict]:
        """Search Amazon products using RapidAPI, guided by Qloo's cultural insights"""
        try:
            search_query = " ".join(keywords)
            
            params = {
                'domainCode': 'com',
                'keyword': search_query,
                'page': 1,
                'excludeSponsored': 'false',
                'sortBy': 'relevanceblender',
                'withCache': 'true'
            }
            
            response = requests.get(
                self.search_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('responseStatus') == 'PRODUCT_FOUND_RESPONSE':
                    products = []
                    search_details = data.get('searchProductDetails', [])
                    
                    for product_detail in search_details[:max_results]:
                        formatted_product = self._format_search_product(product_detail)
                        products.append(formatted_product)
                    
                    return products
                else:
                    logger.warning(f"No products found for keywords: {keywords}")
                    return []
            else:
                logger.error(f"RapidAPI search request failed with status {response.status_code}: {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("RapidAPI search request timed out")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"RapidAPI search request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in RapidAPI search: {e}")
            return []
    
    def get_product_details(self, product_url: str) -> Optional[Dict]:
        """Get detailed Amazon product information for Qloo-driven recommendations"""
        try:
            params = {
                'url': product_url
            }
            
            response = requests.get(
                self.details_url,
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('responseStatus') == 'PRODUCT_FOUND_RESPONSE':
                    return self._format_detailed_product(data)
                else:
                    logger.warning(f"Product details not found for URL: {product_url}")
                    return None
            else:
                logger.error(f"RapidAPI details request failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("RapidAPI details request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"RapidAPI details request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in RapidAPI details: {e}")
            return None
    
    def get_product_details_by_asin(self, asin: str) -> Optional[Dict]:
        """Get product details by ASIN for Qloo-enhanced recommendations"""
        amazon_url = f"https://www.amazon.com/dp/{asin}/"
        return self.get_product_details(amazon_url)
    
    def _format_search_product(self, product_detail: Dict) -> Dict:
        """Convert RapidAPI search product format to internal format"""
        rating_str = product_detail.get('productRating', '0 out of 5 stars')
        try:
            rating = float(rating_str.split(' ')[0]) if rating_str else 0.0
        except (ValueError, IndexError):
            rating = 0.0
        
        dp_url = product_detail.get('dpUrl', '')
        full_url = f"https://amazon.com{dp_url}" if dp_url else ""
        
        return {
            "product_id": product_detail.get('asin', ''),
            "title": product_detail.get('productDescription', ''),
            "url": full_url,
            "image": product_detail.get('imgUrl', ''),
            "price": product_detail.get('price', 0),
            "retail_price": product_detail.get('retailPrice', 0),
            "rating": rating,
            "reviews": product_detail.get('countReview', 0),
            "prime": product_detail.get('prime', False),
            "delivery_message": product_detail.get('deliveryMessage', ''),
            "variations": product_detail.get('variations', []),
            "retailer": "amazon",
            "data_type": "search_result"
        }
    
    def _format_detailed_product(self, product_data: Dict) -> Dict:
        """Convert RapidAPI detailed product format to internal format"""
        rating_str = product_data.get('productRating', '0 out of 5 stars')
        try:
            rating = float(rating_str.split(' ')[0]) if rating_str else 0.0
        except (ValueError, IndexError):
            rating = 0.0
        
        features = product_data.get('features', [])
        
        product_details = {}
        for detail in product_data.get('productDetails', []):
            product_details[detail.get('name', '')] = detail.get('value', '')
        
        reviews = []
        for review in product_data.get('reviews', [])[:5]:
            reviews.append({
                'rating': review.get('rating', ''),
                'title': review.get('title', ''),
                'text': review.get('text', ''),
                'date': review.get('date', ''),
                'user_name': review.get('userName', ''),
                'variations': review.get('variationList', [])
            })
        
        review_insights = product_data.get('reviewInsights', {})
        feature_aspects = []
        for aspect in review_insights.get('featureAspects', []):
            feature_aspects.append({
                'name': aspect.get('name', ''),
                'sentiment': aspect.get('sentiment', ''),
                'summary': aspect.get('summary', ''),
                'positive_count': aspect.get('featureMentionPositiveCount', 0),
                'negative_count': aspect.get('featureMentionNegativeCount', 0),
                'total_count': aspect.get('featureMentionCount', 0)
            })
        
        variations = []
        for variation in product_data.get('variations', []):
            variation_values = []
            for value in variation.get('values', []):
                variation_values.append({
                    'value': value.get('value', ''),
                    'available': value.get('available', False),
                    'price': value.get('price', 0),
                    'asin': value.get('asin', ''),
                    'image_url': value.get('imageUrl', '')
                })
            
            variations.append({
                'name': variation.get('variationName', ''),
                'values': variation_values
            })
        
        images = product_data.get('imageUrlList', [])
        main_image = product_data.get('mainImage', {})
        
        return {
            "product_id": product_data.get('asin', ''),
            "title": product_data.get('productTitle', ''),
            "url": f"https://amazon.com/dp/{product_data.get('asin', '')}/",
            "image": main_image.get('imageUrl', ''),
            "images": images,
            "price": product_data.get('price', 0),
            "retail_price": product_data.get('retailPrice', 0),
            "rating": rating,
            "reviews_count": product_data.get('countReview', 0),
            "prime": product_data.get('prime', False),
            "manufacturer": product_data.get('manufacturer', ''),
            "brand": product_details.get('Brand', ''),
            "color": product_details.get('Color', ''),
            "material": product_details.get('Material', ''),
            "features": features,
            "product_description": product_data.get('productDescription', ''),
            "product_details": product_details,
            "reviews": reviews,
            "review_insights_summary": review_insights.get('summary', ''),
            "feature_aspects": feature_aspects,
            "variations": variations,
            "categories": product_data.get('categories', []),
            "delivery_message": product_data.get('priceShippingInformation', ''),
            "warehouse_availability": product_data.get('warehouseAvailability', ''),
            "price_saving": product_data.get('priceSaving', ''),
            "past_sales": product_data.get('pastSales', ''),
            "deal": product_data.get('deal', False),
            "retailer": "amazon",
            "data_type": "detailed_product"
        }

class ProductService:
    def __init__(self):
        self.amazon_service = RapidAPIAmazonService()
    
    def search_products(self, cultural_context: Dict, product_mapping: Dict) -> List[Dict]:
        """Search products using Qloo's cultural insights as the primary recommendation engine"""
        try:
            keywords = self._extract_search_keywords(cultural_context, product_mapping)
            
            if not keywords:
                logger.warning("No keywords extracted from Qloo's cultural insights")
                return []
            
            amazon_products = self.amazon_service.search_products(keywords, max_results=15)
            
            scored_products = []
            
            for product in amazon_products:
                cultural_score = self._calculate_cultural_match_score(
                    product, cultural_context, product_mapping
                )
                scored_products.append({
                    **product,
                    'cultural_match_score': cultural_score,
                    'qloo_insights': product_mapping.get('cultural_insights', [])
                })
            
            scored_products.sort(key=lambda x: x['cultural_match_score'], reverse=True)
            
            return scored_products[:12]
        
        except Exception as e:
            logger.error(f"Error searching products with Qloo insights: {e}")
            return []
    
    def get_enhanced_product_details(self, product_id: str, cultural_context: Dict = None) -> Optional[Dict]:
        """Get enhanced product details with Qloo-powered cultural analysis"""
        try:
            detailed_product = self.amazon_service.get_product_details_by_asin(product_id)
            
            if not detailed_product:
                return None
            
            if cultural_context:
                cultural_analysis = self._analyze_product_cultural_fit(
                    detailed_product, cultural_context
                )
                detailed_product['cultural_analysis'] = cultural_analysis
            
            return detailed_product
            
        except Exception as e:
            logger.error(f"Error getting enhanced product details: {e}")
            return None
    
    def _analyze_product_cultural_fit(self, product: Dict, cultural_context: Dict) -> Dict:
        """Analyze product fit using Qloo-driven cultural insights"""
        analysis = {
            'overall_fit_score': 0.0,
            'feature_matches': [],
            'aesthetic_alignment': {},
            'user_sentiment_analysis': {},
            'cultural_keywords_found': []
        }
        
        try:
            title = product.get('title', '').lower()
            description = product.get('product_description', '').lower()
            features = product.get('features', [])
            
            aesthetic_keywords = cultural_context.get('aesthetic_keywords', [])
            found_keywords = []
            
            for keyword in aesthetic_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in title or keyword_lower in description:
                    found_keywords.append(keyword)
                
                for feature in features:
                    if keyword_lower in feature.lower():
                        found_keywords.append(keyword)
                        break
            
            analysis['cultural_keywords_found'] = list(set(found_keywords))
            
            feature_aspects = product.get('feature_aspects', [])
            relevant_aspects = []
            
            for aspect in feature_aspects:
                aspect_name = aspect.get('name', '').lower()
                if any(pref.lower() in aspect_name for pref in cultural_context.get('style_preferences', [])):
                    relevant_aspects.append({
                        'aspect': aspect.get('name'),
                        'sentiment': aspect.get('sentiment'),
                        'summary': aspect.get('summary'),
                        'positive_mentions': aspect.get('positive_count', 0),
                        'total_mentions': aspect.get('total_count', 0)
                    })
            
            analysis['feature_matches'] = relevant_aspects
            
            # Prioritize Qloo's cultural insights for scoring
            qloo_insights = cultural_context.get('qloo_mapping', {}).get('cultural_insights', [])
            insight_score = 0.0
            for insight in qloo_insights:
                insight_name = insight.get('name', '').lower()
                if insight_name in title or insight_name in description:
                    insight_score += 0.2
            
            keyword_score = min(len(found_keywords) * 0.1, 0.3)
            feature_score = min(len(relevant_aspects) * 0.05, 0.15)
            rating_bonus = 0.05 if product.get('rating', 0) > 4.5 else 0
            
            analysis['overall_fit_score'] = min(insight_score + keyword_score + feature_score + rating_bonus, 1.0)
            
            reviews = product.get('reviews', [])
            positive_cultural_mentions = 0
            total_cultural_mentions = 0
            
            for review in reviews:
                review_text = review.get('text', '').lower()
                for keyword in aesthetic_keywords:
                    if keyword.lower() in review_text:
                        total_cultural_mentions += 1
                        rating = review.get('rating', '')
                        if '5.0' in rating or '4.0' in rating:
                            positive_cultural_mentions += 1
            
            if total_cultural_mentions > 0:
                analysis['user_sentiment_analysis'] = {
                    'positive_cultural_mentions': positive_cultural_mentions,
                    'total_cultural_mentions': total_cultural_mentions,
                    'sentiment_ratio': positive_cultural_mentions / total_cultural_mentions
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing cultural fit with Qloo: {e}")
            return analysis
    
    def _extract_search_keywords(self, cultural_context: Dict, product_mapping: Dict) -> List[str]:
        """Extract search keywords prioritizing Qloo's cultural insights"""
        keywords = []
        
        # Prioritize Qloo's cultural insights
        for insight in product_mapping.get('cultural_insights', []):
            keywords.append(insight.get('name', ''))
        
        keywords.extend(cultural_context.get('aesthetic_keywords', []))
        keywords.extend(cultural_context.get('style_preferences', []))
        keywords.extend(cultural_context.get('mood_descriptors', []))
        keywords.extend(product_mapping.get('product_categories', []))
        
        keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
        keywords = list(set(keywords))
        
        return keywords[:8]
    
    def _calculate_cultural_match_score(self, product: Dict, cultural_context: Dict, product_mapping: Dict) -> float:
        """Calculate cultural match score with Qloo's Taste AI™ as the primary driver"""
        score = 0.0
        
        # Prioritize Qloo's cultural insights
        qloo_insights = product_mapping.get('cultural_insights', [])
        insight_score = 0.0
        title_lower = product['title'].lower()
        description = product.get('product_description', '').lower()
        
        for insight in qloo_insights:
            insight_name = insight.get('name', '').lower()
            if insight_name in title_lower or insight_name in description:
                insight_score += 0.25
        
        score += min(insight_score, 0.6)  # Qloo insights contribute up to 60% of score
        
        aesthetic_keywords = cultural_context.get('aesthetic_keywords', [])
        aesthetic_matches = sum(1 for keyword in aesthetic_keywords if keyword.lower() in title_lower)
        score += min(aesthetic_matches * 0.1, 0.2)
        
        style_preferences = cultural_context.get('style_preferences', [])
        style_matches = sum(1 for pref in style_preferences if pref.lower() in title_lower)
        score += min(style_matches * 0.05, 0.1)
        
        mood_descriptors = cultural_context.get('mood_descriptors', [])
        mood_matches = sum(1 for mood in mood_descriptors if mood.lower() in title_lower)
        score += min(mood_matches * 0.05, 0.1)
        
        rating = product.get('rating', 0)
        if rating > 4.5:
            score += 0.05
        elif rating > 4.0:
            score += 0.03
        
        review_count = product.get('reviews', 0)
        if review_count > 1000:
            score += 0.02
        elif review_count > 100:
            score += 0.01
        
        if product.get('prime', False):
            score += 0.02
        
        retail_price = product.get('retail_price', 0)
        current_price = product.get('price', 0)
        if retail_price > 0 and current_price > 0 and current_price < retail_price:
            discount_ratio = (retail_price - current_price) / retail_price
            score += min(discount_ratio * 0.05, 0.02)
        
        return min(score, 1.0)
    
    def get_product_categories_from_search(self, keywords: List[str]) -> List[str]:
        """Get product categories for Qloo-driven search keywords"""
        try:
            search_query = " ".join(keywords)
            params = {
                'domainCode': 'com',
                'keyword': search_query,
                'page': 1,
                'excludeSponsored': 'false',
                'sortBy': 'relevanceblender',
                'withCache': 'true'
            }
            
            response = requests.get(
                self.amazon_service.search_url,
                headers=self.amazon_service.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('categories', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []