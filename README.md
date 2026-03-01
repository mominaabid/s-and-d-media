# S&D Media Admin Panel – Setup Guide

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create superuser
```bash
python manage.py createsuperuser
```

### 4. Run development server
```bash
python manage.py runserver
```

### 5. Open admin panel
```
http://127.0.0.1:8000/admin/
```

---

## Admin Panel Structure

### Left Sidebar Modules (S&D Media Content):

| Module | What you can do |
|--------|----------------|
| **Hero Section** | Add/edit heading, subtitle, background video URL or file. Only 1 active at a time. |
| **Trusted Logos (Logo Bar)** | Add company logos + links. Drag order. |
| **Portfolio Categories** | Add categories (e.g. Wedding, Corporate). Inline: add videos directly. |
| **Portfolio Videos** | Add/edit videos per category. Set order, thumbnail, active status. |
| **Video Testimonials** | Add video testimonials with name, optional designation, video URL. |
| **Pricing Cards** | 3 cards (Bundle, Custom, Dedicated). Edit heading, subheading, button text. Inline: add feature lines. |
| **Video Types (Custom Order)** | Add video types + pricing for custom order selection. |
| **Leads / Submissions** | See all form submissions. Filter by plan. Export to Excel or CSV. |
| **Text Reviews** | Add reviews with photo, name, title, star rating. |
| **Our Team** | Add team members with photo, role, bio, LinkedIn. |

---

## API Endpoints

All endpoints return JSON: `{ "success": true, "data": [...] }`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/v1/hero/` | GET | Active hero section |
| `GET /api/v1/logos/` | GET | All active logos |
| `GET /api/v1/portfolio/categories/` | GET | Portfolio categories |
| `GET /api/v1/portfolio/videos/?category=1` | GET | Portfolio videos (optional filter) |
| `GET /api/v1/testimonials/` | GET | Video testimonials |
| `GET /api/v1/pricing/` | GET | Pricing cards + features |
| `GET /api/v1/pricing/video-types/` | GET | Video types for custom order |
| `POST /api/v1/leads/submit/` | POST | Submit lead from pricing modal |
| `GET /api/v1/reviews/` | GET | Text reviews |
| `GET /api/v1/team/` | GET | Team members |
| `GET /admin/export/leads/` | GET | Download all leads as Excel (staff only) |

### Lead Submission JSON Body:
```json
{
  "name": "John Doe",
  "company_name": "XYZ Corp",
  "phone": "+1234567890",
  "email": "john@example.com",
  "selected_plan": "custom",
  "video_type_ids": [1, 2, 3]
}
```
`selected_plan` must be: `bundle`, `custom`, or `dedicated`

---

## Production Checklist

In `sdmedia/settings.py`:

```python
DEBUG = False
SECRET_KEY = 'your-super-secret-key'  # Use env variable
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000

# Static files (run: python manage.py collectstatic)
STATIC_ROOT = '/var/www/sdmedia/static/'
MEDIA_ROOT = '/var/www/sdmedia/media/'
```

## Project Structure

```
sdmedia_admin/
├── manage.py
├── requirements.txt
├── db.sqlite3              (auto-created after migrate)
├── media/                  (uploaded files)
├── static/
│   └── admin/
│       └── css/
│           └── custom_admin.css  ← Theme
├── templates/
│   └── admin/
│       ├── base_site.html        ← Branding
│       └── index.html            ← Dashboard with stats
├── sdmedia/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── core/
    ├── models.py       ← All 7 section models + Lead
    ├── admin.py        ← Full admin config
    ├── views.py        ← API endpoints + Excel export
    └── apps.py
```
