# chat/models.py
from django.contrib.auth.models import User
from django.db import models


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    cultural_context_summary = models.JSONField(default=dict, blank=True, help_text="Summary of Qloo-driven cultural insights for the conversation")

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title or 'Conversation'}"

    def update_cultural_context_summary(self, cultural_context: dict):
        """
        Update the cultural context summary with Qloo-driven insights.
        Stores aggregated cultural signals without personal data, emphasizing Qloo's privacy-first approach.
        """
        existing_summary = self.cultural_context_summary or {}
        for key, value in cultural_context.items():
            if isinstance(value, list):
                if key not in existing_summary:
                    existing_summary[key] = []
                existing_summary[key] = list(set(existing_summary[key] + value))
        self.cultural_context_summary = existing_summary
        self.save()


class Message(models.Model):
    MESSAGE_TYPES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    cultural_context = models.JSONField(default=dict, blank=True, help_text="Qloo Taste AI™-derived cultural context for this message")
    qloo_insights = models.JSONField(default=dict, blank=True, help_text="Qloo-specific insights mapping cultural signals to preferences")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.conversation} - {self.message_type}: {self.content[:50]}..."


class CulturalPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    preference_type = models.CharField(max_length=50)  # e.g., 'movie', 'music', 'aesthetic', 'food'
    preference_value = models.CharField(max_length=200)
    confidence_score = models.FloatField(default=0.0)
    extracted_from_message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    qloo_entity_id = models.CharField(max_length=100, blank=True, null=True, help_text="Qloo entity ID for cross-domain mapping")
    qloo_tag_id = models.CharField(max_length=100, blank=True, null=True, help_text="Qloo tag ID for cultural tags")

    class Meta:
        unique_together = ['user', 'preference_type', 'preference_value']
        indexes = [
            models.Index(fields=['preference_type', 'preference_value']),
            models.Index(fields=['qloo_entity_id']),
            models.Index(fields=['qloo_tag_id']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.preference_type}: {self.preference_value}"