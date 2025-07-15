# api/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('saved-products/', views.SavedProductsView.as_view(), name='saved-products'),
    path('saved-products/<int:pk>/', views.SavedProductDetailView.as_view(), name='saved-product-detail'),
]