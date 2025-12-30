# OBSOLETE — DocuHub Setup Instructions

**Status:** OBSOLETE — duplicate
**Reason:** Duplicate of setup_guide.md with unclear filename. Superseded by /docs/02_modules/08-environment-setup.md
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
touch apps/__init__.py

# Create Django apps
python manage.py startapp projects apps/projects
python manage.py startapp accounts apps/accounts
python manage.py startapp notifications apps/notifications
python manage.py startapp core apps/core
```

### 4. Environment Configuration

Create a `.env` file in your project root:
```env
SECRET_KEY=your-very-secret-key-here-make-it-long-and-random
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
BREVO_API_KEY=your-brevo-api-key-here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
BREVO_SENDER_NAME=DocuHub System
FRONTEND_URL=http://localhost:8000
REDIS_URL=redis://localhost:6379/0
```

**Note**: SQLite database will be automatically created as `db.sqlite3` in your project root.

### 5. Apply All Files

Copy all the provided files to their respective locations:

- `requirements.txt` → project root
- `docuhub/settings.py` → replace existing
- `docuhub/urls.py` → replace existing
- All app files to their respective directories
- Template files to `templates/` directory

### 6. Create Directory Structure

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

### 7. Database Migration

```bash
# Create and apply migrations
python manage.py makemigrations accounts
python manage.py makemigrations projects
python manage.py makemigrations notifications
python manage.py makemigrations core
python manage.py migrate
```

### 8. Create Superuser

```bash
python manage.py createsuperuser
```

### 9. Run Development Server

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
├── db.sqlite3                    # SQLite database (auto-created)
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

## SQLite Database Benefits

✅ **No Installation Required** - SQLite comes built-in with Python
✅ **Zero Configuration** - No database server setup needed
✅ **File-based** - Database stored as a single file
✅ **Perfect for Development** - Easy to backup, move, or reset
✅ **Production Ready** - Suitable for small to medium applications

## Database Management

### View Database Contents
```bash
# Install SQLite browser (optional)
# Windows: Download DB Browser for SQLite
# macOS: brew install --cask db-browser-for-sqlite
# Linux: sudo apt-get install sqlitebrowser

# Or use command line
sqlite3 db.sqlite3
.tables
.schema projects
SELECT * FROM projects;
.quit
```

### Reset Database
```bash
# Delete database file
rm db.sqlite3

# Recreate database
python manage.py migrate
python manage.py createsuperuser
```

### Backup Database
```bash
# Simple file copy
cp db.sqlite3 backup_$(date +%Y%m%d).sqlite3

# Or use Django dumpdata
python manage.py dumpdata > backup_data.json
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

**Note**: Email features will work without Brevo setup, but emails won't be sent.

## Production Considerations

For production deployment with SQLite:

### Pros:
- Simple deployment (just copy the database file)
- No database server maintenance
- Fast for read-heavy workloads
- Built-in backup (file copy)

### Cons:
- No concurrent writes (Django handles this)
- File-based (not suitable for distributed systems)
- Limited to single server deployment

### When to Switch to PostgreSQL:
- Multiple servers needed
- Heavy concurrent write operations
- Need advanced database features
- Scaling beyond single server

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all apps are properly added to `INSTALLED_APPS`
2. **Database Locked**: Close any open SQLite browser connections
3. **Template Errors**: Ensure template directories are created
4. **Static Files**: Run `python manage.py collectstatic` for production
5. **Permission Errors**: Check file permissions on db.sqlite3

### Database Issues
```bash
# Check database integrity
sqlite3 db.sqlite3 "PRAGMA integrity_check;"

# Rebuild database if corrupted
rm db.sqlite3
python manage.py migrate
```

### Getting Help

1. Check Django documentation: https://docs.djangoproject.com/
2. SQLite documentation: https://sqlite.org/docs.html
3. Review error logs for specific issues
4. Ensure all dependencies are installed correctly

## Migration to PostgreSQL (Future)

If you need to switch to PostgreSQL later:

1. Install PostgreSQL and psycopg2-binary
2. Create PostgreSQL database
3. Update DATABASE_URL in .env
4. Export data: `python manage.py dumpdata > data.json`
5. Migrate: `python manage.py migrate`
6. Import data: `python manage.py loaddata data.json`

## Next Steps

After setup:

1. Create user accounts through the registration page
2. Create your first project
3. Add drawings to the project
4. Test the approval workflow
5. Configure email notifications (optional)
6. Customize the interface as needed

Your DocuHub application with SQLite is now ready for use!
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