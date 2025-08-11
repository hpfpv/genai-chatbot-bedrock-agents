"""
Unit tests for core components
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.app_config import AppConfig
from config.mcp_config import MCPConfig
from core.isolated_mcp_client import IsolatedMCPClient
from core.agent import SimpleAgent


class TestAppConfig(unittest.TestCase):
    """Test AppConfig functionality."""
    
    def test_app_config_creation(self):
        """Test AppConfig can be created."""
        config = AppConfig.from_env()
        self.assertIsInstance(config, AppConfig)
        self.assertTrue(hasattr(config, 'bedrock_model_id'))
        self.assertTrue(hasattr(config, 'temperature'))
        self.assertTrue(hasattr(config, 'top_p'))
    
    def test_app_config_defaults(self):
        """Test AppConfig has reasonable defaults."""
        config = AppConfig.from_env()
        self.assertIsNotNone(config.bedrock_model_id)
        self.assertGreaterEqual(config.temperature, 0.0)
        self.assertLessEqual(config.temperature, 1.0)
        self.assertGreaterEqual(config.top_p, 0.0)
        self.assertLessEqual(config.top_p, 1.0)


class TestMCPConfig(unittest.TestCase):
    """Test MCPConfig functionality."""
    
    def test_mcp_config_creation(self):
        """Test MCPConfig can be created."""
        config = MCPConfig.from_env()
        self.assertIsInstance(config, MCPConfig)
        self.assertTrue(hasattr(config, 'servers'))
    
    def test_mcp_config_servers(self):
        """Test MCPConfig has configured servers."""
        config = MCPConfig.from_env()
        self.assertIsInstance(config.servers, dict)
        self.assertGreater(len(config.servers), 0)
        
        # Check for expected servers
        expected_servers = ['aws-api', 'aws-docs']
        for server in expected_servers:
            self.assertIn(server, config.servers)


class TestIsolatedMCPClient(unittest.TestCase):
    """Test IsolatedMCPClient functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = MCPConfig.from_env()
        self.client = IsolatedMCPClient(self.config)
    
    def test_client_creation(self):
        """Test MCP client can be created."""
        self.assertIsInstance(self.client, IsolatedMCPClient)
        self.assertEqual(self.client.config, self.config)
        self.assertIsInstance(self.client.tools, dict)
    
    def test_client_properties(self):
        """Test MCP client properties."""
        self.assertTrue(hasattr(self.client, 'servers_count'))
        self.assertTrue(hasattr(self.client, 'get_server_status'))
        self.assertIsInstance(self.client.servers_count, int)
    
    def test_server_status(self):
        """Test server status functionality."""
        status = self.client.get_server_status()
        self.assertIsInstance(status, dict)


class TestSimpleAgent(unittest.TestCase):
    """Test SimpleAgent functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app_config = AppConfig.from_env()
        self.mcp_config = MCPConfig.from_env()
        self.mcp_client = IsolatedMCPClient(self.mcp_config)
        
        # Mock AWS session
        self.mock_session = Mock()
        
        self.agent = SimpleAgent(
            self.app_config,
            self.mcp_client,
            self.mock_session
        )
    
    def test_agent_creation(self):
        """Test agent can be created."""
        self.assertIsInstance(self.agent, SimpleAgent)
        self.assertEqual(self.agent.app_config, self.app_config)
        self.assertEqual(self.agent.mcp_client, self.mcp_client)
        self.assertEqual(self.agent.aws_session, self.mock_session)
    
    def test_agent_properties(self):
        """Test agent properties."""
        self.assertTrue(hasattr(self.agent, 'conversation_history'))
        self.assertTrue(hasattr(self.agent, '_initialized'))
        self.assertTrue(hasattr(self.agent, '_last_tool_calls'))
        self.assertIsInstance(self.agent.conversation_history, list)
        self.assertIsInstance(self.agent._last_tool_calls, list)
    
    @patch('core.agent.boto3')
    def test_agent_initialization(self, mock_boto3):
        """Test agent initialization."""
        # Mock Bedrock client
        mock_bedrock = Mock()
        mock_boto3.Session.return_value.client.return_value = mock_bedrock
        
        # Test initialization doesn't raise errors
        try:
            import asyncio
            asyncio.run(self.agent.initialize())
            self.assertTrue(True)  # If we get here, no exception was raised
        except Exception as e:
            self.fail(f"Agent initialization failed: {e}")


if __name__ == '__main__':
    unittest.main()
