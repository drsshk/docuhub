# DocuHub Environment Setup Guide

This guide provides comprehensive instructions for setting up the DocuHub environment configuration.

## Overview

DocuHub uses environment variables to configure database connections, email services, security settings, and other application parameters. This approach allows the same codebase to work across development, staging, and production environments with different configurations.

## Quick Setup

### 1. Copy Environment Template
```bash
# Copy the template file
cp .env.example .env

# Edit with your actual values
nano .env  # or your preferred editor
```

### 2. Required Variables
At minimum, you must set these variables:
- `SECRET_KEY` - Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Database credentials
- `DEBUG` - Set to `False` in production

## Environment Variables Reference

### 🔑 **Critical Settings** (Required)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ Yes | None | Django secret key for cryptographic signing |
| `DEBUG` | ✅ Yes | False | Debug mode - MUST be False in production |
| `DB_NAME` | ✅ Yes | None | MySQL database name |
| `DB_USER` | ✅ Yes | None | MySQL username |
| `DB_PASSWORD` | ✅ Yes | None | MySQL password |
| `DB_HOST` | ✅ Yes | None | MySQL host (usually localhost) |
| `DB_PORT` | ✅ Yes | None | MySQL port (usually 3306) |

### 🌐 **Web Server Configuration**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ALLOWED_HOSTS` | ✅ Yes | None | Comma-separated list of allowed hostnames |
| `CORS_ALLOWED_ORIGINS` | ✅ Yes | None | Comma-separated list of allowed frontend origins |
| `FRONTEND_URL` | ✅ Yes | http://localhost:8000 | Base URL for frontend application |
| `USE_HTTPS` | No | False | Enable HTTPS security headers |

### 📧 **Email Configuration** (Brevo)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BREVO_API_KEY` | For email | None | Brevo API key for transactional emails |
| `BREVO_SMTP_KEY` | For email | None | Brevo SMTP password |
| `DEFAULT_FROM_EMAIL` | For email | info@docuhub.rujilabs.com | Default sender email address |
| `BREVO_SENDER_NAME` | No | DocuHub System | Display name for email sender |

### 📧 **Email Templates** (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_TEMPLATE_PROJECT_SUBMITTED` | No | 1 | Brevo template ID for project submission |
| `EMAIL_TEMPLATE_PROJECT_APPROVED` | No | 2 | Brevo template ID for project approval |
| `EMAIL_TEMPLATE_PROJECT_REJECTED` | No | 3 | Brevo template ID for project rejection |
| `EMAIL_TEMPLATE_PROJECT_REVISE_RESUBMIT` | No | 4 | Brevo template ID for revision requests |
| `EMAIL_TEMPLATE_PROJECT_OBSOLETE` | No | 5 | Brevo template ID for obsolete projects |
| `EMAIL_TEMPLATE_ADMIN_NEW_SUBMISSION` | No | 6 | Brevo template ID for admin notifications |
| `EMAIL_TEMPLATE_ADMIN_RESUBMISSION` | No | 7 | Brevo template ID for admin resubmissions |

### 🔄 **Caching & Background Tasks** (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | No | redis://localhost:6379/0 | Redis connection for caching and Celery |

### 📊 **Monitoring** (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENTRY_DSN` | No | None | Sentry DSN for error tracking |

### 🎨 **Email Branding** (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_COMPANY_NAME` | No | DocuHub | Company name in emails |
| `EMAIL_LOGO_URL` | No | None | Logo URL for email templates |
| `EMAIL_WELCOME_MESSAGE` | No | Default message | Welcome message for new users |

## Environment-Specific Configuration

### 📝 **Development Environment**

```bash
# .env for development
SECRET_KEY=dev_secret_key_not_for_production
DEBUG=True
DB_NAME=docuhub_dev
DB_USER=dev_user
DB_PASSWORD=dev_password
DB_HOST=localhost
DB_PORT=3306
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
FRONTEND_URL=http://localhost:8000
USE_HTTPS=False
```

### 🏭 **Production Environment**

```bash
# .env for production
SECRET_KEY=super_long_random_secret_key_for_production
DEBUG=False
DB_NAME=docuhub_production
DB_USER=docuhub_prod_user
DB_PASSWORD=very_secure_password
DB_HOST=your-mysql-server.com
DB_PORT=3306
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
FRONTEND_URL=https://your-domain.com
USE_HTTPS=True
BREVO_API_KEY=your_actual_brevo_api_key
BREVO_SMTP_KEY=your_actual_brevo_smtp_key
REDIS_URL=redis://your-redis-server:6379/0
SENTRY_DSN=https://your_sentry_dsn_here
```

## Setup Instructions by Environment

### 🔧 **Local Development Setup**

1. **Install Dependencies**
   ```bash
   # Install MySQL
   sudo apt install mysql-server  # Ubuntu/Debian
   # or
   brew install mysql             # macOS

   # Install Redis (optional)
   sudo apt install redis-server  # Ubuntu/Debian
   # or  
   brew install redis             # macOS
   ```

