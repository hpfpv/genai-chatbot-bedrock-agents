# 🤖 AWS MCP Agent - Complete Guide

## 📖 **Table of Contents**

1. [Getting Started](#-getting-started)
2. [Installation & Setup](#-installation--setup)
3. [Using the Application](#-using-the-application)
4. [Production Deployment](#-production-deployment)
5. [Security & Monitoring](#-security--monitoring)
6. [Maintenance & Troubleshooting](#-maintenance--troubleshooting)

---

## 🎯 **Getting Started**

### **What is AWS MCP Agent?**
AWS MCP Agent is an intelligent assistant that helps you manage your AWS infrastructure using natural language. It connects to your AWS accounts through secure SSO authentication and provides real-time access to AWS services and documentation.

### **Key Capabilities**
- 🔍 **Query AWS Resources** - List EC2 instances, S3 buckets, IAM roles, and more
- 🛠️ **Manage Infrastructure** - Create, modify, and delete AWS resources
- 📚 **Access Documentation** - Search and read AWS documentation instantly
- 🔐 **Secure Authentication** - Enterprise-grade SSO integration
- 🌍 **Multi-language Support** - Available in English and French

### **System Requirements**
- **Python**: 3.8 or higher
- **Memory**: 1GB RAM (minimum), 2GB recommended
- **Storage**: 500MB free space
- **Network**: Active internet connection
- **AWS**: CLI installed and configured
- **Dependencies**: `uvx` package manager for MCP servers

---

## 🔧 **Installation & Setup**

### **Quick Start Installation**

#### **Step 1: Clone and Setup**
```bash
# Clone the repository
git clone <repository-url>
cd mcp-chatbot

# Make scripts executable
chmod +x setup.sh run.sh run_tests.py

# Run automated setup
./setup.sh
```

#### **Step 2: Configure Environment**
```bash
# Copy environment template
cp .env.template .env

# Edit configuration
nano .env
```

**Environment Configuration:**
```bash
# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
TEMPERATURE=0.0
TOP_P=0.5

# AWS Configuration (optional - SSO preferred)
AWS_REGION=ca-central-1
```

#### **Step 3: Test Installation**
```bash
# Run comprehensive test suite
python3 run_tests.py

# Expected output: "🎉 All tests passed! Ready for production."
```

### **AWS SSO Configuration**

#### **Option A: Web Interface (Recommended)**
1. Launch the application: `./run.sh`
2. Open browser to: **http://localhost:8501**
3. Click **"➕ Add New Profile"** tab
4. Fill in your organization's SSO details:

**Example Configuration:**
```
Profile Name: my-company-prod
SSO Start URL: https://d-1234567890.awsapps.com/start
SSO Region: us-east-1
AWS Account ID: 123456789012
SSO Role Name: AWSAdministratorAccess
Default Region: us-east-1
```

5. Click **"🔧 Configure SSO Profile"**
6. Follow authentication flow

#### **Option B: AWS CLI**
```bash
# Configure SSO profile
aws configure sso

# Test SSO login
aws sso login --profile your-profile-name

# Verify credentials
aws sts get-caller-identity --profile your-profile-name
```

### **First Authentication**
1. Select your profile from the dropdown
2. Click **"🔐 Login with SSO"**
3. Complete authentication in your browser
4. Return to the application - you're ready to go!

---

## 💬 **Using the Application**

### **Interface Overview**

#### **Sidebar Layout**
```
┌─────────────────┐
│ 🔍 Debug Info   │ ← Toggle for development info
├─────────────────┤
│ 🔐 Auth Status  │ ← Current profile and account
├─────────────────┤
│ 📡 MCP Servers  │ ← Server connection status
├─────────────────┤
│ 🛠️ Tools        │ ← Available AWS operations
├─────────────────┤
│ 🎛️ Controls     │ ← Clear chat, restart app
└─────────────────┘
```

#### **Main Chat Area**
- **Clean interface** focused on conversation
- **Message history** preserved during session
- **Real-time responses** from AWS services
- **Error handling** with helpful suggestions

### **Basic Commands**

#### **List Resources**
```
"show me my EC2 instances"
"list my S3 buckets"
"what IAM roles do I have?"
"show me my Lambda functions"
"list my VPCs"
```

#### **Get Resource Details**
```
"describe instance i-1234567890abcdef0"
"show me details for bucket my-bucket-name"
"what permissions does role MyRole have?"
"show me the configuration of VPC vpc-12345"
```

#### **Create Resources**
```
"create an S3 bucket called my-new-bucket"
"launch a t2.micro EC2 instance"
"create a new IAM role for Lambda"
"create a VPC with CIDR 10.0.0.0/16"
```

#### **Modify Resources**
```
"add versioning to bucket my-bucket"
"stop instance i-1234567890abcdef0"
"attach policy AmazonS3ReadOnlyAccess to role MyRole"
"modify security group sg-12345 to allow port 443"
```

#### **Delete Resources**
```
"delete bucket my-old-bucket"
"terminate instance i-1234567890abcdef0"
"delete VPC vpc-12345"
"remove IAM role MyOldRole"
```

### **Documentation Queries**
```
"how do I configure VPC peering?"
"show me S3 encryption best practices"
"find Lambda deployment documentation"
"search for CloudFormation examples"
"what are the EC2 instance types?"
```

### **Multi-language Support**
The agent supports both English and French:

**French Examples:**
```
"liste mes instances EC2"
"créé un bucket S3 avec versioning"
"supprime le VPC vpc-12345"
"montre-moi mes rôles IAM"
```

### **Debug and Monitoring**

#### **Debug Information**
Enable debug mode to see:
- **Live system status** - MCP servers, tools, connections
- **Request details** - Your questions and commands
- **Tool calls** - AWS operations being executed
- **Raw responses** - Complete AI agent responses
- **Performance metrics** - Response times and errors

#### **Using Debug Mode**
1. Check **"Show Debug Details"** in the sidebar
2. Enable **"Auto-refresh debug info"** for live updates
3. Review debug history for troubleshooting
4. Use **"Clear Debug"** to reset information

### **Profile Management**

#### **Multiple Profiles**
Configure multiple AWS SSO profiles for different:
- **Organizations** - Different companies or departments
- **Environments** - Development, staging, production
- **Accounts** - Different AWS accounts
- **Roles** - Different permission levels

#### **Switching Profiles**
1. Select different profile from dropdown
2. Click **"🔐 Login with SSO"** if needed
3. Verify authentication status
4. Start using the new profile

#### **Profile Actions**
- **🔄 Refresh** - Update authentication status
- **🚪 Logout** - Sign out and return to login screen
- **🗑️ Remove Profile** - Delete profile configuration

---

## 🌐 **Production Deployment**

### **Deployment Options**

#### **Option 1: Local Development**
```bash
# Start the application
./run.sh

# Access at http://localhost:8501
```

#### **Option 2: Server Deployment**
```bash
# Install on server
git clone <repository-url>
cd mcp-chatbot
./setup.sh

# Configure environment
cp .env.template .env
# Edit .env with production settings

# Run with custom port
streamlit run src/app.py --server.port 8080 --server.address 0.0.0.0
```

#### **Option 3: Docker Deployment**
```dockerfile
# Dockerfile (create this file)
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
RUN pip install uvx

EXPOSE 8501

CMD ["streamlit", "run", "src/app.py", "--server.address", "0.0.0.0"]
```

```bash
# Build and run
docker build -t aws-mcp-agent .
docker run -p 8501:8501 -v ~/.aws:/root/.aws aws-mcp-agent
```

### **Production Configuration**

#### **Streamlit Production Settings**
```bash
# Configure Streamlit for production
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << 'EOF'
[server]
port = 8501
address = "0.0.0.0"
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
base = "light"
EOF
```

#### **System Optimization**
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize Python
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1
```

---

## 🔒 **Security & Monitoring**

### **Security Configuration**

#### **Production Security Checklist**
- [ ] Use AWS SSO (never hardcode credentials)
- [ ] Configure proper IAM roles with least privilege
- [ ] Enable HTTPS in production
- [ ] Set up proper network security groups
- [ ] Configure logging and monitoring
- [ ] Regular security updates

#### **IAM Permissions**
Create an IAM policy with appropriate permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "ec2:Describe*",
                "s3:List*",
                "s3:Get*",
                "iam:List*",
                "iam:Get*",
                "lambda:List*",
                "lambda:Get*"
            ],
            "Resource": "*"
        }
    ]
}
```

#### **Network Security**
```bash
# For server deployment, configure firewall
sudo ufw allow 8501/tcp
sudo ufw enable

# For production, use reverse proxy
# nginx configuration example:
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### **Monitoring & Logging**

#### **Application Monitoring**
```bash
# Check application logs
tail -f logs/app.log

# Monitor system resources
htop

# Check MCP server status
ps aux | grep uvx
```

#### **Health Checks**
```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501)
if [ $response -eq 200 ]; then
    echo "✅ Application is healthy"
    exit 0
else
    echo "❌ Application is unhealthy (HTTP $response)"
    exit 1
fi
EOF

chmod +x health_check.sh
```

#### **Log Rotation**
```bash
# Configure logrotate
sudo cat > /etc/logrotate.d/aws-mcp-agent << 'EOF'
/path/to/mcp-chatbot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 user user
}
EOF
```

### **Backup & Recovery**

#### **Backup Strategy**
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/aws-mcp-agent"

mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    .env \
    config/ \
    ~/.aws/config \
    ~/.aws/credentials

# Backup logs (last 7 days)
find logs/ -name "*.log" -mtime -7 -exec cp {} $BACKUP_DIR/ \;

echo "✅ Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh
```

#### **Recovery Procedure**
```bash
# Restore from backup
tar -xzf config_backup.tar.gz

# Verify configuration
python3 run_tests.py

# Restart application
./run.sh
```

---

## 🔧 **Maintenance & Troubleshooting**

### **Regular Maintenance**

#### **Weekly Maintenance Tasks**
```bash
# Weekly maintenance script
cat > maintenance.sh << 'EOF'
#!/bin/bash
echo "🔧 Starting weekly maintenance..."

# Update MCP servers
uvx install --force awslabs.aws-api-mcp-server@latest
uvx install --force awslabs.aws-documentation-mcp-server@latest

# Clean up logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete

# Run health checks
python3 run_tests.py

# Backup configuration
./backup.sh

echo "✅ Maintenance completed"
EOF

chmod +x maintenance.sh

# Schedule with cron
echo "0 2 * * 0 /path/to/mcp-chatbot/maintenance.sh" | crontab -
```

#### **Update Procedure**
```bash
# Update application
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests
python3 run_tests.py

# Restart application
./run.sh
```

### **Troubleshooting**

#### **Common Issues**

##### **Application Won't Start**
**Symptoms:** Application fails to launch
**Solutions:**
```bash
# Check Python environment
python3 --version
which python3

# Check dependencies
pip list | grep streamlit
pip list | grep boto3

# Check ports
netstat -tlnp | grep 8501

# Check virtual environment
source venv/bin/activate
```

##### **Authentication Problems**
**Symptoms:** "Not authenticated" message
**Solutions:**
1. Click **"🔐 Login"** to re-authenticate
2. Check if your SSO session expired
3. Verify your profile configuration
4. Try refreshing the page

```bash
# Check AWS configuration
aws configure list
aws sts get-caller-identity

# Check SSO status
aws sso login --profile your-profile

# Verify Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

##### **MCP Server Issues**
**Symptoms:** Tools not available or server errors
**Solutions:**
```bash
# Check uvx installation
uvx --version

# Reinstall MCP servers
uvx install --force awslabs.aws-api-mcp-server@latest
uvx install --force awslabs.aws-documentation-mcp-server@latest

# Check server processes
ps aux | grep uvx
```

##### **Command Not Working**
**Symptoms:** Error messages or unexpected responses
**Solutions:**
1. Enable debug mode to see details
2. Check if you have necessary permissions
3. Verify resource names and IDs
4. Try rephrasing your request

##### **Slow Responses**
**Symptoms:** Long wait times for responses
**Solutions:**
1. Check your internet connection
2. Verify AWS service status
3. Try simpler commands first
4. Check debug timing information

#### **Debug Mode**
```bash
# Enable debug logging
export STREAMLIT_LOGGER_LEVEL=debug

# Run with verbose output
streamlit run src/app.py --logger.level debug
```

### **Best Practices**

#### **Security**
- ✅ **Use SSO authentication** - Never share credentials
- ✅ **Regular logout** - Especially on shared computers
- ✅ **Least privilege** - Use roles with minimal required permissions
- ✅ **Monitor activity** - Review debug logs for unusual activity

#### **Efficient Usage**
- ✅ **Be specific** - Include resource IDs when possible: `"stop instance i-1234567890abcdef0"`
- ✅ **Use regions** - Specify regions for cross-region operations: `"list EC2 instances in us-west-2"`
- ✅ **Batch operations** - Group related commands together: `"list all my VPCs and their subnets"`
- ✅ **Check documentation** - Use built-in doc search for guidance

#### **Troubleshooting**
- ✅ **Enable debug mode** - For detailed operation information
- ✅ **Check authentication** - Verify profile status regularly
- ✅ **Review errors** - Debug panel shows complete error context
- ✅ **Clear chat** - Reset conversation if needed

### **Common Use Cases**

#### **Infrastructure Monitoring**
```
"show me all running EC2 instances"
"what S3 buckets are using the most storage?"
"list all Lambda functions that haven't been used recently"
"show me security groups with open ports"
```

#### **Cost Management**
```
"show me my largest S3 buckets"
"list all running instances by type"
"what RDS instances do I have?"
"show me unused Elastic IPs"
```

#### **Security Auditing**
```
"list all IAM users with admin access"
"show me security groups allowing SSH from anywhere"
"what S3 buckets are publicly accessible?"
"list all IAM roles with cross-account trust"
```

#### **Development Support**
```
"create a development VPC"
"set up a Lambda function for testing"
"create an S3 bucket for application logs"
"configure a security group for web servers"
```

### **Getting Help**

#### **Support Resources**
1. **Check debug information** - Enable debug mode for details
2. **Review error messages** - Look for specific error codes
3. **Try simpler commands** - Start with basic list operations
4. **Check documentation** - Use built-in doc search
5. **Clear and restart** - Use controls to reset if needed

#### **Reporting Issues**
When reporting issues, include:
- Operating system and Python version
- Complete error messages
- Steps to reproduce
- Debug information from the application
- Test results (`python3 run_tests.py`)

---

## 💡 **Tips and Tricks**

### **Efficient Commands**
- Use **resource IDs** for specific operations
- Specify **regions** when needed
- Use **filters** for large results
- Try **different phrasings** if commands don't work

### **Documentation Search**
- Be **specific**: `"S3 bucket encryption options"` vs `"S3 encryption"`
- Use **service names**: `"Lambda environment variables"` vs `"environment variables"`
- Try **different terms**: `"EC2 pricing"` and `"instance costs"`

### **Batch Operations**
- Group **related commands**
- Use **follow-up questions** after listing resources
- **Chain operations** when possible

### **Debugging**
- **Enable auto-refresh** for live monitoring during operations
- **Check timing** to identify slow operations
- **Review tool calls** to understand what's happening
- **Clear debug** regularly to avoid clutter

---

**🎉 Your AWS MCP Agent is now ready for both development and production use!**

This complete guide covers everything from initial setup to production deployment and ongoing maintenance. Start with simple commands and gradually explore more complex operations as you become familiar with the interface.

For the latest updates and community support, visit the [GitHub repository](https://github.com/your-repo).
