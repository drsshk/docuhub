# 📋 DocuHub - Technical Drawing Management System

<div align="center">
  <img src="https://img.shields.io/badge/Django-4.2.7-green?style=for-the-badge&logo=django" alt="Django">
  <img src="https://img.shields.io/badge/React-18-blue?style=for-the-badge&logo=react" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-5.2-blue?style=for-the-badge&logo=typescript" alt="TypeScript">
  <img src="https://img.shields.io/badge/MySQL-8.0-orange?style=for-the-badge&logo=mysql" alt="MySQL">
  <img src="https://img.shields.io/badge/TailwindCSS-3.4-teal?style=for-the-badge&logo=tailwindcss" alt="Tailwind">
</div>

<div align="center">
  <h3>🏢 Enterprise-Grade Document Lifecycle Management</h3>
  <p><em>Streamline technical drawing workflows with automated approvals, audit trails, and role-based access control</em></p>
</div>

---

## 🚀 **What is DocuHub?**

DocuHub is a comprehensive web application designed for organizations that need to manage technical drawings, engineering documents, and design files through structured approval workflows. Built with modern web technologies, it provides a secure, scalable platform for document lifecycle management.

### **🎯 Who It's For**
- **Engineering Teams** - Manage CAD drawings, specifications, and technical documentation
- **Architecture Firms** - Handle blueprints, design revisions, and project documentation  
- **Construction Companies** - Track drawing versions, approvals, and project changes
- **Manufacturing** - Manage product drawings, specifications, and engineering changes
- **Any Organization** - Requiring structured document approval workflows

---

## ✨ **Key Features**

### 📁 **Project Management**
- **Project Organization**: Group related drawings into projects with version control
- **Drawing Management**: Upload, organize, and track individual technical drawings
- **Version Control**: Automatic versioning system with project grouping
- **Bulk Operations**: Manage multiple drawings and projects efficiently

### 👥 **User & Role Management** 
- **Role-Based Access Control**: Admin, Approver, Submitter, and Viewer roles
- **User Profiles**: Comprehensive user management with departments and job titles
- **Permission System**: Granular control over who can view, edit, and approve
- **Session Management**: Secure user authentication and session tracking

### 🔄 **Approval Workflows**
- **Multi-Stage Approvals**: Configurable approval processes
- **Status Tracking**: Draft → Pending → Approved → Obsolete lifecycle
- **Automated Notifications**: Email alerts for status changes and actions needed
- **Approval History**: Complete audit trail of all approval activities

### 📧 **Communication System**
- **Email Integration**: Brevo email service for transactional emails
- **Notification Center**: In-app notifications for real-time updates
- **Template System**: Customizable email templates for different actions
- **Alert Management**: Configure notification preferences per user

### 📊 **Reporting & Analytics**
- **Project Reports**: Status summaries and progress tracking
- **User Activity**: Monitor user actions and system usage
- **Approval Metrics**: Track approval times and bottlenecks
- **Export Capabilities**: Generate reports in various formats

### 🔒 **Security & Compliance**
- **Audit Trails**: Complete logging of all user actions and changes
- **Data Security**: Input sanitization, CSRF protection, and secure sessions
- **Access Control**: IP tracking, session management, and permission enforcement
- **Compliance Ready**: Built for industries requiring documentation compliance

## 🏗️ **System Architecture**

### **🖥️ Backend (Django)**
```
apps/
├── 🔐 accounts/          # User management, authentication, roles
├── 📋 projects/          # Project and drawing management
├── 📧 notifications/     # Email and notification system  
└── ⚙️  core/            # Shared utilities and core functionality
```

### **🎨 Frontend (React)**
```
src/
├── 🧩 components/        # Reusable UI components
│   └── ui/              # Design system components
├── 📄 pages/            # Application pages and routes
├── 🔧 services/         # API communication layer
├── 📱 contexts/         # React state management
└── 📚 lib/              # Utility functions and constants
```

### **💾 Database Schema**
- **Projects**: Main project entities with version grouping
- **Drawings**: Individual drawing records linked to projects
- **Users & Profiles**: User management with role assignments
- **Approval History**: Complete audit trail of all actions
- **Notifications**: Email logs and notification preferences

---

## 🛠️ **Technology Stack**

### **🐍 Backend Technologies**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12+ | Core programming language |
| **Django** | 4.2.7 | Web framework and ORM |
| **Django REST Framework** | 3.14.0 | API development |
| **MySQL** | 8.0+ | Production database |
| **Redis** | 5.0+ | Caching and session storage |
| **Celery** | 5.3.4 | Background task processing |
| **Gunicorn** | 22.0+ | WSGI application server |

