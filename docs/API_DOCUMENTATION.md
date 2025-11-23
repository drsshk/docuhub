# DocuHub API Documentation

## Overview

DocuHub API provides a RESTful interface for managing document-centric project workflows. The API follows the new ERD architecture where:

- **Projects** group documents by version but have no status
- **Documents** carry workflow status and approval state
- **Project Groups** link multiple versions of the same project
- **Approval workflows** happen at the document level

## Base URL

```
http://127.0.0.1:8000/api/
```

## Authentication

All API endpoints require authentication. Use Django's built-in session authentication or token-based authentication.

### Headers Required
```
Content-Type: application/json
Authorization: Token your-token-here
```

---

## API Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/project-groups/` | GET, POST | List/Create project groups |
| `/api/project-groups/{id}/` | GET, PUT, PATCH, DELETE | Project group detail operations |
| `/api/projects/` | GET, POST | List/Create projects |
| `/api/projects/{id}/` | GET, PUT, PATCH, DELETE | Project detail operations |
| `/api/documents/` | GET, POST | List/Create documents |
| `/api/documents/{id}/` | GET, PUT, PATCH, DELETE | Document detail operations |
| `/api/projects/{id}/submit/` | POST | Submit project for review |
| `/api/projects/{id}/review/` | POST | Review project (approve/reject) |
| `/api/approval-history/` | GET | List approval history |
| `/api/project-history/` | GET | List project history/audit logs |
| `/api/auth/token/` | POST | Generate authentication token |
| `/api/auth/profile/` | GET, PATCH | User profile management |

---

# Project Groups API

## 1. List Project Groups
**Endpoint:** `GET /api/project-groups/`
**Description:** Get all project groups (logical families of projects)

```bash
# Get all project groups
curl -X GET "http://127.0.0.1:8000/api/project-groups/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json"

# Filter by client
curl -X GET "http://127.0.0.1:8000/api/project-groups/?client_name=Hospital" \
  -H "Authorization: Token your-token"
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "code": "HEP-2024",
      "name": "Hospital Extension Phase 1",
      "client_name": "City General Hospital",
      "created_by": 1,
      "created_by_name": "John Architect",
      "created_at": "2024-01-10T09:00:00Z",
      "updated_at": "2024-01-20T14:22:00Z",
      "latest_project": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "version_number": 2,
        "version_display": "V002",
        "created_at": "2024-01-15T10:30:00Z"
      }
    }
  ]
}
```

## 2. Create Project Group
**Endpoint:** `POST /api/project-groups/`
**Description:** Create a new project group

```bash
curl -X POST "http://127.0.0.1:8000/api/project-groups/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SCH-2024",
    "name": "School Building Complex",
    "client_name": "Department of Education"
  }'
```

**Response:** `201 Created`
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "code": "SCH-2024", 
  "name": "School Building Complex",
  "client_name": "Department of Education",
  "created_by": 1,
  "created_by_name": "John Architect",
  "created_at": "2024-01-25T11:15:00Z",
  "updated_at": "2024-01-25T11:15:00Z",
  "latest_project": null
}
```

## 3. Get Project Group Details
**Endpoint:** `GET /api/project-groups/{id}/`

```bash
curl -X GET "http://127.0.0.1:8000/api/project-groups/770e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Token your-token"
```

**Response:** `200 OK`
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "code": "SCH-2024",
  "name": "School Building Complex", 
  "client_name": "Department of Education",
  "created_by": 1,
  "created_by_name": "John Architect",
  "projects": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440000",
      "version_number": 1,
      "is_latest": true,
      "created_at": "2024-01-25T11:20:00Z"
    }
  ]
}
```

---

# Projects API

## 1. Create Project

**Endpoint:** `POST /api/projects/`
**Description:** Create a new project version

