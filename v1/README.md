# 🏢 HomayOMS - Inventory & Order Management System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2+-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-orange.svg)]()

> **Enterprise-grade Inventory & Order Management System** with multi-role authentication, SMS verification, and modern UI/UX design.

## 📋 Table of Contents

- [🎯 Project Overview](#-project-overview)
- [🚀 Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📦 Installation](#-installation)
- [🔧 Django Management Commands](#-django-management-commands)
- [🔐 Authentication System](#-authentication-system)
- [📊 Project Structure](#-project-structure)
- [✅ Completed Features](#-completed-features)
- [📝 TODO List](#-todo-list)
- [🤝 Contributing](#-contributing)
- [👥 Contributors](#-contributors)
- [📄 License](#-license)

## 🎯 Project Overview

HomayOMS is a comprehensive **Inventory & Order Management System** designed for modern businesses. Built with Django and featuring a sophisticated multi-role authentication system, it provides secure access for different user types with role-based permissions and SMS verification for customers.

### 🎨 Key Highlights

- **🔐 Multi-Role Authentication**: 4 distinct user roles with separate login flows
- **📱 SMS Verification**: Secure customer authentication via SMS
- **🎨 Modern UI/UX**: Beautiful, responsive design with Tailwind CSS
- **🌐 Persian RTL Support**: Full support for Persian language and RTL layout
- **🔒 Role-Based Access Control**: Granular permissions for each user type
- **📊 Real-time Dashboard**: Role-specific dashboards with relevant metrics

## 🚀 Features

### 🔐 Authentication & Security
- **4-Role Login System**: Super Admin, Admin, Finance, Customer
- **SMS Verification**: Customer authentication via mobile verification
- **Session Management**: Secure user sessions with activity tracking
- **Password Security**: Encrypted password storage with expiration
- **Role Validation**: Strict role-based access control

### 👥 User Management
- **Custom User Model**: Extended Django User with role-based fields
- **Profile Management**: User profile editing and management
- **Status Tracking**: Active, Inactive, Suspended, Pending statuses
- **Activity Monitoring**: Last login and activity tracking

### 🏢 Business Features
- **Customer Management**: Complete customer profile system
- **Inventory Tracking**: Product and stock management (planned)
- **Order Processing**: Order creation and management (planned)
- **Financial Management**: Pricing and invoice system (planned)
- **Reporting System**: Business analytics and reports (planned)

### 🎨 User Interface
- **Responsive Design**: Works perfectly on all devices
- **Modern UI**: Clean, professional interface with animations
- **Persian Support**: Full RTL layout and Persian text support
- **Accessibility**: WCAG compliant design patterns
- **Dark/Light Mode**: Theme switching capability (planned)

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**: Core programming language
- **Django 5.2+**: Web framework with admin interface
- **SQLite/PostgreSQL**: Database management
- **Django REST Framework**: API development (planned)

### Frontend
- **Tailwind CSS**: Utility-first CSS framework
- **HTML5/CSS3**: Modern web standards
- **JavaScript**: Interactive functionality
- **Vazirmatn Font**: Persian typography

### DevOps & Tools
- **Git**: Version control
- **Docker**: Containerization (planned)
- **GitHub Actions**: CI/CD pipeline (planned)
- **Nginx**: Web server (production)

### Security
- **Django Security**: Built-in security features
- **HTTPS**: SSL/TLS encryption
- **CSRF Protection**: Cross-site request forgery protection
- **XSS Prevention**: Cross-site scripting protection

## 📦 Installation

### Prerequisites
```bash
Python 3.8+
pip
git
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/amirholakoo/IOMS.git
cd IOMS/v1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create test customer
python manage.py create_test_customer

# Run development server
python manage.py runserver
```

### Environment Configuration
```bash
# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env
```

## 🔧 Django Management Commands

> **For Next Developer:**  
> This section explains how to use, extend, and troubleshoot all custom Django management commands in this project. If you want to automate tasks, create test data, or add your own scripts, start here!

### 📋 What are Django Management Commands?
Django management commands are scripts you run with `python manage.py <command>` to automate tasks like creating test data, setting up roles, or running custom scripts.

---

### 🚀 How to Use Our Custom Commands

**1. List all available commands:**
```bash
python manage.py help
```
Look for commands like:
```
create_full_test_data
setup_roles
create_test_products
create_daily_test_customer
...
```

**2. Get help for a specific command:**
```bash
python manage.py help create_full_test_data
```

**3. Run a command (example):**
```bash
python manage.py create_full_test_data
```
This will create test users for all roles and print their credentials in the terminal.

**4. Typical development workflow:**
```bash
# Setup roles and permissions
python manage.py setup_roles --create-superuser --username admin --password admin123

# Create test users and products
python manage.py create_full_test_data
python manage.py create_test_products --count 10

# Create daily test customers for SMS login
python manage.py create_daily_test_customer --count 3
```

**5. See output and use credentials:**
After running `create_full_test_data`, you'll see a table of test users and passwords you can use to log in.

---

### 🛠️ How to Add Your Own Custom Command

1. **Create the folder structure (if not already present):**
   ```
   yourapp/
     management/
       commands/
         __init__.py
         your_command.py
   ```

2. **Write your command:**
   ```python
   # yourapp/management/commands/hello.py
   from django.core.management.base import BaseCommand

   class Command(BaseCommand):
       help = 'Prints Hello World'

       def handle(self, *args, **kwargs):
           self.stdout.write(self.style.SUCCESS('Hello, World!'))
   ```

3. **Run your command:**
   ```bash
   python manage.py hello
   ```

4. **Best practices:**
   - Use `self.stdout.write(self.style.SUCCESS(...))` for nice output.
   - Add a `help` string and docstring.
   - Handle errors gracefully and print useful messages.
   - Document your new command in this section for future developers!

---

### 📝 Tips & Troubleshooting

- **Always activate your virtual environment** before running commands.
- If you get `CommandError` or `ModuleNotFoundError`, check your folder structure and `__init__.py` files.
- Use `python manage.py help` to discover all commands.
- For bulk data, use `--count` or similar arguments if available.
- If you add a new command, document it in this section for the next developer!

---

### 📚 Resources

- [Django Custom Management Commands Documentation](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/)
- [Project Command Reference Table](#-django-management-commands)

---

**Now, any new developer can:**
- See all available commands
- Run and test with real data in seconds
- Add their own commands with confidence
- Troubleshoot common issues quickly

---

## 🔐 Authentication System

### User Roles & Permissions

| Role | Access Level | Features |
|------|-------------|----------|
| **🔴 Super Admin** | Full System Access | User management, System settings, All modules |
| **🟡 Admin** | Operational Access | Customer management, Orders, Inventory, Reports |
| **🟢 Finance** | Financial Access | Pricing, Invoices, Financial reports, Payments |
| **🔵 Customer** | Limited Access | Own orders, Profile management, SMS verification |

### Login Flows

1. **Staff Login** (`/accounts/staff/login/`)
   - Username + Password authentication
   - Role validation
   - Session management

2. **Customer Login** (`/accounts/customer/login/`)
   - Phone number verification
   - SMS code authentication
   - No password required

## 📊 Project Structure

```
HomayOMS/
├── accounts/                 # User authentication & management
│   ├── models.py            # Custom User model with roles
│   ├── views.py             # Authentication views
│   ├── urls.py              # URL routing
│   └── management/          # Django management commands
├── core/                    # Core business logic
│   ├── models.py            # Customer, Order models
│   ├── views.py             # Business views
│   └── urls.py              # Core URL routing
├── HomayOMS/                # Project settings
│   ├── settings/            # Environment-based settings
│   ├── urls.py              # Main URL configuration
│   └── baseModel.py         # Base model with timestamps
├── templates/               # HTML templates
│   ├── accounts/            # Authentication templates
│   └── core/                # Business templates
├── static/                  # Static files (CSS, JS, images)
├── requirements.txt         # Python dependencies
└── manage.py               # Django management script
```

## ✅ Completed Features

### 🔐 Authentication & User Management
- ✅ **Custom User Model**: Extended Django User with role-based fields
- ✅ **Multi-Role Login System**: 4 distinct login flows
- ✅ **SMS Verification**: Customer authentication via phone
- ✅ **Role-Based Access Control**: Granular permissions
- ✅ **Session Management**: User activity tracking
- ✅ **Profile Management**: User profile editing

### 🎨 User Interface
- ✅ **Professional Login Pages**: Beautiful 4-role login interface
- ✅ **Responsive Design**: Mobile-first approach
- ✅ **Persian RTL Support**: Full Persian language support
- ✅ **Modern UI Components**: Tailwind CSS styling
- ✅ **Customer Dashboard**: Role-specific dashboard
- ✅ **Staff Dashboard**: Admin and management interfaces

### 🏢 Business Logic
- ✅ **Customer Model**: Complete customer profile system
- ✅ **Base Model**: Timestamp fields for all models
- ✅ **Admin Interface**: Django admin customization
- ✅ **Management Commands**: Test user creation utilities

### 🔧 Development & DevOps
- ✅ **Environment Configuration**: Local, Dev, Production settings
- ✅ **Git Version Control**: Complete project history
- ✅ **Documentation**: Comprehensive code documentation
- ✅ **Code Quality**: Persian comments and emojis
- ✅ **Security Best Practices**: CSRF, XSS protection

## 📝 TODO List

### 🔐 Authentication Enhancements
- [ ] **SMS API Integration**: Connect to SMS service provider
- [ ] **Two-Factor Authentication**: Additional security layer
- [ ] **Password Reset**: Email-based password recovery
- [ ] **Account Lockout**: Brute force protection
- [ ] **Login History**: Detailed login tracking

### 🏢 Business Features
- [ ] **Product Management**: Product catalog and categories
- [ ] **Inventory Tracking**: Stock levels and movements
- [ ] **Order Management**: Order creation and processing
- [ ] **Invoice System**: Automated invoice generation
- [ ] **Payment Integration**: Payment gateway integration
- [ ] **Shipping Management**: Delivery tracking
- [ ] **Supplier Management**: Vendor and supplier profiles

### 📊 Analytics & Reporting
- [ ] **Sales Reports**: Revenue and sales analytics
- [ ] **Inventory Reports**: Stock level reports
- [ ] **Customer Analytics**: Customer behavior insights
- [ ] **Financial Reports**: Profit/loss statements
- [ ] **Dashboard Widgets**: Real-time metrics

### 🎨 User Experience
- [ ] **Dark Mode**: Theme switching capability
- [ ] **Notifications**: Real-time notifications
- [ ] **Search Functionality**: Global search across modules
- [ ] **Data Export**: CSV/Excel export capabilities
- [ ] **Bulk Operations**: Mass data operations

### 🔧 Technical Improvements
- [ ] **API Development**: RESTful API endpoints
- [ ] **Database Optimization**: Query optimization
- [ ] **Caching System**: Redis integration
- [ ] **Background Tasks**: Celery integration
- [ ] **Testing Suite**: Unit and integration tests
- [ ] **Docker Deployment**: Containerization
- [ ] **CI/CD Pipeline**: Automated deployment

### 📱 Mobile & Integration
- [ ] **Mobile App**: React Native mobile application
- [ ] **Webhook Integration**: Third-party integrations
- [ ] **Email Notifications**: Automated email system
- [ ] **SMS Notifications**: Bulk SMS capabilities
- [ ] **Barcode Scanning**: QR code integration

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 Python style guide
- Add Persian comments with emojis
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages

## 👥 Contributors

### Lead Developers

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/idarbandi">
        <img src="https://avatars.githubusercontent.com/idarbandi" width="100px;" alt=""/>
        <br />
        <sub><b>Amir DarBandi</b></sub>
      </a>
      <br />
      <sub>Full Stack Developer</sub>
      <br />
      <a href="https://github.com/idarbandi" title="GitHub">🔗 GitHub</a>
    </td>
    <td align="center">
      <a href="https://github.com/Parsa-Parvizi">
        <img src="https://avatars.githubusercontent.com/Parsa-Parvizi" width="100px;" alt=""/>
        <br />
        <sub><b>Parsa Parvizi</b></sub>
      </a>
      <br />
      <sub>Backend Developer</sub>
      <br />
      <a href="https://github.com/Parsa-Parvizi" title="GitHub">🔗 GitHub</a>
    </td>
  </tr>
</table>

### Development Team

- **🎯 Amir DarBandi** - Project Lead & Full Stack Development
  - Expertise: Python, Django, JavaScript, React, Laravel
  - Focus: System architecture, UI/UX, DevOps
  
- **🎯 Parsa Parvizi** - Backend Development & Security
  - Expertise: Python, Django, Cybersecurity, Database Design
  - Focus: Authentication system, Security implementation

### Special Thanks
- **Homayoun Paper & Cardboard Industries Co.** - Project sponsor
- **Django Community** - Framework and documentation
- **Tailwind CSS Team** - UI framework

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**🏢 HomayOMS** - *Enterprise Inventory & Order Management System*

[![GitHub stars](https://img.shields.io/github/stars/amirholakoo/IOMS?style=social)](https://github.com/amirholakoo/IOMS)
[![GitHub forks](https://img.shields.io/github/forks/amirholakoo/IOMS?style=social)](https://github.com/amirholakoo/IOMS)

*Built with ❤️ by the HomayOMS Team*

</div> 
