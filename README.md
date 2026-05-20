# BodyFit Django Project

BodyFit is a Django and Django REST Framework application for body-shape analysis, fashion image management, dashboard analytics, notifications, and photo-guided outfit recommendations.

## Features

- Public landing page with quick body-shape analysis.
- JWT authentication for users.
- User registration and login pages.
- Professional dashboard with analytics, recent activity, notifications, charts, and supported fit-version photo recommendations.
- Fashion gallery with authenticated image upload, filtering, preview, delete actions, and 20 curated outfit photos across different colors, designs, and body-shape matches.
- REST API for profiles, fashion images, body analyses, analytics, notifications, and supported AI models.
- Django admin moved away from the user-facing navigation and available only at `/staff-admin/`.

## Supported Fit Versions

The recommendation system supports these body-shape versions:

- `Hourglass`: balanced curve version.
- `Pear`: lower curve version.
- `Apple`: soft midline version.
- `Rectangle`: straight frame version.
- `Inverted Triangle`: strong shoulder version.

The dashboard shows each version with a representative fashion photo and highlights the most common shape from the user's saved analyses.

## Requirements

- Python 3.11 or newer.
- SQLite for local development.
- The Python packages listed in `requirements.txt`.

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run database migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create a staff admin account when needed:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

Open the app:

```text
http://127.0.0.1:8000/
```

Open the staff admin:

```text
http://127.0.0.1:8000/staff-admin/
```

## Environment Variables

The app uses `python-decouple`. You can create a `.env` file in the project root.

```env
SECRET_KEY=change-this-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

`DEBUG` accepts common values such as `True`, `False`, `development`, `debug`, `production`, and `release`.

## User Flow

1. Register at `/register/`.
2. Log in at `/login/`.
3. Use the quick analysis form on `/` or upload fashion images in `/gallery/`.
4. View analytics and fit-version recommendations at `/dashboard/`.
5. Review quick analysis output at `/results/`.

JWT tokens are stored in browser local storage by the current frontend.

## API Overview

Authentication:

```text
POST /api/register/
POST /api/auth/login/
POST /api/token/
POST /api/token/refresh/
```

Application resources:

```text
/api/profiles/
/api/fashion-images/
/api/body-analyses/
/api/analytics/
/api/notifications/
/api/ai-models/
```

Useful actions:

```text
GET  /api/profiles/me/
POST /api/profiles/toggle_dark_mode/
GET  /api/fashion-images/recent/
POST /api/body-analyses/analyze_image/
GET  /api/body-analyses/summary/
GET  /api/analytics/dashboard/
GET  /api/notifications/unread/
POST /api/notifications/mark_all_read/
```

## Validation

Run Django's checks:

```bash
python manage.py check
```

Run tests:

```bash
python manage.py test
```

At the time of this update, the project has no custom tests, but Django system checks pass.

## Notes For Production

- Set `DEBUG=False` or `DEBUG=production`.
- Replace the default `SECRET_KEY`.
- Use a production database such as PostgreSQL.
- Configure a real static/media file host.
- Configure secure CORS and CSRF origins for the deployed domain.
- Use HTTPS and set secure cookie settings to `True`.
