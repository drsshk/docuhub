# DocuHub - Drawing Version Management System

A professional Django application for managing technical drawing versions with automated workflows, approval processes, and email notifications.

## 🚀 Features

✅ **Automatic Version Control** - Incremental version numbering for all projects with project grouping  
✅ **Approval Workflow** - Structured review process with admin oversight and status tracking  
✅ **Email Notifications** - Brevo integration for automated status updates with template management  
✅ **User Management** - Role-based permissions with detailed user profiles and session tracking  
✅ **Drawing Management** - External link storage with validation and discipline categorization  
✅ **Modern UI** - Responsive design with comprehensive template system  
✅ **Admin Dashboard** - Comprehensive management tools with pending approval queue  
✅ **Audit Trail** - Complete history tracking with approval history and user sessions
✅ **History Log** - Detailed log of project submissions including project, version, submitter, date, submission link, drawing quantity, drawing numbers, receipt ID, and approval status  
✅ **SQLite Database** - Simple setup with file-based storage and optimized indexes  
✅ **Service-Based Architecture** - Business logic extracted into dedicated service classes  
✅ **Comprehensive Validation** - Input validation at model and form levels with security checks  
✅ **Environment-Specific Settings** - Separate configurations for development and production  
✅ **Query Optimization** - Database queries optimized with select_related and prefetch_related  
✅ **Structured Logging** - Comprehensive logging system with file and console output  
✅ **Version Tracking System** - Built-in application version management with detailed release notes and modal display  

## 📋 System Requirements

- Python 3.8+
- Django 4.2.7
- SQLite3 (included with Python)
- Virtual environment (recommended)

## 🛠️ Installation & Setup

### 1. Clone and Setup Environment
```bash
git clone <repository-url>
cd docuhub
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy the example environment file and configure:
```bash
cp .env.example .env
# Edit .env with your specific settings
```

Key environment variables:
```env
# Django Environment Configuration
DJANGO_ENVIRONMENT=development
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=your-database-url # e.g., mysql://user:password@host:port/database or sqlite:///db.sqlite3
# For MySQL:
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_PORT=your-db-port

# Email Configuration (Brevo)
BREVO_API_KEY=your-brevo-api-key
DEFAULT_FROM_EMAIL=your-default-from-email
BREVO_SENDER_NAME=DocuHub System

ADMIN_EMAIL=your-admin-email

# Email Template IDs (Brevo)
EMAIL_TEMPLATE_PROJECT_SUBMITTED=1
EMAIL_TEMPLATE_PROJECT_APPROVED=2
EMAIL_TEMPLATE_PROJECT_REJECTED=3
EMAIL_TEMPLATE_PROJECT_REVISE_RESUBMIT=4
EMAIL_TEMPLATE_PROJECT_OBSOLETE=5
EMAIL_TEMPLATE_ADMIN_NEW_SUBMISSION=6
EMAIL_TEMPLATE_ADMIN_RESUBMISSION=7

# Frontend Configuration
FRONTEND_URL=http://localhost:8000

# Redis Configuration (for cache and Celery)
REDIS_URL=redis://localhost:6379/0

# CORS Configuration (production)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Production Email (SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Monitoring (optional)
SENTRY_DSN=your-sentry-dsn-here

# Admin URL (production security)
ADMIN_URL=secure-admin-path/
```

### 3. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

```

### 4. Run Development Server
```bash
python manage.py runserver
```

### 5. Access Application
- **Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Endpoints**: http://localhost:8000/api/

## 📁 Project Structure

```
docuhub/
├── apps/                          # Django applications
│   ├── accounts/                  # User management & authentication
│   │   ├── models.py             # User profiles, roles, sessions, audit logs
│   │   ├── views.py              # Authentication, profile management
│   │   ├── services.py           # User account business logic
│   │   ├── forms.py              # User forms and validation
│   │   ├── urls.py               # Account-related URLs
│   │   └── migrations/           # Database migrations
│   ├── projects/                  # Project and drawing management
│   │   ├── models.py             # Project, Drawing, ApprovalHistory, ProjectHistory
│   │   ├── views.py              # Project CRUD, approval workflow
│   │   ├── services.py           # Project business logic services
│   │   ├── validators.py         # Custom validation functions
│   │   ├── api_views.py          # REST API endpoints
│   │   ├── forms.py              # Project and drawing forms
│   │   ├── permissions.py        # Custom permission classes
│   │   └── serializers.py        # API serializers
│   ├── notifications/             # Email notification system
│   │   ├── models.py             # Notification preferences, email logs
│   │   ├── services.py           # Email sending services
│   │   └── views.py              # Notification management
│   ├── core/                      # Core functionality
│   │   ├── views.py              # Dashboard, home page, version management
│   │   ├── models.py             # Version tracking models
│   │   ├── forms.py              # Version management forms
│   │   ├── admin.py              # Version administration
│   │   ├── context_processors.py # Global template context
│   │   └── urls.py               # Core URLs
├── templates/                     # HTML templates
│   ├── base.html                 # Base template
│   ├── accounts/                 # User account templates
│   ├── projects/                 # Project-related templates
│   ├── notifications/            # Notification templates
│   └── core/                     # Core page templates
├── static/                        # Static files
│   ├── css/                      # Stylesheets
│   ├── js/                       # JavaScript files
│   └── images/                   # Static images
├── media/                         # User-uploaded files
├── docs/                          # Documentation
├── management/                    # Custom management commands
│   └── commands/
│       └── sample_data.py        # Generate sample data
├── docuhub/                       # Django project settings
│   ├── settings/                 # Environment-specific settings
│   │   ├── __init__.py          # Settings loader
│   │   ├── base.py              # Base settings
│   │   ├── development.py       # Development settings
│   │   └── production.py        # Production settings
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py                   # WSGI configuration
│   └── asgi.py                   # ASGI configuration
├── requirements.txt               # Python dependencies
├── manage.py                     # Django management script
├── .env.example                  # Environment configuration template
├── .gitignore                    # Git ignore rules
└── db.sqlite3                    # SQLite database
```

## 🔄 User Workflow

### Standard User Journey
1. **Registration/Login** - Create account or sign in <--- admin will approve because user can login
2. **Profile Setup** - Complete user profile with department, job title
3. **Create Project** - Add project details (starts as Draft status)
4. **Add Drawings** - Include drawing numbers (4-character alphanumeric) and external links
5. **Submit for Approval** - Send to admin for review (status: Pending Approval)
6. **Admin Review** - Admin approves/rejects with comments
7. **Email Notifications** - Automatic updates for all status changes
8. **Version Management** - Create new versions when needed

### Project Status Flow
```
Draft → Pending Approval → Approved & Endorsed/Conditional Approval/Request for Revision/Rejected/Rescinded & Revoked → Obsolete
```