```bash
curl -X POST "http://127.0.0.1:8000/api/projects/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Office Building Renovation",
    "client_name": "Tech Corp Inc",
    "project_description": "Complete renovation of 10-story office building",
    "project_priority": "Normal",
    "deadline_date": "2024-06-30",
    "reference_no": "OBR-2024-003",
    "notes": "Phase 1 - Initial design concepts"
  }'
```

**Response:** `201 Created`
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "project_group": "880e8400-e29b-41d4-a716-446655440000",
  "project_name": "Office Building Renovation",
  "client_name": "Tech Corp Inc",
  "project_description": "Complete renovation of 10-story office building",
  "version_number": 1,
  "is_latest": true,
  "created_by": 1,
  "created_by_name": "John Architect",
  "project_priority": "Normal",
  "deadline_date": "2024-06-30",
  "reference_no": "OBR-2024-003",
  "notes": "Phase 1 - Initial design concepts",
  "no_of_drawings": 0,
  "created_at": "2024-01-25T09:15:00Z",
  "updated_at": "2024-01-25T09:15:00Z",
  "documents": [],
  "approval_history": []
}
```

## 2. Get Project Details

**Endpoint:** `GET /api/projects/{id}/`

```bash
curl -X GET "http://127.0.0.1:8000/api/projects/770e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json"
```

**Response:** `200 OK`
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "project_group": "880e8400-e29b-41d4-a716-446655440000",
  "project_name": "Office Building Renovation",
  "client_name": "Tech Corp Inc",
  "version_number": 1,
  "is_latest": true,
  "documents": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440000",
      "document_number": "A001",
      "title": "Ground Floor Plan",
      "status": "Draft",
      "discipline": "Architecture"
    }
  ],
  "approval_history": []
}
```

## 3. Update Project

**Endpoint:** `PUT /api/projects/{id}/` or `PATCH /api/projects/{id}/`

```bash
# Full update (PUT)
curl -X PUT "http://127.0.0.1:8000/api/projects/770e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Office Building Renovation - Updated",
    "client_name": "Tech Corp Inc",
    "project_description": "Complete renovation with green building features",
    "project_priority": "High",
    "deadline_date": "2024-08-15",
    "notes": "Updated scope to include sustainability features"
  }'

# Partial update (PATCH)
curl -X PATCH "http://127.0.0.1:8000/api/projects/770e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "project_priority": "Urgent",
    "notes": "Client requested expedited timeline"
  }'
```

## 4. Delete Project

**Endpoint:** `DELETE /api/projects/{id}/`

```bash
curl -X DELETE "http://127.0.0.1:8000/api/projects/770e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Token your-token"
```

**Response:** `204 No Content`

---

# Documents API

## 1. List Documents

**Endpoint:** `GET /api/documents/`

```bash
# Get all documents
curl -X GET "http://127.0.0.1:8000/api/documents/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json"

# Filter by project
curl -X GET "http://127.0.0.1:8000/api/documents/?project=770e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Token your-token"

# Filter by status
curl -X GET "http://127.0.0.1:8000/api/documents/?status=Draft" \
  -H "Authorization: Token your-token"
```

**Response:** `200 OK`
```json
{
  "count": 3,
  "results": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440000",
      "project": "770e8400-e29b-41d4-a716-446655440000",
      "document_number": "A001",
      "title": "Ground Floor Plan",
      "description": "Detailed ground floor architectural plan",
      "discipline": "Architecture",
      "revision": "A",
      "status": "Draft",
      "file_path": "/media/documents/A001_ground_floor.pdf",
      "created_by": 1,
      "created_by_name": "John Architect",
      "created_at": "2024-01-25T10:30:00Z",
      "updated_at": "2024-01-25T10:30:00Z"
    }
  ]
}
```

## 2. Create Document

**Endpoint:** `POST /api/documents/`

```bash
curl -X POST "http://127.0.0.1:8000/api/documents/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "770e8400-e29b-41d4-a716-446655440000",
    "document_number": "S001",
    "title": "Foundation Plan",
    "description": "Structural foundation layout and details",
    "discipline": "Structural",
    "revision": "A",
    "status": "Draft"
  }'
```

