# chat/services.py
import os
import json
import logging
import google.generativeai as genai
from typing import Dict, List, Any, Optional
from django.conf import settings
from .models import Conversation, Message, CulturalPreference
from api.models import UserProfile
from products.services import ProductService

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def extract_cultural_preferences(self, message: str) -> Dict[str, Any]:
        """Extract cultural preferences from user message using Gemini"""
        prompt = f"""
        Analyze the following message and extract cultural preferences, aesthetics, and style references.
        Return a JSON object with the following structure:
        {{
            "cultural_references": ["list of cultural references like movies, music, books, etc."],
            "aesthetic_keywords": ["list of aesthetic descriptors"],
            "style_preferences": ["list of style preferences"],
            "product_categories": ["list of relevant product categories"],
            "mood_descriptors": ["list of mood/vibe descriptors"],
            "confidence_score": 0.0-1.0
        }}
        
        Message: "{message}"
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse the JSON response
            cultural_data = json.loads(response.text)
            return cultural_data
        except Exception as e:
            logger.error(f"Error extracting cultural preferences: {e}")
            return {
                "cultural_references": [],
                "aesthetic_keywords": [],
                "style_preferences": [],
                "product_categories": [],
                "mood_descriptors": [],
                "confidence_score": 0.0
            }
    
    def generate_response(self, message: str, conversation_history: List[Dict], cultural_context: Dict) -> str:
        """Generate AI response using Gemini"""
        history_context = "\n".join([
            f"{msg['message_type']}: {msg['content']}" 
            for msg in conversation_history[-5:]  # Last 5 messages for context
        ])
        
        cultural_info = json.dumps(cultural_context, indent=2)
        
        prompt = f"""
        You are TasteMatch, an AI shopping assistant that understands cultural preferences and aesthetics.
        
        Cultural Context: {cultural_info}
        
        Recent Conversation:
        {history_context}
        
        Current Message: {message}
        
        Respond as a helpful, culturally-aware shopping assistant. Be conversational, understanding, and helpful.
        If the user describes aesthetics or cultural preferences, acknowledge them and ask clarifying questions.
        If they're ready to shop, suggest that you can find products that match their vibe.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."

class QlooService:
    def __init__(self):
        self.api_key = settings.QLOO_API_KEY
        self.base_url = "https://api.qloo.com/v1"
    
    def map_cultural_to_products(self, cultural_preferences: Dict) -> Dict[str, Any]:
        """Map cultural preferences to product categories using Qloo API"""
        # This is a placeholder implementation
        # In a real implementation, you'd make API calls to Qloo
        
        # Mock mapping based on cultural preferences
        mapping = {
            "product_categories": [],
            "brand_recommendations": [],
            "style_tags": [],
            "taste_score": 0.0
        }
        
        # Extract cultural references and map to categories
        cultural_refs = cultural_preferences.get("cultural_references", [])
        aesthetic_keywords = cultural_preferences.get("aesthetic_keywords", [])
        
        # Simple mapping logic (replace with actual Qloo API calls)
        category_mapping = {
            "studio ghibli": ["Home & Garden", "Books", "Clothing"],
            "dark academia": ["Books", "Clothing", "Home Decor"],
            "minimalist": ["Home & Garden", "Electronics", "Clothing"],
            "vintage": ["Clothing", "Home Decor", "Books"],
            "bohemian": ["Home & Garden", "Clothing", "Jewelry"],
            "scandinavian": ["Home & Garden", "Furniture", "Lighting"],
            "japanese": ["Home & Garden", "Books", "Electronics"],
            "korean": ["Beauty", "Clothing", "Books"],
            "indie": ["Music", "Books", "Clothing"],
            "cozy": ["Home & Garden", "Bedding", "Lighting"]
        }
        
        categories = set()
        for ref in cultural_refs + aesthetic_keywords:
            ref_lower = ref.lower()
            for key, cats in category_mapping.items():
                if key in ref_lower:
                    categories.update(cats)
        
        mapping["product_categories"] = list(categories)
        mapping["taste_score"] = cultural_preferences.get("confidence_score", 0.5)
        
        return mapping

class ChatService:
    def __init__(self):
        self.gemini_service = GeminiService()
        self.qloo_service = QlooService()
        self.product_service = ProductService()
    
    def process_message(self, user, message: str, conversation_id: Optional[int] = None, voice_input: bool = False) -> Dict[str, Any]:
        """Process incoming chat message"""
        try:
            # Get or create conversation
            if conversation_id:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
            else:
                conversation = Conversation.objects.create(
                    user=user,
                    title=message[:50] + "..." if len(message) > 50 else message
                )
            
            # Save user message
            user_message = Message.objects.create(
                conversation=conversation,
                message_type='user',
                content=message
            )
            
            # Extract cultural preferences
            cultural_context = self.gemini_service.extract_cultural_preferences(message)
            
            # Update user's cultural preferences
            self._update_user_cultural_preferences(user, cultural_context, user_message)
            
            # Get conversation history
            conversation_history = list(conversation.messages.values(
                'message_type', 'content', 'timestamp'
            ))
            
            # Generate AI response
            ai_response = self.gemini_service.generate_response(
                message, conversation_history, cultural_context
            )
            
            # Save AI response
            ai_message = Message.objects.create(
                conversation=conversation,
                message_type='assistant',
                content=ai_response,
                cultural_context=cultural_context
            )
            
            # Check if we should search for products
            should_search_products = self._should_search_products(message, cultural_context)
            
            products = []
            if should_search_products:
                # Map cultural preferences to products
                product_mapping = self.qloo_service.map_cultural_to_products(cultural_context)
                
                # Search for products
                products = self.product_service.search_products(
                    cultural_context, product_mapping
                )
            
            # Update conversation timestamp
            conversation.save()
            
            return {
                'success': True,
                'conversation_id': conversation.id,
                'message': ai_response,
                'cultural_context': cultural_context,
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
        """Update user's cultural preferences based on extracted context"""
        try:
            # Update UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Merge new cultural preferences with existing ones
            existing_prefs = profile.cultural_preferences or {}
            
            for key, values in cultural_context.items():
                if isinstance(values, list) and values:
                    if key not in existing_prefs:
                        existing_prefs[key] = []
                    # Add new values that aren't already present
                    for value in values:
                        if value not in existing_prefs[key]:
                            existing_prefs[key].append(value)
            
            profile.cultural_preferences = existing_prefs
            profile.save()
            
            # Save individual cultural preferences
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
        """Determine if we should search for products based on message content"""
        search_keywords = [
            'find', 'search', 'buy', 'purchase', 'shop', 'recommend', 'suggest',
            'want', 'need', 'looking for', 'show me', 'products', 'items'
        ]
        
        message_lower = message.lower()
        
        # Check if message contains search keywords
        for keyword in search_keywords:
            if keyword in message_lower:
                return True
        
        # Check if cultural context has high confidence and specific categories
        if cultural_context.get('confidence_score', 0) > 0.6:
            if cultural_context.get('product_categories'):
                return True
        
        return False
    
    def get_conversation_history(self, user, conversation_id: int) -> Dict[str, Any]:
        """Get conversation history"""
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
        """Get user's conversation list"""
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