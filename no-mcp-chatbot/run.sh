#!/bin/bash

# AWS Bedrock Chatbot Run Script
echo "🤖 Starting AWS Bedrock Chatbot..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the no-mcp-chatbot directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if configuration exists
if [ ! -f "config.py" ]; then
    echo "❌ Configuration file not found. Please copy config.py.template to config.py and configure it."
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."
python3 -c "import streamlit, boto3, langchain" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

# Check AWS credentials
echo "☁️ Checking AWS credentials..."
if ! python3 -c "import boto3; boto3.Session().get_credentials()" 2>/dev/null; then
    echo "⚠️  AWS credentials not found or invalid"
    echo "   Please configure AWS credentials:"
    echo "   - aws configure"
    echo "   - aws configure sso"
    echo "   - or set environment variables"
    echo ""
    echo "Continuing anyway (you can configure in the app)..."
fi

echo ""
echo "🚀 Starting Streamlit application..."
echo "   Access the app at: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

# Start the application
streamlit run app.py
