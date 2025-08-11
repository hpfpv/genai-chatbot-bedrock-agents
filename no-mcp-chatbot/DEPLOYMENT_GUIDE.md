# 🚀 AWS Bedrock Chatbot - Deployment Guide

This guide covers different deployment options for the AWS Bedrock Chatbot with custom tools.

## 📋 **Pre-Deployment Checklist**

### **✅ System Requirements**
- [ ] Python 3.8+ installed
- [ ] AWS CLI installed and configured
- [ ] Internet connection
- [ ] 1GB RAM available
- [ ] 500MB disk space available

### **✅ AWS Prerequisites**
- [ ] AWS account with appropriate permissions
- [ ] Bedrock access enabled in your region
- [ ] IAM permissions configured
- [ ] AWS credentials configured (CLI profile or environment variables)

### **✅ Optional Services**
- [ ] SerpAPI account for web search functionality

## 🏠 **Local Development Deployment**

### **Quick Setup**
```bash
# Clone and setup
git clone <repository-url>
cd no-mcp-chatbot

# Run automated setup
./setup.sh

# Configure your settings
cp config.py.template config.py
# Edit config.py with your AWS profile and settings

# Start the application
./run.sh
```

### **Manual Setup**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS
aws configure
# or
aws configure sso

# Create configuration
cp config.py.template config.py
# Edit config.py

# Run application
streamlit run app.py
```

## 🖥️ **Server Deployment**

### **Linux Server Setup**

#### **1. System Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### **2. Application Setup**
```bash
# Create application directory
sudo mkdir -p /opt/aws-bedrock-chatbot
sudo chown $USER:$USER /opt/aws-bedrock-chatbot
cd /opt/aws-bedrock-chatbot

# Clone repository
git clone <repository-url> .

# Run setup
./setup.sh

# Configure application
cp config.py.template config.py
# Edit config.py with your settings
```

#### **3. Configure AWS Credentials**
```bash
# Option 1: AWS CLI configuration
aws configure

# Option 2: IAM Role (recommended for EC2)
# Attach IAM role to EC2 instance with required permissions

# Option 3: Environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1
```

#### **4. Run as Service (systemd)**
```bash
# Create service file
sudo tee /etc/systemd/system/aws-bedrock-chatbot.service > /dev/null <<EOF
[Unit]
Description=AWS Bedrock Chatbot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/aws-bedrock-chatbot
Environment=PATH=/opt/aws-bedrock-chatbot/venv/bin
ExecStart=/opt/aws-bedrock-chatbot/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable aws-bedrock-chatbot
sudo systemctl start aws-bedrock-chatbot

# Check status
sudo systemctl status aws-bedrock-chatbot
```

### **Reverse Proxy Setup (Nginx)**
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/aws-bedrock-chatbot > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/aws-bedrock-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🐳 **Docker Deployment**

### **Dockerfile**
```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws/

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create configuration from template
RUN cp config.py.template config.py

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
```

### **Docker Compose**
```yaml
version: '3.8'

services:
  aws-bedrock-chatbot:
    build: .
    ports:
      - "8501:8501"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
    volumes:
      - ./config.py:/app/config.py:ro
      - ~/.aws:/root/.aws:ro  # Mount AWS credentials
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### **Build and Run**
```bash
# Build image
docker build -t aws-bedrock-chatbot .

# Run container
docker run -d \
  --name aws-bedrock-chatbot \
  -p 8501:8501 \
  -v $(pwd)/config.py:/app/config.py:ro \
  -v ~/.aws:/root/.aws:ro \
  aws-bedrock-chatbot

# Or use docker-compose
docker-compose up -d
```

## ☁️ **AWS EC2 Deployment**

### **Launch EC2 Instance**
1. **Choose AMI**: Amazon Linux 2 or Ubuntu 20.04 LTS
2. **Instance Type**: t3.medium (minimum) or t3.large (recommended)
3. **Security Group**: Allow HTTP (80), HTTPS (443), and custom port (8501)
4. **IAM Role**: Attach role with Bedrock and required AWS permissions

### **IAM Role Permissions**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels",
                "ec2:DescribeInstances",
                "ec2:StartInstances",
                "ec2:StopInstances",
                "s3:ListAllMyBuckets",
                "s3:ListBucket",
                "s3:GetObject"
            ],
            "Resource": "*"
        }
    ]
}
```

### **User Data Script**
```bash
#!/bin/bash
yum update -y
yum install -y python3 python3-pip git

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Clone and setup application
cd /opt
git clone <repository-url> aws-bedrock-chatbot
cd aws-bedrock-chatbot
chmod +x setup.sh run.sh
./setup.sh

# Configure application (you'll need to customize this)
cp config.py.template config.py
# Edit config.py as needed

# Start application
nohup ./run.sh > /var/log/aws-bedrock-chatbot.log 2>&1 &
```

## 🔒 **Security Considerations**

### **Production Security Checklist**
- [ ] Use IAM roles instead of access keys when possible
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure proper security groups/firewall rules
- [ ] Regular security updates
- [ ] Monitor application logs
- [ ] Use secrets management for sensitive data

### **Network Security**
```bash
# Configure firewall (Ubuntu/Debian)
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# For development only
sudo ufw allow 8501/tcp
```

### **SSL/HTTPS Setup**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 **Monitoring and Logging**

### **Application Logs**
```bash
# View application logs
sudo journalctl -u aws-bedrock-chatbot -f

# Streamlit logs location
~/.streamlit/logs/
```

### **System Monitoring**
```bash
# Install monitoring tools
sudo apt install htop iotop -y

# Monitor resources
htop
iotop
df -h
free -h
```

### **Log Rotation**
```bash
# Configure logrotate
sudo tee /etc/logrotate.d/aws-bedrock-chatbot > /dev/null <<EOF
/var/log/aws-bedrock-chatbot.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 ubuntu ubuntu
}
EOF
```

## 🔄 **Backup and Updates**

### **Backup Strategy**
```bash
# Backup configuration and data
tar -czf backup-$(date +%Y%m%d).tar.gz \
    config.py \
    ~/.aws/ \
    /var/log/aws-bedrock-chatbot.log
```

### **Update Procedure**
```bash
# Stop service
sudo systemctl stop aws-bedrock-chatbot

# Backup current version
cp -r /opt/aws-bedrock-chatbot /opt/aws-bedrock-chatbot.backup

# Update code
cd /opt/aws-bedrock-chatbot
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl start aws-bedrock-chatbot
```

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Application Won't Start**
```bash
# Check service status
sudo systemctl status aws-bedrock-chatbot

# Check logs
sudo journalctl -u aws-bedrock-chatbot -n 50

# Check port availability
sudo netstat -tlnp | grep 8501
```

#### **AWS Authentication Issues**
```bash
# Test AWS credentials
aws sts get-caller-identity

# Check IAM permissions
aws bedrock list-foundation-models --region us-east-1

# Verify configuration
python3 -c "from config import *; print(f'Profile: {AWS_PROFILE}, Region: {AWS_DEFAULT_REGION}')"
```

#### **Performance Issues**
```bash
# Check system resources
htop
free -h
df -h

# Check application performance
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8501"
```

## 📞 **Support**

For deployment issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Review application and system logs
4. Test AWS connectivity and permissions
5. Check the GitHub repository for known issues

---

**🎉 Your AWS Bedrock Chatbot is now ready for production deployment!**

Choose the deployment method that best fits your infrastructure and security requirements.
