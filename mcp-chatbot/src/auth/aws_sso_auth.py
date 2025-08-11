"""
AWS SSO Authentication for MCP Chatbot
Provides UI-based AWS SSO login functionality
"""

import streamlit as st
import boto3
import json
import os
import subprocess
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import configparser

logger = logging.getLogger(__name__)


class AWSSSOAuthenticator:
    """
    AWS SSO authenticator with Streamlit UI integration.
    """
    
    def __init__(self):
        self.aws_home = os.path.expanduser("~/.aws")
        self.config_file = os.path.join(self.aws_home, "config")
        self.credentials_file = os.path.join(self.aws_home, "credentials")
        
    def get_available_sso_profiles(self) -> Dict[str, Dict[str, str]]:
        """Get available SSO profiles from AWS config."""
        sso_profiles = {}
        
        if not os.path.exists(self.config_file):
            return sso_profiles
            
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            for section_name in config.sections():
                section = config[section_name]
                
                # Check if this is an SSO profile
                if 'sso_start_url' in section:
                    profile_name = section_name.replace('profile ', '') if section_name.startswith('profile ') else section_name
                    
                    sso_profiles[profile_name] = {
                        'sso_start_url': section.get('sso_start_url', ''),
                        'sso_region': section.get('sso_region', ''),
                        'sso_account_id': section.get('sso_account_id', ''),
                        'sso_role_name': section.get('sso_role_name', ''),
                        'region': section.get('region', 'ca-central-1')
                    }
                    
        except Exception as e:
            logger.error(f"Error reading AWS config: {e}")
            
        return sso_profiles
        
    def is_profile_authenticated(self, profile_name: str) -> bool:
        """Check if an SSO profile is currently authenticated."""
        try:
            # Try to get caller identity with the profile
            session = boto3.Session(profile_name=profile_name)
            sts = session.client('sts')
            sts.get_caller_identity()
            return True
        except Exception as e:
            logger.debug(f"Profile {profile_name} not authenticated: {e}")
            return False
            
    def get_profile_identity(self, profile_name: str) -> Optional[Dict[str, str]]:
        """Get the identity information for a profile."""
        try:
            session = boto3.Session(profile_name=profile_name)
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            return {
                'account': identity.get('Account', ''),
                'user_id': identity.get('UserId', ''),
                'arn': identity.get('Arn', '')
            }
        except Exception as e:
            logger.debug(f"Could not get identity for {profile_name}: {e}")
            return None
            
    def login_sso_profile(self, profile_name: str) -> bool:
        """Login to AWS SSO for a specific profile."""
        try:
            logger.info(f"🔐 Starting SSO login for profile: {profile_name}")
            
            # Run aws sso login command
            cmd = ["aws", "sso", "login", "--profile", profile_name]
            
            # Use subprocess to run the command
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if process.returncode == 0:
                logger.info(f"✅ SSO login successful for {profile_name}")
                return True
            else:
                logger.error(f"❌ SSO login failed for {profile_name}: {process.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏰ SSO login timeout for {profile_name}")
            return False
        except Exception as e:
            logger.error(f"💥 SSO login error for {profile_name}: {e}")
            return False
            
    def logout_sso(self) -> bool:
        """Logout from AWS SSO."""
        try:
            logger.info("🔐 Logging out from AWS SSO")
            
            cmd = ["aws", "sso", "logout"]
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0:
                logger.info("✅ SSO logout successful")
                return True
            else:
                logger.error(f"❌ SSO logout failed: {process.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"💥 SSO logout error: {e}")
            return False
            
    def configure_new_sso_profile(self, profile_name: str, sso_start_url: str, 
                                 sso_region: str, sso_account_id: str, 
                                 sso_role_name: str, region: str = "ca-central-1") -> bool:
        """
        Configure a new SSO profile in AWS config.
        
        Args:
            profile_name: Name for the new profile
            sso_start_url: SSO start URL
            sso_region: SSO region
            sso_account_id: AWS account ID
            sso_role_name: SSO role name
            region: Default region for the profile
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"🔧 [SSO] Configuring new SSO profile: {profile_name}")
            
            # Ensure AWS config directory exists
            os.makedirs(self.aws_home, exist_ok=True)
            
            # Read existing config
            config = configparser.ConfigParser()
            if os.path.exists(self.config_file):
                config.read(self.config_file)
            
            # Create new profile section
            section_name = f"profile {profile_name}" if profile_name != "default" else "default"
            
            if section_name not in config:
                config.add_section(section_name)
            
            # Set SSO configuration
            config.set(section_name, 'sso_start_url', sso_start_url)
            config.set(section_name, 'sso_region', sso_region)
            config.set(section_name, 'sso_account_id', sso_account_id)
            config.set(section_name, 'sso_role_name', sso_role_name)
            config.set(section_name, 'region', region)
            config.set(section_name, 'output', 'json')
            
            # Write back to config file
            with open(self.config_file, 'w') as f:
                config.write(f)
                
            logger.info(f"✅ [SSO] Successfully configured profile: {profile_name}")
            return True
            
        except Exception as e:
            logger.error(f"💥 [SSO] Error configuring profile {profile_name}: {e}")
            return False
            
    def validate_sso_configuration(self, sso_start_url: str, sso_region: str, 
                                  sso_account_id: str, sso_role_name: str) -> Dict[str, str]:
        """
        Validate SSO configuration parameters.
        
        Returns:
            Dictionary with validation results and error messages
        """
        errors = {}
        
        # Validate SSO start URL
        if not sso_start_url:
            errors['sso_start_url'] = "SSO start URL is required"
        elif not sso_start_url.startswith('https://'):
            errors['sso_start_url'] = "SSO start URL must start with https://"
        elif '.awsapps.com' not in sso_start_url:
            errors['sso_start_url'] = "SSO start URL should contain .awsapps.com"
            
        # Validate SSO region
        if not sso_region:
            errors['sso_region'] = "SSO region is required"
        elif not sso_region.startswith(('us-', 'eu-', 'ap-', 'ca-', 'sa-')):
            errors['sso_region'] = "Invalid AWS region format"
            
        # Validate account ID
        if not sso_account_id:
            errors['sso_account_id'] = "Account ID is required"
        elif not sso_account_id.isdigit() or len(sso_account_id) != 12:
            errors['sso_account_id'] = "Account ID must be 12 digits"
            
        # Validate role name
        if not sso_role_name:
            errors['sso_role_name'] = "Role name is required"
        elif len(sso_role_name) < 1 or len(sso_role_name) > 64:
            errors['sso_role_name'] = "Role name must be 1-64 characters"
            
        return errors
            
    def render_new_sso_profile_form(self):
        """Render form for adding new SSO profile."""
        st.subheader("➕ Add New SSO Profile")
        
        # Add some helpful text
        st.info("Configure a new AWS SSO profile to connect to your organization's AWS accounts.")
        
        with st.form("new_sso_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                profile_name = st.text_input(
                    "Profile Name",
                    placeholder="e.g., my-company-prod",
                    help="Unique name for this SSO profile"
                )
                
                sso_start_url = st.text_input(
                    "SSO Start URL",
                    placeholder="https://d-xxxxxxxxxx.awsapps.com/start",
                    help="Your organization's AWS SSO start URL"
                )
                
                sso_region = st.selectbox(
                    "SSO Region",
                    ["ca-central-1", "us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                    help="Region where your SSO is configured"
                )
                
            with col2:
                sso_account_id = st.text_input(
                    "AWS Account ID",
                    placeholder="123456789012",
                    help="12-digit AWS account ID"
                )
                
                sso_role_name = st.text_input(
                    "SSO Role Name",
                    placeholder="AWSAdministratorAccess",
                    help="Name of the SSO role to assume"
                )
                
                default_region = st.selectbox(
                    "Default Region",
                    ["ca-central-1", "us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                    help="Default AWS region for this profile"
                )
            
            # Form submission
            submitted = st.form_submit_button("🔧 Configure SSO Profile")
            
            if submitted:
                # Validate inputs
                if not all([profile_name, sso_start_url, sso_region, sso_account_id, sso_role_name]):
                    st.error("❌ All fields are required")
                    return False
                    
                # Validate configuration
                errors = self.validate_sso_configuration(
                    sso_start_url, sso_region, sso_account_id, sso_role_name
                )
                
                if errors:
                    st.error("❌ Configuration errors:")
                    for field, error in errors.items():
                        st.error(f"  • {field}: {error}")
                    return False
                
                # Check if profile already exists
                existing_profiles = self.get_available_sso_profiles()
                if profile_name in existing_profiles:
                    st.error(f"❌ Profile '{profile_name}' already exists")
                    return False
                
                # Configure the new profile
                success = self.configure_new_sso_profile(
                    profile_name=profile_name,
                    sso_start_url=sso_start_url,
                    sso_region=sso_region,
                    sso_account_id=sso_account_id,
                    sso_role_name=sso_role_name,
                    region=default_region
                )
                
                if success:
                    st.success(f"✅ Successfully configured SSO profile: {profile_name}")
                    st.info("🔄 Please refresh the page to see the new profile in the dropdown")
                    
                    # Show next steps
                    st.info("📋 Next steps:")
                    st.code(f"aws sso login --profile {profile_name}")
                    
                    return True
                else:
                    st.error("❌ Failed to configure SSO profile. Check the logs for details.")
                    return False
        
        # Show example configuration
        with st.expander("💡 Example Configuration", expanded=False):
            st.text("Profile Name: my-company-prod")
            st.text("SSO Start URL: https://d-1234567890.awsapps.com/start")
            st.text("SSO Region: us-east-1")
            st.text("AWS Account ID: 123456789012")
            st.text("SSO Role Name: AWSAdministratorAccess")
            st.text("Default Region: us-east-1")
        
        return False
        
    def _remove_sso_profile(self, profile_name: str) -> bool:
        """Remove an SSO profile from AWS config."""
        try:
            logger.info(f"🗑️ [SSO] Removing SSO profile: {profile_name}")
            
            if not os.path.exists(self.config_file):
                logger.warning(f"⚠️ [SSO] Config file not found: {self.config_file}")
                return False
            
            # Read existing config
            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            # Determine section name
            section_name = f"profile {profile_name}" if profile_name != "default" else "default"
            
            if section_name not in config:
                logger.warning(f"⚠️ [SSO] Profile section not found: {section_name}")
                return False
            
            # Remove the section
            config.remove_section(section_name)
            
            # Write back to config file
            with open(self.config_file, 'w') as f:
                config.write(f)
                
            logger.info(f"✅ [SSO] Successfully removed profile: {profile_name}")
            return True
            
        except Exception as e:
            logger.error(f"💥 [SSO] Error removing profile {profile_name}: {e}")
            return False
            
    def set_environment_for_profile(self, profile_name: str) -> bool:
        try:
            # Set the AWS profile environment variable
            os.environ["AWS_PROFILE"] = profile_name
            
            # Get the profile's region
            sso_profiles = self.get_available_sso_profiles()
            if profile_name in sso_profiles:
                region = sso_profiles[profile_name].get('region', 'ca-central-1')
                os.environ["AWS_DEFAULT_REGION"] = region
                os.environ["AWS_REGION"] = region
                
            logger.info(f"✅ Environment set for profile: {profile_name}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error setting environment for {profile_name}: {e}")
            return False
            
    def render_sso_login_ui(self):
        """Render the SSO login UI in Streamlit."""
        st.header("🔐 AWS SSO Authentication")
        
        # Get available SSO profiles
        sso_profiles = self.get_available_sso_profiles()
        
        # Create tabs for existing profiles and new profile configuration
        if sso_profiles:
            tab1, tab2 = st.tabs(["🔑 Existing Profiles", "➕ Add New Profile"])
            
            with tab1:
                return self._render_existing_profiles_ui(sso_profiles)
                
            with tab2:
                self.render_new_sso_profile_form()
                return False  # New profile form doesn't authenticate immediately
        else:
            st.warning("❌ No AWS SSO profiles found in ~/.aws/config")
            st.info("Configure your first SSO profile below:")
            return self.render_new_sso_profile_form()
            
    def _render_existing_profiles_ui(self, sso_profiles):
        """Render UI for existing SSO profiles."""
        st.info("Select an AWS SSO profile to authenticate:")
        
        # Profile selection
        profile_names = list(sso_profiles.keys())
        selected_profile = st.selectbox(
            "Choose AWS SSO Profile:",
            profile_names,
            key="sso_profile_selector"
        )
        
        if selected_profile:
            profile_info = sso_profiles[selected_profile]
            
            # Show profile information
            with st.expander("📋 Profile Details", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Account ID:** {profile_info.get('sso_account_id', 'N/A')}")
                    st.write(f"**Role:** {profile_info.get('sso_role_name', 'N/A')}")
                with col2:
                    st.write(f"**Region:** {profile_info.get('region', 'N/A')}")
                    st.write(f"**SSO Region:** {profile_info.get('sso_region', 'N/A')}")
                st.write(f"**SSO URL:** {profile_info.get('sso_start_url', 'N/A')}")
            
            # Check authentication status
            is_authenticated = self.is_profile_authenticated(selected_profile)
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🔐 Login with SSO", key="sso_login_btn"):
                    with st.spinner(f"Logging in to {selected_profile}..."):
                        success = self.login_sso_profile(selected_profile)
                        
                        if success:
                            st.success("✅ SSO login successful!")
                            # Set environment variables
                            self.set_environment_for_profile(selected_profile)
                            st.rerun()
                        else:
                            st.error("❌ SSO login failed. Please try again.")
                            
            with col2:
                if st.button("🔄 Check Status", key="sso_status_btn"):
                    st.rerun()
                    
            with col3:
                if st.button("🚪 Logout", key="sso_logout_btn"):
                    with st.spinner("Logging out..."):
                        success = self.logout_sso()
                        if success:
                            st.success("✅ Logged out successfully!")
                            # Clear environment variables
                            for var in ["AWS_PROFILE", "AWS_REGION", "AWS_DEFAULT_REGION"]:
                                if var in os.environ:
                                    del os.environ[var]
                            st.rerun()
                        else:
                            st.error("❌ Logout failed.")
                            
            with col4:
                if st.button("🗑️ Remove Profile", key="sso_remove_btn"):
                    if st.session_state.get('confirm_remove', False):
                        # Actually remove the profile
                        success = self._remove_sso_profile(selected_profile)
                        if success:
                            st.success(f"✅ Removed profile: {selected_profile}")
                            st.session_state.confirm_remove = False
                            st.rerun()
                        else:
                            st.error("❌ Failed to remove profile")
                    else:
                        # Ask for confirmation
                        st.session_state.confirm_remove = True
                        st.warning("⚠️ Click again to confirm removal")
            
            # Show current authentication status
            if is_authenticated:
                st.success(f"✅ **Authenticated** as profile: `{selected_profile}`")
                
                # Show identity information
                identity = self.get_profile_identity(selected_profile)
                if identity:
                    with st.expander("👤 Current Identity", expanded=True):
                        st.write(f"**Account:** {identity['account']}")
                        st.write(f"**ARN:** {identity['arn']}")
                        
                # Set environment for the application
                self.set_environment_for_profile(selected_profile)
                
                return True
            else:
                st.warning(f"⚠️ **Not authenticated** for profile: `{selected_profile}`")
                st.info("Click 'Login with SSO' to authenticate.")
                return False
                
        return False
        
    def get_current_profile(self) -> Optional[str]:
        """Get the currently active AWS profile."""
        return os.environ.get("AWS_PROFILE")
        
    def is_authenticated(self) -> bool:
        """Check if any profile is currently authenticated."""
        current_profile = self.get_current_profile()
        if current_profile:
            return self.is_profile_authenticated(current_profile)
        return False