**Response:** `201 Created`
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440000",
  "project": "770e8400-e29b-41d4-a716-446655440000",
  "document_number": "S001",
  "title": "Foundation Plan",
  "description": "Structural foundation layout and details",
  "discipline": "Structural",
  "revision": "A",
  "status": "Draft",
  "file_path": null,
  "created_by": 1,
  "created_by_name": "John Architect",
  "created_at": "2024-01-25T11:45:00Z",
  "updated_at": "2024-01-25T11:45:00Z"
}
```

## 3. Update Document Status

**Endpoint:** `PATCH /api/documents/{id}/`

```bash
# Submit document for review
curl -X PATCH "http://127.0.0.1:8000/api/documents/aa0e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Submitted"
  }'

# Approve document
curl -X PATCH "http://127.0.0.1:8000/api/documents/aa0e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Approved"
  }'
```

## 4. Upload Document File

**Endpoint:** `PATCH /api/documents/{id}/` (with file upload)

```bash
curl -X PATCH "http://127.0.0.1:8000/api/documents/aa0e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Token your-token" \
  -F "file_path=@/path/to/foundation_plan.pdf" \
  -F "title=Foundation Plan - Updated"
```

---

# Custom Workflow Endpoints

## 1. Submit Project for Review

**Endpoint:** `POST /api/projects/{id}/submit/`
**Description:** Submit all documents in a project for review

```bash
curl -X POST "http://127.0.0.1:8000/api/projects/770e8400-e29b-41d4-a716-446655440000/submit/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "submission_notes": "All drawings completed and ready for review"
  }'
```

**Response:** `200 OK`
```json
{
  "message": "Project submitted successfully",
  "submitted_documents": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440000",
      "document_number": "A001",
      "status": "Pending_Review"
    },
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440000", 
      "document_number": "S001",
      "status": "Pending_Review"
    }
  ],
  "submission_id": "bb0e8400-e29b-41d4-a716-446655440000"
}
```

## 2. Review Project

**Endpoint:** `POST /api/projects/{id}/review/`
**Description:** Approve, reject, or request revisions for project documents

```bash
# Approve all documents
curl -X POST "http://127.0.0.1:8000/api/projects/770e8400-e29b-41d4-a716-446655440000/review/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "comments": "All drawings meet requirements. Approved for construction.",
    "documents": [
      {"id": "990e8400-e29b-41d4-a716-446655440000", "status": "Approved"},
      {"id": "aa0e8400-e29b-41d4-a716-446655440000", "status": "Approved"}
    ]
  }'

# Request revisions for specific documents
curl -X POST "http://127.0.0.1:8000/api/projects/770e8400-e29b-41d4-a716-446655440000/review/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "revision_required",
    "comments": "Please address structural comments",
    "documents": [
      {
        "id": "aa0e8400-e29b-41d4-a716-446655440000",
        "status": "Revision_Required",
        "comments": "Foundation depth needs to be increased per soil report"
      }
    ]
  }'
```

**Response:** `200 OK`
```json
{
  "message": "Review completed successfully",
  "action_taken": "revision_required",
  "reviewed_documents": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440000",
      "document_number": "S001", 
      "new_status": "Revision_Required",
      "comments": "Foundation depth needs to be increased per soil report"
    }
  ],
  "review_id": "cc0e8400-e29b-41d4-a716-446655440000"
}
```

---

# Status Workflow

## Document Status Transitions

Documents follow this status workflow:

```
Draft → Submitted → Pending_Review → [Approved | Rejected | Revision_Required]
                                                      ↓
                                              Back to Draft (for revisions)
