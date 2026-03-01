"""
S&D Media — Custom Admin Views (v2)
Fixes: video file uploads, optional price, change password, logout
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.core.paginator import Paginator
from django import forms
from .models import (
    HeroSection, TrustedLogo,
    PortfolioCategory, PortfolioVideo,
    VideoTestimonial,
    PricingCard, PricingFeature, VideoType, Lead,
    TextReview, TeamMember,
)

def is_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def cadmin_required(view_func):
    return login_required(login_url='/cadmin/login/')(
        user_passes_test(is_staff, login_url='/cadmin/login/')(view_func)
    )


# ═══════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════
def cadmin_login(request):
    if request.user.is_authenticated and is_staff(request.user):
        return redirect('cadmin:dashboard')
    error = None
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user and is_staff(user):
            login(request, user)
            return redirect('cadmin:dashboard')
        error = 'Invalid credentials or insufficient permissions.'
    return render(request, 'custom_admin/login.html', {'error': error})


def cadmin_logout(request):
    logout(request)
    return redirect('cadmin:login')


@cadmin_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password changed successfully.')
        return redirect('cadmin:dashboard')
    return render(request, 'custom_admin/change_password.html', {
        'form': form,
        'lead_count': Lead.objects.count(),
    })


# ═══════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════
@cadmin_required
def dashboard(request):
    return render(request, 'custom_admin/dashboard.html', {
        'total_leads':      Lead.objects.count(),
        'bundle_leads':     Lead.objects.filter(selected_plan='bundle').count(),
        'custom_leads':     Lead.objects.filter(selected_plan='custom').count(),
        'dedicated_leads':  Lead.objects.filter(selected_plan='dedicated').count(),
        'portfolio_videos': PortfolioVideo.objects.filter(is_active=True).count(),
        'team_members':     TeamMember.objects.filter(is_active=True).count(),
        'recent_leads':     Lead.objects.prefetch_related('selected_video_types').order_by('-submitted_at')[:8],
        'lead_count':       Lead.objects.count(),
    })


# ═══════════════════════════════════════════════════════════
# FORMS
# ═══════════════════════════════════════════════════════════
class HeroForm(forms.ModelForm):
    class Meta:
        model = HeroSection
        fields = ['heading', 'subtitle', 'background_video_url', 'background_video_file', 'is_active']
        widgets = {
            'heading': forms.TextInput(attrs={'placeholder': 'e.g. We Edit Stories, Not Just Videos'}),
            'subtitle': forms.Textarea(attrs={'rows': 3}),
            'background_video_url': forms.URLInput(attrs={'placeholder': 'https://youtube.com/embed/... (optional)'}),
        }


class LogoForm(forms.ModelForm):
    class Meta:
        model = TrustedLogo
        fields = ['company_name', 'logo', 'link', 'order', 'is_active']


class PortfolioCategoryForm(forms.ModelForm):
    class Meta:
        model = PortfolioCategory
        fields = ['name', 'slug', 'order', 'is_active']


class PortfolioVideoForm(forms.ModelForm):
    class Meta:
        model = PortfolioVideo
        fields = ['category', 'title', 'video_file', 'thumbnail', 'description', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Video title'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class VideoTestimonialForm(forms.ModelForm):
    class Meta:
        model = VideoTestimonial
        fields = ['name', 'designation', 'video_file', 'thumbnail', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Client name'}),
            'designation': forms.TextInput(attrs={'placeholder': 'e.g. CEO at XYZ (optional)'}),
        }


class PricingCardForm(forms.ModelForm):
    class Meta:
        model = PricingCard
        fields = ['card_type', 'heading', 'subheading', 'button_label', 'is_most_popular', 'is_active', 'order']


class VideoTypeForm(forms.ModelForm):
    class Meta:
        model = VideoType
        fields = ['name', 'price', 'order', 'is_active']
        widgets = {'name': forms.TextInput(attrs={'placeholder': 'e.g. Wedding Highlight'})}


class TextReviewForm(forms.ModelForm):
    class Meta:
        model = TextReview
        fields = ['name', 'title', 'picture', 'review_text', 'rating', 'order', 'is_active']
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['name', 'role', 'bio', 'picture', 'linkedin_url', 'order', 'is_active']
        widgets = {'bio': forms.Textarea(attrs={'rows': 3})}


# ═══════════════════════════════════════════════════════════
# HELPER
# ═══════════════════════════════════════════════════════════
def _base_ctx():
    return {'lead_count': Lead.objects.count()}

def _list_view(request, model, template, extra=None):
    qs = model.objects.all()
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    ctx = {**_base_ctx(), 'objects': page.object_list, 'page_obj': page, 'is_paginated': page.has_other_pages()}
    if extra: ctx.update(extra)
    return render(request, template, ctx)

def _form_view(request, form_class, back_url, template, instance=None, ctx_extra=None):
    form = form_class(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Saved successfully.')
        return redirect(back_url), True
    ctx = {**_base_ctx(), 'form': form, 'back_url': back_url}
    if ctx_extra: ctx.update(ctx_extra)
    return render(request, template, ctx), False


# ═══════════════════════════════════════════════════════════
# 1. HERO
# ═══════════════════════════════════════════════════════════
@cadmin_required
def hero_list(request): return _list_view(request, HeroSection, 'custom_admin/hero_list.html')

@cadmin_required
def hero_add(request):
    r, saved = _form_view(request, HeroForm, '/cadmin/hero/', 'custom_admin/generic_form.html',
        ctx_extra={'form_title': 'Add Hero Section', 'section_title': 'Hero Section'})
    if saved: return redirect('cadmin:hero_list')
    return r

@cadmin_required
def hero_edit(request, pk):
    obj = get_object_or_404(HeroSection, pk=pk)
    r, saved = _form_view(request, HeroForm, '/cadmin/hero/', 'custom_admin/generic_form.html', instance=obj,
        ctx_extra={'form_title': 'Edit Hero Section', 'section_title': 'Hero Section'})
    if saved: return redirect('cadmin:hero_list')
    return r

@cadmin_required
def hero_delete(request, pk):
    get_object_or_404(HeroSection, pk=pk).delete()
    messages.success(request, 'Deleted.'); return redirect('cadmin:hero_list')


# ═══════════════════════════════════════════════════════════
# 2. LOGOS
# ═══════════════════════════════════════════════════════════
@cadmin_required
def logo_list(request): return _list_view(request, TrustedLogo, 'custom_admin/logo_list.html')

@cadmin_required
def logo_add(request):
    r, saved = _form_view(request, LogoForm, '/cadmin/logos/', 'custom_admin/generic_form.html',
        ctx_extra={'form_title': 'Add Logo', 'section_title': 'Trusted Logos'})
    if saved: return redirect('cadmin:logo_list')
    return r

@cadmin_required
def logo_edit(request, pk):
    obj = get_object_or_404(TrustedLogo, pk=pk)
    r, saved = _form_view(request, LogoForm, '/cadmin/logos/', 'custom_admin/generic_form.html', instance=obj,
        ctx_extra={'form_title': 'Edit Logo', 'section_title': 'Trusted Logos'})
    if saved: return redirect('cadmin:logo_list')
    return r

@cadmin_required
def logo_delete(request, pk):
    get_object_or_404(TrustedLogo, pk=pk).delete()
    messages.success(request, 'Deleted.'); return redirect('cadmin:logo_list')


# ═══════════════════════════════════════════════════════════
# 3. PORTFOLIO
# ═══════════════════════════════════════════════════════════
@cadmin_required
def portfolio_list(request):
    videos_qs = PortfolioVideo.objects.select_related('category').all()
    paginator = Paginator(videos_qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'custom_admin/portfolio_list.html', {
        **_base_ctx(),
        'categories': PortfolioCategory.objects.prefetch_related('videos').all(),
        'videos': page.object_list, 'page_obj': page, 'is_paginated': page.has_other_pages(),
    })

@cadmin_required
def portfolio_category_add(request):
    r, saved = _form_view(request, PortfolioCategoryForm, '/cadmin/portfolio/', 'custom_admin/generic_form.html',
        ctx_extra={'form_title': 'Add Category', 'section_title': 'Portfolio'})
    if saved: return redirect('cadmin:portfolio_category_list')
    return r

@cadmin_required
def portfolio_category_edit(request, pk):
    obj = get_object_or_404(PortfolioCategory, pk=pk)
    r, saved = _form_view(request, PortfolioCategoryForm, '/cadmin/portfolio/', 'custom_admin/generic_form.html', instance=obj,
        ctx_extra={'form_title': 'Edit Category', 'section_title': 'Portfolio'})
    if saved: return redirect('cadmin:portfolio_category_list')
    return r

@cadmin_required
def portfolio_category_delete(request, pk):
    get_object_or_404(PortfolioCategory, pk=pk).delete()
    messages.success(request, 'Deleted.'); return redirect('cadmin:portfolio_category_list')

@cadmin_required
def portfolio_video_add(request):
    r, saved = _form_view(request, PortfolioVideoForm, '/cadmin/portfolio/', 'custom_admin/generic_form.html',
        ctx_extra={'form_title': 'Add Portfolio Video', 'section_title': 'Portfolio'})
    if saved: return redirect('cadmin:portfolio_category_list')
    return r

@cadmin_required
def portfolio_video_edit(request, pk):
    obj = get_object_or_404(PortfolioVideo, pk=pk)
    r, saved = _form_view(request, PortfolioVideoForm, '/cadmin/portfolio/', 'custom_admin/generic_form.html', instance=obj,
        ctx_extra={'form_title': 'Edit Video', 'section_title': 'Portfolio'})
    if saved: return redirect('cadmin:portfolio_category_list')
    return r

@cadmin_required
def portfolio_video_delete(request, pk):
    get_object_or_404(PortfolioVideo, pk=pk).delete()
    messages.success(request, 'Deleted.'); return redirect('cadmin:portfolio_category_list')


# ═══════════════════════════════════════════════════════════
# 4. VIDEO TESTIMONIALS
# ═══════════════════════════════════════════════════════════
@cadmin_required
def video_testimonial_list(request): return _list_view(request, VideoTestimonial, 'custom_admin/video_testimonial_list.html')

@cadmin_required
def video_testimonial_add(request):
    r, saved = _form_view(request, VideoTestimonialForm, '/cadmin/testimonials/', 'custom_admin/generic_form.html',
        ctx_extra={'form_title': 'Add Video Testimonial', 'section_title': 'Video Testimonials'})
    if saved: return redirect('cadmin:video_testimonial_list')
    return r

@cadmin_required
def video_testimonial_edit(request, pk):
    obj = get_object_or_404(VideoTestimonial, pk=pk)
    r, saved = _form_view(request, VideoTestimonialForm, '/cadmin/testimonials/', 'custom_admin/generic_form.html', instance=obj,
        ctx_extra={'form_title': 'Edit Testimonial', 'section_title': 'Video Testimonials'})
    if saved: return redirect('cadmin:video_testimonial_list')
    return r

@cadmin_required
def video_testimonial_delete(request, pk):
    get_object_or_404(VideoTestimonial, pk=pk).delete()
    messages.success(request, 'Deleted.'); return redirect('cadmin:video_testimonial_list')


# ═══════════════════════════════════════════════════════════
# 5. PRICING
# ═══════════════════════════════════════════════════════════
@cadmin_required
def pricing_list(request): return _list_view(request, PricingCard, 'custom_admin/pricing_list.html')

@cadmin_required
def pricing_add(request):
    form = PricingCardForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        card = form.save()
        texts  = request.POST.getlist('feature_text')
        orders = request.POST.getlist('feature_order')
        for i, text in enumerate(texts):
            if text.strip():
                PricingFeature.objects.create(card=card, text=text.strip(),
                    order=int(orders[i]) if i < len(orders) and orders[i].isdigit() else i)
        messages.success(request, 'Pricing card created.')
        return redirect('cadmin:pricing_list')
    return render(request, 'custom_admin/pricing_form.html', {
        **_base_ctx(), 'form': form, 'form_title': 'Add Pricing Card',
        'section_title': 'Pricing', 'back_url': '/cadmin/pricing/', 'features': [],
    })

@cadmin_required
def pricing_edit(request, pk):
    obj = get_object_or_404(PricingCard, pk=pk)
    form = PricingCardForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        card = form.save()
        card.features.all().delete()
        texts  = request.POST.getlist('feature_text')
        orders = request.POST.getlist('feature_order')
        for i, text in enumerate(texts):
            if text.strip():
                PricingFeature.objects.create(card=card, text=text.strip(),
                    order=int(orders[i]) if i < len(orders) and orders[i].isdigit() else i)
        messages.success(request, 'Updated.')
        return redirect('cadmin:pricing_list')
    return render(request, 'custom_admin/pricing_form.html', {
        **_base_ctx(), 'form': form, 'form_title': 'Edit Pricing Card',
        'section_title': 'Pricing', 'back_url': '/cadmin/pricing/', 'features': obj.features.all(),
    })

@cadmin_required
def pricing_delete(request, pk):
    get_object_or_404(PricingCard, pk=pk).delete()
    messages.success(request, 'Deleted.'); return redirect('cadmin:pricing_list')


@cadmin_required
def video_type_list(request): return _list_view(request, VideoType, 'custom_admin/video_type_list.html')

@cadmin_required
def video_type_add(request):
    r, saved = _form_view(request, VideoTypeForm, '/cadmin/pricing/video-types/', 'custom_admin/generic_form.html',
        ctx_extra={'form_title': 'Add Video Type', 'section_title': 'Video Types'})
    if saved: return redirect('cadmin:video_type_list')
    return r

@cadmin_required
def video_type_edit(request, pk):
    obj = get_object_or_404(VideoType, pk=pk)
    r, saved = _form_view(request, VideoTypeForm, '/cadmin/pricing/video-types/', 'custom_admin/generic_form.html', instance=obj,
        ctx_extra={'form_title': 'Edit Video Type', 'section_title': 'Video Types'})
    if saved: return redirect('cadmin:video_type_list')
    return r

@cadmin_required
def video_type_delete(request, pk):
    get_object_or_404(VideoType, pk=pk).delete()
    messages.success(request, 'Deleted.'); return redirect('cadmin:video_type_list')


# ═══════════════════════════════════════════════════════════
# 6. TEXT REVIEWS
# ═══════════════════════════════════════════════════════════
@cadmin_required
def review_list(request): return _list_view(request, TextReview, 'custom_admin/review_list.html')

@cadmin_required
def review_add(request):
    r, saved = _form_view(request, TextReviewForm, '/cadmin/reviews/', 'custom_admin/generic_form.html',
        ctx_extra={'form_title': 'Add Review', 'section_title': 'Text Reviews'})
    if saved: return redirect('cadmin:review_list')
    return r

@cadmin_required
def review_edit(request, pk):
    obj = get_object_or_404(TextReview, pk=pk)
    r, saved = _form_view(request, TextReviewForm, '/cadmin/reviews/', 'custom_admin/generic_form.html', instance=obj,
        ctx_extra={'form_title': 'Edit Review', 'section_title': 'Text Reviews'})
    if saved: return redirect('cadmin:review_list')
    return r

@cadmin_required
def review_delete(request, pk):
    get_object_or_404(TextReview, pk=pk).delete()
    messages.success(request, 'Deleted.'); return redirect('cadmin:review_list')


# ═══════════════════════════════════════════════════════════
# 7. TEAM
# ═══════════════════════════════════════════════════════════
@cadmin_required
def team_list(request): return _list_view(request, TeamMember, 'custom_admin/team_list.html')

@cadmin_required
def team_add(request):
    r, saved = _form_view(request, TeamMemberForm, '/cadmin/team/', 'custom_admin/generic_form.html',
        ctx_extra={'form_title': 'Add Team Member', 'section_title': 'Our Team'})
    if saved: return redirect('cadmin:team_list')
    return r

@cadmin_required
def team_edit(request, pk):
    obj = get_object_or_404(TeamMember, pk=pk)
    r, saved = _form_view(request, TeamMemberForm, '/cadmin/team/', 'custom_admin/generic_form.html', instance=obj,
        ctx_extra={'form_title': 'Edit Team Member', 'section_title': 'Our Team'})
    if saved: return redirect('cadmin:team_list')
    return r

@cadmin_required
def team_delete(request, pk):
    get_object_or_404(TeamMember, pk=pk).delete()
    messages.success(request, 'Deleted.'); return redirect('cadmin:team_list')


# ═══════════════════════════════════════════════════════════
# LEADS
# ═══════════════════════════════════════════════════════════
@cadmin_required
def lead_list(request):
    plan_filter = request.GET.get('plan', '')
    qs = Lead.objects.prefetch_related('selected_video_types').order_by('-submitted_at')
    if plan_filter:
        qs = qs.filter(selected_plan=plan_filter)
    paginator = Paginator(qs, 30)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'custom_admin/lead_list.html', {
        **_base_ctx(),
        'objects': page.object_list, 'page_obj': page, 'is_paginated': page.has_other_pages(),
        'plan_filter': plan_filter,
        'total_leads':     Lead.objects.count(),
        'bundle_count':    Lead.objects.filter(selected_plan='bundle').count(),
        'custom_count':    Lead.objects.filter(selected_plan='custom').count(),
        'dedicated_count': Lead.objects.filter(selected_plan='dedicated').count(),
    })
