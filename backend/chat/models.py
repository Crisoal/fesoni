# chat/models.py
from django.contrib.auth.models import User
from django.db import models


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.title or 'Conversation'}"


class Message(models.Model):
    MESSAGE_TYPES = (
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    cultural_context = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.conversation} - {self.message_type}: {self.content[:50]}..."


class CulturalPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    preference_type = models.CharField(max_length=50)  # 'movie', 'music', 'aesthetic', etc.
    preference_value = models.CharField(max_length=200)
    confidence_score = models.FloatField(default=0.0)
    extracted_from_message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'preference_type', 'preference_value']

    def __str__(self):
        return f"{self.user.username} - {self.preference_type}: {self.preference_value}"