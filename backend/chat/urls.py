# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path('conversations/', views.ConversationListView.as_view(), name='conversations'),
    path('conversations/<int:conversation_id>/', views.conversation_history, name='conversation-history'),
    path('conversations/<int:conversation_id>/delete/', views.delete_conversation, name='delete-conversation'),
    path('cultural-preferences/', views.CulturalPreferenceView.as_view(), name='cultural-preferences'),
]