# chat/views.py
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, Message, CulturalPreference
from .serializers import (
    ConversationSerializer, 
    ConversationListSerializer,
    ChatRequestSerializer,
    CulturalPreferenceSerializer
)
from .services import ChatService

chat_service = ChatService()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """Main chat endpoint"""
    serializer = ChatRequestSerializer(data=request.data)
    if serializer.is_valid():
        result = chat_service.process_message(
            user=request.user,
            message=serializer.validated_data['message'],
            conversation_id=serializer.validated_data.get('conversation_id'),
            voice_input=serializer.validated_data.get('voice_input', False)
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_history(request, conversation_id):
    """Get conversation history"""
    result = chat_service.get_conversation_history(request.user, conversation_id)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)

class ConversationListView(generics.ListAPIView):
    """List user's conversations"""
    serializer_class = ConversationListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user, is_active=True)

class CulturalPreferenceView(generics.ListAPIView):
    """Get user's cultural preferences"""
    serializer_class = CulturalPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CulturalPreference.objects.filter(user=self.request.user).order_by('-created_at')

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_conversation(request, conversation_id):
    """Delete a conversation"""
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        conversation.is_active = False
        conversation.save()
        return Response({'message': 'Conversation deleted successfully'}, status=status.HTTP_200_OK)
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)