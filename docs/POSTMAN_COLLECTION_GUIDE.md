# Postman Collection Setup Guide for DocuHub API

## 📋 Quick Start Guide

### Step 1: Install Postman
1. Download Postman from [postman.com](https://www.postman.com/)
2. Install and create a free account
3. Open Postman desktop app

### Step 2: Create New Collection
1. Click **"New"** → **"Collection"**
2. Name it **"DocuHub API"**
3. Add description: **"Document management system API for project workflows"**

---

## 🔧 Environment Setup

### Step 3: Create Environment
1. Click **Environment** tab → **"Create Environment"**
2. Name: **"DocuHub Local"**
3. Add these variables:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `http://127.0.0.1:8000` | `http://127.0.0.1:8000` |
| `api_url` | `{{base_url}}/api` | `{{base_url}}/api` |
| `auth_token` | `your-token-here` | `your-token-here` |
| `project_id` | | |
| `document_id` | | |
| `project_group_id` | | |

4. Click **"Save"**
5. Select **"DocuHub Local"** as active environment

---

## 🔐 Authentication Setup

### Step 4: Get Authentication Token

**Method 1: Using Django Admin**
1. Start Django server: `./venv/Scripts/python.exe manage.py runserver`
2. Go to `http://127.0.0.1:8000/admin/`
3. Login with superuser credentials
4. Go to **Auth Tokens** → **Add Token**
5. Select your user and save
6. Copy the token and update `auth_token` variable in Postman

**Method 2: Create Token via API**
```bash
# In terminal/command prompt
curl -X POST "http://127.0.0.1:8000/api-token-auth/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-username",
    "password": "your-password"
  }'
```

### Step 5: Set Global Headers
1. In your collection, click **"..."** → **"Edit"**
2. Go to **"Authorization"** tab
3. Type: **"API Key"**
4. Key: **"Authorization"**
5. Value: **"Token {{auth_token}}"**
6. Add to: **"Header"**

---

## 📁 Collection Structure

Create folders in your collection with this structure:

```
📁 DocuHub API
├── 📁 1. Authentication
├── 📁 2. Project Groups  
├── 📁 3. Projects - CRUD
├── 📁 4. Documents - CRUD
├── 📁 5. Workflow Operations
├── 📁 6. Advanced Queries
└── 📁 7. Error Testing
```

---

## 🚀 Step-by-Step API Testing

### Folder 1: Authentication

#### Request 1.1: Test Authentication
- **Method**: `GET`
- **URL**: `{{api_url}}/projects/`
- **Headers**: Already inherited from collection
- **Expected**: 200 OK with project list

**Test Script:**
```javascript
pm.test("Authentication successful", function () {
    pm.response.to.have.status(200);
    pm.response.to.be.json;
});

pm.test("Response has required structure", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('results');
});
```

---

### Folder 2: Project Groups

#### Request 2.1: List All Projects (Groups)
- **Method**: `GET`
- **URL**: `{{api_url}}/projects/`
- **Description**: View all project versions and groups

**Test Script:**
```javascript
pm.test("Projects list retrieved", function () {
    pm.response.to.have.status(200);
    const jsonData = pm.response.json();
    
    if (jsonData.results.length > 0) {
        pm.environment.set("project_id", jsonData.results[0].id);
        pm.environment.set("project_group_id", jsonData.results[0].project_group);
    }
});
```

---

### Folder 3: Projects - CRUD

#### Request 3.1: Create New Project
- **Method**: `POST`
- **URL**: `{{api_url}}/projects/`
- **Headers**: `Content-Type: application/json`

**Body (JSON):**
```json
{
  "project_name": "Test API Project",
  "client_name": "Postman Testing Corp",
  "project_description": "Project created via Postman for API testing",
  "project_priority": "Normal",
  "deadline_date": "2024-06-30",
  "reference_no": "POST-API-001",
  "notes": "This is a test project created through the API"
}
```

**Test Script:**
```javascript
pm.test("Project created successfully", function () {
    pm.response.to.have.status(201);
    
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('project_name');
    pm.expect(jsonData.project_name).to.eql('Test API Project');
    
    // Save IDs for next requests
    pm.environment.set("project_id", jsonData.id);
    pm.environment.set("project_group_id", jsonData.project_group);
});

pm.test("Version number is 1 for new project", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.version_number).to.eql(1);
    pm.expect(jsonData.is_latest).to.be.true;
});
```

#### Request 3.2: Get Project Details
- **Method**: `GET`
- **URL**: `{{api_url}}/projects/{{project_id}}/`

**Test Script:**
```javascript
pm.test("Project details retrieved", function () {
    pm.response.to.have.status(200);
    const jsonData = pm.response.json();
    pm.expect(jsonData.id).to.eql(pm.environment.get("project_id"));
});
```

#### Request 3.3: Update Project (PATCH)
- **Method**: `PATCH`
- **URL**: `{{api_url}}/projects/{{project_id}}/`

**Body (JSON):**
```json
{
  "project_priority": "High",
  "notes": "Priority updated via Postman API test"
}
```

**Test Script:**
```javascript
pm.test("Project updated successfully", function () {
    pm.response.to.have.status(200);
    const jsonData = pm.response.json();
    pm.expect(jsonData.project_priority).to.eql('High');
});
```

---

### Folder 4: Documents - CRUD

#### Request 4.1: Create Document
- **Method**: `POST`
- **URL**: `{{api_url}}/documents/`

**Body (JSON):**
```json
{
  "project": "{{project_id}}",
  "document_number": "A001",
  "title": "Ground Floor Plan",
  "description": "Architectural ground floor layout",
  "discipline": "Architecture",
  "revision": "A",
  "status": "Draft"
}
```

**Test Script:**
```javascript
pm.test("Document created successfully", function () {
    pm.response.to.have.status(201);
    
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData.document_number).to.eql('A001');
    pm.expect(jsonData.status).to.eql('Draft');
    
    pm.environment.set("document_id", jsonData.id);
});
```

#### Request 4.2: List Documents
- **Method**: `GET`
- **URL**: `{{api_url}}/documents/?project={{project_id}}`

**Test Script:**
```javascript
pm.test("Documents list retrieved", function () {
    pm.response.to.have.status(200);
    const jsonData = pm.response.json();
    pm.expect(jsonData.results).to.be.an('array');
    
    if (jsonData.results.length > 0) {
        pm.expect(jsonData.results[0]).to.have.property('document_number');
    }
});
```

#### Request 4.3: Update Document Status
- **Method**: `PATCH`
- **URL**: `{{api_url}}/documents/{{document_id}}/`

**Body (JSON):**
```json
{
  "status": "Submitted"
}
```

**Test Script:**
```javascript
pm.test("Document status updated", function () {
    pm.response.to.have.status(200);
    const jsonData = pm.response.json();
    pm.expect(jsonData.status).to.eql('Submitted');
});
```

#### Request 4.4: Create Second Document
- **Method**: `POST`
- **URL**: `{{api_url}}/documents/`

**Body (JSON):**
```json
{
  "project": "{{project_id}}",
  "document_number": "S001",
  "title": "Foundation Plan",
  "description": "Structural foundation details",
  "discipline": "Structural",
  "revision": "A",
  "status": "Draft"
}
```

---

### Folder 5: Workflow Operations

#### Request 5.1: Submit Project for Review
- **Method**: `POST`
- **URL**: `{{api_url}}/projects/{{project_id}}/submit/`

**Body (JSON):**
```json
{
  "submission_notes": "All documents ready for review - submitted via Postman"
}
```

**Test Script:**
```javascript
pm.test("Project submitted successfully", function () {
    pm.response.to.have.status(200);
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('message');
    pm.expect(jsonData).to.have.property('submitted_documents');
});
```

#### Request 5.2: Review Project (Approve)
- **Method**: `POST`
- **URL**: `{{api_url}}/projects/{{project_id}}/review/`

**Body (JSON):**
```json
{
  "action": "approve",
  "comments": "All documents approved - tested via Postman API",
  "documents": [
    {
      "id": "{{document_id}}",
      "status": "Approved",
      "comments": "Architecture drawings look good"
    }
  ]
}
```

**Test Script:**
```javascript
pm.test("Project review completed", function () {
    pm.response.to.have.status(200);
    const jsonData = pm.response.json();
    pm.expect(jsonData.action_taken).to.eql('approve');
});
```

#### Request 5.3: Review Project (Request Revisions)
- **Method**: `POST`
- **URL**: `{{api_url}}/projects/{{project_id}}/review/`

**Body (JSON):**
```json
{
  "action": "revision_required",
  "comments": "Some documents need revision",
  "documents": [
    {
      "id": "{{document_id}}",
      "status": "Revision_Required", 
      "comments": "Please update dimensions on ground floor plan"
    }
  ]
}
```

---

### Folder 6: Advanced Queries

#### Request 6.1: Filter Documents by Status
- **Method**: `GET`
- **URL**: `{{api_url}}/documents/?status=Approved`

#### Request 6.2: Search Projects by Name
- **Method**: `GET`
- **URL**: `{{api_url}}/projects/?search=Test`

#### Request 6.3: Filter by Priority
- **Method**: `GET`
- **URL**: `{{api_url}}/projects/?project_priority=High`

#### Request 6.4: Get Latest Versions Only
- **Method**: `GET`
- **URL**: `{{api_url}}/projects/?is_latest=true`

#### Request 6.5: Filter by Discipline
- **Method**: `GET`
- **URL**: `{{api_url}}/documents/?discipline=Architecture`

---

### Folder 7: Error Testing

#### Request 7.1: Invalid Status Transition
- **Method**: `PATCH`
- **URL**: `{{api_url}}/documents/{{document_id}}/`

**Body (JSON):**
```json
{
  "status": "InvalidStatus"
}
```

**Test Script:**
```javascript
pm.test("Invalid status rejected", function () {
    pm.response.to.have.status(400);
});
```

#### Request 7.2: Duplicate Document Number
- **Method**: `POST`
- **URL**: `{{api_url}}/documents/`

**Body (JSON):**
```json
{
  "project": "{{project_id}}",
  "document_number": "A001",
  "title": "Duplicate Document",
  "status": "Draft"
}
```

**Test Script:**
```javascript
pm.test("Duplicate document rejected", function () {
    pm.response.to.have.status(400);
});
```

---

## 🔄 Collection-Level Test Scripts

### Pre-request Script (Collection Level)
```javascript
// Add timestamp to requests for tracking
pm.globals.set("timestamp", new Date().toISOString());

// Log the request for debugging
console.log(`Making ${pm.request.method} request to: ${pm.request.url}`);
```

### Test Script (Collection Level)
```javascript
// Global tests for all requests
pm.test("Response time is less than 2000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});

pm.test("Response has proper headers", function () {
    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");
});

// Log response for debugging
console.log(`Response status: ${pm.response.code}`);
console.log(`Response time: ${pm.response.responseTime}ms`);
```

---

## 📊 Running the Collection

### Option 1: Manual Testing
1. Select each request in order
2. Click **"Send"** 
3. Verify responses and test results
4. Check the **Test Results** tab

### Option 2: Collection Runner
1. Click **"Runner"** button
2. Select **"DocuHub API"** collection
3. Select **"DocuHub Local"** environment
4. Choose iterations: **1**
5. Delay: **1000ms** between requests
6. Click **"Run DocuHub API"**

### Option 3: Newman CLI
```bash
# Install Newman globally
npm install -g newman

# Export collection and environment from Postman
# Then run:
newman run DocuHub-API.postman_collection.json \
  -e DocuHub-Local.postman_environment.json \
  --reporters cli,html \
  --reporter-html-export results.html
```

---

## 📈 Monitoring & Reports

### Collection Variables for Tracking
Add these to monitor your testing:

| Variable | Description |
|----------|-------------|
| `test_run_id` | Unique ID for test run |
| `total_requests` | Counter for requests made |
| `failed_requests` | Counter for failed requests |

### Custom Test Reports
```javascript
// In collection test script
pm.test("Update test counters", function () {
    let total = pm.globals.get("total_requests") || 0;
    pm.globals.set("total_requests", total + 1);
    
    if (pm.response.code >= 400) {
        let failed = pm.globals.get("failed_requests") || 0;
        pm.globals.set("failed_requests", failed + 1);
    }
});
```

---

## 🚨 Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check `auth_token` in environment
   - Verify token is active in Django admin

2. **404 Not Found**
   - Verify Django server is running on port 8000
   - Check `base_url` environment variable

3. **422 Validation Error**
   - Check required fields in request body
   - Verify data types match model requirements

4. **500 Internal Server Error**
   - Check Django server logs
   - Verify database migrations are applied

### Debug Tips
1. Enable **Console** in Postman to see logs
2. Use **Test Results** tab to see detailed test outcomes
3. Check **Response** body for detailed error messages
4. Use Django admin to verify data creation

---

This comprehensive Postman setup will allow you to test all API endpoints systematically and verify the document-centric workflow is working correctly!