# Example Configuration for AWS Bedrock Chatbot
# This file shows example values - copy to config.py and customize

import os

# AWS Configuration
AWS_PROFILE = "default"  # Your AWS CLI profile name
AWS_DEFAULT_REGION = "us-east-1"  # Your preferred AWS region
BEDROCK_MODEL_ID = "anthropic.claude-v2"  # Available models: anthropic.claude-v2, anthropic.claude-instant-v1

# Optional: If using assume role (uncomment and configure)
# BEDROCK_ASSUME_ROLE = "arn:aws:iam::123456789012:role/BedrockRole"

# Optional: SerpAPI key for web search functionality
# Get your free API key from https://serpapi.com/
# SERPAPI_API_KEY = "your_serpapi_key_here"

# Model Parameters
TEMPERATURE = 0.0  # Controls randomness (0.0 = deterministic, 1.0 = very random)
TOP_P = 0.5  # Controls diversity (0.1 = focused, 1.0 = diverse)
MAX_TOKENS = 2000  # Maximum tokens in response

def set_environment():
    """Set environment variables from configuration"""
    os.environ["AWS_PROFILE"] = AWS_PROFILE
    os.environ["AWS_DEFAULT_REGION"] = AWS_DEFAULT_REGION
    
    # Set SerpAPI key if available
    if 'SERPAPI_API_KEY' in globals() and SERPAPI_API_KEY != "your_serpapi_key_here":
        os.environ["SERPAPI_API_KEY"] = SERPAPI_API_KEY
    
    # Set assume role if configured
    if 'BEDROCK_ASSUME_ROLE' in globals():
        os.environ["BEDROCK_ASSUME_ROLE"] = BEDROCK_ASSUME_ROLE
