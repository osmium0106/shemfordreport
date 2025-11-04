#!/bin/bash

# AWS EC2 Deployment Script for Student Report System
# Run this script on your EC2 Ubuntu instance after connecting via SSH

set -e  # Exit on any error

echo "🚀 Starting AWS EC2 deployment for Student Report System..."
echo "⏱️  This will take about 5-10 minutes. Please be patient!"
echo ""

# Function to print colored output
print_status() {
    echo "🔄 $1..."
}

print_success() {
    echo "✅ $1"
}

print_error() {
    echo "❌ $1"
}

# Update system
print_status "Updating system packages (this may take a few minutes)"
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing Docker, Git, and Nginx"
sudo apt install -y docker.io docker-compose-v2 git nginx certbot python3-certbot-nginx curl

# Add user to docker group
print_status "Setting up Docker permissions"
sudo usermod -aG docker $USER

# Start and enable Docker
sudo systemctl enable docker
sudo systemctl start docker

# Create application directory
APP_DIR="/home/ubuntu/shemfordreport"
print_status "Setting up application directory at $APP_DIR"

# Clone repository if not already cloned
if [ ! -d "$APP_DIR" ]; then
    print_status "Downloading your Student Report System from GitHub"
    git clone https://github.com/osmium0106/shemfordreport.git $APP_DIR
else
    print_status "Updating existing application"
    cd $APP_DIR
    git pull origin main
fi

cd $APP_DIR

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating environment configuration"
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "change-this-secret-key-$(date +%s)")
    sed -i "s/your-secret-key-here-change-this-to-a-random-string/$SECRET_KEY/" .env
    
    print_success "Generated secure secret key for your application"
    echo "🔑 If you want to customize settings, edit the .env file later"
fi

# Build and start the application
print_status "Building and starting your Student Report System"
echo "📦 This step downloads and builds all required components..."

# Wait for docker to be ready
sleep 5

# Check if user is in docker group (requires re-login to take effect)
if ! groups $USER | grep -q docker; then
    print_status "Docker group membership requires re-login. Temporarily using sudo..."
    sudo docker-compose up -d --build
else
    docker-compose up -d --build
fi

# Wait for application to start
print_status "Waiting for application to start (30 seconds)"
sleep 30

# Test if application is running
print_status "Testing application"
if curl -f http://localhost:5000 > /dev/null 2>&1; then
    print_success "Application is running successfully!"
else
    print_error "Application failed to start. Let's check the logs..."
    docker-compose logs
    echo ""
    echo "💡 Troubleshooting tips:"
    echo "   1. Check if all containers are running: docker-compose ps"
    echo "   2. View detailed logs: docker-compose logs -f"
    echo "   3. Restart the application: docker-compose restart"
    exit 1
fi

# Configure firewall
print_status "Configuring server firewall"
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp
sudo ufw --force enable

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "Unable to determine")

print_success "Deployment completed successfully!"
echo ""
echo "🎉 Your Student Report System is now running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 ACCESS YOUR APPLICATION:"
echo "   🌐 Direct access: http://$PUBLIC_IP:5000"
echo "   🔗 With domain: http://your-domain.com:5000 (after DNS setup)"
echo ""
echo "🔧 NEXT STEPS:"
echo ""
echo "1. 🌍 SETUP YOUR DOMAIN:"
echo "   • Go to your GoDaddy account"
echo "   • Update A record to point to: $PUBLIC_IP"
echo "   • Wait 5-30 minutes for DNS propagation"
echo ""
echo "2. 🔐 SETUP SSL CERTIFICATE (after domain is working):"
echo "   sudo certbot --nginx -d your-domain.com -d www.your-domain.com"
echo ""
echo "3. ⚙️ CUSTOMIZE YOUR APPLICATION:"
echo "   • Edit settings: nano $APP_DIR/.env"
echo "   • Add your Google Sheets URLs in app_simple.py"
echo ""
echo "📋 USEFUL COMMANDS:"
echo "   • View application logs: cd $APP_DIR && docker-compose logs -f"
echo "   • Restart application: cd $APP_DIR && docker-compose restart"
echo "   • Update application: cd $APP_DIR && git pull && docker-compose up -d --build"
echo "   • Check running containers: docker-compose ps"
echo ""
echo "🆘 NEED HELP?"
echo "   • Check application status: curl http://localhost:5000"
echo "   • View detailed logs: docker-compose logs"
echo "   • Server resource usage: htop (install with: sudo apt install htop)"
echo ""
echo "� IMPORTANT NOTES:"
echo "   • Your application is running on port 5000"
echo "   • After setting up domain and SSL, you can remove port 5000 from firewall"
echo "   • Regular backups recommended for production use"
echo ""
echo "🎯 SUCCESS! Your Student Report System is ready for students and teachers!"