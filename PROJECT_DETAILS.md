# DocuHub – Comprehensive Project Overview

## 1. Product Snapshot
- **Mission**: Enterprise-grade lifecycle management for technical drawings, CAD files, and engineering documentation with configurable approvals and traceability.
- **Target teams**: Engineering, architecture, construction, manufacturing, or any org that needs auditable review workflows.
- **Core value**: Centralize drawing storage, orchestrate approvals, notify all actors, and keep immutable audit trails.

## 2. Technology Stack
| Layer | Details |
| --- | --- |
| **Backend** | Django 4.2.7, Django REST Framework 3.14.0, Python 3.12+, MySQL 8.0+, Redis 5.0+ for caching/queues, Celery 5.3.4 for async tasks, Brevo email service integration |
| **Frontend** | React 18.2+ + Vite 5.2+ + TypeScript 5.2+ + Tailwind CSS 3.4+; React Router 6.8+, Axios 1.11+, React Query 5.84+, Heroicons 2.2+, React Toastify 9.1+ |
| **DevOps** | `.env`-driven config, Sentry 2.32+ monitoring, comprehensive logging, Gunicorn 22.0+ WSGI server, CORS headers, rate limiting, CSRF protection |

## 3. Backend Application Modules (`apps/`)

### 3.1 `accounts`
- **Roles & Profiles**: `Role`, `UserProfile`, `UserSession`, and `AuditLog` models handle RBAC, extended HR metadata, session/IP tracking, and detailed audit events (`apps/accounts/models.py:9`). Departments (8 choices), job titles (13 choices), manager relationships, employee IDs, and notification preferences are first-class fields.
- **Signals**: Post-save hooks auto-provision profiles for each `User` with automatic profile creation and updates.
- **Security Features**: IP tracking, user agent logging, session management with activity monitoring, and comprehensive audit logging for all user actions.
- **Management Commands**: User management utilities for testing, email validation, and session cleanup.

### 3.2 `projects`
- **Project entity**: Versioned via `project_group_id`, strict validators, deadlines, priority flags (4 levels), and enforced status transition rules ensuring lifecycle integrity (`apps/projects/models.py:33`). 8 status choices from Draft to Obsolete with controlled transitions.
- **Drawing entity**: Uppercases drawing numbers, validates metadata (scale, sheet size, revision), and keeps per-project uniqueness for draft drawings while auto-syncing counts (`apps/projects/models.py:155`).
- **Approval tracking**: `ApprovalHistory` logs 11 action types with actor, IP, comments, and status changes; `ProjectHistory` preserves submission metadata with receipt IDs for each version.
- **APIs & permissions**: REST endpoints with role-based throttling (ProjectUserRateThrottle, ProjectAdminRateThrottle), CSRF protection, and granular DRF permissions (`apps/projects/api_views.py:21`).
- **Services & validators**: `ProjectSubmissionService` orchestrates submission/resubmission with UUID receipt generation; 10+ validators centralize business rules for names, revisions, URLs, and comments.
- **Recent migrations**: 10 migrations including project folder link migration (0005), status choice updates (0008-0010), and drawing discipline removal (0007).

### 3.3 `notifications`
- **Email telemetry**: `EmailLog` captures delivery state, Brevo message IDs, retries, engagement timestamps, and template types with comprehensive error tracking.
- **Brevo integration**: `BrevoEmailService` renders HTML/text templates, posts to Brevo REST API, and records outcomes for 8+ email events including submissions, approvals, rejections, revision requests, admin alerts, and password resets (`apps/notifications/services.py:11`).
- **Template system**: Custom HTML/text email templates with dynamic context, company branding, and multi-language support.
- **Fallback handling**: Graceful degradation when API key not configured, with warning logs and failed status tracking.

### 3.4 `core`
- **Release tracking**: `Version` and `VersionImprovement` models publish change logs directly in the product UI, automatically ensuring only one “current” release (`apps/core/models.py:1`).
- **Site-wide utilities**: Context processors, middleware, template tags, and commands (e.g., `create_sample_versions`) live here for cross-app reuse.

## 4. Frontend Application (`frontend/`)

### 4.1 Structure
```
src/
├── components/          # Layout, navigation, notification bell, ProtectedRoute
│   └── ui/              # Design system (Button, Card, Input, Badge, StatusBadge, Avatar, Textarea) with Jest tests
├── contexts/            # AuthContext for login state and role-based access control
├── pages/               # Dashboard, Projects (CRUD + review flows), AdminUsers, Profile, Notifications, Reports
│   └── projects/        # Create/Edit/Submit/Review/New Version entry points with full workflow
├── services/            # Axios API wrapper, auth service, project service, user service
├── lib/                 # Constants, utility helpers, and TypeScript types
└── assets/ + styles     # Tailwind-driven styling with custom design tokens
```