### **⚛️ Frontend Technologies**
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2+ | UI framework |
| **TypeScript** | 5.2+ | Type-safe JavaScript |
| **Vite** | 5.2+ | Build tool and dev server |
| **Tailwind CSS** | 3.4+ | Utility-first CSS framework |
| **Axios** | 1.11+ | HTTP client |
| **React Router** | 6.8+ | Client-side routing |

### **🔧 Development Tools**
| Tool | Purpose |
|------|---------|
| **ESLint & Prettier** | Code linting and formatting |
| **Jest & Testing Library** | Frontend testing |
| **Django Test Framework** | Backend testing |
| **Git** | Version control |

---

## 🎨 **User Interface**

### **Modern Design System**
- **Glass-morphism UI**: Premium design with backdrop blur effects
- **Responsive Layout**: Mobile-first design that works on all devices
- **Dark/Light Themes**: Consistent color palette with semantic naming
- **Component Library**: 8+ reusable UI components with TypeScript support

### **Mobile Experience**
- **Bottom Navigation**: Native app-style navigation on mobile devices
- **Touch-Optimized**: Proper touch targets and gesture support
- **Responsive Design**: Seamless experience across all screen sizes
- **PWA Ready**: Progressive web app capabilities for mobile installation

### **Desktop Features**
- **Compact Sidebar**: Collapsible navigation to maximize workspace
- **Keyboard Navigation**: Full keyboard accessibility support
- **Contextual Menus**: Right-click actions and keyboard shortcuts
- **Multi-window Support**: Works perfectly in multiple browser tabs

## 🚀 **Quick Start**

### **⚡ 5-Minute Setup**

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd docuhub
   
   # Backend setup
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   
   # Frontend setup  
   cd frontend
   npm install
   cd ..
   ```

2. **Configure Environment**
   ```bash
   # Copy and edit environment variables
   cp .env.example .env
   nano .env  # Update with your settings
   ```

3. **Initialize Database**
   ```bash
   # Apply migrations and create admin user
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Start Development Servers**
   ```bash
   # Terminal 1: Backend
   python manage.py runserver
   
   # Terminal 2: Frontend  
   cd frontend
   npm run dev
   ```

5. **Access Application**
   - **Frontend**: http://localhost:3000
   - **Backend Admin**: http://localhost:8000/admin
   - **API**: http://localhost:8000/api

---

## 📖 **User Guide**

### **👤 Getting Started as a User**

#### **1. Login & Profile Setup**
- Access the application through the provided URL
- Log in with credentials provided by your administrator  
- Complete your profile with department and contact information
- Set notification preferences

#### **2. Creating Projects**
- Navigate to **Projects** → **New Project**
- Fill in project details: name, description, priority, deadline
- Add initial drawings with metadata (drawing number, title, scale)
- Save as draft or submit for approval

#### **3. Managing Drawings**
- **Upload**: Add drawings to existing projects
- **Edit**: Update drawing metadata and descriptions
- **Version Control**: System automatically tracks versions
- **Status Tracking**: Monitor approval progress

#### **4. Approval Workflow**
- **Submit**: Send projects for approval review
- **Track**: Monitor approval status and comments
- **Respond**: Address revision requests promptly
- **Notifications**: Receive email alerts for status changes

### **👨‍💼 Administrative Functions**

#### **User Management**
- **Create Users**: Add new team members with appropriate roles
- **Assign Roles**: Set permissions (Admin, Approver, Submitter, Viewer)
- **Manage Departments**: Organize users by department and function
- **Monitor Activity**: Track user actions and system usage

#### **System Configuration**
- **Email Templates**: Customize notification messages
- **Approval Workflows**: Configure multi-stage approval processes
- **Security Settings**: Manage session timeouts and access controls
- **Report Generation**: Create custom reports and analytics

---

## 🔧 **Development Guide**

### **🏗️ Project Structure**
```
docuhub/
├── 📁 apps/                    # Django applications
│   ├── accounts/              # User management
│   ├── projects/              # Core functionality  
│   ├── notifications/         # Email system
│   └── core/                  # Shared utilities
├── 📁 frontend/               # React application
│   ├── src/components/        # UI components
│   ├── src/pages/            # Application pages
│   ├── src/services/         # API services
│   └── src/contexts/         # State management
├── 📁 templates/              # Django templates
├── 📁 static/                 # Static assets
├── 📁 docs/                   # Documentation
└── 📁 logs/                   # Application logs
```

