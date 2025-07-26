#!/bin/bash
# 🔧 Manual Docker Installation for Raspberry Pi
# 🐳 Alternative installation method when automatic fails

set -e

echo "🔧 Manual Docker Installation for Raspberry Pi"
echo "=============================================="

# Fix GPG issues first
echo "🔧 Fixing repository issues..."

# Remove problematic repositories
sudo rm -f /etc/apt/sources.list.d/seeed-studio.list
sudo rm -f /etc/apt/sources.list.d/seeed-studio.list.save

# Clean and update
sudo apt-get clean
sudo apt-get update --fix-missing

# Install required packages
echo "📦 Installing required packages..."
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
echo "🔑 Adding Docker GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository for ARM
echo "📋 Adding Docker repository..."
echo "deb [arch=arm64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list
sudo apt-get update

# Install Docker
echo "🐳 Installing Docker..."
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Start and enable Docker
echo "🚀 Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
echo "👤 Adding user to docker group..."
sudo usermod -aG docker $USER

# Install Docker Compose
echo "📦 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
echo "🔍 Verifying installation..."
docker --version
docker-compose --version

echo ""
echo "✅ Docker installation complete!"
echo "🔄 Please log out and log back in, or run: newgrp docker"
echo "🔧 Then run: ./raspberry-pi-setup-fixed.sh" 