#### Status Definitions
- **Draft**: Initial project creation state - submitter can edit
- **Pending Approval**: Project submitted and awaiting review
- **Approved & Endorsed**: Fully approved project - no further edits allowed
- **Conditional Approval**: Approved with conditions - submitter can edit and resubmit
- **Request for Revision**: Reviewer requests changes - creates new version
- **Rejected**: Project rejected - no edits allowed
- **Rescinded & Revoked**: Previously approved project revoked - no edits allowed
- **Obsolete**: Project marked as obsolete - archived state

## 👥 User Roles & Permissions

### 1. Admin (Project Administrator)
This is the highest-level role with complete control over the system. Admins are typically superusers.

**Permissions:**
- **Full Project Management**: Can create, view, edit, and delete *any* project.
- **Full Drawing Management**: Can add, edit, and delete drawings from *any* project.
- **Review and Approve**: Can review, approve, reject, and request revisions for all projects.
- **Bulk Operations**: Can perform bulk actions (approve, reject, revise) on multiple projects at once.
- **Restore Projects**: Can restore projects that have been marked as "Obsolete."
- **User Management**: Has access to the Django admin panel to manage user accounts and assign roles.
- **History Log**: Access to 

### 2. Approver (Project Manager)
This role is responsible for the project review and approval process, ensuring quality and adherence to standards.

**Permissions:**
- **Review Projects**: Can review submitted projects and set status to:
  - **Approved & Endorsed**: Full approval without conditions
  - **Conditional Approval**: Approval with conditions requiring resubmission
  - **Request for Revision**: Request changes that create a new version
  - **Rejected**: Reject the project completely
  - **Rescinded & Revoked**: Revoke previously approved projects
- **View All Projects**: Can view all projects in the system, *except* for those in "Draft" status.
- **Bulk Operations**: Can perform bulk actions on pending projects from the admin dashboard.
- **Cannot Edit**: To maintain a separation of duties, Approvers cannot edit project details.
- **History Log**: Access to complete project approval history 

### 3. Submitter (Project User)
This is the standard user role for creating and managing projects.

**Permissions:**
- **Create and Manage Own Projects**: Can create new projects and edit their own projects when they are in "Draft" or "Conditional Approval" status only.
- **Submit for Approval**: Can submit their projects for review once they are ready.
- **Create New Versions**: Can create new versions when their projects have "Request for Revision" status.
- **View Permissions**:
    - Can view all of their own projects, regardless of status.
    - Can view all "Approved & Endorsed" projects from *any* user in the system.

**Edit Restrictions:**
- **No Editing**: Cannot edit projects in "Pending Approval," "Approved & Endorsed," "Rejected," "Rescinded & Revoked," or "Obsolete" status.
- **Version Creation**: "Request for Revision" status automatically creates a new version instead of allowing edits.

### 4. Viewer
This role is defined in the system for future use but is not fully implemented in the current business logic. The intended purpose is to grant read-only access to projects without any creation or editing rights.

## 🎨 Admin Features

### Admin Dashboard
- **Pending Approvals Queue** - Review submitted projects with filtering
- **Project Management** - Oversee all projects with search and pagination
- **User Administration** - Manage accounts, roles, and permissions
- **Email Logs** - Monitor notification delivery and status
- **System Statistics** - View usage metrics and performance data

### Administrative Tools
- **Bulk Operations** - Mass approve/reject projects
- **User Management** - Create users, assign roles, manage sessions
- **Email Templates** - Configure Brevo email templates
- **System Settings** - Configure application settings

## 🗄️ Database Schema

### Key Models

#### User Management
- **UserProfile**: Extended user information with department, job title, manager
- **Role**: User roles and permissions
- **UserSession**: Session tracking with IP and user agent
- **AuditLog**: Complete audit trail of user actions

#### Project Management
- **Project**: Main project entity with version control and approval workflow
- **Drawing**: Technical drawings with validation and categorization
- **ApprovalHistory**: Complete history of project status changes
- **ProjectHistory**: Detailed log of project submissions and their status

#### Notifications
- **NotificationPreferences**: User notification settings
- **EmailLog**: Email delivery tracking and status

### Database Features
- **UUID Primary Keys** - All models use UUID for security
- **Optimized Indexes** - Strategic indexing for performance
- **Foreign Key Relations** - Proper relationships with cascading deletes
- **Data Validation** - Model-level validation for data integrity

## 📋 Version Tracking System

DocuHub includes a comprehensive version tracking system that allows administrators to manage application versions with detailed release notes and improvements.

### 🚀 Features

**Version Management:**
- **Version Creation**: Create new versions with semantic version numbers (e.g., 1.0.0, 1.1.0, 2.0.0)
- **Version Types**: Support for Major, Minor, Patch, and Beta releases
- **Current Version Tracking**: Mark specific versions as current with automatic version file updates
- **Release Documentation**: Detailed descriptions for each version release

**Improvement Tracking:**
- **Categorized Improvements**: Track different types of improvements:
  - 🌟 **Feature**: New functionality and capabilities
  - 🔧 **Enhancement**: Improvements to existing features
  - 🐛 **Bug Fix**: Resolved issues and problems
  - 🔒 **Security**: Security-related updates and fixes
  - ⚡ **Performance**: Speed and efficiency improvements
  - 🎨 **UI/UX**: User interface and experience enhancements
  - 🔌 **API**: API changes and additions
  - 📚 **Documentation**: Documentation updates and additions

**User Experience:**
- **Footer Version Display**: Current version shown in page footer with clickable link
- **Version Modal**: Interactive modal showing detailed version information
- **Version History Page**: Complete timeline of all releases with improvements
- **Version Detail Pages**: Detailed view of specific versions with all improvements

### 🔧 Admin Interface

**Version Administration:**
- **Django Admin Integration**: Full admin interface for version management
- **Inline Improvements**: Add/edit improvements directly within version forms
- **Rich Admin Forms**: User-friendly forms with proper validation
- **Auto-sync**: Automatically updates `docuhub/version.py` when marking versions as current

**Modern UI Forms:**
- **Enhanced Form Design**: Beautiful, responsive forms with gradient backgrounds
- **Dynamic Form Management**: Add/remove improvement forms dynamically
- **Real-time Validation**: Instant feedback on form validation
- **Smooth Animations**: Polished user experience with animations and transitions

### 🎯 Usage

**For Administrators:**

1. **Access Admin Interface**:
   ```
   /admin/core/version/
   ```

2. **Create New Version**:
   - Navigate to Version History page
   - Click "Add Version" button
   - Fill in version details and improvements
   - Mark as current if active release

3. **Edit Existing Version**:
   - Click "Edit Version" on version detail page
   - Update version information and improvements
   - Save changes

**For Users:**

1. **View Current Version**:
   - Check footer of any page
   - Click version number for detailed information

2. **Browse Version History**:
   - Navigate to Settings → Version History
   - View complete timeline of releases
   - Click any version for detailed view

### 🔗 API Integration

**Version API Endpoint:**
```
GET /api/current-version/
```

