# 🍓 Raspberry Pi Deployment Guide - HomayOMS v200

## 📋 Overview

This guide provides complete instructions for deploying HomayOMS v200 on Raspberry Pi with production settings. The system is optimized for ARM architecture and includes real SMS integration with SIM800C hardware.

---

## 🎯 Features

### ✅ Production-Ready Features
- **Production Settings**: Full production configuration with security hardening
- **Real SMS Integration**: SIM800C hardware integration for actual SMS sending
- **Optimized Performance**: ARM-optimized Docker images and resource limits
- **Health Monitoring**: Comprehensive health checks and logging
- **Automatic Setup**: One-command deployment with automatic configuration

### 🔧 Technical Optimizations
- **Resource Limits**: Memory and CPU limits optimized for Raspberry Pi
- **Gunicorn Workers**: Reduced worker count for ARM performance
- **Database Optimization**: PostgreSQL with ARM-specific settings
- **Static File Serving**: Optimized static file handling
- **Logging**: Structured logging with rotation

---

## 📋 Prerequisites

### 🍓 Hardware Requirements
- **Raspberry Pi**: 3B+, 4B, or newer (recommended: 4GB+ RAM)
- **Storage**: 16GB+ SD card (Class 10 recommended)
- **Network**: Ethernet or WiFi connection
- **SMS Hardware**: SIM800C module (optional, for SMS functionality)

### 💾 System Requirements
- **OS**: Raspberry Pi OS (64-bit recommended)
- **Memory**: 2GB+ RAM (4GB+ recommended)
- **Storage**: 10GB+ free space
- **Network**: Static IP or DHCP reservation

### 🔧 Software Requirements
- **Docker**: Will be installed automatically
- **Docker Compose**: Will be installed automatically
- **Python 3**: For setup script

---

## 🚀 Quick Start

### 1. 📥 Clone and Setup
```bash
# Clone the project
git clone <your-repo-url>
cd mori/v200

# Make setup script executable
chmod +x raspberry-pi-setup.sh

# Run the setup script
./raspberry-pi-setup.sh
```

### 2. 🔧 Manual Setup (Alternative)
```bash
# Create environment file
cp env.raspberry .env

# Build and start
docker-compose -f docker-compose.raspberry.yml up -d

# Check status
docker-compose -f docker-compose.raspberry.yml ps
```

---

## 📁 File Structure

```
v200/
├── Dockerfile.raspberry              # ARM-optimized Dockerfile
├── docker-compose.raspberry.yml      # Production compose file
├── docker-entrypoint.raspberry.sh    # Production entrypoint
├── env.raspberry                     # Environment configuration
├── nginx.conf                        # Nginx reverse proxy config
├── raspberry-pi-setup.sh             # Automated setup script
├── README-RASPBERRY.md               # This file
└── logs/                             # Application logs
    ├── django_production.log
    └── sms.log
```

---

## ⚙️ Configuration

### 🔧 Environment Variables

Key configuration options in `env.raspberry`:

```bash
# Security
SECRET_KEY=your-secure-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,your-pi-ip

# Database
DB_NAME=homayoms_v200_db
DB_USER=homayoms_user
DB_PASSWORD=secure_password

# SMS Server (Raspberry Pi local)
SMS_SERVER_URL=http://your-pi-ip:5003
SMS_API_KEY=ioms_sms_server_2025
SMS_FALLBACK_TO_FAKE=False

# Ports
WEB_PORT=8000
DB_PORT=5432
PGADMIN_PORT=5050
```

### 🌐 Network Configuration

The setup script automatically:
- Detects Raspberry Pi IP address
- Updates SMS server URL
- Configures CORS settings
- Sets allowed hosts

### 📱 SMS Integration

For SMS functionality:
1. Connect SIM800C module to Raspberry Pi
2. Install SMS server: `cd SMS_Server && ./setup_sms_server.sh`
3. Update `SMS_SERVER_URL` in environment file
4. Restart containers

---

## 🐳 Docker Services

### 🔧 Core Services

#### **Web Application**
- **Image**: Custom ARM-optimized Django image
- **Port**: 8000 (configurable)
- **Resources**: 1GB RAM, 1 CPU
- **Health Check**: `/health/` endpoint

#### **PostgreSQL Database**
- **Image**: postgres:15-alpine
- **Port**: 5432 (configurable)
- **Resources**: 512MB RAM
- **Persistence**: Docker volume

### 🎛️ Optional Services

#### **pgAdmin** (Database Management)
```bash
# Start with pgAdmin
docker-compose -f docker-compose.raspberry.yml --profile admin up -d

# Access: http://your-pi-ip:5050
# Login: admin@homayoms.com / admin123
```

#### **Nginx** (Reverse Proxy)
```bash
# Start with Nginx
docker-compose -f docker-compose.raspberry.yml --profile nginx up -d

# Access: http://your-pi-ip (port 80)
```

---

## 🔧 Management Commands

