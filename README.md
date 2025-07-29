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
- **Inventory Tracking**: Product and stock management with external SQLite sync
- **Order Processing**: Atomic order creation and management system
- **Financial Management**: Pricing and invoice system with cash/credit control
- **Reporting System**: Business analytics and reports with Persian calendar

### 🔄 Advanced Features (v201+)
- **🔄 Atomic Order System**: Eliminates unfinished orders with immediate creation
- **📱 Real SMS Integration**: SIM800C hardware with Raspberry Pi server
- **🔄 Inventory Synchronization**: Bidirectional sync with external SQLite databases
- **💰 Cash Purchase Control**: Super Admin can disable cash purchases
- **📅 Persian Calendar**: Automatic Jalali date conversion and display
- **🔒 Enhanced Security**: Customer deletion protection, comprehensive logging

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
- **PostgreSQL**: Production database (SQLite for development)
- **Gunicorn**: Production WSGI server
- **Nginx**: Reverse proxy and static file serving

### Frontend
- **HTML5/CSS3**: Modern web standards
- **JavaScript**: Interactive functionality with Persian support
- **Vazirmatn Font**: Persian typography
- **Responsive Design**: Mobile-first approach

### Hardware Integration (v201+)
- **SIM800C GSM Module**: Real SMS functionality
- **Raspberry Pi**: Hardware server platform
- **Flask**: SMS API server
- **Serial Communication**: Hardware control via serial ports

### DevOps & Tools
- **Git**: Version control
- **Docker**: Containerization with Docker Compose
- **Systemd**: Service management on Raspberry Pi
- **GitHub Actions**: CI/CD pipeline (planned)

### Security
- **Django Security**: Built-in security features
- **HTTPS**: SSL/TLS encryption
- **CSRF Protection**: Cross-site request forgery protection
- **XSS Prevention**: Cross-site scripting protection
- **Role-Based Permissions**: Granular access control

## 📦 Installation

### Prerequisites
```bash
Python 3.8+
pip
git
PostgreSQL (for production)
SQLite3 (for inventory sync)
```

### Quick Start
```bash
# Clone the repository
git clone https://github.com/amirholakoo/IOMS.git
cd IOMS/v201  # Use v201 for latest features

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Setup roles and permissions
python manage.py setup_roles

# Create superuser
python manage.py createsuperuser

# Setup SMS templates
python manage.py setup_sms_templates

# Setup field mappings for inventory sync
python manage.py setup_field_mappings

# Create test data
python manage.py create_full_test_data

# Run development server
python manage.py runserver
```

### Environment Configuration
```bash
# Copy environment file
cp env.local .env

# Edit environment variables
nano .env
```

### ⚠️ Important: Inventory Sync Setup

**The inventory sync app requires an external SQLite database file that is NOT included in the repository.**

#### Setting Up Your SQLite Database
```bash
# Create a new SQLite database
sqlite3 inventory_sync/db.sqlite3

# Or use your existing inventory database
cp /path/to/your/existing/inventory.db inventory_sync/db.sqlite3

# Required table structure
CREATE TABLE Products (
    id INTEGER PRIMARY KEY,
    reel_number TEXT UNIQUE NOT NULL,
    width INTEGER,
    length INTEGER,
    weight REAL,
    status TEXT DEFAULT 'In-stock',
    date TEXT,
    notes TEXT
);
```

#### Configure Database Path
```bash
# In your .env file
SQLITE_DB_PATH=/path/to/your/inventory.db
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
setup_sms_templates
setup_field_mappings
test_sqlite_connection
test_sms_connection
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

# Setup SMS templates and field mappings
python manage.py setup_sms_templates
python manage.py setup_field_mappings

# Create test users and products
python manage.py create_full_test_data
python manage.py create_test_products --count 10

# Test connections
python manage.py test_sqlite_connection
python manage.py test_sms_connection
```

**5. See output and use credentials:**
After running `create_full_test_data`, you'll see a table of test users and passwords you can use to log in.

---

### 🔄 Inventory Sync Commands

**Test SQLite Connection:**
```bash
python manage.py test_sqlite_connection
```
Tests connectivity to external SQLite database for inventory sync.

**Setup Field Mappings:**
```bash
python manage.py setup_field_mappings
```
Creates default field mappings for inventory synchronization.

