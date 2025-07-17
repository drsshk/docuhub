# DocuHub - Technical Drawing Version Management System

## Executive Summary

DocuHub is an enterprise-grade Django web application designed to provide a **Streamlined Document Workflow** for managing technical drawing versions with automated approval workflows, comprehensive audit trails, and integrated email notification systems. The platform provides structured project lifecycle management with role-based access control and enterprise security features.

## User Registration

User registration in DocuHub is handled by administrators. When an admin creates a new user, a password is automatically generated and sent to the user's email. For security, passwords are encrypted and cannot be viewed by anyone, including administrators, in the database.

## Recent Updates

### Drawing Status Management System (Latest)
Enhanced granular control over individual drawing approvals during project review:
- **Status Synchronization**: Main project decision automatically syncs all drawing statuses with intelligent mapping
- **Individual Override**: Reviewers can modify individual drawing statuses after bulk sync for granular control
- **Clean Review Interface**: Hidden edit/delete actions during review to focus on approval decisions
- **CSRF Protection**: Secure HTMX requests for real-time status updates
- **Visual Feedback**: Color-coded status indicators with smooth UI transitions

### Project Review System Overhaul
Major improvements to the project approval workflow and permissions:
- **Fixed approval status inconsistencies**: Corrected template status names to match model definitions (`Approved_Endorsed`, `Rescinded_Revoked`)
- **Enhanced ReviewForm**: Added all 4 approval options (Approved & Endorsed, Conditional Approval, Request for Revision, Rejected)
- **Role-based permissions**: Migrated from Django Groups to custom Role model (`apps.accounts.models.Role`)
- **Conditional Approval workflow**: When projects receive conditional approval, users can no longer edit directly but must create new versions
- **Permission logic refinement**: 
  - `Conditional_Approval` status removed from editable statuses
  - `Conditional_Approval` added to versionable statuses
  - Users must create new versions to address conditional approval requirements

### Role System Implementation
Replaced Django Groups with custom Role model:
- **Roles**: Admin, Approver, Submitter, Viewer
- **Permission classes updated**: All permission logic now uses `user.profile.role.name`
- **Template integration**: Uses existing `has_role` template tag
- **Setup function**: `setup_project_roles()` replaces group-based setup

### Previous Changes
- **Project Folder Link Migration**: Moved project folder links from drawings to project level
- **UUID Import Fix**: Resolved project submission errors with missing UUID imports
- **Database Schema Updates**: Applied migration `0005_remove_drawing_drawing_list_link_and_more.py`

## System Architecture

### Technology Stack
- **Backend Framework**: Django 4.2.7 with Python 3.8+
- **Database**: MySQL with SQLite development support

- **Email Service**: Brevo API integration
- **API Framework**: Django REST Framework
- **Authentication**: Token-based and session authentication
- **Security**: CSRF protection, rate limiting, security headers

### Core Features
- Automated version control with incremental numbering
- Multi-stage approval workflow with status transitions
- Role-based permission system (Admin, Approver, Submitter, Viewer)
- Email notification system with delivery tracking
- RESTful API with comprehensive endpoints
- Comprehensive audit logging and session tracking
- Bulk operations for administrative efficiency
- Project restoration and recovery mechanisms

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- Django 4.2.7
- MySQL 5.7+ 
- 2GB RAM minimum, 4GB recommended
- 10GB storage minimum


## Installation and Configuration

### Environment Setup

#### 1. Repository Clone and Virtual Environment
```bash
git clone <repository-url>
cd docuhub
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### 2. Environment Configuration
Create a `.env` file in the project root directory:

```env
# Core Django Configuration
DJANGO_SETTINGS_MODULE=docuhub.settings
SECRET_KEY=your-cryptographically-secure-secret-key
DEBUG=False

# Network Configuration
ALLOWED_HOSTS=your-server-ip,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://your-server-ip,http://localhost:8000,http://127.0.0.1:8000
FRONTEND_URL=http://your-server-ip

# Database Configuration
DB_NAME=docuhub_production
DB_USER=docuhub_user
DB_PASSWORD=secure_database_password
DB_HOST=your-database-host
DB_PORT=3306