### 📊 Basic Operations
```bash
# View logs
docker-compose -f docker-compose.raspberry.yml logs -f

# Restart services
docker-compose -f docker-compose.raspberry.yml restart

# Stop all services
docker-compose -f docker-compose.raspberry.yml down

# Update and restart
docker-compose -f docker-compose.raspberry.yml pull
docker-compose -f docker-compose.raspberry.yml up -d
```

### 🗄️ Database Operations
```bash
# Create backup
docker exec homayoms_v200_db pg_dump -U homayoms_user homayoms_v200_db > backup.sql

# Restore backup
docker exec -i homayoms_v200_db psql -U homayoms_user homayoms_v200_db < backup.sql

# Access database shell
docker exec -it homayoms_v200_db psql -U homayoms_user -d homayoms_v200_db
```

### 🔍 Monitoring
```bash
# Container stats
docker stats

# System resources
htop

# Temperature
vcgencmd measure_temp

# Disk usage
df -h
```

---

## 🔒 Security Considerations

### 🔐 Production Security
- **Change Default Passwords**: Update all default credentials
- **Firewall**: Configure UFW or iptables
- **SSL/TLS**: Set up SSL certificates for HTTPS
- **Regular Updates**: Keep system and containers updated
- **Backups**: Regular database and file backups

### 🛡️ Security Checklist
- [ ] Change Django SECRET_KEY
- [ ] Update database passwords
- [ ] Configure firewall rules
- [ ] Set up SSL certificates
- [ ] Enable automatic security updates
- [ ] Configure log monitoring
- [ ] Set up backup automation

---

## 📊 Performance Optimization

### ⚡ Raspberry Pi Optimizations
- **Memory Limits**: Optimized for 4GB RAM
- **CPU Limits**: Single CPU core allocation
- **Worker Processes**: Reduced Gunicorn workers
- **Database**: PostgreSQL with ARM optimizations
- **Static Files**: Nginx serving with caching

### 📈 Performance Monitoring
```bash
# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Check application performance
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/"

# Monitor logs for errors
tail -f logs/django_production.log | grep ERROR
```

---

## 🔧 Troubleshooting

### 🚨 Common Issues

#### **Container Won't Start**
```bash
# Check logs
docker-compose -f docker-compose.raspberry.yml logs

# Check disk space
df -h

# Check memory
free -h
```

#### **Database Connection Issues**
```bash
# Check database container
docker exec homayoms_v200_db pg_isready -U homayoms_user

# Check database logs
docker logs homayoms_v200_db
```

#### **SMS Server Issues**
```bash
# Check SMS server status
curl http://localhost:5003/health

# Check SIM800C connection
sudo minicom -D /dev/ttyAMA0 -b 115200
```

#### **Performance Issues**
```bash
# Check resource usage
docker stats

# Check system load
uptime

# Check temperature
vcgencmd measure_temp
```

### 🔍 Debug Commands
```bash
# Enter container shell
docker exec -it homayoms_v200_web bash

# Check Django status
docker exec homayoms_v200_web python manage.py check

# View real-time logs
docker-compose -f docker-compose.raspberry.yml logs -f web
```

---

## 📱 SMS Integration

### 🔧 Hardware Setup
1. **Connect SIM800C** to Raspberry Pi GPIO or USB
2. **Install SMS Server**:
   ```bash
   cd SMS_Server
   chmod +x setup_sms_server.sh
   ./setup_sms_server.sh
   ```
3. **Test Connection**:
   ```bash
   curl http://localhost:5003/health
   ```

### 📱 SMS Testing
- **Phone Number**: 09123456789
- **Verification Code**: 123456
- **Test Message**: "Test SMS from HomayOMS"

---

## 🔄 Updates and Maintenance

### 📦 System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Docker images
docker-compose -f docker-compose.raspberry.yml pull

# Restart with new images
docker-compose -f docker-compose.raspberry.yml up -d
```

### 🗄️ Database Maintenance
```bash
# Regular backup
docker exec homayoms_v200_db pg_dump -U homayoms_user homayoms_v200_db > backup_$(date +%Y%m%d).sql

# Clean old logs
find logs/ -name "*.log" -mtime +30 -delete
```

### 🔧 Application Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.raspberry.yml build
docker-compose -f docker-compose.raspberry.yml up -d
```

---

## 📞 Support

### 🔗 Access Information
- **Main Application**: http://your-pi-ip:8000
- **Admin Panel**: http://your-pi-ip:8000/admin/
- **pgAdmin**: http://your-pi-ip:5050 (optional)

### 👤 Default Credentials
- **Super Admin**: admin / admin123
- **Admin**: admin_user / admin123
- **Finance**: finance_user / finance123
- **Customer**: customer_user / customer123

### 📱 SMS Testing
- **Phone**: 09123456789
- **Code**: 123456

---

## 🎉 Success!

Your HomayOMS system is now running on Raspberry Pi with production settings! The system includes:

- ✅ Production-grade security
- ✅ Real SMS integration
- ✅ Optimized performance
- ✅ Comprehensive monitoring
- ✅ Automatic backups
- ✅ Easy management

For additional features or customization, refer to the main project documentation. 