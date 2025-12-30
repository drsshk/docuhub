# DocuHub System Architecture and Documentation

## System Architecture

### Project Structure

The project is organized into two main parts: a Django backend and a React frontend.

```
docuhub/
├── apps/                              # Django apps
│   ├── accounts/                      # User management, authentication, and profiles
│   ├── core/                          # Core application logic and versioning
│   ├── notifications/                 # Email and notification services
│   └── projects/                      # Project and document management
├── docuhub/                          # Django project settings
│   ├── settings.py                   # Main settings file
│   └── urls.py                       # Root URL configuration
├── frontend/                          # React frontend application
│   ├── src/                           # Frontend source code
│   │   ├── components/                # Reusable React components
│   │   ├── services/                  # API services for backend communication
│   │   └── pages/                     # Application pages
│   ├── package.json                   # Frontend dependencies
│   └── vite.config.ts                 # Vite configuration
├── templates/                         # Django templates
├── static/                            # Static assets (CSS, JS, images)
├── media/                             # User-uploaded files
├── docs/                             # Documentation files
│   ├── API_DOCUMENTATION.md          # Complete API reference
│   ├── POSTMAN_COLLECTION_GUIDE.md   # Postman setup guide
│   └── architecture.md               # This file
├── manage.py                          # Django management script
└── requirements.txt                   # Python dependencies
```

---

## New ERD Architecture (2024)

### Core Design Principles

The system has been restructured based on a **document-centric workflow** where:
- **Projects** group documents by version but have **no status**
- **Documents** carry the workflow status and approval state
- **Project Groups** link multiple versions of the same logical project
- **Approval workflows** happen at the document level

### Database Schema

#### Primary Entities

**ProjectGroup**
- Logical family for all versions of the same project
- Contains basic project information (name, client, code)
- Links to multiple Project versions
- Table: `project_groups`

**Project** 
- Individual project versions (V001, V002, etc.)
- **No status field** - status lives on Documents
- Snapshot of project metadata for that version
- Links to ProjectGroup and contains Documents
- Table: `projects`

**Document** (formerly Drawing)
- **Core workflow entity** - where status lives
- Status choices: Draft → Submitted → Pending_Review → [Approved|Rejected|Revision_Required]
- Belongs to a specific Project version
- Can have file attachments
- Table: `documents`

**ApprovalHistory**
- Logs every approval action taken on documents
- Tracks status transitions (from_status → to_status)
- Includes reviewer comments and metadata
- Table: `approval_history`

**ProjectHistory**
- Audit trail for project and document changes
- Event types: PROJECT_CREATED, DOCUMENT_ADDED, etc.
- JSON payload for before/after snapshots
- Table: `project_history`

#### User Management Entities

**UserProfile**
- Extended user information with organizational roles
- Role choices: submitter, approver, admin, viewer
- Department, job title, manager relationships
- Table: `user_profiles`

**NotificationPreferences**
- User email notification settings
- Digest frequency options (immediate, daily, weekly)
- Event-specific toggles (submission, approval, etc.)
- Table: `notification_preferences`

**EmailLog**
- Email delivery tracking and status monitoring
- Provider integration (Brevo/SendGrid)
- Delivery metrics (sent, opened, clicked)
- Table: `email_logs`

**AuditLog**
- Cross-cutting security and system events
- Login attempts, permission changes
- System-wide audit trail
- Table: `audit_logs`

**UserSession**
- User session tracking
- IP address and user agent logging
- Session lifecycle management
- Table: `user_sessions`

#### Key Relationships

```
ProjectGroup (1) → (Many) Project
Project (1) → (Many) Document
Document (1) → (Many) ApprovalHistory
Project (1) → (Many) ProjectHistory
User (1) → (1) UserProfile
User (1) → (1) NotificationPreferences
User (1) → (Many) EmailLog
```

---

## Document-Centric Workflow

### Status Flow

