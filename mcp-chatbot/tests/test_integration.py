"""
Integration tests for AWS MCP Agent
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import SimpleMCPApp
from auth.aws_sso_auth import AWSSSOAuthenticator


class TestSSOIntegration(unittest.TestCase):
    """Test SSO authentication integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sso_auth = AWSSSOAuthenticator()
    
    def test_sso_authenticator_creation(self):
        """Test SSO authenticator can be created."""
        self.assertIsInstance(self.sso_auth, AWSSSOAuthenticator)
        self.assertTrue(hasattr(self.sso_auth, 'get_available_sso_profiles'))
        self.assertTrue(hasattr(self.sso_auth, 'validate_sso_configuration'))
    
    def test_sso_profile_validation(self):
        """Test SSO profile validation."""
        # Test valid configuration
        valid_errors = self.sso_auth.validate_sso_configuration(
            'https://d-1234567890.awsapps.com/start',
            'ca-central-1',
            '123456789012',
            'AWSAdministratorAccess'
        )
        self.assertEqual(len(valid_errors), 0)
        
        # Test invalid configuration
        invalid_errors = self.sso_auth.validate_sso_configuration(
            'invalid-url',
            'invalid-region',
            '123',
            ''
        )
        self.assertGreater(len(invalid_errors), 0)
        self.assertIn('sso_start_url', invalid_errors)
        self.assertIn('sso_region', invalid_errors)
        self.assertIn('sso_account_id', invalid_errors)
        self.assertIn('sso_role_name', invalid_errors)
    
    def test_get_available_profiles(self):
        """Test getting available SSO profiles."""
        profiles = self.sso_auth.get_available_sso_profiles()
        self.assertIsInstance(profiles, dict)
        # Note: This may be empty in test environment, which is fine


class TestAppIntegration(unittest.TestCase):
    """Test main application integration."""
    
    @patch('streamlit.session_state', new_callable=dict)
    def test_app_creation(self, mock_session_state):
        """Test main app can be created."""
        # Mock session state
        mock_session_state.update({
            'messages': [],
            'debug_info': [],
            'show_debug': False,
            'authenticated': False
        })
        
        app = SimpleMCPApp()
        self.assertIsInstance(app, SimpleMCPApp)
        self.assertTrue(hasattr(app, 'app_config'))
        self.assertTrue(hasattr(app, 'mcp_config'))
        self.assertTrue(hasattr(app, 'sso_authenticator'))
    
    def test_app_components(self):
        """Test app components are properly initialized."""
        app = SimpleMCPApp()
        
        # Test config objects
        self.assertIsNotNone(app.app_config)
        self.assertIsNotNone(app.mcp_config)
        self.assertIsNotNone(app.sso_authenticator)
        
        # Test SSO authenticator
        self.assertIsInstance(app.sso_authenticator, AWSSSOAuthenticator)


class TestEndToEndFlow(unittest.TestCase):
    """Test end-to-end application flow."""
    
    def test_import_chain(self):
        """Test all imports work correctly."""
        try:
            # Test core imports
            from config.app_config import AppConfig
            from config.mcp_config import MCPConfig
            from core.isolated_mcp_client import IsolatedMCPClient
            from core.agent import SimpleAgent
            from core.async_handler import streamlit_async_handler
            from auth.aws_sso_auth import AWSSSOAuthenticator
            from app import SimpleMCPApp
            
            self.assertTrue(True)  # If we get here, all imports worked
        except ImportError as e:
            self.fail(f"Import failed: {e}")
    
    def test_configuration_chain(self):
        """Test configuration loading chain."""
        try:
            # Import here to avoid module-level import issues
            from config.app_config import AppConfig
            from config.mcp_config import MCPConfig
            from core.isolated_mcp_client import IsolatedMCPClient
            from core.agent import SimpleAgent
            
            # Load configurations
            app_config = AppConfig.from_env()
            mcp_config = MCPConfig.from_env()
            
            # Create MCP client
            mcp_client = IsolatedMCPClient(mcp_config)
            
            # Create agent (with mock session)
            mock_session = Mock()
            agent = SimpleAgent(app_config, mcp_client, mock_session)
            
            self.assertTrue(True)  # If we get here, configuration chain worked
        except Exception as e:
            self.fail(f"Configuration chain failed: {e}")


if __name__ == '__main__':
    unittest.main()
