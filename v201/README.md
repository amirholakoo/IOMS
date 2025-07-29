# 🏢 HomayOMS v201 - Advanced Order Management System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2+-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

> **Enterprise-grade Order Management System** with atomic order processing, real SMS integration, inventory synchronization, and comprehensive Persian UI/UX.

## 📋 Table of Contents

- [🎯 Project Overview](#-project-overview)
- [🚀 Key Features](#-key-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📦 Installation](#-installation)
- [🔧 Environment Configuration](#-environment-configuration)
- [📱 SMS Integration](#-sms-integration)
- [🔄 Inventory Sync App](#-inventory-sync-app)
- [🔐 Authentication System](#-authentication-system)
- [📊 Project Structure](#-project-structure)
- [🚀 Production Deployment](#-production-deployment)
- [🔧 Django Management Commands](#-django-management-commands)
- [✅ Completed Features](#-completed-features)
- [📝 TODO List](#-todo-list)
- [🤝 Contributing](#-contributing)
- [👥 Contributors](#-contributors)
- [📄 License](#-license)

## 🎯 Project Overview

HomayOMS v201 is the **latest production-ready version** of our comprehensive Order Management System. Built with Django and featuring advanced features like atomic order processing, real SMS integration with SIM800C hardware, and inventory synchronization with extetrnal SQLite databases.

### 🎨 Key Highlights

- **🔄 Atomic Order System**: Eliminates unfinished orders with immediate order creation
- **📱 Real SMS Integration**: SIM800C hardware with Raspberry Pi server
- **🔄 Inventory Sync**: Bidirectional synchronization with external SQLite databases
- **💰 Cash Purchase Control**: Super Admin can disable cash purchases
- **📅 Persian Calendar**: Automatic Jalali date conversion and display
- **🔒 Enhanced Security**: Customer deletion protection, comprehensive logging
- **🎨 Modern UI/UX**: Beautiful Persian RTL interface with responsive design

## 🚀 Key Features

### 🔄 Atomic Order Processing
- **Immediate Order Creation**: Orders created with items when entering selected_products page
- **Page Exit Protection**: Automatic order cancellation on page exit with warning modals
- **Product Reservation**: Products marked as 'Pre-order' to prevent double booking
- **Automatic Cleanup**: Draft orders cancelled after timeout or page exit

### 📱 Real SMS System
- **SIM800C Hardware**: Real SMS functionality with GSM module
- **Raspberry Pi Server**: Flask API server for hardware control
- **Customer Activation**: Automatic SMS notifications when accounts are activated
- **Verification System**: Secure SMS code authentication for customers
- **Message Templates**: Configurable SMS templates with variable substitution

### 🔄 Inventory Synchronization
- **External SQLite Integration**: Bidirectional sync with external inventory systems
- **Field Mapping System**: Configurable field mappings between systems
- **Product Import/Export**: Import products and export sales status
- **Comprehensive Logging**: All sync operations logged with detailed information
- **Mobile-Friendly Persian UI**: Responsive interface for sync management

### 💰 Cash Purchase Control
- **Super Admin Control**: Toggle cash purchase availability
- **Dynamic UI Updates**: Real-time interface updates based on settings
- **Customer Guidance**: Clear notifications about payment limitations
- **Alternative Options**: Credit (نسیه) payment remains available

### 📅 Persian Calendar Integration
- **Automatic Conversion**: All dates automatically converted to Persian Jalali format
- **Accurate Algorithm**: Proper Persian calendar conversion with leap year support
- **Client-Side Processing**: No server overhead, pure JavaScript conversion
- **Visual Styling**: Converted dates displayed in blue with medium font weight

### 🔒 Enhanced Security
- **Customer Deletion Protection**: Atomic deletion of Customer and User objects
- **Activity Logging**: Comprehensive audit trail for all operations
- **Role-Based Permissions**: Granular access control for all user types
- **Session Management**: Secure user sessions with activity tracking

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

### Hardware Integration
- **SIM800C GSM Module**: Real SMS functionality
- **Raspberry Pi**: Hardware server platform
- **Flask**: SMS API server
- **Serial Communication**: Hardware control via serial ports

### DevOps & Tools
- **Docker**: Containerization support
- **Docker Compose**: Multi-container orchestration
- **Systemd**: Service management on Raspberry Pi
- **Git**: Version control

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
cd IOMS/v201

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## 🔧 Environment Configuration

### Environment Files
The project uses multiple environment files for different deployment scenarios:

```bash
# Development
cp env.local .env

# Production
cp env.production .env

# Raspberry Pi deployment
cp env.raspberry .env
```

### Key Environment Variables
```bash
# Django Settings
SECRET_KEY=your-super-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DB_HOST=localhost
DB_PORT=5433
DB_NAME=homayoms_v201_db
DB_USER=homayoms_user
DB_PASSWORD=homayoms_password

# SMS Server
SMS_SERVER_URL=http://192.168.237.102:5003
SMS_API_KEY=ioms_sms_server_2025
SMS_TIMEOUT=30
SMS_RETRY_ATTEMPTS=3

# Inventory Sync
SQLITE_DB_PATH=/path/to/your/inventory.db
SYNC_TIMEOUT=300
SYNC_BATCH_SIZE=100
```

## 📱 SMS Integration

### Hardware Setup
1. **SIM800C Module**: Connect to Raspberry Pi via USB or GPIO
2. **Flask Server**: SMS API server running on port 5003
3. **Serial Communication**: Auto-detection of `/dev/ttyAMA0` or `/dev/ttyUSB0`

### Configuration
```bash
# SMS Server URL (Raspberry Pi IP)
SMS_SERVER_URL=http://192.168.237.102:5003

# API Key for authentication
SMS_API_KEY=ioms_sms_server_2025

# Timeout and retry settings
SMS_TIMEOUT=30
SMS_RETRY_ATTEMPTS=3
```

### Testing SMS
```bash
# Test SMS server health
curl http://192.168.237.102:5003/health

# Test SMS sending
curl -X POST http://192.168.237.102:5003/api/v1/verify/send \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+989109462034", "message": "Test message"}'
```

## 🔄 Inventory Sync App

### ⚠️ Important: SQLite Database Requirement

**The inventory sync app requires an external SQLite database file that is NOT included in the repository due to security and size considerations.**

### Setting Up Your SQLite Database

1. **Create SQLite Database**:
   ```bash
   # Create a new SQLite database
   sqlite3 inventory_sync/db.sqlite3
   
   # Or use your existing inventory database
   cp /path/to/your/existing/inventory.db inventory_sync/db.sqlite3
   ```

2. **Required Table Structure**:
   ```sql
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

3. **Configure Database Path**:
   ```bash
   # In your .env file
   SQLITE_DB_PATH=/path/to/your/inventory.db
   ```

### Inventory Sync Features

#### 🔧 **Core Functionality**
- **Product Import**: Import products from SQLite to Django with field mapping
- **Sales Export**: Export sold/delivered products back to SQLite
- **Bidirectional Sync**: Automatic and manual synchronization
- **Field Mapping**: Configurable field mappings between systems
- **Comprehensive Logging**: All operations logged with detailed information

#### 📱 **User Interface**
- **Persian Language**: Complete Persian UI with RTL support
- **Mobile Responsive**: Optimized for mobile devices
- **Dashboard**: Sync statistics and quick actions
- **Real-time Updates**: Live sync status and progress

#### 🔐 **Security & Access**
- **Super Admin Only**: All sync operations require super admin permissions
- **Audit Trail**: Complete logging of all sync operations
- **Data Validation**: Input validation and SQL injection protection
- **Connection Testing**: Validates SQLite connectivity before operations

### Using the Inventory Sync App

#### 1. **Access the Dashboard**
```
URL: /inventory-sync/dashboard/
Access: Super Admin only
```

#### 2. **Import Products**
```
URL: /inventory-sync/import/
Features:
- View importable products from SQLite
- Filter by width, status, or other criteria
- Select products for import
- Configure field mappings
- Monitor import progress
```

#### 3. **Export Sales Status**
```
URL: /inventory-sync/export/
Features:
- Export sold/delivered products to SQLite
- Update product status in external system
- Track export operations
- Handle export errors
```

#### 4. **View Sync Logs**
```
URL: /inventory-sync/logs/
Features:
- Complete history of sync operations
- Success/failure statistics
- Error details and troubleshooting
- User activity tracking
```

#### 5. **Manage Field Mappings**
```
URL: /inventory-sync/mappings/
Features:
- Configure field relationships
- Map SQLite fields to Django models
- Set transformation rules
- Enable/disable mappings
```

### Management Commands

#### Setup Field Mappings
```bash
python manage.py setup_field_mappings
```
Creates default field mappings for common inventory fields.

#### Test SQLite Connection
```bash
python manage.py test_sqlite_connection
```
Tests connectivity to the external SQLite database.

### Troubleshooting Inventory Sync

#### Common Issues

1. **SQLite File Not Found**:
   ```bash
   # Check if file exists
   ls -la inventory_sync/db.sqlite3
   
   # Check permissions
   chmod 644 inventory_sync/db.sqlite3
   ```

2. **Connection Errors**:
   ```bash
   # Test connection manually
   sqlite3 inventory_sync/db.sqlite3 ".tables"
   
   # Check file path in settings
   echo $SQLITE_DB_PATH
   ```

3. **Field Mapping Issues**:
   ```bash
   # Reset field mappings
   python manage.py setup_field_mappings --reset
   
   # Check existing mappings
   python manage.py shell
   >>> from inventory_sync.models import FieldMapping
   >>> FieldMapping.objects.all()
   ```

4. **Import/Export Errors**:
   ```bash
   # Check sync logs
   python manage.py shell
   >>> from inventory_sync.models import SyncLog
   >>> SyncLog.objects.filter(errors__isnull=False).order_by('-executed_at')[:5]
   ```

## 🔐 Authentication System

### User Roles & Permissions

| Role | Access Level | Features |
|------|-------------|----------|
| **🔴 Super Admin** | Full System Access | All modules, SMS management, Inventory sync, System settings |
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
   - SMS code authentication
   - No password required

## 📊 Project Structure

```
v201/
├── accounts/                 # User authentication & management
│   ├── models.py            # Custom User model with roles
│   ├── views.py             # Authentication views
│   ├── permissions.py       # Role-based permissions
│   └── management/          # Django management commands
├── core/                    # Core business logic
│   ├── models.py            # Customer, Order, Product models
│   ├── views.py             # Business views with atomic order system
│   ├── urls.py              # Core URL routing
│   └── management/          # Management commands
├── inventory_sync/          # Inventory synchronization
│   ├── models.py            # SyncConfig, SyncLog, ProductMapping
│   ├── services.py          # SQLiteInventoryService, InventorySyncService
│   ├── views.py             # Sync management views
│   └── templates/           # Persian UI templates
├── payments/                # Payment processing
│   ├── models.py            # Payment models
│   ├── services.py          # Payment services
│   └── views.py             # Payment views
├── sms/                     # SMS integration
│   ├── models.py            # SMS templates, messages, verifications
│   ├── services.py          # SMSService, SMSNotificationService
│   └── views.py             # SMS management views
├── HomayOMS/                # Project settings
│   ├── settings/            # Environment-based settings
│   ├── urls.py              # Main URL configuration
│   └── baseModel.py         # Base model with timestamps
├── templates/               # HTML templates
│   ├── accounts/            # Authentication templates
│   ├── core/                # Business templates
│   └── inventory_sync/      # Sync templates
├── static/                  # Static files (CSS, JS, images)
├── requirements.txt         # Python dependencies
├── config.py               # Environment configuration
└── manage.py               # Django management script
```

## 🚀 Production Deployment

### Raspberry Pi Deployment

The system is successfully deployed on Raspberry Pi with the following configuration:

```bash
# Production Environment
Platform: Raspberry Pi (ARM architecture)
IP Address: 192.168.237.102
Database: PostgreSQL on port 5433
Web Server: Nginx + Gunicorn
Status: ✅ FULLY OPERATIONAL
```

### Deployment Commands
```bash
# SSH to Raspberry Pi
ssh admin@192.168.237.102

# Check service status
sudo systemctl status homayoms
sudo systemctl status nginx

# View logs
sudo journalctl -u homayoms -f
sudo journalctl -u nginx -f

# Restart services
sudo systemctl restart homayoms
sudo systemctl restart nginx

# Update IP address (if needed)
cd /opt/homayoms && ./update-ip.sh
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs web
docker-compose logs db
```

## 🔧 Django Management Commands

### Core Commands

#### Setup Roles and Permissions
```bash
python manage.py setup_roles --create-superuser --username admin --password admin123
```
Creates user roles and permissions with optional superuser.

#### Setup SMS Templates
```bash
python manage.py setup_sms_templates
```
Creates default SMS templates for verification and notifications.

#### Setup Field Mappings
```bash
python manage.py setup_field_mappings
```
Creates default field mappings for inventory sync.

#### Create Test Data
```bash
python manage.py create_full_test_data
python manage.py create_test_products --count 10
python manage.py create_daily_test_customer --count 3
```
Creates test users, products, and customers for development.

### Inventory Sync Commands

#### Test SQLite Connection
```bash
python manage.py test_sqlite_connection
```
Tests connectivity to external SQLite database.

#### Cleanup Empty Orders
```bash
python manage.py cleanup_empty_orders --dry-run
python manage.py cleanup_empty_orders
```
Identifies and removes empty orders from database.

### SMS Commands

#### Test SMS Connection
```bash
python manage.py test_sms_connection
```
Tests SMS server connectivity and hardware status.

#### Send Test SMS
```bash
python manage.py send_test_sms --phone +989109462034 --message "Test message"
```
Sends test SMS message for verification.

## ✅ Completed Features

### 🔄 Atomic Order System
- ✅ **Immediate Order Creation**: Orders created with items when entering selected_products page
- ✅ **Page Exit Protection**: Automatic order cancellation on page exit
- ✅ **Product Reservation**: Products marked as 'Pre-order' to prevent double booking
- ✅ **Automatic Cleanup**: Draft orders cancelled after timeout or page exit

### 📱 Real SMS Integration
- ✅ **SIM800C Hardware**: Real SMS functionality with GSM module
- ✅ **Raspberry Pi Server**: Flask API server for hardware control
- ✅ **Customer Activation**: Automatic SMS notifications when accounts are activated
- ✅ **Verification System**: Secure SMS code authentication
- ✅ **Message Templates**: Configurable SMS templates with variable substitution

### 🔄 Inventory Synchronization
- ✅ **External SQLite Integration**: Bidirectional sync with external inventory systems
- ✅ **Field Mapping System**: Configurable field mappings between systems
- ✅ **Product Import/Export**: Import products and export sales status
- ✅ **Comprehensive Logging**: All sync operations logged with detailed information
- ✅ **Mobile-Friendly Persian UI**: Responsive interface for sync management

### 💰 Cash Purchase Control
- ✅ **Super Admin Control**: Toggle cash purchase availability
- ✅ **Dynamic UI Updates**: Real-time interface updates based on settings
- ✅ **Customer Guidance**: Clear notifications about payment limitations
- ✅ **Alternative Options**: Credit (نسیه) payment remains available

### 📅 Persian Calendar Integration
- ✅ **Automatic Conversion**: All dates automatically converted to Persian Jalali format
- ✅ **Accurate Algorithm**: Proper Persian calendar conversion with leap year support
- ✅ **Client-Side Processing**: No server overhead, pure JavaScript conversion
- ✅ **Visual Styling**: Converted dates displayed in blue with medium font weight

### 🔒 Enhanced Security
- ✅ **Customer Deletion Protection**: Atomic deletion of Customer and User objects
- ✅ **Activity Logging**: Comprehensive audit trail for all operations
- ✅ **Role-Based Permissions**: Granular access control for all user types
- ✅ **Session Management**: Secure user sessions with activity tracking

### 🎨 User Interface
- ✅ **Professional Design**: Beautiful Persian RTL interface
- ✅ **Responsive Layout**: Mobile-first approach with touch-friendly elements
- ✅ **Modern Components**: Clean, professional interface with animations
- ✅ **Accessibility**: WCAG compliant design patterns

### 🔧 Development & DevOps
- ✅ **Environment Configuration**: Local, Dev, Production settings
- ✅ **Docker Support**: Containerization with Docker Compose
- ✅ **Production Deployment**: Manual deployment on Raspberry Pi
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
- Test inventory sync with real SQLite database

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
    <td align="center">
      <a href="https://github.com/Parsa-Parvizi">
        <img src="https://avatars.githubusercontent.com/Parsa-Parvizi" width="100px;" alt=""/>
        <br />
        <sub><b>Amir Holakoo</b></sub>
      </a>
      <br />
      <sub>Project Manager</sub>
      <br />
      <a href="https://github.com/amirholakoo" title="GitHub">🔗 GitHub</a>
    </td>
  </tr>
</table>

### Development Team

- **🎯 Amir DarBandi** - Project Lead & Full Stack Development
  - Expertise: Python, Django, JavaScript, React, Laravel
  - Focus: System architecture, UI/UX, DevOps, SMS integration
  
- **🎯 Parsa Parvizi** - Backend Development & Security
  - Expertise: Python, Django, Cybersecurity, Database Design
  - Focus: HTML CSS
  

### Special Thanks
- **Homayoun Paper & Cardboard Industries Co.** - Project sponsor
- **Django Community** - Framework and documentation
- **SIM800C Hardware Community** - SMS module integration support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**🏢 HomayOMS v201** - *Advanced Order Management System with Real SMS Integration*

[![GitHub stars](https://img.shields.io/github/stars/amirholakoo/IOMS?style=social)](https://github.com/amirholakoo/IOMS)
[![GitHub forks](https://img.shields.io/github/forks/amirholakoo/IOMS?style=social)](https://github.com/amirholakoo/IOMS)

*Built with ❤️ by the HomayOMS Team*

**🚀 Production Ready - Deployed on Raspberry Pi**

</div> 