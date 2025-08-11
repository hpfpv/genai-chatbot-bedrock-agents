"""MCP server configuration using official AWS Labs MCP servers."""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue without it
    pass


@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server."""
    
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    working_dir: Optional[str] = None
    timeout: int = 30
    auto_approve: List[str] = field(default_factory=list)
    disabled: bool = False


@dataclass
class MCPConfig:
    """Configuration for official AWS Labs MCP servers with Python fallback."""
    
    servers: Dict[str, MCPServerConfig] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize official AWS Labs MCP server configurations."""
        self._setup_official_aws_labs_servers()
        self._setup_python_fallback_servers()
    
    def _setup_official_aws_labs_servers(self):
        """Setup official AWS Labs MCP server configurations."""
        
        # Check if we should prioritize reliable servers
        prioritize_reliable = os.getenv("PRIORITIZE_RELIABLE_SERVERS", "true").lower() == "true"
        
        # AWS API MCP Server - Main server for AWS operations
        self.servers["aws-api"] = MCPServerConfig(
            name="aws-api",
            command="uvx",
            args=["awslabs.aws-api-mcp-server@latest"],
            env={
                "AWS_REGION": os.getenv("AWS_REGION", "ca-central-1"),
                "AWS_API_MCP_PROFILE_NAME": os.getenv("AWS_PROFILE", ""),
                "AWS_API_MCP_WORKING_DIR": os.getenv("AWS_API_MCP_WORKING_DIR", "/tmp"),
            },
            timeout=30,  # Increased timeout for pre-installed servers
            auto_approve=[
                "ec2:DescribeInstances",
                "ec2:StartInstances", 
                "ec2:StopInstances",
                "s3:ListBuckets",
                "s3:GetBucketLocation",
                "s3:ListObjects",
                "iam:ListUsers",
                "iam:GetUser",
                "cloudformation:ListStacks",
                "cloudformation:DescribeStacks",
                "rds:DescribeDBInstances",
                "lambda:ListFunctions",
                "ec2:DescribeVpcs",
                "ec2:DescribeSubnets",
                "ec2:DescribeSecurityGroups"
            ],
            disabled=prioritize_reliable  # Disable by default if prioritizing reliable servers
        )
        
        # AWS Documentation MCP Server - For searching AWS docs
        self.servers["aws-docs"] = MCPServerConfig(
            name="aws-docs",
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server@latest"],
            env={
                "AWS_REGION": os.getenv("AWS_REGION", "ca-central-1"),
            },
            timeout=20,  # Increased timeout for pre-installed servers
            auto_approve=["*"],
            disabled=prioritize_reliable  # Disable by default if prioritizing reliable servers
        )
        
        # AWS Pricing MCP Server - For cost information
        if os.getenv("ENABLE_AWS_PRICING", "false").lower() == "true":
            self.servers["aws-pricing"] = MCPServerConfig(
                name="aws-pricing",
                command="uvx",
                args=["awslabs.aws-pricing-mcp-server@latest"],
                env={
                    "AWS_REGION": os.getenv("AWS_REGION", "ca-central-1"),
                },
                timeout=15,  # Shorter timeout to prevent hanging
                auto_approve=["*"],
                disabled=prioritize_reliable  # Disable by default if prioritizing reliable servers
            )
    
    def _setup_python_fallback_servers(self):
        """Setup reliable Python-based fallback servers."""
        
        # Get the absolute path to the project root directory
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        src_dir = os.path.join(project_root, "src")
        
        # Python AWS Tools Server (fallback)
        self.servers["aws-tools-python"] = MCPServerConfig(
            name="aws-tools-python",
            command="python",
            args=[os.path.join(src_dir, "mcp_servers", "aws_tools", "server.py")],
            env={
                "AWS_REGION": os.getenv("AWS_REGION", "ca-central-1"),
                "AWS_PROFILE": os.getenv("AWS_PROFILE", ""),
                "PYTHONPATH": src_dir,
            },
            working_dir=project_root,
            auto_approve=[
                "aws:ec2:describe_instances",
                "aws:s3:list_buckets",
                "aws:iam:list_users",
                "aws:cloudformation:list_stacks"
            ],
            disabled=False  # Always enabled for reliability
        )
        
        # System Tools Server
        self.servers["system-tools"] = MCPServerConfig(
            name="system-tools",
            command="python",
            args=[os.path.join(src_dir, "mcp_servers", "system_tools", "server.py")],
            env={
                "PYTHONPATH": src_dir,
            },
            working_dir=project_root,
            auto_approve=[
                "system:get_info",
                "system:list_processes",
                "system:get_disk_usage"
            ],
            disabled=False  # Always enabled
        )
    
    def enable_fallback_servers(self):
        """Enable fallback servers when official servers fail."""
        if "aws-tools-python" in self.servers:
            self.servers["aws-tools-python"].disabled = False
    
    def add_server(self, server_config: MCPServerConfig):
        """Add a new MCP server configuration."""
        self.servers[server_config.name] = server_config
    
    def remove_server(self, name: str):
        """Remove an MCP server configuration."""
        if name in self.servers:
            del self.servers[name]
    
    def get_server(self, name: str) -> Optional[MCPServerConfig]:
        """Get MCP server configuration by name."""
        return self.servers.get(name)
    
    def get_enabled_servers(self) -> Dict[str, MCPServerConfig]:
        """Get all enabled MCP server configurations."""
        return {
            name: config 
            for name, config in self.servers.items() 
            if not config.disabled
        }
    
    def to_mcp_client_config(self) -> Dict[str, Any]:
        """Convert to MCP client configuration format."""
        config = {"mcpServers": {}}
        
        for name, server_config in self.get_enabled_servers().items():
            config["mcpServers"][name] = {
                "command": server_config.command,
                "args": server_config.args,
                "env": server_config.env,
            }
            
            if server_config.working_dir:
                config["mcpServers"][name]["cwd"] = server_config.working_dir
            
            if server_config.auto_approve:
                config["mcpServers"][name]["autoApprove"] = server_config.auto_approve
        
        return config
    
    @classmethod
    def from_env(cls) -> "MCPConfig":
        """Create MCP configuration from environment variables."""
        return cls()
