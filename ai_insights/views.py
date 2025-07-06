from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from tenants.mixins import TenantRequiredMixin, PermissionRequiredMixin
from analytics.models import Insight


class InsightListView(TenantRequiredMixin, ListView):
    """
    List all AI insights
    """
    model = Insight
    template_name = 'ai_insights/list.html'
    context_object_name = 'insights'
    paginate_by = 20
    
    def get_queryset(self):
        return Insight.objects.filter(
            analysis__created_by=self.request.user,
            is_hidden=False
        ).order_by('-importance_score', '-created_at')


class InsightDetailView(TenantRequiredMixin, DetailView):
    """
    View insight details
    """
    model = Insight
    template_name = 'ai_insights/detail.html'
    context_object_name = 'insight'
    
    def get_queryset(self):
        return Insight.objects.filter(
            analysis__created_by=self.request.user
        )


class GenerateInsightsView(TenantRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Generate new AI insights
    """
    template_name = 'ai_insights/generate.html'
    required_permission = 'create_reports'


class ChatView(TenantRequiredMixin, TemplateView):
    """
    AI chat interface for data questions
    """
    template_name = 'ai_insights/chat.html'


class RecommendationsView(TenantRequiredMixin, ListView):
    """
    View AI recommendations
    """
    template_name = 'ai_insights/recommendations.html'
    context_object_name = 'recommendations'
    paginate_by = 20
    
    def get_queryset(self):
        return Insight.objects.filter(
            analysis__created_by=self.request.user,
            insight_type='recommendation',
            is_hidden=False
        ).order_by('-importance_score', '-created_at')
