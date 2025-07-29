#!/bin/bash
# 🍓 Raspberry Pi Setup Script for HomayOMS v200
# 🔧 Complete setup and deployment script for Raspberry Pi

set -e

echo "🍓 Raspberry Pi Setup for HomayOMS v200"
echo "========================================"

# 🔍 Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    echo "   It may work on other ARM devices but is not guaranteed"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 🔧 Check system requirements
echo "🔍 Checking system requirements..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed. Please log out and back in, then run this script again."
    exit 0
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Check available memory
MEMORY_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEMORY_GB=$((MEMORY_KB / 1024 / 1024))
echo "💾 Available memory: ${MEMORY_GB}GB"

if [ $MEMORY_GB -lt 2 ]; then
    echo "⚠️  Warning: Less than 2GB RAM detected. Performance may be limited."
    echo "   Recommended: 4GB+ RAM for optimal performance"
fi

# Check available storage
STORAGE_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
echo "💿 Available storage: ${STORAGE_GB}GB"

if [ $STORAGE_GB -lt 10 ]; then
    echo "❌ Error: Less than 10GB free storage. Please free up space."
    exit 1
fi

# 📁 Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs csv_logs postgres_backups ssl

# 🔧 Set proper permissions
echo "🔧 Setting permissions..."
chmod +x docker-entrypoint.raspberry.sh

# 🌐 Configure network settings
echo "🌐 Configuring network settings..."

# Get Raspberry Pi IP address
PI_IP=$(hostname -I | awk '{print $1}')
echo "📍 Raspberry Pi IP: $PI_IP"

# Update environment file with correct IP
sed -i "s|SMS_SERVER_URL=.*|SMS_SERVER_URL=http://$PI_IP:5003|g" env.raspberry
sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,$PI_IP,192.168.1.0/24,192.168.0.0/24|g" env.raspberry
sed -i "s|CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,http://$PI_IP:8000,http://192.168.1.0/24,http://192.168.0.0/24|g" env.raspberry

# 🔐 Generate secure secret key
echo "🔐 Generating secure secret key..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" env.raspberry

# 🐳 Build and start containers
echo "🐳 Building and starting containers..."

# Load environment variables
set -a
source env.raspberry
set +a

# Build the image
echo "🔨 Building Docker image..."
docker-compose -f docker-compose.raspberry.yml build

# Start the services
echo "🚀 Starting services..."
docker-compose -f docker-compose.raspberry.yml up -d

# ⏰ Wait for services to be ready
echo "⏰ Waiting for services to be ready..."
sleep 30

# 🔍 Check service status
echo "🔍 Checking service status..."
docker-compose -f docker-compose.raspberry.yml ps

# 📊 Show logs
echo "📊 Recent logs from web service:"
docker-compose -f docker-compose.raspberry.yml logs --tail=20 web

# ✅ Setup complete
echo ""
echo "✅ Raspberry Pi Setup Complete!"
echo "================================"
echo ""
echo "🌐 Access Information:"
echo "🔗 Main Application: http://$PI_IP:8000"
echo "🎛️ Admin Panel: http://$PI_IP:8000/admin/"
echo "🐘 pgAdmin: http://$PI_IP:5050 (optional - use --profile admin)"
echo ""
echo "👤 Default Login Credentials:"
echo "🔑 Super Admin: admin / admin123"
echo "👨‍💼 Admin: admin_user / admin123"
echo "💰 Finance: finance_user / finance123"
echo "👤 Customer: customer_user / customer123"
echo ""
echo "📱 SMS Testing:"
echo "📞 Phone: 09123456789"
echo "🔢 Code: 123456"
echo ""
echo "🔧 Management Commands:"
echo "📊 View logs: docker-compose -f docker-compose.raspberry.yml logs -f"
echo "🔄 Restart: docker-compose -f docker-compose.raspberry.yml restart"
echo "🛑 Stop: docker-compose -f docker-compose.raspberry.yml down"
echo "📦 Backup DB: docker exec homayoms_v200_db pg_dump -U homayoms_user homayoms_v200_db > backup.sql"
echo ""
echo "⚙️ Optional Features:"
echo "🌐 With Nginx: docker-compose -f docker-compose.raspberry.yml --profile nginx up -d"
echo "🎛️ With pgAdmin: docker-compose -f docker-compose.raspberry.yml --profile admin up -d"
echo ""
echo "🔒 Security Notes:"
echo "⚠️  Change default passwords in production"
echo "⚠️  Configure SSL certificates for HTTPS"
echo "⚠️  Set up firewall rules"
echo "⚠️  Regular backups recommended"
echo ""
echo "📈 Performance Monitoring:"
echo "💾 Memory usage: docker stats"
echo "📊 System resources: htop"
echo "🌡️ Temperature: vcgencmd measure_temp"
echo ""
echo "🎉 Setup complete! Your HomayOMS system is now running on Raspberry Pi." 