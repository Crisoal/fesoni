# chat/services.py
import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from django.conf import settings
from .models import Conversation, Message, CulturalPreference
from api.models import UserProfile
from products.services import ProductService
import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        # Configure Gemini API for natural language processing
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def extract_cultural_preferences(self, message: str) -> Dict[str, Any]:
        """Extract cultural signals from user message using Gemini to prepare for Qloo's cultural mapping"""
        prompt = f"""
        Analyze the following message and extract cultural signals for Qloo's Taste AI™ to map to preferences.
        Return a JSON object with:
        {{
            "cultural_references": ["list of cultural references like movies, music, books"],
            "aesthetic_keywords": ["list of aesthetic descriptors"],
            "style_preferences": ["list of style preferences"],
            "product_categories": ["list of relevant product categories"],
            "mood_descriptors": ["list of mood/vibe descriptors"],
            "confidence_score": 0.0-1.0,
            "entities_to_search": ["specific entities like movie titles, artist names for Qloo"],
            "tags_to_search": ["generic tags like 'minimalist', 'cozy' for Qloo"],
            "target_entity_type": "most relevant entity type for Qloo (movie, artist, book, brand)"
        }}
        
        Message: "{message}"
        """
        
        try:
            response = self.model.generate_content(prompt)
            cultural_data = json.loads(response.text)
            return cultural_data
        except Exception as e:
            logger.error(f"Error extracting cultural signals: {e}")
            return {
                "cultural_references": [],
                "aesthetic_keywords": [],
                "style_preferences": [],
                "product_categories": [],
                "mood_descriptors": [],
                "confidence_score": 0.0,
                "entities_to_search": [],
                "tags_to_search": [],
                "target_entity_type": "brand"
            }
    
    def generate_response(self, message: str, conversation_history: List[Dict], cultural_context: Dict) -> str:
        """Generate conversational response using Gemini, guided by Qloo's cultural insights"""
        history_context = "\n".join([
            f"{msg['message_type']}: {msg['content']}" 
            for msg in conversation_history[-5:]
        ])
        
        cultural_info = json.dumps(cultural_context, indent=2)
        
        prompt = f"""
        You are TasteMatch, a cultural intelligence shopping platform powered by Qloo's Taste AI™.
        Qloo maps cultural preferences to product recommendations, enabling personalized shopping without personal data.
        
        Cultural Context (from Qloo): {cultural_info}
        
        Recent Conversation:
        {history_context}
        
        Current Message: {message}
        
        Respond as a culturally-aware assistant. Acknowledge the user's aesthetic preferences, 
        emphasize how Qloo's cultural intelligence powers recommendations, and ask clarifying questions if needed.
        If the user is ready to shop, suggest products matched to their vibe via Qloo's insights.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I'm having trouble processing your request. Please try again."

class QlooService:
    def __init__(self):
        self.api_key = settings.QLOO_API_KEY
        self.base_url = "https://hackathon.api.qloo.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def search_entities(self, query: str, entity_type: Optional[str] = None) -> List[Dict]:
        """Search for cultural entities using Qloo's API to power cross-domain recommendations"""
        try:
            url = f"{self.base_url}/search"
            params = {
                "q": query,
                "limit": 10
            }
            
            if entity_type:
                type_mapping = {
                    "movie": "urn:entity:movie",
                    "artist": "urn:entity:artist", 
                    "book": "urn:entity:book",
                    "brand": "urn:entity:brand",
                    "tv_show": "urn:entity:tv_show",
                    "person": "urn:entity:person",
                    "place": "urn:entity:place"
                }
                if entity_type in type_mapping:
                    params["type"] = type_mapping[entity_type]
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                logger.error(f"Qloo search error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Qloo entities: {e}")
            return []
    
    def search_tags(self, query: str) -> List[Dict]:
        """Search for cultural tags using Qloo's API to enhance aesthetic mapping"""
        try:
            url = f"{self.base_url}/v2/tags"
            params = {
                "q": query,
                "limit": 10
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                logger.error(f"Qloo tags search error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Qloo tags: {e}")
            return []
    
    def get_cultural_insights(self, signal_entities: List[str] = None, signal_tags: List[str] = None, 
                             additional_filters: Dict = None) -> Dict[str, Any]:
        """Get cultural insights using Qloo's Taste AI™ for personalized recommendations"""
        try:
            url = f"{self.base_url}/v2/insights"
            
            params = {
                "filter.type": "urn:entity:brand",
                "limit": 20
            }
            
            if signal_entities:
                params["signal.interests.entities"] = ",".join(signal_entities)
            
            if signal_tags:
                params["signal.interests.tags"] = ",".join(signal_tags)
            
            if additional_filters:
                params.update(additional_filters)
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "cultural_insights": data.get("results", []),
                    "total": data.get("total", 0)
                }
            else:
                logger.error(f"Qloo insights error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting cultural insights: {e}")
            return {"success": False, "error": str(e)}
    
    def get_cultural_trends(self, tags: List[str] = None) -> Dict[str, Any]:
        """Discover cultural trends using Qloo's Taste AI™ for trend analysis"""
        try:
            url = f"{self.base_url}/v2/trends"
            params = {
                "limit": 10
            }
            if tags:
                params["tags"] = ",".join(tags)
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "trends": data.get("results", []),
                    "total": data.get("total", 0)
                }
            else:
                logger.error(f"Qloo trends error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting cultural trends: {e}")
            return {"success": False, "error": str(e)}
    
    def map_cultural_to_products(self, cultural_preferences: Dict) -> Dict[str, Any]:
        """Map cultural preferences to product categories and brands using Qloo's Taste AI™ as the core intelligence engine"""
        try:
            entities_to_search = cultural_preferences.get("entities_to_search", [])
            tags_to_search = cultural_preferences.get("tags_to_search", [])
            target_entity_type = cultural_preferences.get("target_entity_type", "brand")
            
            signal_entity_ids = []
            for entity_query in entities_to_search[:5]:
                entities = self.search_entities(entity_query, target_entity_type)
                if entities:
                    signal_entity_ids.append(entities[0].get("id"))
            
            signal_tag_ids = []
            for tag_query in tags_to_search[:5]:
                tags = self.search_tags(tag_query)
                if tags:
                    signal_tag_ids.append(tags[0].get("id"))
            
            cultural_insights = []
            if signal_entity_ids or signal_tag_ids:
                insights_result = self.get_cultural_insights(
                    signal_entities=signal_entity_ids,
                    signal_tags=signal_tag_ids
                )
                
                if insights_result.get("success"):
                    cultural_insights = insights_result.get("cultural_insights", [])
            
            # Fetch cultural trends for discovery
            trend_data = self.get_cultural_trends(tags=tags_to_search)
            trends = trend_data.get("trends", []) if trend_data.get("success") else []
            
            product_categories = self._map_to_product_categories(cultural_preferences, cultural_insights)
            
            return {
                "success": True,
                "signal_entities": signal_entity_ids,
                "signal_tags": signal_tag_ids,
                "cultural_insights": cultural_insights,
                "cultural_trends": trends,
                "product_categories": product_categories,
                "qloo_mapping": {
                    "entities_found": len(signal_entity_ids),
                    "tags_found": len(signal_tag_ids),
                    "insights_found": len(cultural_insights),
                    "trends_found": len(trends)
                }
            }
            
        except Exception as e:
            logger.error(f"Error mapping cultural preferences with Qloo: {e}")
            return {
                "success": False,
                "error": str(e),
                "product_categories": cultural_preferences.get("product_categories", []),
                "cultural_insights": []
            }
    
    def _map_to_product_categories(self, cultural_preferences: Dict, cultural_insights: List[Dict]) -> List[str]:
        """Map cultural preferences and Qloo insights to product categories for cross-domain recommendations"""
        categories = set()
        
        categories.update(cultural_preferences.get("product_categories", []))
        
        aesthetic_keywords = cultural_preferences.get("aesthetic_keywords", [])
        style_preferences = cultural_preferences.get("style_preferences", [])
        
        keyword_category_mapping = {
            # Home & Decor
            "minimalist": ["Home & Garden", "Furniture", "Decor"],
            "cozy": ["Home & Garden", "Bedding", "Lighting"],
            "vintage": ["Home & Garden", "Antiques", "Decor"],
            "modern": ["Furniture", "Electronics", "Home & Garden"],
            "rustic": ["Home & Garden", "Furniture", "Outdoor"],
            "scandinavian": ["Furniture", "Home & Garden", "Lighting"],
            "bohemian": ["Home & Garden", "Textiles", "Decor"],
            "industrial": ["Furniture", "Lighting", "Home & Garden"],
            # Fashion
            "aesthetic": ["Clothing", "Accessories", "Beauty"],
            "grunge": ["Clothing", "Accessories", "Music"],
            "preppy": ["Clothing", "Accessories", "Jewelry"],
            "streetwear": ["Clothing", "Shoes", "Accessories"],
            "elegant": ["Clothing", "Jewelry", "Beauty"],
            "casual": ["Clothing", "Shoes", "Accessories"],
            # Lifestyle
            "wellness": ["Health & Beauty", "Books", "Sports"],
            "outdoorsy": ["Sports & Outdoors", "Clothing", "Equipment"],
            "tech": ["Electronics", "Gadgets", "Books"],
            "artistic": ["Art Supplies", "Books", "Home & Garden"],
            "musical": ["Musical Instruments", "Electronics", "Books"],
            # Food & Kitchen
            "mediterranean": ["Kitchen & Dining", "Cookware", "Home & Garden"],
            "japanese": ["Kitchen & Dining", "Home & Garden", "Decor"],
            "korean": ["Beauty", "Kitchen & Dining", "Books"]
        }
        
        for keyword in aesthetic_keywords + style_preferences:
            keyword_lower = keyword.lower()
            for key, cats in keyword_category_mapping.items():
                if key in keyword_lower:
                    categories.update(cats)
        
        for insight in cultural_insights[:10]:
            insight_name = insight.get("name", "").lower()
            if any(term in insight_name for term in ["fashion", "clothing", "apparel"]):
                categories.update(["Clothing", "Fashion", "Accessories"])
            elif any(term in insight_name for term in ["home", "furniture", "decor"]):
                categories.update(["Home & Garden", "Furniture", "Decor"])
            elif any(term in insight_name for term in ["beauty", "cosmetics", "skincare"]):
                categories.update(["Beauty", "Health & Personal Care"])
            elif any(term in insight_name for term in ["tech", "electronics", "digital"]):
                categories.update(["Electronics", "Technology", "Gadgets"])
            elif any(term in insight_name for term in ["food", "kitchen", "cookware"]):
                categories.update(["Kitchen & Dining", "Cookware"])
        
        return list(categories)