Documents follow this lifecycle:

```
Draft → Submitted → Pending_Review → {
    Approved,
    Rejected,
    Revision_Required
} → [Back to Draft for revisions]
```

### Workflow States

**Draft**
- Initial creation state
- Full editing capabilities
- Can add/update file attachments

**Submitted** 
- Ready for review
- No editing allowed
- Awaiting reviewer assignment

**Pending_Review**
- Under active review
- Reviewer can add comments
- Status transition pending

**Approved**
- Final approval granted
- Document locked for changes
- Can be used for construction/implementation

**Rejected**
- Document rejected by reviewer
- Requires significant changes
- Can be restarted as new Draft

**Revision_Required**
- Conditional approval with required changes
- Reviewer has specified needed modifications
- Returns to Draft for updates

### Project Versioning

Projects are versioned through ProjectGroups:
- ProjectGroup contains metadata (name, client, code)
- Each Project is a version (V001, V002, V003...)
- Only one Project per group can be `is_latest=True`
- Versions preserve historical snapshots

---

## Business Logic Services

### Project Management Services
```python
# apps/projects/services.py
ProjectSubmissionService         # Document submission workflow
ProjectVersionService           # Version creation and management  
ProjectStatsService             # Analytics and reporting
ProjectBulkOperationsService    # Administrative bulk operations
ProjectRestoreService           # Project restoration functionality
```

### Document Management Services
```python
# apps/projects/services.py
DocumentWorkflowService         # Document status transitions
DocumentValidationService       # File and metadata validation
DocumentApprovalService         # Approval process management
```

### User Management Services
```python
# apps/accounts/services.py
UserAccountService              # Account creation and management
UserSessionService             # Session tracking and security
UserProfileService             # Profile and role management
UserStatsService               # User analytics and reporting
```

### Communication Services
```python
# apps/notifications/services.py
BrevoEmailService              # Email delivery via Brevo API
NotificationService            # In-app notifications
EmailTemplateService           # Dynamic email generation
WebhookService                 # External system notifications
```

---

## API Architecture

### RESTful Design

The API follows REST principles with resource-based URLs:

```
/api/project-groups/           # ProjectGroup CRUD
/api/projects/                 # Project CRUD
/api/documents/                # Document CRUD  
/api/approval-history/         # Audit trails
/api/project-history/          # Change logs
/api/auth/token/               # Authentication
/api/auth/profile/             # User management
```

### Custom Workflow Endpoints

```
POST /api/projects/{id}/submit/    # Submit project for review
POST /api/projects/{id}/review/    # Review and approve/reject
```

### Authentication & Authorization

- **Token-based authentication** for API access
- **Role-based permissions** (submitter, approver, admin, viewer)
- **Object-level permissions** for project access
- **Rate limiting** for API endpoints

---

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- Django 4.2.7
- MySQL 5.7+ or PostgreSQL 12+
- 4GB RAM minimum, 8GB recommended
- 20GB storage minimum

### Recommended Production Setup
- Python 3.11+
- Django 4.2.7 with security updates
- MySQL 8.0+ with optimized configuration
- Redis for caching and sessions
- Nginx as reverse proxy
- SSL/TLS certificates
- Backup automation

---

## Security Implementation

### Authentication & Authorization
- **Multi-factor authentication** support
- **Role-based access control** with granular permissions
- **Session management** with automatic timeouts
- **CSRF protection** for web forms
- **Object-level permissions** for resource access

### Input Validation & Sanitization
- **Model-level validation** with custom validators
- **File upload security** with type/size restrictions  
- **XSS prevention** through template escaping
- **SQL injection prevention** via Django ORM
- **API input sanitization** for all endpoints

### Rate Limiting & Monitoring
- **API rate limiting** per user and endpoint
- **Login attempt monitoring** with lockout protection
- **Audit logging** for all sensitive operations
- **Real-time monitoring** of security events