```

### Valid Status Transitions:
- **Draft** → Submitted
- **Submitted** → Pending_Review  
- **Pending_Review** → Approved, Rejected, Revision_Required
- **Revision_Required** → Draft (for updates)
- **Any Status** → Obsolete

---

# Error Handling

## Common HTTP Status Codes

| Status Code | Description | Example |
|-------------|-------------|---------|
| 200 | Success | Request completed successfully |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation errors |
| 500 | Server Error | Internal server error |

## Error Response Format

```json
{
  "error": "Validation failed",
  "details": {
    "field_name": ["This field is required"],
    "status": ["Invalid status transition"]
  },
  "code": "VALIDATION_ERROR"
}
```

## Common Validation Errors

### Project Validation
```json
{
  "error": "Project validation failed", 
  "details": {
    "project_name": ["Project name is required"],
    "deadline_date": ["Date cannot be in the past"]
  }
}
```

### Document Validation
```json
{
  "error": "Document validation failed",
  "details": {
    "document_number": ["Document number A001 already exists in this project"],
    "status": ["Cannot transition from Approved to Draft"]
  }
}
```

---

# Pagination

All list endpoints support pagination:

**Request:**
```bash
curl -X GET "http://127.0.0.1:8000/api/projects/?page=2&page_size=10" \
  -H "Authorization: Token your-token"
```

**Response:**
```json
{
  "count": 45,
  "next": "http://127.0.0.1:8000/api/projects/?page=3&page_size=10",
  "previous": "http://127.0.0.1:8000/api/projects/?page=1&page_size=10", 
  "results": [...]
}
```

---

# Filtering and Search

## Project Filtering
```bash
# Filter by priority
GET /api/projects/?project_priority=High

# Filter by client
GET /api/projects/?client_name=Tech Corp

# Search by name
GET /api/projects/?search=Hospital

# Filter latest versions only
GET /api/projects/?is_latest=true
```

## Document Filtering  
```bash
# Filter by status
GET /api/documents/?status=Pending_Review

# Filter by discipline
GET /api/documents/?discipline=Architecture

# Filter by project
GET /api/documents/?project={project_id}

# Search by title or number
GET /api/documents/?search=foundation
```

---

# Rate Limiting

API endpoints are rate-limited per user:
- **Authenticated users**: 1000 requests/hour
- **Project operations**: 100 requests/hour

Rate limit headers in response:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1643723400
```

---

# Data Models

## Project Model Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | - | Auto-generated project ID |
| project_group | UUID | Yes | Links project versions |
| project_name | String | Yes | Project name (max 255 chars) |
| client_name | String | No | Client organization name |
| version_number | Integer | - | Auto-incremented version |
| is_latest | Boolean | - | True for latest version |
| project_description | Text | No | Detailed project description |
| project_priority | Choice | No | Low, Normal, High, Urgent |
| deadline_date | Date | No | Project deadline |
| reference_no | String | No | External reference number |
| notes | Text | No | Internal project notes |
| created_by | Integer | - | User who created project |
| created_at | DateTime | - | Creation timestamp |
| updated_at | DateTime | - | Last update timestamp |

## Document Model Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | - | Auto-generated document ID |
| project | UUID | Yes | Parent project ID |
| document_number | String | Yes | Unique document identifier |
| title | String | No | Document title |
| description | Text | No | Document description |
| discipline | String | No | Engineering discipline |
| revision | String | No | Document revision (A, B, C...) |
| status | Choice | Yes | Workflow status |
| file_path | File | No | Uploaded document file |
| created_by | Integer | - | User who created document |
| updated_by | Integer | No | User who last updated |
| created_at | DateTime | - | Creation timestamp |
| updated_at | DateTime | - | Last update timestamp |

---

# Approval History API

## 1. List Approval History
**Endpoint:** `GET /api/approval-history/`
**Description:** Get approval history records for audit and tracking