---

### 📱 SMS Commands

**Test SMS Connection:**
```bash
python manage.py test_sms_connection
```
Tests SMS server connectivity and hardware status.

**Setup SMS Templates:**
```bash
python manage.py setup_sms_templates
```
Creates default SMS templates for verification and notifications.

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
- **For inventory sync**: Ensure your SQLite database file exists and is accessible.
- **For SMS testing**: Ensure SMS server is running and hardware is connected.
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
- Set up inventory sync and SMS functionality properly

---

## 🔐 Authentication System

### User Roles & Permissions

| Role | Access Level | Features |
|------|-------------|----------|
| **🔴 Super Admin** | Full System Access | User management, System settings, All modules, SMS management, Inventory sync |
| **🟡 Admin** | Operational Access | Customer management, Orders, Inventory, Reports |
| **🟢 Finance** | Financial Access | Pricing, Invoices, Financial reports, Payments |
| **🔵 Customer** | Limited Access | Own orders, Profile management, SMS verification |

### Login Flows

1. **Staff Login** (`/accounts/staff/login/`)
   - Username + Password authentication
   - Role validation and permissions
   - Session management

2. **Customer SMS Login** (`/accounts/customer/login/`)
   - Phone number verification
   - SMS code authentication via SIM800C hardware
   - No password required
   - Customer activation notifications

## 📊 Project Structure

```
HomayOMS/
├── v201/                    # 🎯 Latest Production Version
│   ├── accounts/            # User authentication & management
│   │   ├── models.py        # Custom User model with roles
│   │   ├── views.py         # Authentication views
│   │   ├── permissions.py   # Role-based permissions
│   │   └── management/      # Django management commands
│   ├── core/                # Core business logic
│   │   ├── models.py        # Customer, Order, Product models
│   │   ├── views.py         # Business views with atomic order system
│   │   ├── urls.py          # Core URL routing
│   │   └── management/      # Management commands
│   ├── inventory_sync/      # Inventory synchronization
│   │   ├── models.py        # SyncConfig, SyncLog, ProductMapping
│   │   ├── services.py      # SQLiteInventoryService, InventorySyncService
│   │   ├── views.py         # Sync management views
│   │   └── templates/       # Persian UI templates
│   ├── payments/            # Payment processing
│   │   ├── models.py        # Payment models
│   │   ├── services.py      # Payment services
│   │   └── views.py         # Payment views
│   ├── sms/                 # SMS integration
│   │   ├── models.py        # SMS templates, messages, verifications
│   │   ├── services.py      # SMSService, SMSNotificationService
│   │   └── views.py         # SMS management views
│   ├── HomayOMS/            # Project settings
│   │   ├── settings/        # Environment-based settings
│   │   ├── urls.py          # Main URL configuration
│   │   └── baseModel.py     # Base model with timestamps
│   ├── templates/           # HTML templates
│   │   ├── accounts/        # Authentication templates
│   │   ├── core/            # Business templates
│   │   └── inventory_sync/  # Sync templates
│   ├── static/              # Static files (CSS, JS, images)
│   ├── requirements.txt     # Python dependencies
│   ├── config.py            # Environment configuration
│   └── manage.py            # Django management script
├── v200/                    # Previous version
├── v1.1/                    # Legacy version
├── v1/                      # Legacy version
└── v0/                      # Initial version
```

## ✅ Completed Features

### 🔐 Authentication & User Management
- ✅ **Custom User Model**: Extended Django User with role-based fields
- ✅ **Multi-Role Login System**: 4 distinct login flows
- ✅ **SMS Verification**: Customer authentication via phone
- ✅ **Role-Based Access Control**: Granular permissions
- ✅ **Session Management**: User activity tracking
- ✅ **Profile Management**: User profile editing

### 🔄 Advanced Order System (v201+)
- ✅ **Atomic Order Creation**: Orders created with items immediately
- ✅ **Page Exit Protection**: Automatic order cancellation on page exit
- ✅ **Product Reservation**: Products marked as 'Pre-order' to prevent double booking
- ✅ **Automatic Cleanup**: Draft orders cancelled after timeout or page exit
- ✅ **Unfinished Orders**: Continue payment for incomplete orders

