from django.urls import path
from . import views

app_name = 'ai_insights'

urlpatterns = [
    path('', views.InsightListView.as_view(), name='list'),
    path('<uuid:pk>/', views.InsightDetailView.as_view(), name='detail'),
    path('generate/', views.GenerateInsightsView.as_view(), name='generate'),
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('recommendations/', views.RecommendationsView.as_view(), name='recommendations'),
]