### **🛠️ Development Workflow**

#### **Backend Development**
```bash
# Create new Django app
python manage.py startapp myapp

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Run tests
python manage.py test

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

#### **Frontend Development**
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build

# Lint and format
npm run lint
```

### **🧪 Testing**

#### **Backend Tests**
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.projects

# Run with coverage
coverage run manage.py test
coverage report
```

#### **Frontend Tests**  
```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### **📝 Code Style**

- **Python**: Follow PEP 8, use Black formatter
- **JavaScript/TypeScript**: ESLint with Prettier
- **Git**: Conventional commit messages
- **Documentation**: Comprehensive docstrings and comments

---

## 📚 **API Documentation**

### **🔗 REST API Endpoints**

#### **Authentication**
```http
POST /api/auth/login/          # User login
POST /api/auth/logout/         # User logout  
GET  /api/auth/user/           # Current user info
```

#### **Projects**
```http
GET    /api/projects/          # List projects
POST   /api/projects/          # Create project
GET    /api/projects/{id}/     # Project detail
PUT    /api/projects/{id}/     # Update project  
DELETE /api/projects/{id}/     # Delete project
```

#### **Drawings**
```http
GET    /api/drawings/          # List drawings
POST   /api/drawings/          # Create drawing
GET    /api/drawings/{id}/     # Drawing detail
PUT    /api/drawings/{id}/     # Update drawing
DELETE /api/drawings/{id}/     # Delete drawing
```

#### **Users**
```http
GET    /api/users/             # List users (admin only)
POST   /api/users/             # Create user (admin only)
GET    /api/users/{id}/        # User detail
PUT    /api/users/{id}/        # Update user
```

### **📄 Response Format**
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully",
  "errors": null
}
```

---

## 🔒 **Security Features**

### **🛡️ Built-in Security**
- **CSRF Protection**: Cross-site request forgery prevention
- **XSS Prevention**: Input sanitization with Bleach library
- **SQL Injection**: Django ORM protection
- **Session Security**: Secure cookie configuration
- **Rate Limiting**: API throttling and abuse prevention
- **Input Validation**: Comprehensive form and API validation

### **🔐 Access Control**
- **Role-Based Permissions**: Granular access control system
- **IP Tracking**: Monitor and log user locations
- **Session Management**: Automatic timeout and session tracking
- **Audit Trails**: Complete logging of all user actions

### **📊 Monitoring**
- **Error Tracking**: Sentry integration for error monitoring
- **Performance Monitoring**: Application performance insights
- **Security Logging**: Detailed security event logging
- **User Activity**: Track user actions and system usage

---

## 📞 **Support & Documentation**

### **📖 Documentation**
- **[Environment Setup](docs/environment_setup_guide.md)** - Configuration guide
- **[Deployment Guide](docs/deployment_guide.md)** - Production deployment
- **[Architecture Overview](docs/architecture.md)** - System design
- **[Security Report](docs/security_report.md)** - Security analysis
- **[UI Style Guide](docs/UI_STYLE_GUIDE.md)** - Design system

### **🆘 Getting Help**
- **Issues**: GitHub Issues for bug reports and feature requests
- **Documentation**: Comprehensive guides in the `docs/` directory
- **Email**: Technical support contact information
- **Community**: Developer discussions and support

### **📋 FAQ**
**Q: Can I use this for non-technical documents?**  
A: Yes! While designed for technical drawings, DocuHub works for any document requiring approval workflows.

**Q: Is there a mobile app?**  
A: The web application is mobile-responsive and can be installed as a PWA for a native app experience.

**Q: Can I customize the approval workflow?**  
A: Yes, approval workflows are configurable through the admin interface.

---

## 🤝 **Contributing**

### **👨‍💻 Development Setup**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Set up development environment (see Quick Start)
4. Make changes and add tests
5. Commit changes: `git commit -m 'Add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### **📋 Contribution Guidelines**
- Follow existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting
- Write clear, descriptive commit messages

### **🐛 Bug Reports**
- Use GitHub Issues for bug reports
- Include detailed reproduction steps
- Provide system information and logs
- Screenshots for UI-related issues

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **Django Community** - For the excellent web framework
- **React Team** - For the powerful frontend library
- **Tailwind CSS** - For the utility-first CSS framework
- **Open Source Contributors** - For the amazing tools and libraries

---

<div align="center">
  <p><strong>Built with ❤️ for engineering teams worldwide</strong></p>
  <p><em>DocuHub - Streamlining Technical Document Management</em></p>
</div>