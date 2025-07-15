# products/models.py
from django.contrib.auth.models import User
from django.db import models

class ProductSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    search_query = models.TextField()
    cultural_context = models.JSONField(default=dict)
    search_timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.search_query[:50]}"

class ProductRecommendation(models.Model):
    search = models.ForeignKey(ProductSearch, on_delete=models.CASCADE, related_name='recommendations')
    product_id = models.CharField(max_length=100)
    product_title = models.CharField(max_length=500)
    product_url = models.URLField()
    product_image = models.URLField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    retailer = models.CharField(max_length=50)  # 'amazon' or 'walmart'
    cultural_match_score = models.FloatField(default=0.0)
    relevance_score = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-cultural_match_score', '-relevance_score']
    
    def __str__(self):
        return f"{self.product_title} - {self.retailer}"