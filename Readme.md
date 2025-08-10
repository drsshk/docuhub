# DocuHub - Technical Drawing Version Management System

## Overview

DocuHub is an enterprise-grade Django web application designed to streamline the management of technical drawing versions. It features automated approval workflows, comprehensive audit trails, and an integrated email notification system. The platform provides structured project lifecycle management with role-based access control and enterprise security features.

## Technology Stack

### Backend
- Python 3.8+
- Django 4.2.7
- Django REST Framework
- Celery for background tasks
- MySQL (Production) / SQLite (Development)
- Gunicorn

### Frontend
- React
- Vite
- TypeScript
- Tailwind CSS
- Axios

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Node.js and npm
- MySQL server

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd docuhub
    ```

2.  **Setup Backend:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # or
    # venv\Scripts\activate     # Windows
    pip install -r requirements.txt
    ```

3.  **Setup Frontend:**
    ```bash
    cd frontend
    npm install
    cd ..
    ```

4.  **Configure Environment:**
    - Create a `.env` file in the project root. Use `.env.example` as a template.
    - Update the database credentials and other settings.

5.  **Initialize Database and Static Files:**
    ```bash
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py collectstatic --noinput
    python manage.py setup_roles
    ```

### Running the Application

1.  **Start the Backend Server:**
    ```bash
    python manage.py runserver
    ```

2.  **Start the Frontend Development Server:**
    ```bash
    cd frontend
    npm run dev
    ```

The application will be available at `http://localhost:5173`.

## Documentation

For detailed documentation on system architecture, workflows, API, and more, please see the [documentation in the docs/ directory](./docs/architecture.md).
