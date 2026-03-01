"""
S&D Media URL Configuration
Custom admin at /cadmin/ | API at /api/v1/
Django admin REMOVED as requested.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

API_PREFIX = 'api/v1/'

urlpatterns = [
    # ─── CUSTOM ADMIN PANEL ───────────────────────────────────────
    path('cadmin/', include('core.cadmin_urls', namespace='cadmin')),

    # ─── EXPORT (accessible to logged-in staff) ───────────────────
    path('export/leads/', core_views.export_leads_excel, name='export-leads'),

    # ─── PUBLIC API ENDPOINTS ─────────────────────────────────────
    path(API_PREFIX + 'hero/',                    core_views.HeroAPIView.as_view(),             name='api-hero'),
    path(API_PREFIX + 'logos/',                   core_views.LogoBarAPIView.as_view(),           name='api-logos'),
    path(API_PREFIX + 'portfolio/categories/',    core_views.PortfolioCategoryAPIView.as_view(), name='api-portfolio-categories'),
    path(API_PREFIX + 'portfolio/videos/',        core_views.PortfolioVideoAPIView.as_view(),    name='api-portfolio-videos'),
    path(API_PREFIX + 'testimonials/',            core_views.TestimonialAPIView.as_view(),       name='api-testimonials'),
    path(API_PREFIX + 'pricing/',                 core_views.PricingAPIView.as_view(),           name='api-pricing'),
    path(API_PREFIX + 'pricing/video-types/',     core_views.VideoTypeAPIView.as_view(),         name='api-video-types'),
    path(API_PREFIX + 'leads/submit/',            core_views.LeadSubmitAPIView.as_view(),        name='api-lead-submit'),
    path(API_PREFIX + 'reviews/',                 core_views.TextReviewAPIView.as_view(),        name='api-reviews'),
    path(API_PREFIX + 'team/',                    core_views.TeamMemberAPIView.as_view(),        name='api-team'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