```bash
# Get all approval history
curl -X GET "http://127.0.0.1:8000/api/approval-history/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json"

# Filter by project
curl -X GET "http://127.0.0.1:8000/api/approval-history/?project=770e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Token your-token"

# Filter by action
curl -X GET "http://127.0.0.1:8000/api/approval-history/?action=APPROVED" \
  -H "Authorization: Token your-token"

# Filter by date range
curl -X GET "http://127.0.0.1:8000/api/approval-history/?performed_at__gte=2024-01-01&performed_at__lte=2024-02-01" \
  -H "Authorization: Token your-token"
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": "dd0e8400-e29b-41d4-a716-446655440000",
      "project": "770e8400-e29b-41d4-a716-446655440000",
      "project_name": "Office Building Renovation",
      "document": "aa0e8400-e29b-41d4-a716-446655440000",
      "document_number": "S001",
      "action": "APPROVED",
      "from_status": "Pending_Review",
      "to_status": "Approved",
      "performed_by": 2,
      "performed_by_name": "Sarah Reviewer",
      "performed_at": "2024-01-26T14:30:00Z",
      "comment": "Foundation plan meets all structural requirements",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

## 2. Get Approval History Details
**Endpoint:** `GET /api/approval-history/{id}/`

```bash
curl -X GET "http://127.0.0.1:8000/api/approval-history/dd0e8400-e29b-41d4-a716-446655440000/" \
  -H "Authorization: Token your-token"
```

---

# Project History API

## 1. List Project History
**Endpoint:** `GET /api/project-history/`
**Description:** Get project and document change history for audit trail

```bash
# Get all project history
curl -X GET "http://127.0.0.1:8000/api/project-history/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json"

# Filter by event type
curl -X GET "http://127.0.0.1:8000/api/project-history/?event_type=DOCUMENT_ADDED" \
  -H "Authorization: Token your-token"

# Filter by project
curl -X GET "http://127.0.0.1:8000/api/project-history/?project=770e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Token your-token"
```

**Response:**
```json
{
  "count": 8,
  "results": [
    {
      "id": "ee0e8400-e29b-41d4-a716-446655440000",
      "project": "770e8400-e29b-41d4-a716-446655440000",
      "project_name": "Office Building Renovation",
      "document": "aa0e8400-e29b-41d4-a716-446655440000",
      "document_number": "S001",
      "event_type": "DOCUMENT_ADDED",
      "payload": {
        "document_details": {
          "title": "Foundation Plan",
          "discipline": "Structural",
          "status": "Draft"
        },
        "metadata": {
          "file_size": 2048576,
          "created_by_role": "engineer"
        }
      },
      "performed_by": 1,
      "performed_by_name": "John Architect", 
      "performed_at": "2024-01-25T11:45:00Z"
    }
  ]
}
```

---

# Authentication API

## 1. Generate Authentication Token
**Endpoint:** `POST /api/auth/token/`
**Description:** Generate API authentication token using username/password

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.architect",
    "password": "your-password"
  }'
```

**Response:** `200 OK`
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "john.architect",
    "email": "john@company.com",
    "first_name": "John",
    "last_name": "Architect"
  },
  "expires_at": "2024-02-25T11:45:00Z"
}
```

## 2. Refresh Token
**Endpoint:** `POST /api/auth/token/refresh/`

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/token/refresh/" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

**Response:** `200 OK`
```json
{
  "token": "8833a08088b51abce8307ac745cd3d4aaefc5d3a",
  "expires_at": "2024-03-25T11:45:00Z"
}
```

---

# User Profile API

## 1. Get User Profile
**Endpoint:** `GET /api/auth/profile/`
**Description:** Get current user's profile information

```bash
curl -X GET "http://127.0.0.1:8000/api/auth/profile/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json"
```

**Response:** `200 OK`
```json
{
  "id": "ff0e8400-e29b-41d4-a716-446655440000",
  "user": {
    "id": 1,
    "username": "john.architect",
    "email": "john@company.com", 
    "first_name": "John",
    "last_name": "Architect",
    "is_staff": false,
    "is_active": true,
    "date_joined": "2024-01-01T10:00:00Z"
  },
  "full_name": "John Architect",
  "department": "Architecture",
  "job_title": "Senior Architect",
  "role": "submitter",
  "manager": null,
  "time_zone": "Asia/Kuala_Lumpur",
  "phone_number": "+60-123-456-789",
  "employee_id": "EMP001",
  "bio": "Senior architect with 10+ years experience in commercial projects",
  "location": "Kuala Lumpur, Malaysia",
  "hire_date": "2020-01-15",
  "is_active_employee": true,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-25T09:30:00Z"
}
```

## 2. Update User Profile
**Endpoint:** `PATCH /api/auth/profile/`

```bash
curl -X PATCH "http://127.0.0.1:8000/api/auth/profile/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+60-123-456-999",
    "bio": "Senior architect specializing in sustainable design",
    "time_zone": "Asia/Singapore"
  }'