**Response Format:**
```json
{
  "version_number": "1.0.0",
  "version_type": "Major Release",
  "description": "Initial release with core functionality",
  "release_date": "2024-01-15T10:30:00Z",
  "is_current": true,
  "improvements": [
    {
      "improvement_type": "feature",
      "improvement_type_display": "New Feature",
      "title": "User Management System",
      "description": "Complete user authentication and management",
      "order": 0
    }
  ]
}
```

### 📁 File Structure

```
apps/core/
├── models.py                 # Version and VersionImprovement models
├── admin.py                  # Admin interface configuration
├── forms.py                  # Version management forms
├── views.py                  # Version views and API endpoints
├── urls.py                   # Version-related URLs
├── management/
│   └── commands/
│       ├── version.py        # Version management command
│       └── create_sample_versions.py  # Sample data generator
└── templatetags/
    └── custom_filters.py     # Version display filters

templates/core/
├── version_history.html      # Version timeline page
├── version_detail.html       # Individual version details
└── add_version.html          # Version creation/editing form

docuhub/
├── version.py               # Current version file (auto-updated)
└── __init__.py             # Version import
```

### 🛠️ Management Commands

**Check Current Version:**
```bash
python manage.py version
```

**Set New Version:**
```bash
python manage.py version --set 1.1.0
```

**Create Sample Versions:**
```bash
python manage.py create_sample_versions
```

### 🎨 UI Components

**Version Modal Features:**
- **Version Badges**: Color-coded version information
- **Release Information**: Date, type, and current status
- **Improvement Categories**: Organized by improvement type
- **Navigation**: Links to full version history
- **Responsive Design**: Works on all device sizes

**Version History Timeline:**
- **Chronological Layout**: Timeline view of all versions
- **Improvement Previews**: Quick overview of changes
- **Interactive Elements**: Hover effects and animations
- **Search & Filter**: Find specific versions easily

### 🔄 Version Workflow

1. **Development**: Work on new features and improvements
2. **Version Creation**: Admin creates new version entry
3. **Improvement Documentation**: Add detailed improvement descriptions
4. **Release**: Mark version as current (auto-updates app version)
5. **User Notification**: Version appears in footer and history
6. **Feedback**: Users can view changes and improvements

### 🔍 Integration Points

**Template Integration:**
- `{{ APP_VERSION }}` - Current version number in templates
- Footer version link with modal functionality
- Settings menu version history access

**Context Processor:**
- Automatic version injection into all templates
- Current version availability globally

**Admin Integration:**
- Seamless Django admin interface
- Inline improvement editing
- Automatic version file updates

This version tracking system provides complete transparency about application changes and improvements, enhancing user experience and administrative control over release management.

---

## 🔌 API Endpoints

### Authentication
- `POST /accounts/login/` - User login
- `POST /accounts/logout/` - User logout
- `GET /accounts/profile/` - Get user profile

### Projects
- `GET /api/projects/` - List projects (with pagination)
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Get project details
- `PUT /api/projects/{id}/` - Update project
- `POST /api/projects/{id}/submit/` - Submit for approval
- `POST /api/projects/{id}/review/` - Admin review (approve/reject)

### Drawings
- `GET /api/projects/{id}/drawings/` - List project drawings
- `POST /api/projects/{id}/drawings/` - Add drawing to project
- `PUT /api/drawings/{id}/` - Update drawing
- `DELETE /api/drawings/{id}/` - Delete drawing

### Version Management
- `GET /api/current-version/` - Get current version details with improvements

## API Documentation

This section provides detailed documentation for the REST API endpoints available in DocuHub.

### Authentication

All API endpoints require token-based authentication. Users must include a valid `Authorization: Token <token>` header in their requests.

### Projects API

The Projects API allows for the management of projects.

**Endpoints:**

-   `GET /api/projects/`
    -   **Description**: Retrieves a list of projects. Project Managers can see all projects; other users can only see their own.
    -   **Permissions**: `IsAuthenticated`
    -   **Response**: A paginated list of project objects.

-   `POST /api/projects/`
    -   **Description**: Creates a new project. The `submitted_by` field is automatically set to the current user.
    -   **Permissions**: `IsAuthenticated`
    -   **Request Body**: `ProjectSerializer` data.
    -   **Response**: The created project object.

-   `GET /api/projects/{id}/`
    -   **Description**: Retrieves the details of a specific project.
    -   **Permissions**: `IsAuthenticated`, `ProjectOwnerPermission`
    -   **Response**: A project object.

-   `PUT /api/projects/{id}/` / `PATCH /api/projects/{id}/`
    -   **Description**: Updates a project.
    -   **Permissions**: `IsAuthenticated`, `ProjectOwnerPermission`
    -   **Request Body**: `ProjectSerializer` data.
    -   **Response**: The updated project object.

-   `DELETE /api/projects/{id}/`
    -   **Description**: Deletes a project.
    -   **Permissions**: `IsAuthenticated`, `ProjectOwnerPermission`
    -   **Response**: `204 No Content`.

**Actions:**

-   `POST /api/projects/{pk}/submit/`
    -   **Description**: Submits a project for approval. The project must be in 'Draft' or 'Revise_and_Resubmit' status and have at least one drawing.
    -   **Permissions**: `IsAuthenticated`
    -   **Response**: Success or error message.

-   `POST /api/projects/{pk}/review/`
    -   **Description**: Reviews a pending project. This endpoint is for Project Managers only.
    -   **Permissions**: `IsAuthenticated`, `ProjectManagerPermission`
    -   **Request Body**:
        -   `action` (string, required): 'approve', 'reject', or 'revise'.
        -   `comments` (string, optional): Required if the action is 'reject' or 'revise'.
    -   **Response**: Success or error message.

### Drawings API

The Drawings API allows for the management of drawings within a project.

**Endpoints:**

-   `GET /api/drawings/`
    -   **Description**: Retrieves a list of drawings. Project Managers can see all drawings; other users can only see drawings in their own projects.
    -   **Permissions**: `IsAuthenticated`
    -   **Response**: A paginated list of drawing objects.

-   `POST /api/drawings/`
    -   **Description**: Creates a new drawing. The `added_by` field is automatically set to the current user.
    -   **Permissions**: `IsAuthenticated`
    -   **Request Body**: `DrawingSerializer` data.
    -   **Response**: The created drawing object.

-   `GET /api/drawings/{id}/`
    -   **Description**: Retrieves the details of a specific drawing.
    -   **Permissions**: `IsAuthenticated`, `ProjectOwnerPermission`
    -   **Response**: A drawing object.

-   `PUT /api/drawings/{id}/` / `PATCH /api/drawings/{id}/`
    -   **Description**: Updates a drawing.
    -   **Permissions**: `IsAuthenticated`, `ProjectOwnerPermission`
    -   **Request Body**: `DrawingSerializer` data.
    -   **Response**: The updated drawing object.

-   `DELETE /api/drawings/{id}/`
    -   **Description**: Deletes a drawing.
    -   **Permissions**: `IsAuthenticated`, `ProjectOwnerPermission`
    -   **Response**: `204 No Content`.


## 📧 Email Integration (Brevo)