class ChatService:
    def __init__(self):
        self.gemini_service = GeminiService()
        self.qloo_service = QlooService()
        self.product_service = ProductService()
    
    def process_message(self, user, message: str, conversation_id: Optional[int] = None, voice_input: bool = False) -> Dict[str, Any]:
        """Process user message, leveraging Qloo's Taste AI™ as the core cultural intelligence engine"""
        try:
            if conversation_id:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
            else:
                conversation = Conversation.objects.create(
                    user=user,
                    title=message[:50] + "..." if len(message) > 50 else message
                )
            
            user_message = Message.objects.create(
                conversation=conversation,
                message_type='user',
                content=message
            )
            
            # Extract cultural signals for Qloo processing
            cultural_context = self.gemini_service.extract_cultural_preferences(message)
            
            self._update_user_cultural_preferences(user, cultural_context, user_message)
            
            conversation_history = list(conversation.messages.values(
                'message_type', 'content', 'timestamp'
            ))
            
            ai_response = self.gemini_service.generate_response(
                message, conversation_history, cultural_context
            )
            
            ai_message = Message.objects.create(
                conversation=conversation,
                message_type='assistant',
                content=ai_response,
                cultural_context=cultural_context
            )
            
            should_search_products = self._should_search_products(message, cultural_context)
            
            products = []
            qloo_data = {}
            
            if should_search_products:
                # Use Qloo's Taste AI™ as the primary engine for cultural-to-product mapping
                qloo_mapping = self.qloo_service.map_cultural_to_products(cultural_context)
                qloo_data = qloo_mapping
                
                products = self.product_service.search_products(
                    cultural_context, qloo_mapping
                )
            
            conversation.save()
            
            return {
                'success': True,
                'conversation_id': conversation.id,
                'message': ai_response,
                'cultural_context': cultural_context,
                'qloo_data': qloo_data,
                'products': products,
                'voice_input': voice_input
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_user_cultural_preferences(self, user, cultural_context: Dict, message: Message):
        """Update user's cultural preferences without storing personal data, powered by Qloo"""
        try:
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            existing_prefs = profile.cultural_preferences or {}
            
            for key, values in cultural_context.items():
                if isinstance(values, list) and values:
                    if key not in existing_prefs:
                        existing_prefs[key] = []
                    for value in values:
                        if value not in existing_prefs[key]:
                            existing_prefs[key].append(value)
            
            profile.cultural_preferences = existing_prefs
            profile.save()
            
            for pref_type, values in cultural_context.items():
                if isinstance(values, list):
                    for value in values:
                        CulturalPreference.objects.get_or_create(
                            user=user,
                            preference_type=pref_type,
                            preference_value=value,
                            defaults={
                                'confidence_score': cultural_context.get('confidence_score', 0.5),
                                'extracted_from_message': message
                            }
                        )
                        
        except Exception as e:
            logger.error(f"Error updating cultural preferences: {e}")
    
    def _should_search_products(self, message: str, cultural_context: Dict) -> bool:
        """Determine if product search is needed based on message and Qloo's cultural context"""
        search_keywords = [
            'find', 'search', 'buy', 'purchase', 'shop', 'recommend', 'suggest',
            'want', 'need', 'looking for', 'show me', 'products', 'items'
        ]
        
        message_lower = message.lower()
        
        for keyword in search_keywords:
            if keyword in message_lower:
                return True
        
        if cultural_context.get('confidence_score', 0) > 0.6:
            if cultural_context.get('product_categories'):
                return True
        
        return False
    
    def get_conversation_history(self, user, conversation_id: int) -> Dict[str, Any]:
        """Retrieve conversation history with Qloo-powered cultural context"""
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
            messages = conversation.messages.all()
            
            return {
                'success': True,
                'conversation': {
                    'id': conversation.id,
                    'title': conversation.title,
                    'created_at': conversation.created_at,
                    'messages': [
                        {
                            'id': msg.id,
                            'message_type': msg.message_type,
                            'content': msg.content,
                            'cultural_context': msg.cultural_context,
                            'timestamp': msg.timestamp
                        }
                        for msg in messages
                    ]
                }
            }
        except Conversation.DoesNotExist:
            return {
                'success': False,
                'error': 'Conversation not found'
            }
    
    def get_user_conversations(self, user) -> List[Dict[str, Any]]:
        """Get list of user conversations with Qloo-driven insights"""
        conversations = Conversation.objects.filter(user=user, is_active=True)
        
        return [
            {
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at,
                'updated_at': conv.updated_at,
                'message_count': conv.messages.count(),
                'last_message': conv.messages.last().content[:100] if conv.messages.exists() else None
            }
            for conv in conversations
        ]