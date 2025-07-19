# products/serializers.py
from rest_framework import serializers
from .models import ProductSearch, ProductRecommendation


class ProductRecommendationSerializer(serializers.ModelSerializer):
    qloo_insights_applied = serializers.JSONField(read_only=True, help_text="Qloo Taste AI™ insights used for this recommendation")

    class Meta:
        model = ProductRecommendation
        fields = ['id', 'product_id', 'product_title', 'product_url', 'product_image', 
                  'price', 'retailer', 'cultural_match_score', 'qloo_insights_applied']

class ProductSearchSerializer(serializers.ModelSerializer):
    recommendations = ProductRecommendationSerializer(many=True, read_only=True)
    qloo_insights = serializers.JSONField(read_only=True, help_text="Qloo Taste AI™ insights mapping cultural preferences")
    cultural_trends = serializers.JSONField(read_only=True, help_text="Qloo-derived cultural trends for discovery")

    class Meta:
        model = ProductSearch
        fields = ['id', 'search_query', 'cultural_context', 'qloo_insights', 'cultural_trends', 
                  'search_timestamp', 'recommendations']