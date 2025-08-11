"""Application configuration settings."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppConfig:
    """Application configuration settings."""
    
    # AWS Configuration
    aws_profile: str = "bedrock-agent"
    aws_region: str = "ca-central-1"  # Default to Canada Central
    bedrock_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    
    # UI Configuration
    app_title: str = "Votre chatbot d'infrastructure intelligent"
    user_icon_path: str = "assets/images/user-icon.png"
    ai_icon_path: str = "assets/images/bedrock-icon.png"
    
    # Model Configuration
    temperature: float = 0.0
    top_p: float = 0.5
    max_tokens: int = 2000
    max_iterations: int = 5  # Increased from 2 to allow proper completion
    
    # Session Configuration
    memory_k: int = 5
    
    # External APIs
    serpapi_api_key: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Load configuration from environment variables."""
        self.aws_profile = os.getenv("AWS_PROFILE", self.aws_profile)
        self.aws_region = os.getenv("AWS_REGION", self.aws_region)
        self.bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", self.bedrock_model_id)
        self.serpapi_api_key = os.getenv("SERPAPI_API_KEY", self.serpapi_api_key)
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        
        # Validate region (simplified validation)
        valid_regions = [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'ca-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3',
            'eu-central-1', 'ap-southeast-1', 'ap-southeast-2',
            'ap-northeast-1', 'ap-northeast-2', 'ap-south-1'
        ]
        
        if self.aws_region not in valid_regions:
            print(f"Warning: '{self.aws_region}' may not be a recognized AWS region.")
        
        # Validate required configurations
        if not self.serpapi_api_key:
            print("Warning: SERPAPI_API_KEY not set. Web search functionality will be limited.")
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        return cls()
