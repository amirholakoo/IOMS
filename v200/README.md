# 🏢 HomayOMS v200 - Order Management System

## 📋 Table of Contents
- [System Introduction](#system-introduction)
- [Key Features](#key-features)
- [Installation & Setup](#installation--setup)
- [Project Structure](#project-structure)
- [Persian Date System](#persian-date-system)
- [User Management](#user-management)
- [Product Management](#product-management)
- [Order System](#order-system)
- [Payment System](#payment-system)
- [Reporting & Logs](#reporting--logs)
- [APIs](#apis)
- [Testing](#testing)
- [Recent Changes](#recent-changes)

## 🎯 System Introduction

HomayOMS is an advanced order management system designed for managing industrial product sales. The system includes comprehensive user management, product management, order processing, payment handling, and reporting capabilities.

### 🚀 Main Features
- **Multi-user management** with different access levels
- **Advanced order system** with cash and installment payment options
- **Product inventory management** with precise tracking
- **Secure payment system** with multiple gateways
- **Comprehensive reporting** and activity logs
- **Persian user interface** with responsive design
- **Complete Persian date system**

## ⭐ Key Features

### 📅 Persian Date System
- **Automatic date conversion** to Persian format
- **Persian month names** (Farvardin, Ordibehesht, etc.)
- **Time support** (hours and minutes)
- **JavaScript conversion** without server dependency
- **Browser caching** for better performance

### 👥 User Management
- **Different access levels**:
  - Super Admin (Full Administrator)
  - Admin (Manager)
  - Customer (Client)
- **Secure authentication** with SMS
- **User profile management**
- **Activity history**

### 📦 Product Management
- **Product categorization** by quality
- **Precise inventory management**
- **Dynamic pricing**
- **Advanced search and filtering**
- **Product images**

### 🛒 Order System
- **Cash and installment orders**
- **Automatic price calculation**
- **Order status tracking**
- **Order history**
- **Order cancellation and editing**

### 💳 Payment System
- **Multiple payment gateways**
- **Cash and installment payments**
- **Transaction history**
- **Financial reports**
- **High security**

## 🛠️ Installation & Setup

### Prerequisites
```bash
Python 3.8+
Django 4.2+
PostgreSQL (Recommended)
Redis (for caching)
```

### Installation
```bash
# Clone the project
git clone <repository-url>
cd v200

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env file

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run server
python manage.py runserver
```

### Environment Configuration
```bash
# .env file
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/homayoms
REDIS_URL=redis://localhost:6379
SMS_API_KEY=your-sms-api-key
PAYMENT_GATEWAY_KEY=your-payment-key
```

## 📁 Project Structure

```
v200/
├── accounts/                 # User management
│   ├── models.py            # User models
│   ├── views.py             # Authentication views
│   └── templates/           # User templates
├── core/                    # Core system
│   ├── models.py            # Product and order models
│   ├── views.py             # Main views
│   ├── management/          # Management commands
│   └── templates/           # Main templates
├── payments/                # Payment system
│   ├── models.py            # Payment models
│   ├── views.py             # Payment views
│   └── templates/           # Payment templates
├── static/                  # Static files
│   ├── css/                 # Stylesheets
│   ├── js/                  # Scripts
│   └── images/              # Images
├── templates/               # Base templates
├── HomayOMS/               # Django settings
└── manage.py               # Django management file
```

## 📅 Persian Date System

### Implementation
The Persian date system is implemented using JavaScript and includes:

#### Main Files
- `static/js/jalali-date-converter.js` - Date conversion function
- `static/js/jalali-date-initializer.js` - Initialization
- `templates/base.html` - Script loading

#### Usage
```html
<!-- In templates -->
<span class="jalali-date" data-date="{{ object.created_at|date:'Y-m-d H:i:s' }}">
    {{ object.created_at|date:"Y/m/d H:i" }}
</span>
```

#### Automatic Conversion
```javascript
// Automatic conversion of all dates
function convertToPersianDate(englishDate) {
    // Convert Gregorian to Persian date
    // Display Persian month names
    // Add time
}
```

### Date System Features
- ✅ Automatic conversion of all dates
- ✅ Persian month names display
- ✅ Time support
- ✅ Error-free operation
- ✅ Browser caching
- ✅ Compatible with all pages

## 👥 User Management

### Access Levels
1. **Super Admin**: Full access to all sections
2. **Admin**: Product and order management
3. **Customer**: Product viewing and ordering

### Authentication
- Login with mobile number
- SMS verification
- Session management
- Automatic logout

## 📦 Product Management

### Product Features
- Roll number
- Dimensions (width, length, weight)
- Quality (A, B, C)
- Storage location
- Price
- Inventory

### Operations
- Add new product
- Edit information
- Inventory management
- Price changes
- Delete product

## 🛒 Order System

### Order Types
- **Cash**: Immediate payment
- **Installment**: Payment in multiple stages

### Order Process
1. Product selection
2. Order confirmation
3. Payment
4. Final confirmation
5. Delivery

### Order Status
- Pending payment
- Paid
- Processing
- Shipped
- Delivered
- Cancelled

## 💳 Payment System

### Payment Gateways
- National gateway
- ZarinPal gateway
- Cash payment
- Installment payment

### Security
- Data encryption
- Transaction verification
- Complete operation logs
- CSRF protection

## 📊 Reporting & Logs

### Available Reports
- Daily/monthly sales reports
- Best-selling products report
- Customer reports
- Financial reports
- Inventory reports

### System Logs
- User login logs
- Product operation logs
- Order logs
- Payment logs
- Error logs

## 🔌 APIs

### Main APIs
```python
# Authentication
POST /api/auth/login/
POST /api/auth/verify/

# Products
GET /api/products/
GET /api/products/{id}/

# Orders
GET /api/orders/
POST /api/orders/
GET /api/orders/{id}/

# Payments
GET /api/payments/
POST /api/payments/
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Test specific section
python manage.py test accounts
python manage.py test core
python manage.py test payments

# Test with code coverage
coverage run --source='.' manage.py test
coverage report
```

### Available Tests
- Authentication tests
- Product tests
- Order tests
- Payment tests
- Persian date tests

## 📝 Recent Changes

### Version v200 (Latest)
- ✅ **Complete Persian date system implementation**
- ✅ **Automatic conversion of all dates to Persian**
- ✅ **Fixed JavaScript errors**
- ✅ **Performance optimization**
- ✅ **UI improvements**
- ✅ **Added activity logs**
- ✅ **Enhanced system security**

### Persian Date System Details
1. **Created efficient conversion function**
2. **Fixed `JalaliDateConverter is not defined` errors**
3. **Updated all templates**
4. **Added browser caching**
5. **Performance optimization**

### Modified Files
- `static/js/jalali-date-converter.js` - New conversion function
- `static/js/jalali-date-initializer.js` - Improved initialization
- `templates/base.html` - Script loading
- All templates with dates

## 🤝 Contributing

To contribute to the project:
1. Fork the project
2. Create a new branch
3. Make changes
4. Submit Pull Request

## 📞 Support

For support and bug reports:
- Email: support@homayoms.com
- Phone: +98-21-12345678
- Telegram: @homayoms_support

## 📄 License

This project is licensed under the MIT License.

---

**Developer**: Homay Development Team  
**Last Updated**: March 25, 2025  
**Version**: v200