### Configuration
1. Sign up at [brevo.com](https://brevo.com)
2. Get API key from account settings
3. Create email templates in Brevo dashboard
4. Update `.env` with credentials

### Email Templates
- **PROJECT_SUBMITTED** - Notification when project is submitted
- **PROJECT_APPROVED** - Notification when project is approved
- **PROJECT_REJECTED** - Notification when project is rejected
- **PROJECT_REVISE_RESUBMIT** - Notification for revision requests
- **PROJECT_OBSOLETE** - Notification when project becomes obsolete
- **ADMIN_NEW_SUBMISSION** - Admin notification for new submissions
- **ADMIN_RESUBMISSION** - Admin notification for resubmissions
- **PASSWORD_RESET** - Temporary password sent to user's email upon request (uses username for request)

### Email Features
- **Automated Notifications** - Changes in project status (e.g., approval, rejection, revision requests) automatically trigger email notifications to relevant users.
- **Template Management** - Configurable email templates are used for different notification types.
- **Delivery Tracking** - The `EmailLog` model tracks the delivery status of all sent emails, allowing monitoring of notification delivery and status.
- **Retry Logic** - Automatic retry for failed emails ensures reliable delivery.
- **Logging** - A complete email audit trail is maintained in the `EmailLog` for all sent notifications.

## 🚀 Production Deployment

### Pre-deployment Checklist
1. Set `DEBUG=False` in settings
2. Configure proper `SECRET_KEY`
3. Set up allowed hosts
4. Configure static file serving
5. Set up email backend (Brevo)
6. Configure Redis for Celery (optional)

### Deployment Steps
```bash
# Update settings for production
export DEBUG=False
export SECRET_KEY=your-production-secret-key
export ALLOWED_HOSTS=your-domain.com

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Web Server Configuration (Nginx + Gunicorn)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /path/to/docuhub/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/docuhub/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Considerations
- **HTTPS Configuration** - SSL/TLS certificates
- **Security Headers** - HSTS, CSP, X-Frame-Options
- **Database Security** - Consider PostgreSQL for production
- **Environment Variables** - Secure credential management
- **Regular Backups** - Database and media file backups

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.projects
python manage.py test apps.accounts

# Run with coverage
coverage run manage.py test
coverage report
```

### Test Data
```bash
# Create sample data for testing
python manage.py sample_data
```

## 🏗️ Architecture & Code Quality

### Service-Based Architecture
The application now uses a clean service-based architecture with business logic separated from views:

#### Service Classes
- **ProjectVersionService**: Handles project version creation and management
- **ProjectSubmissionService**: Manages project submissions, approvals, and reviews
- **ProjectStatsService**: Provides statistics and reporting functionality
- **UserAccountService**: Handles user account creation and management
- **UserSessionService**: Manages user session tracking and cleanup
- **UserStatsService**: Provides user statistics and analytics
- **BrevoEmailService**: Handles all email notifications and delivery tracking

#### Input Validation & Security
- **Custom Validators**: Comprehensive validation functions in `validators.py`
- **Model-Level Validation**: Validation at the database model level
- **Security Checks**: Protection against XSS, script injection, and malicious content
- **Status Transition Validation**: Ensures valid project status changes
- **Data Integrity**: Unique constraints and referential integrity

#### Performance Optimizations
- **Query Optimization**: Strategic use of `select_related()` and `prefetch_related()`
- **Database Indexing**: Optimized indexes for frequently queried fields
- **Pagination**: Efficient pagination for large datasets
- **Caching**: Production-ready caching configuration

#### Environment Configuration
- **Development Settings**: Debug-friendly configuration with file logging
- **Production Settings**: Security-hardened configuration with rotating logs
- **Environment Variables**: Secure configuration management
- **Settings Inheritance**: Modular settings structure

## 🔧 Development

### Adding New Features
1. Create feature branch
2. Add models to appropriate app with proper validation
3. Create or update service classes for business logic
4. Create migrations
5. Add views (thin controllers) and templates
6. Update URLs
7. Add tests
8. Update documentation

### Code Style & Standards
- Follow Django conventions and best practices
- Use service classes for business logic
- Keep views thin (controller pattern)
- Add comprehensive validation at model level
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions small and focused
- Use proper logging instead of print statements

### Performance Guidelines
- Always use `select_related()` for foreign keys
- Use `prefetch_related()` for many-to-many and reverse foreign keys
- Add database indexes for frequently queried fields
- Implement pagination for list views
- Use caching for expensive operations

## 📈 Monitoring & Logging

### Application Logging
- **User Actions** - Complete audit trail
- **Email Delivery** - Delivery status and errors
- **System Events** - Application events and errors

### Performance Monitoring
- **Database Queries** - Monitor query performance
- **Response Times** - Track page load times
- **User Sessions** - Monitor active users

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow Django best practices
- Write tests for new features
- Update documentation
- Follow code style guidelines

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support & Troubleshooting

### Common Issues

**Migration Errors**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Static Files Not Loading**
```bash
python manage.py collectstatic
```

**Email Not Sending**
- Check Brevo API key
- Verify email templates
- Check email logs in admin

### Getting Help
- Check the documentation
- Review error logs in Django admin
- Create GitHub issue with error details
- Contact system administrator

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Brevo API Documentation](https://developers.brevo.com/)
- [SQLite Documentation](https://sqlite.org/docs.html)

## 🔄 Recent Improvements (Latest Refactoring)

### Code Quality Enhancements
- ✅ **Removed Duplicate Code**: Eliminated duplicate `admin_users_list` function
- ✅ **Service Layer Implementation**: Extracted business logic into dedicated service classes
- ✅ **Comprehensive Validation**: Added custom validators and model-level validation
- ✅ **Security Hardening**: Added protection against XSS and malicious content
- ✅ **Debug Code Cleanup**: Replaced print statements with proper logging

### Architecture Improvements
- ✅ **Environment-Specific Settings**: Split settings into development/production configurations
- ✅ **Query Optimization**: Implemented select_related/prefetch_related across all views
- ✅ **Logging System**: Structured logging with file rotation and environment-specific configuration
- ✅ **Unused Code Removal**: Removed empty PaperKeep app
- ✅ **Configuration Management**: Added .env.example with comprehensive environment variables

### Performance Optimizations
- ✅ **Database Query Optimization**: Reduced N+1 queries across the application
- ✅ **Model Relationships**: Optimized foreign key relationships with proper select_related
- ✅ **Caching Configuration**: Production-ready caching with Redis support
- ✅ **Pagination Efficiency**: Optimized pagination for large datasets

### Developer Experience
- ✅ **Modular Settings**: Easy environment switching with DJANGO_ENVIRONMENT variable
- ✅ **Enhanced Documentation**: Updated with architectural decisions and best practices
- ✅ **Development Guidelines**: Clear coding standards and performance guidelines
- ✅ **Error Handling**: Improved error handling and user feedback

---

## 🚨 Known Issues & Future Enhancements

This section outlines the current limitations, known issues, and areas identified for future development and improvement within the DocuHub project.

### Current Gaps & Outstanding Issues

**1. Core Development Practices**
- ❌ **No Comprehensive Test Suite**:
    - **Problem**: Complete absence of unit tests, integration tests, and end-to-end tests.
    - **Impact**: High risk of regressions, difficult to refactor safely, and hinders rapid feature development.
    - **Proposed Solution**: Implement a robust testing strategy aiming for at least 80% code coverage, utilizing Django's testing framework and potentially tools like Selenium for E2E tests.
- ❌ **Limited Management Commands**:
    - **Problem**: Lack of custom Django management commands for common administrative tasks (e.g., data cleanup, user management utilities beyond `createsuperuser`).
    - **Impact**: Manual and error-prone administrative processes, reduced operational efficiency.
    - **Proposed Solution**: Develop custom management commands for recurring maintenance and administrative operations.
- ❌ **Limited Migrations**:
    - **Problem**: Only a few migration files are present, suggesting limited schema evolution testing or a lack of historical record for database changes.
    - **Impact**: Potential for database inconsistencies, difficult to track schema changes over time.
    - **Proposed Solution**: Ensure `makemigrations` is run consistently with model changes, and review migration history for completeness.
- ❌ **No Test Fixtures**:
    - **Problem**: Absence of predefined test data fixtures.
    - **Impact**: Difficult to set up consistent and reproducible testing environments, reliance on `sample_data` which might not cover all test cases.
    - **Proposed Solution**: Create dedicated test fixtures for various testing scenarios to ensure reliable and isolated tests.

**2. Security & Data Integrity**
- ❌ **Missing Input Sanitization**:
    - **Problem**: While validators exist, there's no explicit HTML sanitization before storing user-generated content in the database.
    - **Impact**: Potential for Cross-Site Scripting (XSS) vulnerabilities if malicious scripts are injected and rendered unsanitized.
    - **Proposed Solution**: Implement a robust HTML sanitization library (e.g., `bleach`) for all user-submitted text fields before saving to the database.
- ❌ **No Database Constraints**:
    - **Problem**: Critical fields may lack unique constraints or other database-level integrity checks.
    - **Impact**: Risk of data duplication or inconsistencies that bypass application-level validation.
    - **Proposed Solution**: Add appropriate unique constraints and foreign key constraints at the database level for critical fields to enforce data integrity.
- ❌ **Weak Date Validation**:
    - **Problem**: Deadline dates only validate against past dates, but may lack more complex business rule validations (e.g., project start date must be before end date).
    - **Impact**: Allows for illogical date entries, potentially affecting project scheduling and reporting.
    - **Proposed Solution**: Enhance date validation to include cross-field checks and more complex business rules where applicable.
- ❌ **No Cross-Field Validation**:
    - **Problem**: Validation logic might not adequately cover interdependencies between multiple fields in a form or model.
    - **Impact**: Allows for inconsistent or contradictory data to be saved, leading to logical errors in the application.
    - **Proposed Solution**: Implement comprehensive cross-field validation at the form and model levels to ensure data consistency.

**3. Error Handling & Monitoring**
- ❌ **Incomplete Exception Handling**:
    - **Problem**: Many views and service functions lack proper `try-except` blocks for robust error handling.
    - **Impact**: Unhandled exceptions can lead to 500 errors, poor user experience, and potential information disclosure.
    - **Proposed Solution**: Implement comprehensive exception handling across the application, providing graceful degradation and informative error messages.
- ❌ **Inconsistent Logging**:
    - **Problem**: Logging practices are inconsistent; some operations are logged, while others are not, making debugging and auditing difficult.
    - **Impact**: Challenges in diagnosing issues, tracking user activity, and monitoring system health.
    - **Proposed Solution**: Standardize logging practices, ensuring all critical operations, errors, and warnings are logged consistently with appropriate detail.
- ❌ **Missing Custom Error Pages**:
    - **Problem**: No custom error page handling for common HTTP errors (e.g., 400, 403, 404, 500).
    - **Impact**: Default server error pages provide a poor user experience and can expose server details.
    - **Proposed Solution**: Implement custom, user-friendly error pages for all relevant HTTP status codes.
- ❌ **No Integrated Monitoring**:
    - **Problem**: Lack of integration with external monitoring tools or health checks.
    - **Impact**: Difficult to proactively identify performance bottlenecks, system outages, or security incidents in a production environment.
    - **Proposed Solution**: Integrate with monitoring solutions (e.g., Prometheus, Sentry) and implement health check endpoints.

**4. API & Documentation Gaps**
- ❌ **Missing REST API Endpoints**:
    - **Problem**: Key functionalities like statistics, bulk operations (beyond what's implemented in the admin), and file uploads lack dedicated REST API endpoints.
    - **Impact**: Limits the extensibility and integration capabilities of the application with other systems or frontend frameworks.
    - **Proposed Solution**: Develop REST API endpoints for all core functionalities, ensuring consistency and proper authentication/authorization.
- ❌ **No OpenAPI/Swagger Documentation**:
    - **Problem**: Absence of automated API documentation (e.g., OpenAPI/Swagger).
    - **Impact**: Developers need to manually inspect code to understand API contracts, leading to increased development time and potential integration errors.
    - **Proposed Solution**: Integrate a tool like `drf-spectacular` or `drf-yasg` to generate interactive OpenAPI/Swagger documentation for all REST API endpoints.
- ❌ **Incomplete Model Docstrings**:
    - **Problem**: Many model methods and fields lack comprehensive docstrings.
    - **Impact**: Reduces code readability and maintainability, makes it harder for new developers to understand the codebase.
    - **Proposed Solution**: Add detailed docstrings to all models, methods, and complex fields, explaining their purpose, parameters, and return values.
- ❌ **Missing Code Examples**:
    - **Problem**: Lack of usage examples within docstrings or separate documentation for complex functions/APIs.
    - **Impact**: Increases the learning curve for developers trying to use existing components.
    - **Proposed Solution**: Include practical code examples in docstrings or a dedicated `examples/` directory to illustrate how to use key functionalities.

**5. Production Readiness**
- ❌ **No Health Check Endpoints**:
    - **Problem**: Absence of dedicated endpoints for monitoring application health (e.g., database connection, external service availability).
    - **Impact**: Prevents automated monitoring systems from accurately assessing application status, leading to delayed incident response.
    - **Proposed Solution**: Implement simple health check endpoints that return HTTP 200 OK if the application is healthy, and appropriate error codes otherwise.
- ❌ **Missing Cleanup Jobs**:
    - **Problem**: No scheduled tasks or management commands for routine data cleanup (e.g., old logs, temporary files, soft-deleted records).
    - **Impact**: Database bloat, performance degradation over time, and increased storage costs.
    - **Proposed Solution**: Implement periodic cleanup jobs using Django's management commands or a task queue like Celery Beat.
- ❌ **No Automated Backup Strategy**:
    - **Problem**: Lack of an automated and tested backup strategy for the database and media files.
    - **Impact**: High risk of data loss in case of system failure, corruption, or accidental deletion.
    - **Proposed Solution**: Implement automated daily/weekly backups of the database and media files to a secure offsite location.
- ❌ **Missing Performance Monitoring**:
    - **Problem**: No dedicated tools or integrations for continuous performance monitoring in production.
    - **Impact**: Difficult to identify and diagnose performance bottlenecks (e.g., slow queries, high memory usage) in a live environment.
    - **Proposed Solution**: Integrate with application performance monitoring (APM) tools (e.g., Sentry, New Relic, Datadog) to track key metrics.

### Resolved Issues

This section lists significant issues that have been identified and successfully addressed, contributing to the stability, security, and functionality of the DocuHub project.

**1. Workflow Gaps Resolution**
- ✅ **Incomplete Review Form**:
    - **Resolution**: Added 'Request Revision' option to ReviewForm with proper validation requiring comments for rejection and revision requests.
    - **Impact**: Completed the project approval workflow, allowing for more nuanced feedback.
- ✅ **Bulk Operations**:
    - **Resolution**: Implemented a complete bulk operations system with `ProjectBulkOperationsService`, `BulkActionForm`, and an enhanced admin UI for approve/reject/revise actions.
    - **Impact**: Significantly improved administrative efficiency for project managers.
- ✅ **No Rollback Mechanism**:
    - **Resolution**: Created `ProjectRestoreService` and admin-only restoration functionality, allowing obsoleted projects to be restored to Draft or Approved status with an audit trail.
    - **Impact**: Enhanced data recovery capabilities and project lifecycle management.
- ✅ **Missing Draft Recovery**:
    - **Resolution**: Added `recover_draft` functionality, allowing project owners to recover rejected/obsolete projects as drafts, clearing review information and enabling re-editing.
    - **Impact**: Improved user experience by preventing accidental loss of project drafts.

**2. Security Vulnerabilities Resolution**
- ✅ **Missing CSRF Protection**:
    - **Resolution**: Added `@csrf_protect` decorators to all critical views and API endpoints, enhanced REST Framework with proper authentication classes, and implemented secure cookie settings.
    - **Impact**: Significantly mitigated Cross-Site Scripting (CSRF) attacks.
- ✅ **No Rate Limiting**:
    - **Resolution**: Implemented a comprehensive rate limiting system with custom middleware, REST Framework throttling classes, and configurable limits.
    - **Impact**: Protected against brute-force attacks, denial-of-service attempts, and API abuse.
- ✅ **Weak Permission Checks**:
    - **Resolution**: Created a robust role-based permission system with custom groups and granular permissions, replacing all `is_staff` checks.
    - **Impact**: Enforced fine-grained access control, enhancing overall application security.
- ✅ **Inconsistent Audit Logging**:
    - **Resolution**: Added comprehensive audit logging middleware for security events, suspicious activities, and admin access tracking.
    - **Impact**: Improved traceability, accountability, and security monitoring capabilities.

**3. Performance Optimizations Resolution**
- ✅ **N+1 Query Problems**:
    - **Resolution**: Fixed by consistently using `select_related` and `prefetch_related` in all relevant views.
    - **Impact**: Drastically reduced the number of database queries, improving application response times.
- ✅ **Missing Database Indexes**:
    - **Resolution**: Added strategic indexes to frequently queried fields like `status` and `date_submitted`.
    - **Impact**: Accelerated database query performance for common operations.
- ✅ **Inefficient Queryset Filtering**:
    - **Resolution**: Optimized queryset filtering logic for better performance.
    - **Impact**: Improved the efficiency of data retrieval operations.
- ✅ **No Query Optimization (select/defer)**:
    - **Resolution**: Implemented `only()` and `defer()` for large datasets to retrieve only necessary fields.
    - **Impact**: Reduced memory consumption and improved query performance for large data sets.

### Improvement Priorities

**🔥 High Priority (Critical):**
1.  **Comprehensive Test Suite**: Implement a robust test suite with at least 80% code coverage to ensure stability and enable safe refactoring.
2.  **Robust Error Handling & Logging**: Implement proper exception handling and consistent, structured logging throughout the application for better debugging and monitoring.
3.  **Input Sanitization**: Implement HTML sanitization for all user-generated content to prevent XSS vulnerabilities.
4.  **Database Constraints & Validation**: Add missing database-level constraints and enhance cross-field validation for improved data integrity.
5.  **API Documentation**: Generate comprehensive OpenAPI/Swagger documentation for all REST API endpoints.

**⚠️ Medium Priority (Important):**
1.  **Missing API Endpoints**: Develop REST API endpoints for currently unsupported functionalities (e.g., statistics, file uploads).
2.  **Production Monitoring**: Integrate with monitoring tools and implement health check endpoints for proactive issue detection.
3.  **Automated Backups**: Implement an automated and tested backup strategy for the database and media files.
4.  **Cleanup Jobs**: Implement scheduled tasks for routine data cleanup to maintain performance and reduce storage.
5.  **Code Examples**: Add practical code examples for key functionalities and API usage.

**💡 Low Priority (Enhancement):**
1.  **Custom Management Commands**: Develop custom management commands for routine maintenance and administrative tasks.
2.  **Test Fixtures**: Create dedicated test data fixtures for consistent and reproducible testing environments.
3.  **Custom Error Pages**: Implement custom, user-friendly error pages for all relevant HTTP status codes.
4.  **Advanced Features**: Explore and implement advanced features like project comparison or enhanced reporting.
5.  **Notification Center**: Develop an in-app notification center and user preference management.

### Code Quality Assessment

**✅ Strengths:**
-   Good Django architecture with proper separation of concerns.
-   Service-based architecture with business logic extraction.
-   Comprehensive model validation and security checks (where implemented).
-   Proper UUID usage and database relationships.
-   Environment-specific settings configuration.

**❌ Weaknesses (Areas for Improvement):**
-   Missing comprehensive test coverage (currently 0%).
-   Incomplete error handling and exception management.
-   Remaining security vulnerabilities (e.g., input sanitization).
-   Lack of automated production monitoring and maintenance features.
-   Incomplete API documentation and code examples.

**Note:** While the project has a solid foundation, addressing the outstanding issues, particularly in testing, error handling, and security, is crucial for production readiness and long-term maintainability.

---

## 🔧 Recent Workflow Fixes (Latest Update)

### **Workflow Gaps Resolution**

**✅ Enhanced Review Process**
- **Fixed ReviewForm**: Added missing 'Request Revision' option to complete the approval workflow
- **Improved Validation**: Enhanced form validation requiring comments for rejection and revision requests
- **Complete Status Transitions**: Now supports all status transitions: Draft → Pending → Approved/Rejected/Revise & Resubmit

**✅ Bulk Operations Implementation**
- **Service Layer**: Created `ProjectBulkOperationsService` with transaction-safe bulk operations
- **Forms & Validation**: Implemented `BulkActionForm` with proper project ID validation
- **Admin Interface**: Enhanced admin pending page with:
  - Checkbox selection (individual and select-all)
  - Bulk actions panel with toggle functionality
  - JavaScript confirmations with project names
  - Real-time selection counter
- **Supported Actions**: Bulk approve, reject, and request revision with optional comments
- **Error Handling**: Comprehensive error reporting for failed operations

**✅ Project Restoration System**
- **Admin Restoration**: `ProjectRestoreService` allows admins to restore obsoleted projects
- **Status Recovery**: Projects can be restored to Draft or Approved status
- **Audit Trail**: Complete logging of restoration actions with comments and metadata
- **Permission Control**: Admin-only access with proper authorization checks
- **User Interface**: Dedicated restoration form with warnings and project information display

**✅ Draft Recovery Mechanism**
- **Owner Recovery**: Project owners can recover rejected/obsolete projects as drafts
- **Clean Slate**: Recovery clears review information (reviewer, comments, dates)
- **Re-editing**: Recovered drafts allow full editing and resubmission
- **Dual Access**: Available to both project owners and admins
- **Status Transitions**: Supports recovery from Rejected and Obsolete statuses

### **Technical Implementation Details**

**New Service Classes:**
```python
# apps/projects/services.py
class ProjectBulkOperationsService:
    - bulk_approve_projects()
    - bulk_reject_projects()
    - bulk_request_revision()

class ProjectRestoreService:
    - restore_project()
```

**New Forms:**
```python
# apps/projects/forms.py
class BulkActionForm:          # Bulk operations with validation
class ProjectRestoreForm:      # Admin project restoration
class ReviewForm (enhanced):   # Added 'revise' option
```

**New Views:**
```python
# apps/projects/views.py
- bulk_action_projects()    # Handle bulk operations
- restore_project()         # Admin restoration
- recover_draft()          # Owner draft recovery
```

**New Templates:**
```html
templates/projects/project_restore.html   # Admin restoration interface
templates/projects/project_recover.html   # Draft recovery interface
templates/projects/admin_pending.html     # Enhanced with bulk operations
```

**Enhanced URLs:**
```python
# apps/projects/urls.py
path('admin/bulk-action/', views.bulk_action_projects, name='bulk_action')
path('<uuid:pk>/restore/', views.restore_project, name='restore')
path('<uuid:pk>/recover/', views.recover_draft, name='recover_draft')
```

### **User Experience Improvements**

**For Administrators:**
- Bulk operations interface with intuitive checkboxes and selection feedback
- Clear confirmation dialogs showing affected project names
- Restoration workflow with detailed project information
- Enhanced admin pending page with improved functionality

**For Project Owners:**
- Draft recovery option for rejected/obsolete projects
- Clear visual indicators for available actions
- Guided recovery process with warnings and confirmations
- Seamless transition back to editable draft status

**System-wide Enhancements:**
- Complete audit trail for all workflow actions
- Email notifications for bulk operations
- Transaction safety with rollback on failures
- Proper error handling and user feedback
- Permission-based access controls throughout

### **Impact Assessment**

**Workflow Completeness**: ✅ **100%** - All identified workflow gaps have been resolved
**Admin Efficiency**: ✅ **Significantly Improved** - Bulk operations reduce administrative overhead
**User Recovery**: ✅ **Fully Implemented** - No more "lost" projects due to status changes
**System Reliability**: ✅ **Enhanced** - Transaction safety and proper error handling
**User Experience**: ✅ **Improved** - Clear interfaces and guided workflows

The workflow system is now complete and production-ready for project lifecycle management.

---

## 🔒 Security Enhancements (Latest Update)

### **Critical Security Vulnerabilities Resolution**

**✅ CSRF Protection Implementation**
- **Enhanced API Security**: All API endpoints now include `@csrf_protect` decorators and proper CSRF token handling
- **Form Protection**: Critical views protected with CSRF tokens and secure cookie settings
- **REST Framework Integration**: Enhanced authentication classes with session and token authentication
- **Cookie Security**: Implemented HttpOnly, Secure, and SameSite attributes for all cookies
- **Session Configuration**: 1-hour session timeout with secure cookie settings

**✅ Comprehensive Rate Limiting System**
- **Multi-Layer Protection**: Custom middleware + REST Framework throttling + view-level decorators
- **User-Type Based Limits**: Different rate limits for regular users, admins, and anonymous users
- **Endpoint-Specific Controls**: Tailored limits for different operation types
- **Configurable Thresholds**: Easy adjustment of rate limits via settings

**✅ Role-Based Permission System**
- **Granular Access Control**: Replaced weak `is_staff` checks with proper permission groups
- **Custom Permission Classes**: Enhanced security with object-level permissions
- **User Group Hierarchy**: Structured roles from basic users to full administrators
- **API Permission Integration**: Consistent permission checking across web and API interfaces

### **Technical Security Implementation**

**New Permission Classes:**
```python
# apps/projects/permissions.py
class ProjectManagerPermission(BasePermission):    # Review and approval access
class ProjectOwnerPermission(BasePermission):      # Object-level ownership
class ProjectUserRateThrottle(UserRateThrottle):   # User-specific throttling
class ProjectAdminRateThrottle(UserRateThrottle):  # Admin-specific throttling
```

**Security Middleware Stack:**
```python
# apps/core/middleware.py
class SecurityHeadersMiddleware:     # CSP, HSTS, X-Frame-Options, XSS Protection
class RateLimitMiddleware:          # Custom rate limiting with cache backend
class AuditLoggingMiddleware:       # Security event logging and monitoring
```

**Permission Groups:**
```python
# Automatically created via management command
'Project Users':         # Basic project operations
'Project Managers':      # Review, approve, bulk operations
'Project Administrators': # Full system access, restoration
```

**Rate Limiting Configuration:**
```python
# Configurable limits by operation type
Authentication:     5 attempts / 5 minutes
Project Creation:   5 projects / hour
Project Submission: 10 submissions / minute
Bulk Operations:    5 operations / minute
API Requests:       1000/hour (users), 2000/hour (admins)
```

### **Security Headers Implementation**

**Enhanced Response Headers:**
- **Content Security Policy**: Prevents XSS attacks with strict content sources
- **HTTP Strict Transport Security**: Enforces HTTPS connections
- **X-Frame-Options**: Prevents clickjacking attacks
- **X-Content-Type-Options**: Prevents MIME type sniffing
- **Referrer Policy**: Controls referrer information leakage

### **Audit and Monitoring Features**

**Security Event Logging:**
- **Failed Authentication Attempts**: IP-based tracking and alerting
- **Suspicious Request Patterns**: Detection of potential attack vectors
- **Admin Access Monitoring**: Complete audit trail of administrative actions
- **Rate Limit Violations**: Logging of throttling events for analysis

**Monitoring Capabilities:**
- **Real-time Security Events**: Immediate logging of security-relevant activities
- **IP-based Tracking**: Client IP extraction with proxy support
- **User Agent Analysis**: Detection of automated tools and suspicious clients
- **Request Pattern Analysis**: Identification of potential security threats

### **Management and Deployment**

**Setup Command:**
```bash
# Initialize security system
python manage.py setup_permissions
python manage.py setup_permissions --assign-existing-staff --assign-superusers
```

**Updated Dependencies:**
```python
# requirements.txt additions
django-ratelimit==4.1.0              # View-level rate limiting
djangorestframework-throttling==0.2.1 # Enhanced API throttling
```

**Configuration Options:**
```python
# Environment variables for security tuning
RATELIMIT_ENABLE=True
CSRF_COOKIE_AGE=31449600
SESSION_COOKIE_AGE=3600
SECURE_HSTS_SECONDS=31536000
```

### **Security Compliance Features**

**Production-Ready Security:**
- **OWASP Compliance**: Addresses major security vulnerabilities
- **Enterprise Standards**: Role-based access control with audit trails
- **Data Protection**: Secure cookie handling and session management
- **Attack Prevention**: Multi-layer protection against common threats

**Automated Security Measures:**
- **Permission Setup**: Management command for easy deployment
- **User Assignment**: Automatic role assignment for existing users
- **Error Handling**: Graceful degradation with security logging
- **Cache Integration**: Efficient rate limiting with minimal performance impact

### **Impact Assessment**

**Security Posture**: ✅ **Significantly Enhanced** - Enterprise-grade security implementation
**Vulnerability Mitigation**: ✅ **Critical Issues Resolved** - CSRF, Rate Limiting, Permissions
**Compliance Readiness**: ✅ **Production Standard** - OWASP-compliant security measures
**Monitoring Capability**: ✅ **Comprehensive** - Full audit trail and event logging
**Scalability**: ✅ **Enterprise-Ready** - Configurable limits and role-based access

The security system now meets enterprise standards with comprehensive protection against common web application vulnerabilities, proper role-based access control, and extensive monitoring capabilities.

---

## 📋 Project Status System (Latest Update)

### **Enhanced Approval Workflow**

DocuHub now features a comprehensive project status system designed to provide granular control over the approval process, enabling more nuanced project management and better workflow flexibility.

### **New Status Options for Approvers**

**✅ Approved & Endorsed**
- **Purpose**: Full approval without any conditions
- **Effect**: Project is completely approved and locked from further edits
- **User Impact**: Submitters cannot edit; project is publicly visible
- **Next Steps**: Project enters final approved state

**✅ Conditional Approval**
- **Purpose**: Approval with conditions that require resubmission
- **Effect**: Submitters can edit the project and resubmit for final approval
- **User Impact**: Allows continued editing while maintaining approved status
- **Next Steps**: Submitter can modify and resubmit or escalate to full approval

**✅ Request for Revision**
- **Purpose**: Request significant changes that warrant a new version
- **Effect**: Automatically creates a new project version for major revisions
- **User Impact**: Creates clean separation between versions
- **Next Steps**: New version created for submitter to work on

**✅ Rejected**
- **Purpose**: Complete rejection of the project
- **Effect**: Project cannot be edited; submitter needs to start over
- **User Impact**: Clear indication that project does not meet requirements
- **Next Steps**: Project remains in rejected state; no further action possible

**✅ Rescinded & Revoked**
- **Purpose**: Revoke previously approved projects
- **Effect**: Removes approval status from projects that were previously approved
- **User Impact**: Previously approved projects become unavailable
- **Next Steps**: Project moves to revoked state; admin intervention required

### **Edit Permission Rules**

**Submitters Can Edit When:**
- ✅ **Draft**: Initial creation and preparation phase
- ✅ **Conditional Approval**: Approved with conditions requiring changes

**Submitters Cannot Edit When:**
- ❌ **Pending Approval**: Under review by approvers
- ❌ **Approved & Endorsed**: Fully approved and locked
- ❌ **Request for Revision**: Creates new version instead
- ❌ **Rejected**: Cannot be modified after rejection
- ❌ **Rescinded & Revoked**: Revoked projects are locked
- ❌ **Obsolete**: Archived projects cannot be edited

### **Version Management Workflow**

**Automatic Version Creation:**
- **Trigger**: When approver selects "Request for Revision"
- **Effect**: Creates new version of the project with incremented version number
- **Purpose**: Maintains history while allowing major changes
- **User Experience**: Submitter receives new version to work on

**Manual Version Creation:**
- **Available For**: Project owners on their own projects
- **Conditions**: From certain statuses (varies by workflow requirements)
- **Purpose**: Allow submitters to create new versions when needed

### **Status Transition Matrix**

```
Current Status          → Possible Next Status
─────────────────────────────────────────────────────────────
Draft                   → Pending Approval, Obsolete
Pending Approval        → Approved & Endorsed, Conditional Approval, 
                          Request for Revision, Rejected, Rescinded & Revoked
Approved & Endorsed     → Rescinded & Revoked, Obsolete
Conditional Approval    → Approved & Endorsed, Request for Revision, 
                          Rejected, Rescinded & Revoked, Obsolete
Request for Revision    → Pending Approval, Draft, Obsolete (via new version)
Rejected                → Draft, Obsolete
Rescinded & Revoked     → Draft, Obsolete
Obsolete                → (No transitions allowed)
```

### **Implementation Details**

**Database Changes:**
- **Updated Status Choices**: All models now use new status values
- **Migration Support**: Automated database migration to new status structure
- **Backward Compatibility**: Proper migration path from old status values

**Permission System Updates:**
- **Enhanced Permission Classes**: Updated to support new status-based editing rules
- **View Restrictions**: Proper enforcement of edit permissions based on status
- **API Consistency**: REST API endpoints respect new permission rules

**User Interface Improvements:**
- **Status Indicators**: Clear visual representation of project status
- **Action Availability**: Buttons and links shown based on current status and permissions
- **Workflow Guidance**: Clear indication of available actions for each status

### **Benefits of New System**

**For Approvers:**
- **More Control**: Granular approval options for different scenarios
- **Workflow Flexibility**: Can choose appropriate response based on project needs
- **Better Communication**: Clear status indicates exact approval state

**For Submitters:**
- **Clear Guidance**: Obvious next steps based on current status
- **Continued Editing**: Conditional approval allows refinement without full rejection
- **Version Control**: Automatic version creation for major revisions

**For Organizations:**
- **Audit Trail**: Complete history of status changes and decisions
- **Process Standardization**: Consistent workflow across all projects
- **Quality Control**: Multiple approval levels ensure thorough review

### **Migration Notes**

**Existing Projects:**
- **Automatic Migration**: Existing projects migrated to new status values
- **Status Mapping**: Old statuses mapped to equivalent new statuses
- **No Data Loss**: All existing data preserved during migration

**Deployment:**
- **Database Migration**: Run `python manage.py migrate` to apply changes
- **No Downtime**: Migration designed for zero-downtime deployment
- **Rollback Support**: Migration can be reversed if needed

This enhanced status system provides the flexibility and control needed for sophisticated project approval workflows while maintaining simplicity for everyday use.