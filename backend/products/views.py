# products/views.py
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ProductSearch, ProductRecommendation
from .serializers import ProductSearchSerializer, ProductRecommendationSerializer
from .services import ProductService

product_service = ProductService()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_products(request):
    """Search products using Qloo's Taste AI™ as the core cultural intelligence engine"""
    try:
        cultural_context = request.data.get('cultural_context', {})
        search_query = request.data.get('search_query', '')
        qloo_data = request.data.get('qloo_data', {})  # Expect Qloo insights from chat endpoint
        
        # Validate Qloo data
        if not qloo_data.get('success', False):
            return Response({
                'success': False,
                'error': 'Invalid Qloo data provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Search products using Qloo-driven insights
        products = product_service.search_products(cultural_context, qloo_data)
        
        # Save search for analytics
        search_obj = ProductSearch.objects.create(
            user=request.user,
            search_query=search_query,
            cultural_context=cultural_context,
            qloo_insights=qloo_data.get('cultural_insights', []),
            cultural_trends=qloo_data.get('cultural_trends', [])
        )
        
        # Save recommendations with Qloo insights
        for product in products:
            ProductRecommendation.objects.create(
                search=search_obj,
                product_id=product['product_id'],
                product_title=product['title'],
                product_url=product['url'],
                product_image=product.get('image'),
                price=product.get('price'),
                retailer=product['retailer'],
                cultural_match_score=product['cultural_match_score'],
                qloo_insights_applied=product.get('qloo_insights', [])
            )
        
        return Response({
            'success': True,
            'search_id': search_obj.id,
            'products': products,
            'qloo_insights': qloo_data.get('cultural_insights', []),
            'cultural_trends': qloo_data.get('cultural_trends', [])
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

class ProductSearchHistoryView(generics.ListAPIView):
    """Retrieve user's product search history with Qloo-driven cultural insights"""
    serializer_class = ProductSearchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProductSearch.objects.filter(user=self.request.user).order_by('-search_timestamp')