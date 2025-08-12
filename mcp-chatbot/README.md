# 🤖 AWS MCP Agent - Modern Infrastructure Management

A next-generation AI-powered assistant that leverages the **Model Context Protocol (MCP)** and **official AWS Labs MCP servers** to provide seamless AWS infrastructure management through natural language. This project demonstrates the modern approach to AI-tool integration using standardized protocols.

> **Note**: This is the evolution of custom tool-based AI agents. For comparison with the traditional approach, see the companion `no-mcp-chatbot` project.

## ✨ **Features**

- 🔌 **Official AWS Labs MCP Servers** - Standardized AWS CLI and documentation access
- 🔐 **Enterprise AWS SSO Authentication** - Secure, multi-profile management
- **Amazon Bedrock Integration** - Advanced Claude models for natural language processing
- 🌐 **Professional Web Interface** - Enhanced Streamlit UI with real-time monitoring
- 🔍 **Live Debug Monitoring** - Real-time system status and operation tracking
- 🌍 **Multi-language Support** - English and French localization
- 📚 **Built-in Documentation Access** - Intelligent AWS documentation search and retrieval
- 🏗️ **Production-Ready Architecture** - Comprehensive testing, logging, and deployment guides

## 🏗️ **Architecture**

```
User Input → Enhanced Streamlit UI → Simple Agent → MCP Client → Official AWS MCP Servers → AWS Services
```

### **MCP Servers Included:**
- **aws-api**: Full AWS CLI operations and intelligent command suggestions
- **aws-docs**: AWS documentation search, best practices, and contextual help
- **Standardized Protocol**: No custom tool development required

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8 or higher
- AWS CLI installed and configured
- `uvx` package manager for MCP servers
- AWS SSO configured (recommended) or AWS credentials
- Internet connection for MCP server communication

### **Installation**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mcp-chatbot
   ```

2. **Run automated setup**
   ```bash
   ./setup.sh
   ```

3. **Configure environment (optional)**
   ```bash
   cp .env.template .env
   # Edit .env with your preferred settings
   ```

4. **Launch the application**
   ```bash
   ./run.sh
   ```

5. **Open your browser**
   Navigate to: **http://localhost:8501**

## ⚙️ **Configuration**

### **AWS SSO Setup (Recommended)**

#### **Option 1: Web Interface**
1. Launch the application
2. Click **"➕ Add New Profile"** tab
3. Fill in your organization's SSO details:

```
Profile Name: my-company-prod
SSO Start URL: https://d-1234567890.awsapps.com/start
SSO Region: us-east-1
AWS Account ID: 123456789012
SSO Role Name: AWSAdministratorAccess
Default Region: us-east-1
```

4. Click **"🔧 Configure SSO Profile"**
5. Complete authentication in your browser

#### **Option 2: AWS CLI**
```bash
# Configure SSO profile
aws configure sso

# Test authentication
aws sso login --profile your-profile-name
aws sts get-caller-identity --profile your-profile-name
```

### **Environment Configuration**
Create `.env` file for custom settings:
```bash
# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
TEMPERATURE=0.0
TOP_P=0.5

# AWS Configuration
AWS_REGION=us-east-1
```

### **AWS Permissions**
Your AWS profile needs permissions for:
- `bedrock:InvokeModel`
- `ec2:Describe*`, `s3:List*`, `iam:List*`, `lambda:List*`
- Any specific operations you want to perform

Example IAM policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "ec2:*",
                "s3:*",
                "iam:List*",
                "iam:Get*",
                "lambda:*"
            ],
            "Resource": "*"
        }
    ]
}
```

## 💬 **Usage Examples**

### **Infrastructure Management**
```
"show me my EC2 instances"
"list all S3 buckets with their sizes"
"what Lambda functions do I have?"
"describe the security group sg-12345"
"create a new VPC with CIDR 10.0.0.0/16"
```

### **Resource Operations**
```
"start instance i-1234567890abcdef0"
"stop all instances tagged Environment=dev"
"create an S3 bucket called my-new-bucket"
"delete the unused security group sg-67890"
"modify the Lambda function timeout to 5 minutes"
```

### **Documentation Queries**
```
"how do I configure VPC peering?"
"show me S3 encryption best practices"
"find CloudFormation examples for Lambda"
"what are the different EC2 instance types?"
"search for IAM policy examples"
```

### **Multi-language Support**
The agent supports both English and French:

**French Examples:**
```
"liste mes instances EC2"
"créé un bucket S3 avec versioning"
"montre-moi la documentation sur les VPC"
"supprime le groupe de sécurité sg-12345"
```

## 🎛️ **Interface Overview**

### **Main Features**
- **Clean Chat Interface** - Natural language interaction with AWS
- **SSO Profile Management** - Easy switching between AWS accounts/roles
- **Live Debug Monitoring** - Real-time system status and operation tracking
- **Multi-language Support** - Seamless language switching
- **Error Handling** - Comprehensive error messages with suggestions

### **Sidebar Components**
```
┌─────────────────┐
│ 🔐 Auth Status  │ ← Current profile and authentication
├─────────────────┤
│ 📡 MCP Servers  │ ← Server connection status
├─────────────────┤
│ 🛠️ Available Tools │ ← AWS operations and documentation
├─────────────────┤
│ 🔍 Debug Info   │ ← Live system monitoring
├─────────────────┤
│ 🎛️ Controls     │ ← Clear chat, restart, settings
└─────────────────┘
```

### **Debug and Monitoring**

