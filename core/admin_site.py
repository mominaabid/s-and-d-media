"""
Custom Admin Site – injects stats into the dashboard context
"""
from django.contrib.admin import AdminSite


class SDMediaAdminSite(AdminSite):
    site_header = "S&D Media Admin"
    site_title  = "S&D Media"
    index_title = "Dashboard"

    def index(self, request, extra_context=None):
        from .models import Lead, PortfolioVideo, TeamMember
        from django.db.models import Count

        stats = {
            'total_leads':     Lead.objects.count(),
            'bundle_leads':    Lead.objects.filter(selected_plan='bundle').count(),
            'custom_leads':    Lead.objects.filter(selected_plan='custom').count(),
            'dedicated_leads': Lead.objects.filter(selected_plan='dedicated').count(),
            'portfolio_videos': PortfolioVideo.objects.filter(is_active=True).count(),
            'team_members':    TeamMember.objects.filter(is_active=True).count(),
            'recent_leads':    Lead.objects.prefetch_related('selected_video_types').order_by('-submitted_at')[:8],
        }
        extra_context = extra_context or {}
        extra_context.update(stats)
        return super().index(request, extra_context)
