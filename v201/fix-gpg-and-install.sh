#!/bin/bash
# 🔧 COMPLETE GPG FIX AND DOCKER INSTALLATION
# 🐳 This script will fix the GPG error and install Docker properly

set -e

echo "🔧 COMPLETE GPG FIX AND DOCKER INSTALLATION"
echo "============================================"

# Step 1: Find and remove ALL problematic repositories
echo "🔍 Step 1: Finding and removing problematic repositories..."

# Remove any seeed-studio repositories
sudo rm -f /etc/apt/sources.list.d/seeed-studio.list
sudo rm -f /etc/apt/sources.list.d/seeed-studio.list.save
sudo rm -f /etc/apt/sources.list.d/seeed-studio.list.disabled

# Check if the repository is in the main sources.list
if grep -q "seeed-studio" /etc/apt/sources.list; then
    echo "🗑️ Removing seeed-studio from main sources.list..."
    sudo sed -i '/seeed-studio/d' /etc/apt/sources.list
fi

# Check for any other problematic repositories
echo "🔍 Checking for other problematic repositories..."
find /etc/apt/sources.list.d/ -name "*.list" -exec grep -l "seeed-studio\|stretch" {} \; 2>/dev/null | while read file; do
    echo "🗑️ Removing problematic file: $file"
    sudo rm -f "$file"
done

# Step 2: Clean everything
echo "🧹 Step 2: Cleaning package cache..."
sudo apt-get clean
sudo apt-get autoclean
sudo rm -rf /var/lib/apt/lists/*
sudo mkdir -p /var/lib/apt/lists/partial

# Step 3: Update without the problematic repository
echo "🔄 Step 3: Updating package lists..."
sudo apt-get update --allow-releaseinfo-change

# Step 4: Install Docker using the official method
echo "🐳 Step 4: Installing Docker..."

# Remove any old Docker installations
echo "🗑️ Removing old Docker installations..."
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

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
echo "✅ DOCKER INSTALLATION COMPLETE!"
echo "================================"
echo ""
echo "🔄 Next steps:"
echo "1. Log out and log back in, OR run: newgrp docker"
echo "2. Then run: ./raspberry-pi-setup-fixed.sh"
echo ""
echo "🔧 To test Docker, run: docker run hello-world" 