#### **Real-time Information**
- **System Status** - MCP servers, connections, tool availability
- **Operation Tracking** - AWS API calls, response times, errors
- **Performance Metrics** - Tool usage statistics, success rates
- **Error Context** - Detailed error information with resolution suggestions

#### **Using Debug Mode**
1. Enable **"Show Debug Details"** in the sidebar
2. Turn on **"Auto-refresh debug info"** for live updates
3. Review operation history for troubleshooting
4. Use **"Clear Debug"** to reset monitoring data

## 🛠️ **Development**

### **Project Structure**
```
mcp-chatbot/
├── src/
│   ├── app.py                    # Main Streamlit application
│   ├── auth/
│   │   └── aws_sso_auth.py      # SSO authentication system
│   ├── core/
│   │   ├── agent.py             # Intelligent AWS agent
│   │   ├── isolated_mcp_client.py # MCP client implementation
│   │   ├── async_handler.py     # Async operation handler
│   │   └── logging_config.py    # Enhanced logging system
│   └── config/
│       ├── app_config.py        # Application configuration
│       └── mcp_config.py        # MCP server configuration
├── tests/                       # Comprehensive test suite
├── config/                      # Configuration files
├── setup.sh                     # Automated setup script
├── run.sh                       # Application launcher
├── run_tests.py                 # Test runner
└── requirements.txt             # Python dependencies
```

### **Key Components**

#### **Simple Agent** (`src/core/agent.py`)
- Direct Bedrock integration without LangChain complexity
- Context-aware processing and tool selection
- Intelligent response generation

#### **MCP Client** (`src/core/isolated_mcp_client.py`)
- Manages communication with official AWS MCP servers
- Process isolation and error recovery
- Performance monitoring and optimization

#### **SSO Authentication** (`src/auth/aws_sso_auth.py`)
- Web-based AWS SSO integration
- Multi-profile management
- Secure session handling

### **Adding Custom Functionality**

While the MCP approach reduces custom development, you can still extend functionality:

1. **Custom MCP Servers** - Create your own MCP servers for specialized operations
2. **Enhanced UI** - Modify the Streamlit interface in `src/app.py`
3. **Additional Authentication** - Extend the auth system for other providers
4. **Custom Agents** - Implement specialized agents for specific use cases

## 🧪 **Testing**

### **Run Test Suite**
```bash
# Run all tests
python3 run_tests.py

# Run specific test categories
python3 -m pytest tests/test_core.py -v
python3 -m pytest tests/test_integration.py -v
```

### **Test Coverage**
- ✅ **17 comprehensive tests** covering all major functionality
- ✅ **Unit tests** for core components (agent, MCP client, auth)
- ✅ **Integration tests** for end-to-end workflows
- ✅ **SSO authentication** validation and error handling
- ✅ **Configuration loading** and environment setup

## 🔍 **Troubleshooting**

### **Common Issues**

#### **MCP Servers Not Starting**
```bash
# Check uvx installation
uvx --version

# Reinstall MCP servers
uvx install --force awslabs.aws-api-mcp-server@latest
uvx install --force awslabs.aws-documentation-mcp-server@latest

# Check server processes
ps aux | grep uvx
```

#### **Authentication Problems**
- Click **"🔐 Login with SSO"** to re-authenticate
- Verify your SSO profile configuration
- Check if your SSO session expired
- Try refreshing the browser page

#### **AWS Permission Errors**
- Verify your IAM permissions match the required actions
- Check if Bedrock is enabled in your AWS region
- Ensure your SSO role has the necessary policies attached

#### **Slow Responses**
- Check your internet connection
- Verify AWS service status
- Monitor debug information for bottlenecks
- Consider using a different AWS region

### **Debug Mode**
Enable comprehensive debugging:
1. Turn on debug mode in the sidebar
2. Enable auto-refresh for live monitoring
3. Review tool calls and response times
4. Check error messages for specific issues

## 📚 **Learning Resources**

This project demonstrates several advanced concepts:

### **Model Context Protocol (MCP)**
- Standardized AI-tool integration
- Server-client architecture
- Protocol-based communication
- Community-maintained tool ecosystem

### **Modern AI Architecture**
- Agent-based design patterns
- Async/await programming
- Error handling and recovery
- Performance optimization

### **AWS Integration**
- SSO authentication flows
- Multi-account management
- Service-specific operations
- Documentation integration

### **Production Deployment**
- Comprehensive testing strategies
- Logging and monitoring
- Security best practices
- Scalable architecture patterns

## 🔄 **Comparison with Custom Tools**

This MCP-based approach offers significant advantages over custom tool development:

### **Development Efficiency**
- **Before**: 40+ hours for basic AWS operations
- **After**: 8 hours for full setup with comprehensive capabilities

### **Maintenance**
- **Before**: Manual updates for AWS API changes
- **After**: Automatic updates through official MCP servers

### **Scope**
- **Before**: Limited to implemented services
- **After**: Full AWS CLI + documentation access

### **Quality**
- **Before**: Custom error handling and edge cases
- **After**: Production-tested, community-maintained servers

## 🤝 **Contributing**

Contributions are welcome! This project follows modern development practices:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite: `python3 run_tests.py`
5. Submit a pull request

### **Areas for Improvments**
- Additional MCP server integrations
- Enhanced UI components
- More comprehensive testing
- Documentation improvements
- Performance optimizations

## 📄 **License**

This project is provided as-is for educational and demonstration purposes. Use at your own risk in production environments.
