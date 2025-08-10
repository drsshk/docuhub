# DocuHub System Architecture and Documentation

## System Architecture

### Project Structure

The project is organized into two main parts: a Django backend and a React frontend.

```
docuhub/
├── apps/                              # Django apps
│   ├── accounts/                      # User management, authentication
│   ├── core/                          # Core application logic
│   ├── notifications/                 # Email and in-app notifications
│   └── projects/                      # Project and drawing management
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
├── manage.py                          # Django management script
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
- Projects have a one-to-many relationship with Drawings.
- Projects maintain a version hierarchy through self-referential foreign keys.
- `ApprovalHistory` provides a complete audit trail for all status changes.
- `UserProfile` extends Django's built-in User model with organizational data.

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

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- Django 4.2.7
- MySQL 5.7+
- 2GB RAM minimum, 4GB recommended
- 10GB storage minimum

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
- **Draft**: Initial creation state, full editing capabilities.
- **Pending Approval**: Under administrative review, no editing allowed.
- **Approved & Endorsed**: Final approval, project locked.
- **Conditional Approval**: Approved with conditions, **direct editing disabled** - users must create a new version to address requirements.
- **Request for Revision**: Triggers new version creation.
- **Rejected**: Project rejected, requires administrative action for recovery.
- **Rescinded & Revoked**: Previously approved project revoked.
- **Obsolete**: Archived state, no further actions permitted.

### Drawing Status Management

The system provides granular drawing-level status management during the project review process. When a reviewer changes the main project decision, all drawing statuses automatically sync to match, but can be individually overridden.

#### Status Mapping
- **Approve** → `Approved_Endorsed`
- **Conditional Approval** → `Conditional_Approval`
- **Request for Revision** → `Request_for_Revision`
- **Reject** → `Rejected`

### User Role Definitions

-   **Project Administrator**: Complete system access and control.
-   **Project Manager (Approver)**: Project review and approval authority.
-   **Project User (Submitter)**: Project creation and management for their own projects.
-   **Viewer**: Read-only access to approved projects.

## API Documentation

### Authentication
All API endpoints require authentication via session or token authentication.

### Core Endpoints

#### Project Management
```http
GET    /api/projects/              # List projects
POST   /api/projects/              # Create new project
GET    /api/projects/{id}/         # Retrieve project details
PUT    /api/projects/{id}/         # Update project
DELETE /api/projects/{id}/         # Delete project
POST   /api/projects/{id}/submit/  # Submit for approval
POST   /api/projects/{id}/review/  # Administrative review
```

#### Drawing Management
```http
GET    /api/drawings/              # List drawings
POST   /api/drawings/              # Create new drawing
GET    /api/drawings/{id}/         # Retrieve drawing details
PUT    /api/drawings/{id}/         # Update drawing
DELETE /api/drawings/{id}/         # Delete drawing
```

## Security Implementation

-   **Authentication and Authorization**: Role-based access control, object-level permissions, session timeouts, and CSRF protection.
-   **Input Validation**: Model-level validation, custom validators, XSS prevention, and SQL injection prevention via ORM.
-   **Rate Limiting**: Applied to authentication, API requests, and bulk operations.
-   **Security Headers**: Includes CSP, HSTS, X-Frame-Options, and others.

## Monitoring and Maintenance

### Logging
Structured logging is implemented across DEBUG, INFO, WARNING, ERROR, and CRITICAL levels, with logs stored in the `logs/` directory.

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

## Performance Optimization

-   **Database**: Use of `select_related`/`prefetch_related`, indexing, and query optimization.
-   **Caching**: Template fragment and database query caching.
-   **Assets**: Compression, minification, and bundling of static assets.

## Backup and Recovery

### Database Backup
Standard `mysqldump` procedures are recommended for database backups.

### File System Backup
Regular backups of the `media/` and `staticfiles/` directories should be performed using tools like `rsync`.

## Troubleshooting Guide

-   **Database Connection Errors**: Verify service status and credentials in the `.env` file.
-   **Email Delivery Failures**: Check API keys and review email logs in the Django admin.
-   **Authentication Problems**: Verify session configuration, CSRF tokens, and user permissions.
