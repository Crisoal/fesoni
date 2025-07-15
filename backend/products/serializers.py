# products/serializers.py
from rest_framework import serializers
from .models import ProductSearch, ProductRecommendation

class ProductRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRecommendation
        fields = ['id', 'product_id', 'product_title', 'product_url', 'product_image', 
                 'price', 'retailer', 'cultural_match_score', 'relevance_score']

class ProductSearchSerializer(serializers.ModelSerializer):
    recommendations = ProductRecommendationSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductSearch
        fields = ['id', 'search_query', 'cultural_context', 'search_timestamp', 'recommendations']