# Email Service Configuration (Brevo)
BREVO_API_KEY=your-brevo-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
BREVO_SENDER_NAME=DocuHub System

# Cache and Session Configuration


# Email Template Configuration
EMAIL_TEMPLATE_PROJECT_SUBMITTED=1
EMAIL_TEMPLATE_PROJECT_APPROVED=2
EMAIL_TEMPLATE_PROJECT_REJECTED=3
EMAIL_TEMPLATE_PROJECT_REVISE_RESUBMIT=4
EMAIL_TEMPLATE_PROJECT_OBSOLETE=5
EMAIL_TEMPLATE_ADMIN_NEW_SUBMISSION=6
EMAIL_TEMPLATE_ADMIN_RESUBMISSION=7

# Optional: HTTPS Configuration
USE_HTTPS=False

# Optional: Monitoring
SENTRY_DSN=your-sentry-dsn-for-error-tracking
```

#### 3. Database Initialization
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py setup_roles
```

#### 4. Application Deployment
```bash
# Development Server
python manage.py runserver 0.0.0.0:8000

# Production with Gunicorn
gunicorn docuhub.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Production Deployment

#### Web Server Configuration (Nginx)
```nginx
server {
    listen 80;
    server_name your-server-ip;
    client_max_body_size 100M;
    
    location /static/ {
        alias /path/to/docuhub/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /path/to/docuhub/media/;
        expires 7d;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

## System Architecture Documentation

### Application Structure
```
docuhub/
├── apps/                              # Modular application components
│   ├── accounts/                      # User management and authentication
│   │   ├── models.py                 # User profiles, roles, audit logs
│   │   ├── services.py               # User account business logic
│   │   ├── views.py                  # Authentication controllers
│   │   └── utils.py                  # Utility functions
│   ├── projects/                      # Project lifecycle management
│   │   ├── models.py                 # Project, Drawing, ApprovalHistory
│   │   ├── services.py               # Business logic services
│   │   ├── api_views.py              # REST API endpoints
│   │   ├── permissions.py            # Access control logic
│   │   └── validators.py             # Data validation functions
│   ├── notifications/                 # Email notification system
│   │   ├── models.py                 # Email logs and preferences
│   │   ├── services.py               # Email delivery services
│   │   └── views.py                  # Notification management
│   └── core/                          # Core application functionality
│       ├── models.py                 # Version tracking, system settings
│       ├── views.py                  # Dashboard and utilities
│       └── context_processors.py     # Global template context
├── templates/                         # HTML template system
├── static/                           # Static assets (CSS, JS, images)
├── media/                            # User-uploaded files
├── docuhub/                          # Django project configuration
│   ├── settings.py                   # Application configuration
│   ├── urls.py                       # URL routing configuration
│   └── wsgi.py                       # WSGI deployment interface
└── requirements.txt                   # Python dependencies
```

### Database Schema

#### Core Entities
- **Project**: Central entity with version control and status management
- **Drawing**: Technical drawing references with validation
- **ApprovalHistory**: Complete audit trail of status changes
- **ProjectHistory**: Detailed submission and approval logging
- **UserProfile**: Extended user information with organizational data
- **EmailLog**: Email delivery tracking and status monitoring

#### Key Relationships
- Projects have one-to-many relationship with Drawings
- Projects maintain version hierarchy through self-referential foreign keys
- ApprovalHistory provides complete audit trail for all status changes
- UserProfile extends Django's built-in User model with organizational data

### Business Logic Services

#### Project Management Services
```python
# apps/projects/services.py
ProjectStatsService              # Statistical reporting and analytics
ProjectSubmissionService         # Submission and approval workflow
ProjectVersionService           # Version creation and management
ProjectBulkOperationsService    # Administrative bulk operations
ProjectRestoreService           # Project restoration functionality
```

#### User Management Services
```python
# apps/accounts/services.py
UserAccountService              # Account creation and management
UserSessionService             # Session tracking and cleanup
UserStatsService               # User analytics and reporting
```

#### Communication Services
```python
# apps/notifications/services.py
BrevoEmailService              # Email delivery and tracking
```

## Workflow Documentation

### Project Lifecycle States
```
Draft → Pending Approval → {
    Approved & Endorsed,
    Conditional Approval,
    Request for Revision,
    Rejected,
    Rescinded & Revoked
} → Obsolete
```

#### State Definitions
- **Draft**: Initial creation state, full editing capabilities
- **Pending Approval**: Under administrative review, no editing allowed
- **Approved & Endorsed**: Final approval, project locked
- **Conditional Approval**: Approved with conditions, **direct editing disabled** - users must create new version to address requirements
- **Request for Revision**: Triggers new version creation
- **Rejected**: Project rejected, requires administrative action for recovery
- **Rescinded & Revoked**: Previously approved project revoked
- **Obsolete**: Archived state, no further actions permitted

### Drawing Status Management

#### Drawing Status Features
The system provides granular drawing-level status management during the project review process:

##### Status Synchronization
- **Bulk Status Updates**: When reviewers change the main project decision dropdown, all drawing statuses automatically sync to match the decision
- **Individual Control**: After bulk sync, reviewers can still modify individual drawing statuses as needed
- **Real-time Updates**: Status changes are immediately reflected in the UI with visual feedback

##### Status Mapping
The following decision-to-status mappings are automatically applied:
- **Approve** → `Approved_Endorsed`
- **Conditional Approval** → `Conditional_Approval`
- **Request for Revision** → `Request_for_Revision`
- **Reject** → `Rejected`

##### Review Interface Features
- **Clean Review UI**: During review, editing actions (Add Drawing, Edit, Delete) are hidden to focus on approval decisions
- **Visual Status Indicators**: Drawing statuses display with color-coded badges for quick visual identification
- **Contextual Actions**: Only relevant review actions are visible during the approval process

##### Drawing Status States
Each drawing can have the following statuses:
- **Draft**: Initial state, editable
- **Pending_Approval**: Under review
- **Approved_Endorsed**: Finalized and approved
- **Conditional_Approval**: Approved with conditions
- **Request_for_Revision**: Requires changes
- **Rejected**: Not approved
- **Rescinded_Revoked**: Previously approved but revoked
- **Obsolete**: Archived status

##### Technical Implementation
- **CSRF Protection**: All status update requests include proper CSRF tokens
- **HTMX Integration**: Real-time status updates without page reloads
- **Permission Checks**: Only authorized reviewers can modify drawing statuses during review
- **Audit Trail**: All status changes are logged for compliance tracking

### User Role Definitions

#### Project Administrator
- Complete system access and control
- Project creation, modification, and deletion across all users
- Bulk operations on multiple projects
- User management and role assignment
- System configuration and maintenance

#### Project Manager (Approver)
- Project review and approval authority
- Status modification capabilities
- Bulk approval operations
- Access to all submitted projects
- Cannot edit project content (separation of duties)

#### Project User (Submitter)
- Project creation and management within owned projects
- Submission for approval workflow
- Version creation for owned projects
- Access to own projects and all approved projects
- Editing restricted based on project status

#### Viewer
- Read-only access to approved projects
- No creation or modification capabilities
- Reserved for future implementation

## API Documentation

### Authentication
All API endpoints require authentication via one of the following methods:
- Session authentication (web interface)
- Token authentication (API clients)

### Core Endpoints

#### Project Management
```http
GET    /api/projects/              # List projects (paginated)
POST   /api/projects/              # Create new project
GET    /api/projects/{id}/         # Retrieve project details
PUT    /api/projects/{id}/         # Update project
DELETE /api/projects/{id}/         # Delete project
POST   /api/projects/{id}/submit/  # Submit for approval
POST   /api/projects/{id}/review/  # Administrative review
```

#### Drawing Management
```http
GET    /api/drawings/              # List drawings (paginated)
POST   /api/drawings/              # Create new drawing
GET    /api/drawings/{id}/         # Retrieve drawing details
PUT    /api/drawings/{id}/         # Update drawing
DELETE /api/drawings/{id}/         # Delete drawing
```

#### System Information
```http
GET    /api/current-version/       # Application version information
```

### API Response Format
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "pagination": {
    "count": 100,
    "next": "http://api.example.com/api/projects/?page=2",
    "previous": null
  }
}
```

## Security Implementation

### Authentication and Authorization
- Role-based access control with custom Role model (Admin, Approver, Submitter, Viewer)
- Object-level permissions for project ownership
- Session timeout and secure cookie configuration
- CSRF protection on all state-changing operations

### Input Validation and Sanitization
- Model-level validation for all user inputs
- Custom validators for business logic enforcement
- XSS prevention through template auto-escaping
- SQL injection prevention through ORM usage

### Rate Limiting and Abuse Prevention
```python
# Rate limiting configuration
Authentication attempts:     5/5 minutes
Project submissions:        10/minute
API requests (users):       1000/hour
API requests (admins):      2000/hour
Bulk operations:           5/minute
```

### Security Headers
- Content Security Policy (CSP)
- HTTP Strict Transport Security (HSTS)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Referrer Policy: strict-origin-when-cross-origin

## Monitoring and Maintenance

### Logging Configuration
The application implements structured logging with the following levels:
- **DEBUG**: Development debugging information
- **INFO**: Normal operation events
- **WARNING**: Unusual but handled events
- **ERROR**: Error conditions requiring attention
- **CRITICAL**: Serious errors requiring immediate action

### Log Files
```bash
logs/development.log         # Development environment logs
logs/docuhub.log            # Production application logs
logs/errors.log             # Error-specific logs
logs/security.log           # Security events and violations
```

### Maintenance Commands
```bash
# Application version management
python manage.py version
python manage.py version --set 1.2.0

# Sample data generation
python manage.py create_sample_versions
python manage.py sample_data

# System maintenance
python manage.py setup_roles
python manage.py cleanup_sessions
```

### Health Monitoring
Monitor the following system metrics:
- Database connection status

- Email service connectivity
- Disk space utilization
- Memory and CPU usage
- Active user sessions

## Performance Optimization

### Database Optimization
- Strategic use of `select_related()` and `prefetch_related()`
- Database indexing on frequently queried fields
- Query optimization with `only()` and `defer()`
- Connection pooling for production environments

### Caching Strategy

- Template fragment caching
- Database query result caching
- Static file caching with appropriate headers

### Asset Optimization
- Static file compression and minification
- CSS and JavaScript bundling
- Image optimization and responsive delivery
- CDN integration for static assets

## Backup and Recovery

### Database Backup
```bash
# MySQL backup
mysqldump -u username -p database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
0 2 * * * /path/to/backup_script.sh
```

### File System Backup
```bash
# Media files backup
rsync -av /path/to/docuhub/media/ /backup/location/media/

# Static files backup
rsync -av /path/to/docuhub/staticfiles/ /backup/location/static/
```

### Recovery Procedures
1. Restore database from most recent backup
2. Restore media files from backup location
3. Restart application services
4. Verify system functionality
5. Update monitoring systems

## Troubleshooting Guide

### Common Issues

#### Database Connection Errors
```bash
# Verify database service status
systemctl status mysql

# Check database credentials in .env file
# Verify network connectivity to database host
```

#### Email Delivery Failures
```bash
# Check Brevo API key configuration
# Verify email template configuration
# Review email logs in Django admin
# Test API connectivity to Brevo service
```

#### Performance Issues
```bash
# Monitor database query performance

# Review application logs for errors
# Monitor system resource utilization
```

#### Authentication Problems
```bash
# Verify session configuration
# Check CSRF token handling
# Review user permissions and groups
# Validate rate limiting configuration
```

## Support and Maintenance

### Documentation Updates
This documentation should be updated when:
- New features are implemented
- Configuration changes are made
- Security updates are applied
- Performance optimizations are implemented

### Version Control
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Maintain changelog for all releases
- Tag releases in version control system
- Document breaking changes and migration steps

### Contact Information
- **System Administrator**: [Contact Information]
- **Technical Support**: [Support Channel]
- **Emergency Contact**: [Emergency Procedures]

---

**Document Version**: 1.0  
**Last Updated**: $(date)  
**Prepared By**: System Documentation Team  
**Approved By**: Technical Director  

*This document contains confidential and proprietary information. Distribution is restricted to authorized personnel only.*