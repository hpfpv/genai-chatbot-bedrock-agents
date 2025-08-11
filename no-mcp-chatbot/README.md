# 🤖 AWS Bedrock Chatbot with Custom Tools

A proof-of-concept AI-powered chatbot that demonstrates how to build custom AWS infrastructure management tools using Amazon Bedrock and LangChain. This project showcases the traditional approach of building custom tools for AI agents before the advent of standardized protocols like MCP.

> **Note**: This is a demonstration project showing the custom tool approach. For production use, consider the modern MCP-based implementation in the companion `mcp-chatbot` project.

## ✨ **Features**

- 🧠 **Amazon Bedrock Integration** - Uses Claude models for natural language processing
- 🛠️ **Custom AWS Tools** - Hand-built functions for EC2 and S3 management
- 🌐 **Streamlit Web Interface** - User-friendly chat interface
- 🔍 **Web Search** - Optional SerpAPI integration for current events
- 🇫🇷 **French Language Support** - Interface and responses in French
- 🔧 **LangChain Framework** - Traditional agent-tool architecture

## 🏗️ **Architecture**

```
User Input → Streamlit UI → LangChain Agent → Custom Tools → AWS APIs → Response
```

### **Custom Tools Included:**
- **EC2 Management**: List, start, stop instances by tag or ID
- **S3 Operations**: List buckets and basic operations
- **Web Search**: Current events and general information (optional)

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8 or higher
- AWS CLI installed and configured
- AWS Bedrock access enabled
- (Optional) SerpAPI account for web search

### **Installation**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd no-mcp-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your settings**
   ```bash
   cp config.py.template config.py
   # Edit config.py with your AWS profile and preferences
   ```

4. **Set up AWS credentials**
   ```bash
   aws configure
   # Or use AWS SSO: aws configure sso
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   Navigate to: http://localhost:8501

## ⚙️ **Configuration**

### **Basic Configuration**
Edit `config.py` with your settings:

```python
# AWS Configuration
AWS_PROFILE = "your-aws-profile"  # Your AWS CLI profile
AWS_DEFAULT_REGION = "us-east-1"  # Your preferred region
BEDROCK_MODEL_ID = "anthropic.claude-v2"  # Bedrock model

# Model Parameters
TEMPERATURE = 0.0
TOP_P = 0.5
MAX_TOKENS = 2000

# Optional: SerpAPI for web search
SERPAPI_API_KEY = "your-serpapi-key"  # Get from https://serpapi.com/
```

### **AWS Permissions**
Your AWS profile needs permissions for:
- `bedrock:InvokeModel`
- `ec2:Describe*`, `ec2:Start*`, `ec2:Stop*`
- `s3:List*`, `s3:Get*`

Example IAM policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "ec2:DescribeInstances",
                "ec2:StartInstances",
                "ec2:StopInstances",
                "s3:ListAllMyBuckets",
                "s3:ListBucket"
            ],
            "Resource": "*"
        }
    ]
}
```

## 💬 **Usage Examples**

### **EC2 Management**
```
"liste mes instances EC2"
"démarre l'instance i-1234567890abcdef0"
"arrête toutes les instances avec le tag Environment"
"montre-moi les instances en cours d'exécution"
```

### **S3 Operations**
```
"liste mes buckets S3"
"montre-moi les détails du bucket mon-bucket"
```

### **General Queries**
```
"qu'est-ce qu'Amazon EC2?"
"comment configurer un VPC?"
"recherche des informations sur AWS Lambda"
```

## 🛠️ **Development**

### **Project Structure**
```
no-mcp-chatbot/
├── app.py                 # Main Streamlit application
├── config.py.template     # Configuration template
├── requirements.txt       # Python dependencies
├── agents/
│   ├── bedrock.py        # Bedrock integration and agent setup
│   └── tools.py          # Custom tool definitions
├── functions/
│   ├── ec2.py           # EC2 operations
│   └── s3.py            # S3 operations
├── utils/
│   ├── bedrock.py       # Bedrock utilities
│   └── setup.py         # Setup utilities
└── images/              # UI icons and assets
```

### **Adding Custom Tools**

1. **Create the function** in `functions/`:
   ```python
   def my_custom_function(parameter):
       # Your AWS operation here
       return result
   ```

2. **Create the tool wrapper** in `agents/tools.py`:
   ```python
   class tool_my_custom_function(BaseTool):
       name = "my_custom_function"
       description = "Description of what this tool does"
       
       def _run(self, parameter: str):
           return my_custom_function(parameter)
   ```

3. **Add to agent** in `agents/bedrock.py`:
   ```python
   tools.append(tool_my_custom_function())
   ```

### **Customizing the Interface**

The Streamlit interface can be customized in `app.py`:
- Modify the header and styling
- Add new sidebar components
- Change the chat message format
- Add new UI elements

## 🔍 **Troubleshooting**

### **Common Issues**

#### **"Configuration file not found"**
- Copy `config.py.template` to `config.py`
- Update with your AWS profile and settings

#### **"Unable to locate credentials"**
- Run `aws configure` to set up credentials
- Or use `aws configure sso` for SSO authentication
- Verify with `aws sts get-caller-identity`

#### **"Access denied" errors**
- Check your IAM permissions
- Ensure Bedrock access is enabled in your region
- Verify your AWS profile has the necessary permissions

#### **"Model not found" errors**
- Ensure you have access to the specified Bedrock model
- Check if the model is available in your region
- Try a different model ID in your configuration

#### **Slow responses**
- Check your internet connection
- Verify AWS service status
- Consider using a different Bedrock model
- Check if you're hitting API rate limits

### **Debug Mode**
Enable verbose logging by setting `verbose=True` in the agent configuration:
```python
react_agent = initialize_agent(
    tools, 
    llm, 
    verbose=True,  # Enable debug output
    # ... other parameters
)
```

## 📚 **Learning Resources**

This project demonstrates several key concepts:

### **LangChain Framework**
- Agent-tool architecture
- Memory management
- Custom tool creation
- Prompt engineering

### **Amazon Bedrock**
- Model invocation
- Parameter tuning
- Error handling
- Cost optimization

### **AWS Integration**
- Boto3 SDK usage
- IAM permissions
- Service-specific APIs
- Error handling

### **Streamlit Development**
- Session state management
- UI component creation
- Real-time updates
- User interaction handling

## 🔄 **Migration to MCP**

This project represents the "before" state of AI-tool integration. For comparison, see the `mcp-chatbot` project which demonstrates:

- **Standardized protocols** instead of custom tools
- **Official AWS integrations** instead of hand-built functions
- **Reduced maintenance** through community-maintained servers
- **Enhanced capabilities** with built-in documentation access

## 🤝 **Contributing**

This is a demonstration project, but contributions are welcome:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### **Areas for Improvement**
- Add more AWS service integrations
- Improve error handling
- Add unit tests
- Enhance the UI
- Add more language support

## 📄 **License**

This project is provided as-is for educational and demonstration purposes. Use at your own risk in production environments.