### 📱 Real SMS Integration (v201+)
- ✅ **SIM800C Hardware**: Real SMS functionality with GSM module
- ✅ **Raspberry Pi Server**: Flask API server for hardware control
- ✅ **Customer Activation**: Automatic SMS notifications when accounts are activated
- ✅ **Verification System**: Secure SMS code authentication
- ✅ **Message Templates**: Configurable SMS templates with variable substitution

### 🔄 Inventory Synchronization (v201+)
- ✅ **External SQLite Integration**: Bidirectional sync with external inventory systems
- ✅ **Field Mapping System**: Configurable field mappings between systems
- ✅ **Product Import/Export**: Import products and export sales status
- ✅ **Comprehensive Logging**: All sync operations logged with detailed information
- ✅ **Mobile-Friendly Persian UI**: Responsive interface for sync management

### 💰 Cash Purchase Control (v201+)
- ✅ **Super Admin Control**: Toggle cash purchase availability
- ✅ **Dynamic UI Updates**: Real-time interface updates based on settings
- ✅ **Customer Guidance**: Clear notifications about payment limitations
- ✅ **Alternative Options**: Credit (نسیه) payment remains available

### 📅 Persian Calendar Integration (v201+)
- ✅ **Automatic Conversion**: All dates automatically converted to Persian Jalali format
- ✅ **Accurate Algorithm**: Proper Persian calendar conversion with leap year support
- ✅ **Client-Side Processing**: No server overhead, pure JavaScript conversion
- ✅ **Visual Styling**: Converted dates displayed in blue with medium font weight

### 🎨 User Interface
- ✅ **Professional Design**: Beautiful Persian RTL interface
- ✅ **Responsive Layout**: Mobile-first approach with touch-friendly elements
- ✅ **Modern Components**: Clean, professional interface with animations
- ✅ **Accessibility**: WCAG compliant design patterns

### 🔧 Development & DevOps
- ✅ **Environment Configuration**: Local, Dev, Production settings
- ✅ **Production Deployment**: Manual deployment on Raspberry Pi
- ✅ **Docker Support**: Containerization with Docker Compose
- ✅ **Comprehensive Logging**: Structured logging and monitoring
- ✅ **Security Best Practices**: CSRF, XSS protection, secure headers

## 📝 TODO List

### 🔄 Order Management Enhancements
- [ ] **Order Templates**: Predefined order templates for common scenarios
- [ ] **Bulk Order Processing**: Mass order operations
- [ ] **Order History**: Detailed order history and tracking
- [ ] **Order Notifications**: Real-time order status notifications

### 📱 SMS System Improvements
- [ ] **SMS Templates**: More customizable SMS templates
- [ ] **Bulk SMS**: Mass SMS sending capabilities
- [ ] **SMS Analytics**: Message delivery statistics and analytics
- [ ] **SMS Scheduling**: Scheduled SMS sending

### 🔄 Inventory Sync Enhancements
- [ ] **Real-time Sync**: WebSocket-based real-time synchronization
- [ ] **Conflict Resolution**: Handle data conflicts between systems
- [ ] **Incremental Sync**: Only sync changed data
- [ ] **API Integration**: REST API for external system integration

### 📊 Analytics & Reporting
- [ ] **Sales Reports**: Revenue and sales analytics
- [ ] **Inventory Reports**: Stock level reports and alerts
- [ ] **Customer Analytics**: Customer behavior insights
- [ ] **Financial Reports**: Profit/loss statements and cash flow

### 🎨 User Experience
- [ ] **Dark Mode**: Theme switching capability
- [ ] **Notifications**: Real-time notifications system
- [ ] **Search Functionality**: Global search across modules
- [ ] **Data Export**: CSV/Excel export capabilities

### 🔧 Technical Improvements
- [ ] **API Development**: RESTful API endpoints
- [ ] **Database Optimization**: Query optimization and indexing
- [ ] **Caching System**: Redis integration for performance
- [ ] **Background Tasks**: Celery integration for async tasks
- [ ] **Testing Suite**: Unit and integration tests
- [ ] **CI/CD Pipeline**: Automated deployment and testing

### 📱 Mobile & Integration
- [ ] **Mobile App**: React Native mobile application
- [ ] **Webhook Integration**: Third-party integrations
- [ ] **Email Notifications**: Automated email system
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