### 4.2 State & Data Access
- `AuthContext` provides authentication state, user data persistence, role-based access control flags (isProjectManager, isAdmin, etc.), and automatic token refresh.
- `services/api.ts` configures Axios with dynamic base URL, credential cookies, Authorization headers, CSRF injection, comprehensive error handling, and 401 auto-logout.
- `projectService` supplies full CRUD operations, submit/review workflows, and React Query integration for optimistic updates and cache management.
- `userService` handles user profile management, admin operations, and account settings with proper TypeScript typing.

### 4.3 UX Highlights
- **Dashboard**: Real-time project summaries with status filtering, recent activity feed, and interactive status badges using Heroicons for visual clarity.
- **Role-aware routing**: `ProtectedRoute` implements granular access control; responsive sidebar/navbar adapts to user roles and permissions.
- **Modern UI Components**: 8+ reusable UI components with TypeScript support, comprehensive Jest testing, and consistent design system using Tailwind CSS.
- **Toast Notifications**: React Toastify integration for user feedback on actions, form submissions, and error handling with customizable positioning.

## 5. Key Product Workflows
1. **Project authoring**: Submitters create drafts with validated metadata, attach drawing counts, and optionally link to shared folders.
2. **Versioning**: Each submission increments `version` within a shared `project_group_id`, allowing comparisons between releases and ensuring `is_latest_version()` logic can highlight current builds.
3. **Approval cycle**: Multi-stage status transitions are enforced server-side. Approvers review via dedicated UI, changing status to Approved/Conditional/Revise/Rejected with commentary tracked in `ApprovalHistory`.
4. **Notifications**: Upon submission/review events, the Brevo service fan-out emails to submitters and admins respecting user preferences and logging delivery outcomes.
5. **Audit & compliance**: `AuditLog`, `UserSession`, and project history tables deliver end-to-end traceability for security reports.

## 6. API Surface (Representative)
- `/api/projects/` Full CRUD with throttling, role-based permissions, plus `/submit/` and `/review/` actions with workflow validation.
- `/api/drawings/` Drawing lifecycle management with project-scoped access control and automatic count updates.
- `/accounts/api/login|logout|user|change-password|password-reset-request/` Complete authentication system with session management.
- **Rate Limiting**: Tiered throttling (1000/hour for users, 2000/hour for admins, 100/hour for anonymous) with DRF integration.
- **Security**: CSRF protection on all state-changing endpoints, CORS configuration, and request/response logging.

## 7. Security & Compliance
- **Input Validation**: Comprehensive validators for all fields, Bleach integration for HTML sanitization, and Django ORM SQL injection protection.
- **Role-Based Access Control**: 4-tier permission system (Admin/Approver/Submitter/Viewer) with DRF permission classes and API-level throttling.
- **Session Management**: IP tracking, user agent logging, activity monitoring, and secure session configuration with timeout controls.
- **Audit Trail**: Complete logging of all user actions, status changes, and system events with structured data storage for compliance reporting.
- **Production Security**: HTTPS enforcement, HSTS headers, secure cookies, XSS protection, and Sentry error monitoring with PII filtering.

## 8. Documentation & Ops
- **Comprehensive Docs**: Environment setup, deployment guides, architecture documentation, security analysis, UI style guides, and code review standards.
- **Management Commands**: 15+ utilities for data seeding, permission bootstrap, email testing, drawing count fixes, version management, and system maintenance.
- **Testing Strategy**: Backend Django test framework with model/view/serializer testing; frontend Jest + Testing Library with component coverage; API integration testing.
- **Logging & Monitoring**: Multi-level logging (development/production), rotating file handlers, security event logging, Sentry integration, and structured error tracking.
- **Environment Configuration**: `.env`-driven settings with development/production separation, database flexibility (MySQL/PostgreSQL), and Redis caching integration.

## 9. Current Status & Next Steps
- **Production Ready**: Fully functional with comprehensive testing, security measures, and operational tooling. Recent migrations include project folder link migration and status workflow refinements.
- **Integration Points**: REST APIs for external system integration, Brevo email service for notifications, webhooks ready for implementation, and modular component architecture.
- **Scalability Features**: Redis caching, database optimization with proper indexing, async task processing with Celery, and CDN-ready static asset management.
- **Competitive Advantages**: Enterprise-grade audit trails, role-based workflows, real-time notifications, version control with project grouping, and responsive mobile-first UI.
- **Demo Highlights**: Interactive dashboard with live status updates, streamlined approval workflows, comprehensive user management, and detailed reporting capabilities.
