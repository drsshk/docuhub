# OBSOLETE — DocuHub Setup Instructions

**Status:** OBSOLETE — duplicate
**Reason:** Superseded by comprehensive environment_setup_guide.md (now at /docs/02_modules/08-environment-setup.md)
**Replaced by:** /docs/02_modules/08-environment-setup.md
**Moved on:** 2025-12-30

---

# DocuHub Setup Instructions

## Quick Start Guide

Follow these steps to get DocuHub running on your local machine:

### 1. Create Project Directory and Virtual Environment

```bash
# Create project directory
mkdir docuhub
cd docuhub

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install Django and dependencies
pip install -r requirements.txt
```

### 3. Create Django Project Structure

```bash
# Create Django project
django-admin startproject docuhub .

# Create apps directory
mkdir apps
touch apps/__init__.py  #on Linux/macOS
type NUL > apps\__init__.py  #on Windows CMD

# Create Django apps
python manage.py startapp PaperKeep apps/PaperKeep


```

### 4. Database Setup

#### PostgreSQL (Recommended)
```bash
# Install PostgreSQL and create database
psql -U postgres
CREATE DATABASE docuhub_db;
CREATE USER docuhub_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE docuhub_db TO docuhub_user;
ALTER USER docuhub_user CREATEDB;
\q
```

#### SQLite (For Development)
If you prefer SQLite for development, update your `.env` file:
```env
DATABASE_URL=sqlite:///db.sqlite3
```

### 5. Environment Configuration

Create a `.env` file in your project root:
```env
SECRET_KEY=your-very-secret-key-here-make-it-long-and-random
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://docuhub_user:your_password@localhost:5432/docuhub_db
BREVO_API_KEY=your-brevo-api-key-here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
BREVO_SENDER_NAME=DocuHub System
FRONTEND_URL=http://localhost:8000
REDIS_URL=redis://localhost:6379/0
```

### 6. Apply All Files

Copy all the provided files to their respective locations:

- `requirements.txt` → project root
- `docuhub/settings.py` → replace existing
- `docuhub/urls.py` → replace existing
- All app files to their respective directories
- Template files to `templates/` directory

### 7. Create Directory Structure

```bash
# Create necessary directories
mkdir -p templates/registration
mkdir -p templates/projects
mkdir -p templates/core
mkdir -p templates/accounts
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images
mkdir -p media
```

### 8. Database Migration

```bash
# Create and apply migrations
python manage.py makemigrations accounts
python manage.py makemigrations projects
python manage.py makemigrations notifications
python manage.py makemigrations core
python manage.py migrate
```

### 9. Create Superuser

```bash
python manage.py createsuperuser
```

### 10. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to see your DocuHub application!

## File Structure Reference

```
docuhub/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── docuhub/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── migrations/
│   ├── projects/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── permissions.py
│   │   ├── signals.py
│   │   └── migrations/
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── admin.py
│   │   └── migrations/
│   └── core/
│       ├── __init__.py
│       ├── views.py
│       ├── context_processors.py
│       └── apps.py
├── templates/
│   ├── base.html
│   ├── core/
│   │   └── home.html
│   ├── projects/
│   │   ├── dashboard.html
│   │   ├── project_form.html
│   │   └── project_detail.html
│   └── registration/
│       └── login.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── media/
```

## Brevo Email Setup (Optional)

1. Sign up for a [Brevo account](https://www.brevo.com/)
2. Get your API key from the Brevo dashboard
3. Create email templates in Brevo for:
   - Project submission confirmation
   - Project approval notification
   - Project rejection notification
   - Admin new submission alert
4. Update your `.env` file with template IDs

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in your `.env`
2. Configure a proper database (PostgreSQL recommended)
3. Set up a web server (Nginx + Gunicorn)
4. Configure static file serving
5. Set up SSL certificates
6. Configure email settings for production

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all apps are properly added to `INSTALLED_APPS`
2. **Database Errors**: Check your database connection settings
3. **Template Errors**: Ensure template directories are created
4. **Static Files**: Run `python manage.py collectstatic` for production

### Getting Help

1. Check Django documentation: https://docs.djangoproject.com/
2. Review error logs for specific issues
3. Ensure all dependencies are installed correctly

## Next Steps

After setup:

1. Create user accounts through the registration page
2. Create your first project
3. Add drawings to the project
4. Test the approval workflow
5. Configure email notifications
6. Customize the interface as needed

Your DocuHub application is now ready for use!