2. **Create Database**
   ```sql
   CREATE DATABASE docuhub_dev;
   CREATE USER 'dev_user'@'localhost' IDENTIFIED BY 'dev_password';
   GRANT ALL PRIVILEGES ON docuhub_dev.* TO 'dev_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Configure Environment**
   ```bash
   # Copy template
   cp .env.example .env
   
   # Generate secret key
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   
   # Update .env with your values
   nano .env
   ```

4. **Test Configuration**
   ```bash
   # Test Django configuration
   python manage.py check
   
   # Apply migrations
   python manage.py migrate
   
   # Create superuser
   python manage.py createsuperuser
   
   # Start development server
   python manage.py runserver
   ```

### 🚀 **Production Deployment Setup**

1. **Secure Secret Generation**
   ```bash
   # Generate production secret key
   python -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())" >> .env
   ```

2. **Database Setup**
   ```bash
   # Production database with secure credentials
   # Use environment-specific user with minimal privileges
   CREATE DATABASE docuhub_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'docuhub_prod'@'localhost' IDENTIFIED BY 'very_secure_password';
   GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX ON docuhub_production.* TO 'docuhub_prod'@'localhost';
   ```

3. **Email Service Setup**
   - Sign up for Brevo account
   - Create API key in Brevo dashboard
   - Set up SMTP credentials
   - Create email templates (optional)

4. **Redis Setup**
   ```bash
   # Install and configure Redis
   sudo apt install redis-server
   sudo systemctl enable redis-server
   sudo systemctl start redis-server
   ```

## Validation & Testing

### ✅ **Configuration Validation**

```bash
# Test all settings
python manage.py check --deploy

# Test database connection
python manage.py dbshell

# Test email configuration (if configured)
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])

# Test Redis connection (if configured)  
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')
```

### 🔍 **Common Issues & Solutions**

| Issue | Cause | Solution |
|-------|--------|----------|
| `NameError: name 'BASE_DIR' is not defined` | BASE_DIR defined after usage | ✅ **FIXED** - BASE_DIR now defined first |
| `django.db.utils.OperationalError` | Wrong database credentials | Check DB_* variables in .env |
| `CORS errors` | Wrong frontend origins | Update CORS_ALLOWED_ORIGINS |
| `Email not sending` | Missing Brevo configuration | Set BREVO_API_KEY and BREVO_SMTP_KEY |
| `Static files not loading` | Wrong ALLOWED_HOSTS | Add your domain to ALLOWED_HOSTS |

## Security Best Practices

### 🔒 **Production Security Checklist**

- ✅ **Never use DEBUG=True in production**
- ✅ **Generate unique SECRET_KEY for each environment**
- ✅ **Use strong database passwords**
- ✅ **Restrict ALLOWED_HOSTS to actual domains**
- ✅ **Use HTTPS in production (USE_HTTPS=True)**
- ✅ **Keep .env files out of version control**
- ✅ **Use environment-specific database users with minimal privileges**
- ✅ **Regularly rotate API keys and passwords**
- ✅ **Enable error tracking with Sentry**
- ✅ **Use Redis AUTH if Redis is network-accessible**

### 🚫 **What NOT to do**

- ❌ Don't commit .env files to git
- ❌ Don't use the same SECRET_KEY across environments
- ❌ Don't use root database credentials
- ❌ Don't set DEBUG=True in production
- ❌ Don't use weak passwords
- ❌ Don't expose Redis without authentication
- ❌ Don't ignore SSL certificate warnings

## Environment Variable Loading Order

DocuHub loads environment variables in this order:

1. **System environment variables** (highest priority)
2. **.env file** (if present)
3. **Default values** in settings.py (lowest priority)

This means you can override .env values by setting system environment variables.

## Troubleshooting

### 📋 **Debugging Environment Issues**

```bash
# Check current environment variables
python manage.py shell
>>> import os
>>> print("DEBUG:", os.getenv('DEBUG'))
>>> print("DB_NAME:", os.getenv('DB_NAME'))

# Test specific settings
python manage.py diffsettings

# Validate deployment configuration
python manage.py check --deploy
```

### 📞 **Getting Help**

If you encounter issues:

1. **Check the logs**: `tail -f logs/errors.log`
2. **Verify .env syntax**: No spaces around `=`, no quotes unless needed
3. **Test database connection**: `python manage.py dbshell`
4. **Check Django documentation**: [Environment Variables](https://docs.djangoproject.com/en/4.2/topics/settings/#environment-variables)

## Next Steps

After environment setup:

1. **Run migrations**: `python manage.py migrate`
2. **Create superuser**: `python manage.py createsuperuser`
3. **Collect static files**: `python manage.py collectstatic`
4. **Start application**: `python manage.py runserver` (development)

---

**Last Updated**: January 2, 2025  
**Related Documents**:
- [Deployment Guide](deployment_guide.md)
- [Architecture Overview](architecture.md)
- [Security Report](security_report.md)