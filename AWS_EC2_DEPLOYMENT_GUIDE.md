# 🚀 Complete AWS EC2 Deployment Guide for Beginners

## Prerequisites Checklist
- [ ] AWS Account created and verified
- [ ] Credit card added (for verification - we'll use free tier)
- [ ] Domain from GoDaddy ready (you mentioned you have one)
- [ ] Basic understanding that we're creating a virtual server in the cloud

---

## Step 1: Launch EC2 Instance (Your Virtual Server)

### 1.1 Access EC2 Dashboard
1. Go to https://console.aws.amazon.com/
2. Sign in to your AWS account
3. In the top search bar, type "EC2" and click on "EC2" service
4. Click "Launch Instance" (big orange button)

### 1.2 Configure Your Instance

**Name and Tags:**
- Instance name: `student-report-server`

**Application and OS Images (Amazon Machine Image):**
- Choose: **Ubuntu Server 22.04 LTS (HVM), SSD Volume Type**
- Architecture: **64-bit (x86)**
- ✅ This is free tier eligible

**Instance Type:**
- Choose: **t2.micro** (this is free tier eligible)
- 1 vCPU, 1 GB RAM - perfect for our application

**Key Pair (Login):**
- Click "Create new key pair"
- Key pair name: `student-report-key`
- Key pair type: **RSA**
- Private key file format: **.pem** (for SSH)
- Click "Create key pair"
- ⚠️ **IMPORTANT**: Download and save the .pem file securely - you can't download it again!

**Network Settings (Configure Security Group):**
- Click "Edit" next to Network settings
- Security group name: `student-report-security`
- Description: `Security group for Student Report System`

**Add these rules (click "Add security group rule" for each):**

| Type | Protocol | Port Range | Source | Description |
|------|----------|------------|--------|-------------|
| SSH | TCP | 22 | My IP | SSH access |
| HTTP | TCP | 80 | 0.0.0.0/0 | Web traffic |
| HTTPS | TCP | 443 | 0.0.0.0/0 | Secure web traffic |
| Custom TCP | TCP | 5000 | 0.0.0.0/0 | Flask app (temporary) |

**Configure Storage:**
- Keep default: **8 GB gp3** (free tier eligible)

**Advanced Details:**
- Leave everything as default

### 1.3 Launch Instance
1. Review all settings
2. Click "Launch instance"
3. Wait for the instance to show "Running" state (2-3 minutes)

---

## Step 2: Connect to Your Server

### 2.1 Find Your Instance Details
1. In EC2 Dashboard, click "Instances"
2. Click on your `student-report-server` instance
3. Note down the **Public IPv4 address** (e.g., 3.15.123.456)

### 2.2 Connect via SSH

**For Windows (using PowerShell):**

1. Open PowerShell as Administrator
2. Navigate to where you downloaded the .pem file:
   ```powershell
   cd C:\Users\YourUsername\Downloads
   ```

3. Set correct permissions on the key file:
   ```powershell
   icacls student-report-key.pem /inheritance:r
   icacls student-report-key.pem /grant:r %username%:F
   ```

4. Connect to your server (replace with your actual IP):
   ```powershell
   ssh -i student-report-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
   ```
   
   Example:
   ```powershell
   ssh -i student-report-key.pem ubuntu@3.15.123.456
   ```

5. Type "yes" when asked about authenticity

**For Windows (Alternative - using PuTTY):**
If SSH doesn't work, I can guide you through PuTTY setup.

### 2.3 You're In!
If successful, you'll see something like:
```
ubuntu@ip-172-31-XX-XX:~$
```

Congratulations! You're now connected to your cloud server! 🎉

---

## Step 3: Deploy Your Application

### 3.1 Run the Automated Deployment Script

Once connected to your EC2 instance, run these commands:

```bash
# Update system
sudo apt update

# Install git
sudo apt install -y git

# Clone your repository
git clone https://github.com/osmium0106/shemfordreport.git

# Go to the project directory
cd shemfordreport

# Make deployment script executable
chmod +x deploy-aws.sh

# Run the deployment script
./deploy-aws.sh
```

The script will:
- ✅ Install Docker and required packages
- ✅ Build your application container
- ✅ Start your Student Report System
- ✅ Configure firewall settings

### 3.2 Test Your Application

After the script completes:

1. **Test locally on server:**
   ```bash
   curl http://localhost:5000
   ```

2. **Test from your browser:**
   - Go to: `http://YOUR_EC2_PUBLIC_IP:5000`
   - You should see your Student Report System!

---

## Step 4: Configure Your Domain

### 4.1 Point Domain to EC2 Instance

1. **Login to GoDaddy:**
   - Go to https://dcc.godaddy.com/manage/
   - Click on your domain

2. **Update DNS Settings:**
   - Click "DNS" → "Manage Zones"
   - Find the A record (or create one):
     - **Type**: A
     - **Name**: @ (for root domain) or www
     - **Value**: Your EC2 Public IP address
     - **TTL**: 600 seconds
   - Save changes

3. **Wait for DNS propagation** (5-30 minutes)

### 4.2 Setup SSL Certificate (HTTPS)

Once your domain points to your server:

```bash
# Connect back to your EC2 instance
ssh -i student-report-key.pem ubuntu@YOUR_EC2_IP

# Install SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow the prompts and agree to terms
```

---

## Step 5: Configure Production Setup

### 5.1 Setup Nginx Reverse Proxy

```bash
# Create nginx configuration
sudo nano /etc/nginx/sites-available/student-report

# Add this configuration (replace yourdomain.com):
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/student-report /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🎉 Success! Your Application is Live!

Visit: `https://yourdomain.com`

## Common Issues & Solutions

### Issue: Can't connect via SSH
**Solution:** 
- Check security group allows SSH (port 22) from your IP
- Verify you're using the correct .pem file and IP address

### Issue: Application not accessible
**Solution:**
- Check security group allows HTTP (port 80) and HTTPS (port 443)
- Verify the application is running: `docker-compose ps`

### Issue: Domain not working
**Solution:**
- Wait for DNS propagation (up to 24 hours)
- Check DNS settings in GoDaddy
- Verify A record points to correct IP

## Monitoring Your Application

### Check Application Status
```bash
# See if containers are running
docker-compose ps

# View application logs
docker-compose logs -f

# Restart application
docker-compose restart
```

### Update Your Application
```bash
# Pull latest changes from GitHub
cd shemfordreport
git pull origin main

# Rebuild and restart
docker-compose up -d --build
```

## Cost Management

- **t2.micro instance**: Free for first 12 months (750 hours/month)
- **After free tier**: ~$8-10/month
- **Storage**: 8GB free, then ~$1/month per 8GB
- **Data transfer**: 1GB free/month

## Security Best Practices

1. **Regularly update your server:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Monitor access logs:**
   ```bash
   sudo tail -f /var/log/auth.log
   ```

3. **Change SSH port** (optional but recommended)

4. **Setup CloudWatch monitoring** for resource usage

---

**🎯 You've successfully deployed a production Flask application on AWS EC2!**

Need help with any step? Let me know and I'll provide more detailed guidance!