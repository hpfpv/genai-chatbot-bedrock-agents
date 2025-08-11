#!/bin/bash

# AWS MCP Agent with SSO Authentication
# Enhanced startup script with Python launcher

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "🚀 AWS MCP Agent with SSO Authentication"
echo "========================================"
echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    echo "   python -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check dependencies
echo "🔍 Checking dependencies..."
python -c "import streamlit, boto3, asyncio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

# Check AWS SSO profiles
echo "🔐 Checking AWS SSO profiles..."
PYTHONPATH="$SCRIPT_DIR/src" python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    from auth.aws_sso_auth import AWSSSOAuthenticator

    sso_auth = AWSSSOAuthenticator()
    profiles = sso_auth.get_available_sso_profiles()

    if not profiles:
        print('❌ No SSO profiles found. Please configure AWS SSO first:')
        print('   aws configure sso')
        exit(1)

    print(f'✅ Found {len(profiles)} SSO profiles')

    # Check for authenticated profiles
    authenticated = []
    for name, info in profiles.items():
        if sso_auth.is_profile_authenticated(name):
            authenticated.append(name)

    if authenticated:
        print(f'✅ {len(authenticated)} profiles already authenticated:')
        for profile in authenticated:
            print(f'   - {profile}')
    else:
        print('⚠️  No profiles currently authenticated')
        print('   You can authenticate through the web interface')
except ImportError as e:
    print(f'❌ Import error: {e}')
    print('Please check your Python environment')
    exit(1)
"

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "📦 Checking MCP servers..."

# Check if uvx is available
if ! command -v uvx &> /dev/null; then
    echo "❌ uvx not found. Please install it first:"
    echo "   pip install uvx"
    exit 1
fi

echo "✅ uvx found"

echo ""
echo "🎯 Starting application with Python launcher..."
echo "   - AWS SSO authentication enabled"
echo "   - Official AWS Labs MCP servers"
echo "   - Enhanced logging and debugging"
echo "   - Web interface: http://localhost:8501"
echo ""

# Use the Python launcher for better module handling
python3 launch_app.py

echo ""
echo "👋 Application stopped"
