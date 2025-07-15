# api/views.py
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer,
    UserProfileSerializer,
    SavedProductSerializer
)
from .models import UserProfile, SavedProduct


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """User logout endpoint"""
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    except:
        return Response({'message': 'Error logging out'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class SavedProductsView(generics.ListCreateAPIView):
    """List and create saved products"""
    serializer_class = SavedProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedProduct.objects.filter(user=self.request.user).order_by('-saved_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavedProductDetailView(generics.RetrieveDestroyAPIView):
    """Get and delete saved product"""
    serializer_class = SavedProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedProduct.objects.filter(user=self.request.user)