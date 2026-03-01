from django.urls import path
from core import cadmin_views as v

app_name = 'cadmin'

urlpatterns = [
    path('login/',           v.cadmin_login,    name='login'),
    path('logout/',          v.cadmin_logout,   name='logout'),
    path('change-password/', v.change_password, name='change_password'),
    path('',                 v.dashboard,       name='dashboard'),

    path('hero/',               v.hero_list,   name='hero_list'),
    path('hero/add/',           v.hero_add,    name='hero_add'),
    path('hero/<int:pk>/edit/', v.hero_edit,   name='hero_edit'),
    path('hero/<int:pk>/del/',  v.hero_delete, name='hero_delete'),

    path('logos/',               v.logo_list,   name='logo_list'),
    path('logos/add/',           v.logo_add,    name='logo_add'),
    path('logos/<int:pk>/edit/', v.logo_edit,   name='logo_edit'),
    path('logos/<int:pk>/del/',  v.logo_delete, name='logo_delete'),

    path('portfolio/',                          v.portfolio_list,            name='portfolio_category_list'),
    path('portfolio/category/add/',             v.portfolio_category_add,    name='portfolio_category_add'),
    path('portfolio/category/<int:pk>/edit/',   v.portfolio_category_edit,   name='portfolio_category_edit'),
    path('portfolio/category/<int:pk>/del/',    v.portfolio_category_delete, name='portfolio_category_delete'),
    path('portfolio/video/add/',                v.portfolio_video_add,       name='portfolio_video_add'),
    path('portfolio/video/<int:pk>/edit/',      v.portfolio_video_edit,      name='portfolio_video_edit'),
    path('portfolio/video/<int:pk>/del/',       v.portfolio_video_delete,    name='portfolio_video_delete'),

    path('testimonials/',               v.video_testimonial_list,   name='video_testimonial_list'),
    path('testimonials/add/',           v.video_testimonial_add,    name='video_testimonial_add'),
    path('testimonials/<int:pk>/edit/', v.video_testimonial_edit,   name='video_testimonial_edit'),
    path('testimonials/<int:pk>/del/',  v.video_testimonial_delete, name='video_testimonial_delete'),

    path('pricing/',               v.pricing_list,   name='pricing_list'),
    path('pricing/add/',           v.pricing_add,    name='pricing_add'),
    path('pricing/<int:pk>/edit/', v.pricing_edit,   name='pricing_edit'),
    path('pricing/<int:pk>/del/',  v.pricing_delete, name='pricing_delete'),

    path('pricing/video-types/',               v.video_type_list,   name='video_type_list'),
    path('pricing/video-types/add/',           v.video_type_add,    name='video_type_add'),
    path('pricing/video-types/<int:pk>/edit/', v.video_type_edit,   name='video_type_edit'),
    path('pricing/video-types/<int:pk>/del/',  v.video_type_delete, name='video_type_delete'),

    path('reviews/',               v.review_list,   name='review_list'),
    path('reviews/add/',           v.review_add,    name='review_add'),
    path('reviews/<int:pk>/edit/', v.review_edit,   name='review_edit'),
    path('reviews/<int:pk>/del/',  v.review_delete, name='review_delete'),

    path('team/',               v.team_list,   name='team_list'),
    path('team/add/',           v.team_add,    name='team_add'),
    path('team/<int:pk>/edit/', v.team_edit,   name='team_edit'),
    path('team/<int:pk>/del/',  v.team_delete, name='team_delete'),

    path('leads/', v.lead_list, name='lead_list'),
]
