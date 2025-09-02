# DocuHub - Technical Drawing Version Management System

## Overview

DocuHub is an enterprise-grade Django web application meticulously designed to streamline the management and lifecycle of technical drawing versions. It provides a robust platform for organizations to handle their critical design documentation with precision and control. Key features include:

*   **Automated Approval Workflows**: Configurable multi-stage approval processes to ensure drawings meet quality and compliance standards.
*   **Comprehensive Audit Trails**: Detailed logging of all actions, changes, and approvals for full accountability and historical tracking.
*   **Integrated Email Notification System**: Real-time alerts for status changes, new submissions, and approval requests.
*   **Structured Project Lifecycle Management**: Organize drawings within projects, managing their evolution from draft to approved and obsolete states.
*   **Role-Based Access Control (RBAC)**: Granular permissions to control user access and actions based on their roles within the system.
*   **Enterprise Security Features**: Built with security best practices, including API throttling and secure session management.

## Technology Stack

### Backend
*   **Python 3.8+**: The core programming language.
*   **Django 4.2.7**: High-level Python web framework for rapid development and clean, pragmatic design.
*   **Django REST Framework**: Powerful and flexible toolkit for building Web APIs.
*   **Celery**: Distributed task queue for handling background tasks like email notifications and complex data processing.
*   **MySQL (Production) / SQLite (Development)**: Database systems for data persistence.
*   **Gunicorn**: Python WSGI HTTP Server for UNIX, used to run Django applications in production.

### Frontend
*   **React**: A JavaScript library for building user interfaces, providing a component-based architecture.
*   **Vite**: A next-generation frontend tooling that provides extremely fast development server and build times.
*   **TypeScript**: A superset of JavaScript that adds static types, enhancing code quality and maintainability.
*   **Tailwind CSS**: A utility-first CSS framework for rapidly building custom designs.
*   **Axios**: A promise-based HTTP client for making API requests from the browser.

## Getting Started

### Prerequisites
Before you begin, ensure you have the following installed:

*   **Python 3.8 or higher**: Download from [python.org](https://www.python.org/).
*   **Node.js (LTS recommended) and npm**: Download from [nodejs.org](https://nodejs.org/).
*   **MySQL Server**: Required for production deployment. For development, SQLite is used by default.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd docuhub
    ```

2.  **Setup Backend (Python/Django):**
    ```bash
    # Create a Python virtual environment
    python -m venv venv
    # Activate the virtual environment
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate     # On Windows

    # Install backend dependencies
    pip install -r requirements.txt
    ```

3.  **Setup Frontend (React/TypeScript):**
    ```bash
    cd frontend
    # Install frontend dependencies
    npm install
    cd ..
    ```

4.  **Configure Environment Variables:**
    - Create a `.env` file in the project root (`/mnt/c/Users/darus.ishak/Documents/docuhub/.env`).
    - Copy the contents from `docuhub/.env.example` into your new `.env` file.
    - Update the database credentials, secret key, and other settings as required for your environment.

5.  **Initialize Database and Static Files:**
    ```bash
    # Apply database migrations
    python manage.py migrate
    # Create a superuser for administrative access
    python manage.py createsuperuser
    # Collect static files for deployment
    python manage.py collectstatic --noinput
    # Setup default roles (e.g., Admin, Editor, Viewer)
    python manage.py setup_roles
    ```

### Running the Application (Development)

1.  **Start the Backend Development Server:**
    ```bash
    # Ensure your virtual environment is activated
    python manage.py runserver
    ```
    The backend API will be accessible, typically at `http://localhost:8000`.

2.  **Start the Frontend Development Server:**
    ```bash
    cd frontend
    npm run dev
    ```
    The frontend application will be available, typically at `http://localhost:5173`.

    Access the application by navigating to `http://localhost:5173` in your web browser.

## Development Guidelines

### Code Style and Formatting
*   **Python**: We use `Black` for Python code formatting.
    ```bash
    pip install black
    black .
    ```
*   **JavaScript/TypeScript**: We use `ESLint` and `Prettier` for code linting and formatting.
    ```bash
    cd frontend
    npm install # if not already installed
    npm run lint
    # Prettier usually runs on save in most IDEs, or can be run via:
    # npx prettier --write .
    cd ..
    ```

### Running Tests
*   **Backend Tests (Python/Django)**:
    ```bash
    # Ensure your virtual environment is activated
    python manage.py test
    ```
*   **Frontend Tests (React/Jest)**:
    ```bash
    cd frontend
    npm test
    cd ..
    ```

### Database Migrations
When making changes to Django models:
1.  Create new migration files:
    ```bash
    python manage.py makemigrations
    ```
2.  Apply migrations to the database:
    ```bash
    python manage.py migrate
    ```

## Documentation

For comprehensive documentation on system architecture, detailed workflows, API specifications, and more, please refer to the `docs/` directory:

*   **`docs/architecture.md`**: Overview of the system's architectural design.
*   **`docs/deployment_guide.md`**: Instructions for deploying the application.
*   **`docs/document-flow.md`**: Explains the lifecycle and flow of documents within the system.
*   **`docs/UI_STYLE_GUIDE.md`**: Guidelines for consistent user interface design.
*   And more...