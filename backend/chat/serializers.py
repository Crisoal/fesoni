# chat/serializers.py
from rest_framework import serializers
from .models import Conversation, Message, CulturalPreference


class MessageSerializer(serializers.ModelSerializer):
    qloo_insights = serializers.JSONField(read_only=True, help_text="Qloo Taste AI™ insights mapping cultural signals to preferences")

    class Meta:
        model = Message
        fields = ['id', 'message_type', 'content', 'cultural_context', 'qloo_insights', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    cultural_context_summary = serializers.JSONField(read_only=True, help_text="Qloo-driven summary of cultural insights for the conversation")

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_active', 'messages', 'message_count', 'cultural_context_summary']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()


class ConversationListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    cultural_context_summary = serializers.JSONField(read_only=True, help_text="Qloo-driven summary of cultural insights for the conversation")

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_active', 'message_count', 'last_message', 'cultural_context_summary']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'message_type': last_message.message_type,
                'timestamp': last_message.timestamp,
                'qloo_insights': last_message.qloo_insights
            }
        return None


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField()
    conversation_id = serializers.IntegerField(required=False)
    voice_input = serializers.BooleanField(default=False)


class CulturalPreferenceSerializer(serializers.ModelSerializer):
    qloo_entity_id = serializers.CharField(read_only=True, allow_null=True, help_text="Qloo entity ID for cross-domain mapping")
    qloo_tag_id = serializers.CharField(read_only=True, allow_null=True, help_text="Qloo tag ID for cultural tags")

    class Meta:
        model = CulturalPreference
        fields = ['id', 'preference_type', 'preference_value', 'confidence_score', 'created_at', 'qloo_entity_id', 'qloo_tag_id']
        read_only_fields = ['id', 'created_at', 'qloo_entity_id', 'qloo_tag_id']