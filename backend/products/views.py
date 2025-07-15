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
    """Search products based on cultural preferences"""
    try:
        cultural_context = request.data.get('cultural_context', {})
        search_query = request.data.get('search_query', '')
        
        # Mock product mapping for this example
        product_mapping = {
            'product_categories': cultural_context.get('product_categories', []),
            'taste_score': 0.7
        }
        
        # Search products
        products = product_service.search_products(cultural_context, product_mapping)
        
        # Save search for analytics
        search_obj = ProductSearch.objects.create(
            user=request.user,
            search_query=search_query,
            cultural_context=cultural_context
        )
        
        # Save recommendations
        for product in products:
            ProductRecommendation.objects.create(
                search=search_obj,
                product_id=product['product_id'],
                product_title=product['title'],
                product_url=product['url'],
                product_image=product.get('image'),
                price=product.get('price'),
                retailer=product['retailer'],
                cultural_match_score=product['cultural_match_score']
            )
        
        return Response({
            'success': True,
            'search_id': search_obj.id,
            'products': products
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

class ProductSearchHistoryView(generics.ListAPIView):
    """Get user's product search history"""
    serializer_class = ProductSearchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProductSearch.objects.filter(user=self.request.user).order_by('-search_timestamp')
