# products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_products, name='search-products'),
    path('history/', views.ProductSearchHistoryView.as_view(), name='search-history'),
]