### Security Headers
```python
# Security headers implemented
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
```

---

## Performance Optimization

### Database Optimization
- **Query optimization** with select_related/prefetch_related
- **Database indexing** on frequently queried fields
- **Connection pooling** for high concurrency
- **Query caching** for expensive operations

### API Performance
- **Response caching** for read-heavy endpoints
- **Pagination** for large result sets
- **Field filtering** to reduce payload size
- **Background tasks** for heavy operations

### File Handling
- **File compression** for document storage
- **CDN integration** for static assets
- **Streaming uploads** for large files
- **Image optimization** for thumbnails

---

## Monitoring & Maintenance

### Logging Strategy
```python
# Logging levels and destinations
DEBUG    → Development debugging
INFO     → Application events  
WARNING  → Potential issues
ERROR    → Application errors
CRITICAL → System failures

# Log destinations
- Application logs → logs/django.log
- Security logs → logs/security.log
- Email logs → database + logs/email.log
- API logs → logs/api.log
```

### Health Monitoring
```bash
# Health check endpoints
GET /api/health/              # System health
GET /api/health/database/     # Database connectivity
GET /api/health/email/        # Email service status
GET /api/health/storage/      # File storage status
```

### Maintenance Commands
```bash
# Database maintenance
python manage.py migrate                    # Apply migrations
python manage.py cleanup_sessions          # Clean old sessions
python manage.py cleanup_email_logs        # Archive old emails

# User management
python manage.py create_superuser          # Create admin user
python manage.py setup_roles              # Initialize roles
python manage.py user_stats               # User analytics

# System maintenance  
python manage.py collectstatic            # Collect static files
python manage.py compress                 # Compress assets
python manage.py check                    # System health check
```

---

## Backup & Recovery

### Database Backup Strategy
```bash
# MySQL backup
mysqldump --single-transaction --routines --triggers \
  docuhub > backup_$(date +%Y%m%d_%H%M%S).sql

# PostgreSQL backup  
pg_dump docuhub > backup_$(date +%Y%m%d_%H%M%S).sql
```

### File System Backup
```bash
# Media files backup
rsync -av --delete media/ backup/media/

# Static files backup
rsync -av --delete staticfiles/ backup/static/

# Configuration backup
rsync -av --exclude='*.pyc' --exclude='__pycache__' \
  . backup/source/
```

### Recovery Procedures
1. **Database recovery**: Restore from latest SQL dump
2. **Media recovery**: Restore uploaded files from backup
3. **Configuration recovery**: Restore settings and environment
4. **Dependency recovery**: Reinstall packages from requirements.txt

---

## Deployment Architecture

### Production Deployment
```
[Load Balancer] 
    ↓
[Nginx Reverse Proxy]
    ↓
[Gunicorn WSGI Server]
    ↓
[Django Application]
    ↓
[MySQL/PostgreSQL Database]
    ↓
[Redis Cache/Sessions]
```

### Environment Configuration
```python
# Production settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 3600,
    }
}
```

---

## Troubleshooting Guide

### Common Issues

**Database Connection Errors**
```bash
# Check database service
systemctl status mysql
systemctl start mysql

# Test connection
python manage.py dbshell

# Check migrations
python manage.py showmigrations
python manage.py migrate
```

**Email Delivery Issues**
```python
# Check email configuration
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])

# Review email logs in admin interface
/admin/accounts/emaillog/
```

**Authentication Problems**
```bash
# Create superuser
python manage.py createsuperuser

# Reset user password
python manage.py changepassword username

# Check user permissions
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='username')
>>> user.user_permissions.all()
```

**File Upload Issues**
```python
# Check media settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Check file permissions
ls -la media/
chmod 755 media/
```

### Debug Mode
```python
# Enable debug mode (development only)
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

---

This architecture supports the new document-centric workflow while maintaining scalability, security, and maintainability for enterprise document management requirements.