```

**Response:** `200 OK`
```json
{
  "id": "ff0e8400-e29b-41d4-a716-446655440000",
  "phone_number": "+60-123-456-999",
  "bio": "Senior architect specializing in sustainable design",
  "time_zone": "Asia/Singapore",
  "updated_at": "2024-01-26T10:15:00Z"
}
```

## 3. Get Notification Preferences
**Endpoint:** `GET /api/auth/profile/notifications/`

```bash
curl -X GET "http://127.0.0.1:8000/api/auth/profile/notifications/" \
  -H "Authorization: Token your-token"
```

**Response:** `200 OK`
```json
{
  "id": "gg0e8400-e29b-41d4-a716-446655440000",
  "email_on_submission": true,
  "email_on_approval": true,
  "email_on_rejection": true,
  "email_on_revision_required": true,
  "digest_frequency": "IMMEDIATE",
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-15T14:20:00Z"
}
```

## 4. Update Notification Preferences
**Endpoint:** `PATCH /api/auth/profile/notifications/`

```bash
curl -X PATCH "http://127.0.0.1:8000/api/auth/profile/notifications/" \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "email_on_submission": false,
    "digest_frequency": "DAILY"
  }'
```

---

# Advanced Filtering Examples

## Project Groups Filtering
```bash
# Search by name or code
GET /api/project-groups/?search=Hospital

# Filter by creation date
GET /api/project-groups/?created_at__gte=2024-01-01

# Order by name
GET /api/project-groups/?ordering=name
```

## Approval History Filtering
```bash
# Filter by performer
GET /api/approval-history/?performed_by=2

# Filter by date range
GET /api/approval-history/?performed_at__range=2024-01-01,2024-01-31

# Filter by action and status
GET /api/approval-history/?action=APPROVED&to_status=Approved
```

## Project History Filtering
```bash
# Filter by event type
GET /api/project-history/?event_type=VERSION_CREATED

# Filter by user actions
GET /api/project-history/?performed_by__username=john.architect

# Order by date (newest first)
GET /api/project-history/?ordering=-performed_at
```

---

# Webhook Notifications

DocuHub can send webhook notifications for key events:

## Webhook Events
- `project.created` - New project created
- `project.submitted` - Project submitted for review
- `document.status_changed` - Document status updated
- `approval.completed` - Approval/rejection completed

## Webhook Payload Example
```json
{
  "event": "document.status_changed",
  "timestamp": "2024-01-26T10:30:00Z",
  "data": {
    "document_id": "aa0e8400-e29b-41d4-a716-446655440000",
    "document_number": "S001",
    "old_status": "Pending_Review", 
    "new_status": "Approved",
    "project_id": "770e8400-e29b-41d4-a716-446655440000",
    "project_name": "Office Building Renovation",
    "performed_by": {
      "id": 2,
      "username": "sarah.reviewer",
      "full_name": "Sarah Reviewer"
    }
  }
}
```

---

This comprehensive API documentation covers all CRUD operations, workflow endpoints, audit trails, and user management. For Postman setup, import these curl commands or create a Postman collection with the provided examples.