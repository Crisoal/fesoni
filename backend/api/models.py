# api/models.py
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cultural_preferences = models.JSONField(default=dict, blank=True)
    taste_profile = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class SavedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=100)
    product_title = models.CharField(max_length=500)
    product_url = models.URLField()
    product_image = models.URLField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    retailer = models.CharField(max_length=50)  # 'amazon' or 'walmart'
    cultural_match_score = models.FloatField(default=0.0)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product_id', 'retailer']

    def __str__(self):
        return f"{self.user.username} - {self.product_title}"