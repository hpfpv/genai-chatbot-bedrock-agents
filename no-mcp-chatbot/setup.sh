#!/bin/bash

# AWS Bedrock Chatbot Setup Script
echo "🤖 AWS Bedrock Chatbot with Custom Tools - Setup"
echo "================================================"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the no-mcp-chatbot directory"
    exit 1
fi

# Create virtual environment
echo ""
echo "🔧 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check for configuration file
echo ""
echo "⚙️ Checking configuration..."
if [ ! -f "config.py" ]; then
    echo "📝 Creating configuration file from template..."
    cp config.py.template config.py
    echo "✅ Configuration file created: config.py"
    echo ""
    echo "⚠️  IMPORTANT: Please edit config.py with your AWS settings before running the app!"
    echo "   - Set your AWS_PROFILE"
    echo "   - Configure your AWS_DEFAULT_REGION"
    echo "   - (Optional) Add your SERPAPI_API_KEY for web search"
else
    echo "✅ Configuration file already exists"
fi

# Check AWS CLI
echo ""
echo "☁️ Checking AWS CLI..."
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1 | cut -d/ -f2 | cut -d' ' -f1)
    echo "✅ AWS CLI version: $AWS_VERSION"
    
    # Check if AWS is configured
    if aws sts get-caller-identity &> /dev/null; then
        ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
        USER_ARN=$(aws sts get-caller-identity --query Arn --output text 2>/dev/null)
        echo "✅ AWS credentials configured"
        echo "   Account: $ACCOUNT_ID"
        echo "   Identity: $USER_ARN"
    else
        echo "⚠️  AWS credentials not configured"
        echo "   Run: aws configure"
        echo "   Or: aws configure sso"
    fi
else
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
fi

# Check Bedrock access
echo ""
echo "🧠 Checking Bedrock access..."
if command -v aws &> /dev/null && aws sts get-caller-identity &> /dev/null; then
    if aws bedrock list-foundation-models --region us-east-1 &> /dev/null; then
        echo "✅ Bedrock access confirmed"
    else
        echo "⚠️  Bedrock access not confirmed"
        echo "   Make sure Bedrock is enabled in your AWS account"
        echo "   Check your region and IAM permissions"
    fi
else
    echo "⚠️  Cannot check Bedrock access (AWS not configured)"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit config.py with your AWS settings"
echo "2. Ensure AWS credentials are configured"
echo "3. Run the application: streamlit run app.py"
echo ""
echo "🚀 Your AWS Bedrock Chatbot is ready to use!"
echo ""
echo "Need help? Check the README.md for detailed instructions."
