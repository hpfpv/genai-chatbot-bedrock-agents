#!/bin/bash

# AWS MCP Agent Setup Script
# Sets up the environment for official AWS Labs MCP servers integration

echo "🔧 AWS MCP Agent Setup"
echo "======================"
echo ""

# Check Python version
echo "🐍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

# Check if uvx is available
echo "📦 Checking uvx (for official MCP servers)..."
if command -v uvx &> /dev/null; then
    UVX_VERSION=$(uvx --version 2>/dev/null || echo "unknown")
    echo "✅ uvx available: $UVX_VERSION"
else
    echo "⚠️  uvx not found. Install with: pip install uv"
    echo "   uvx is needed for official AWS Labs MCP servers"
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

# Install core dependencies
echo "📦 Installing core dependencies..."
pip install streamlit boto3 python-dotenv

# Install MCP dependencies (minimal set)
echo "📦 Installing MCP dependencies..."
pip install mcp

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Configure AWS credentials: aws configure"
echo "2. (Optional) Pre-install MCP servers: ./scripts/setup-official-mcp-servers.sh"
echo "3. Start the application: ./run.sh"
echo ""
echo "🚀 Your AWS MCP Agent is ready to use!"
