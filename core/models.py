"""
S&D Media - Core Models (v2)
Changes: video file uploads, optional price, removed video_url fields
"""
from django.db import models


class HeroSection(models.Model):
    heading = models.CharField(max_length=255)
    subtitle = models.TextField()
    background_video_url = models.URLField(blank=True, null=True, help_text="YouTube/Vimeo embed URL (optional)")
    background_video_file = models.FileField(upload_to='hero/', blank=True, null=True, help_text="Or upload a video file")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"

    def __str__(self):
        return f"Hero: {self.heading[:50]}"

    def save(self, *args, **kwargs):
        if self.is_active:
            HeroSection.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class TrustedLogo(models.Model):
    company_name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/')
    link = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Trusted Logo"
        verbose_name_plural = "Trusted Logos (Logo Bar)"
        ordering = ['order', 'company_name']

    def __str__(self):
        return self.company_name


class PortfolioCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Portfolio Category"
        verbose_name_plural = "Portfolio Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class PortfolioVideo(models.Model):
    category = models.ForeignKey(PortfolioCategory, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='portfolio/videos/', help_text="Upload video file (mp4, mov, etc.)")
    thumbnail = models.ImageField(upload_to='portfolio/thumbnails/', blank=True, null=True, help_text="Optional thumbnail")
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Portfolio Video"
        verbose_name_plural = "Portfolio Videos"
        ordering = ['category', 'order', 'title']

    def __str__(self):
        return f"{self.category.name} – {self.title}"


class VideoTestimonial(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=150, blank=True, help_text="Optional – e.g. CEO at XYZ")
    video_file = models.FileField(upload_to='testimonials/videos/', help_text="Upload video file")
    thumbnail = models.ImageField(upload_to='testimonials/thumbs/', blank=True, null=True, help_text="Optional thumbnail")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Video Testimonial"
        verbose_name_plural = "Video Testimonials"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name}" + (f" – {self.designation}" if self.designation else "")


CARD_TYPE_CHOICES = [
    ('bundle', 'Buy a Package (Bundle)'),
    ('custom', 'Create Custom Order'),
    ('dedicated', 'Dedicated Editor'),
]

class PricingCard(models.Model):
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, unique=True)
    heading = models.CharField(max_length=200)
    subheading = models.CharField(max_length=200, blank=True)
    button_label = models.CharField(max_length=50, default='Get Started')
    is_most_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Pricing Card"
        verbose_name_plural = "Pricing Cards"
        ordering = ['order']

    def __str__(self):
        return self.get_card_type_display()

    def save(self, *args, **kwargs):
        if self.is_most_popular:
            PricingCard.objects.exclude(pk=self.pk).update(is_most_popular=False)
        super().save(*args, **kwargs)


class PricingFeature(models.Model):
    card = models.ForeignKey(PricingCard, on_delete=models.CASCADE, related_name='features')
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.card} → {self.text}"


class VideoType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Optional price")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Video Type"
        verbose_name_plural = "Video Types (Custom Order)"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Lead(models.Model):
    PLAN_CHOICES = [
        ('bundle', 'Buy a Package'),
        ('custom', 'Create Custom Order'),
        ('dedicated', 'Dedicated Editor'),
    ]
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    selected_plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    selected_video_types = models.ManyToManyField(VideoType, blank=True, related_name='leads')
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Lead / Submission"
        verbose_name_plural = "Leads / Submissions"
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.name} ({self.get_selected_plan_display()}) – {self.submitted_at.strftime('%d %b %Y')}"


class TextReview(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=150)
    picture = models.ImageField(upload_to='reviews/', blank=True, null=True)
    review_text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Text Review"
        verbose_name_plural = "Text Reviews"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.name} – {self.title}"


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    picture = models.ImageField(upload_to='team/')
    linkedin_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Our Team"
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} – {self.role}"
