import asyncio
import logging
import streamlit as st
import sys
import os
import time
import boto3
import json

# Robust path setup for Streamlit
current_file = os.path.abspath(__file__)
src_dir = os.path.dirname(current_file)
project_root = os.path.dirname(src_dir)

# Add both src directory and project root to Python path
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.app_config import AppConfig
from config.mcp_config import MCPConfig
from core.isolated_mcp_client import IsolatedMCPClient
from core.agent import SimpleAgent
from core.async_handler import streamlit_async_handler
from core.logging_config import setup_enhanced_logging, log_separator
from auth.aws_sso_auth import AWSSSOAuthenticator

# Configure enhanced logging
setup_enhanced_logging(level="INFO")
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="AWS MCP Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class SimpleMCPApp:
    """Simplified MCP application focused on official AWS servers with SSO authentication."""
    
    def __init__(self):
        self.app_config = AppConfig.from_env()
        self.mcp_config = MCPConfig.from_env()
        self.sso_authenticator = AWSSSOAuthenticator()
        
        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "debug_info" not in st.session_state:
            st.session_state.debug_info = []
        if "show_debug" not in st.session_state:
            st.session_state.show_debug = False
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
            
    async def initialize_components(self):
        """Initialize MCP client and agent."""
        logger.info("🔄 Initializing application components...")
        
        if "mcp_client" not in st.session_state:
            logger.info("🔧 Creating isolated MCP client...")
            st.session_state.mcp_client = IsolatedMCPClient(self.mcp_config)
            
        if "agent" not in st.session_state:
            logger.info("🤖 Creating agent...")
            # Get AWS session using SSO profile
            current_profile = self.sso_authenticator.get_current_profile()
            if current_profile:
                aws_session = boto3.Session(profile_name=current_profile)
                logger.info(f"✅ Created AWS session with SSO profile: {current_profile}")
            else:
                aws_session = boto3.Session()  # Fallback to default
                logger.warning("⚠️ No SSO profile set, using default session")
                
            st.session_state.agent = SimpleAgent(
                self.app_config,
                st.session_state.mcp_client,
                aws_session
            )
            
        # Initialize if not already done
        if not getattr(st.session_state.agent, '_initialized', False):
            logger.info("🚀 Initializing agent and MCP client...")
            await st.session_state.agent.initialize()
            logger.info("✅ Agent initialization completed")
            
    def render_sidebar(self):
        """Render the left sidebar with debug, login info, MCP info, tools, and controls."""
        with st.sidebar:
            # Header
            st.title("🤖 AWS MCP Agent")
            st.markdown("---")
            
            # Debug Section (Top)
            self.render_debug_section()
            st.markdown("---")
            
            # Login Information
            self.render_login_info()
            st.markdown("---")
            
            # MCP Server Information
            self.render_mcp_server_info()
            st.markdown("---")
            
            # Available Tools (Compact)
            self.render_tools_compact()
            st.markdown("---")
            
            # Controls (Bottom)
            self.render_controls()
            
    def render_debug_section(self):
        """Render debug information section with live data."""
        st.subheader("🔍 Debug Info")
        
        # Debug toggle
        st.session_state.show_debug = st.checkbox(
            "Show Debug Details", 
            value=st.session_state.show_debug,
            key="debug_toggle"
        )
        
        if st.session_state.show_debug:
            # Live system information
            with st.expander("📊 Live System Info", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.text("🔧 System Status:")
                    if hasattr(st.session_state, 'mcp_client'):
                        st.text("✅ MCP Client: Ready")
                    else:
                        st.text("🟡 MCP Client: Initializing")
                        
                    if hasattr(st.session_state, 'agent'):
                        st.text("✅ Agent: Ready")
                        if hasattr(st.session_state.agent, 'conversation_history'):
                            msg_count = len(st.session_state.agent.conversation_history)
                            st.text(f"💬 History: {msg_count} messages")
                    else:
                        st.text("🟡 Agent: Initializing")
                
                with col2:
                    st.text("📡 MCP Status:")
                    if hasattr(st.session_state, 'mcp_client') and st.session_state.mcp_client:
                        server_count = getattr(st.session_state.mcp_client, 'servers_count', 0)
                        st.text(f"🖥️ Servers: {server_count}")
                        
                        tools = getattr(st.session_state.mcp_client, 'tools', {})
                        st.text(f"🛠️ Tools: {len(tools)}")
                    else:
                        st.text("🖥️ Servers: 0")
                        st.text("🛠️ Tools: 0")
                
                # Session state info
                st.text("📋 Session State:")
                st.text(f"💬 Messages: {len(st.session_state.messages)}")
                st.text(f"🔍 Debug entries: {len(st.session_state.debug_info)}")
            
            # Debug history with live updates
            if st.session_state.debug_info:
                with st.expander("📋 Latest Debug Info", expanded=True):
                    latest_debug = st.session_state.debug_info[-1]
                    
                    # Show request info
                    if "request" in latest_debug:
                        st.text("🔤 User Request:")
                        st.code(latest_debug["request"], language="text")
                    
                    # Show tool calls
                    if "tool_calls" in latest_debug and latest_debug["tool_calls"]:
                        st.text("🛠️ Tool Calls:")
                        for i, tool_call in enumerate(latest_debug["tool_calls"]):
                            st.text(f"Tool {i+1}: {tool_call.get('name', 'Unknown')}")
                            if 'arguments' in tool_call:
                                st.code(json.dumps(tool_call['arguments'], indent=2), language="json")
                    
                    # Show raw response
                    if "raw_response" in latest_debug:
                        st.text("🤖 Raw Agent Response:")
                        st.code(latest_debug["raw_response"], language="text")
                    
                    # Show errors
                    if "errors" in latest_debug and latest_debug["errors"]:
                        st.text("❌ Errors:")
                        for error in latest_debug["errors"]:
                            st.error(error)
                    
                    # Show timing
                    if "timing" in latest_debug:
                        st.text(f"⏱️ Response Time: {latest_debug['timing']:.2f}s")
                        
                # Show all debug entries
                if len(st.session_state.debug_info) > 1:
                    with st.expander(f"📚 Debug History ({len(st.session_state.debug_info)} entries)", expanded=False):
                        for i, debug_entry in enumerate(reversed(st.session_state.debug_info[:-1])):
                            st.text(f"Entry {len(st.session_state.debug_info) - i - 1}:")
                            st.text(f"  Request: {debug_entry.get('request', 'N/A')[:50]}...")
                            st.text(f"  Timing: {debug_entry.get('timing', 0):.2f}s")
                            if debug_entry.get('errors'):
                                st.text(f"  Errors: {len(debug_entry['errors'])}")
                        
                # Clear debug button
                if st.button("🗑️ Clear Debug", key="clear_debug"):
                    st.session_state.debug_info = []
                    st.rerun()
            else:
                st.info("No debug information available yet. Start a conversation to see debug data.")
                
            # Auto-refresh toggle
            auto_refresh = st.checkbox("🔄 Auto-refresh debug info", value=False, key="auto_refresh_debug")
            if auto_refresh:
                st.rerun()
                
    def render_login_info(self):
        """Render login information and status."""
        st.subheader("🔐 Authentication")
        
        current_profile = self.sso_authenticator.get_current_profile()
        is_authenticated = self.sso_authenticator.is_authenticated()
        
        if is_authenticated and current_profile:
            st.success(f"✅ Authenticated")
            st.text(f"Profile: {current_profile}")
            
            # Get identity info
            identity = self.sso_authenticator.get_profile_identity(current_profile)
            if identity:
                st.text(f"Account: {identity['account']}")
                
            # Quick profile actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh", key="refresh_auth"):
                    st.rerun()
            with col2:
                if st.button("🚪 Logout", key="logout_btn"):
                    self.logout_user()
        else:
            st.warning("⚠️ Not authenticated")
            if st.button("🔐 Login", key="login_redirect"):
                st.session_state.authenticated = False
                st.rerun()
                
    def render_controls(self):
        """Render control buttons."""
        st.subheader("🎛️ Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat", key="clear_chat"):
                st.session_state.messages = []
                st.session_state.debug_info = []
                st.success("Chat cleared!")
                st.rerun()
                
        with col2:
            if st.button("🔄 Restart", key="restart_app"):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    if key not in ["show_debug"]:  # Keep debug preference
                        del st.session_state[key]
                st.success("Application restarted!")
                st.rerun()
                
    def render_mcp_server_info(self):
        """Render MCP server connection information."""
        st.subheader("📡 MCP Servers")
        
        if hasattr(st.session_state, 'mcp_client') and st.session_state.mcp_client:
            mcp_client = st.session_state.mcp_client
            
            # Get server count
            server_count = getattr(mcp_client, 'servers_count', 0)
            
            if server_count > 0:
                # Get server status
                server_status = {}
                if hasattr(mcp_client, 'get_server_status'):
                    try:
                        server_status = mcp_client.get_server_status()
                    except:
                        server_status = {}
                
                # Count connected servers
                connected_count = len([s for s in server_status.values() if "🟢" in s])
                
                # Show overall status
                if connected_count == server_count:
                    st.success(f"🟢 All {server_count} servers connected")
                elif connected_count > 0:
                    st.warning(f"🟡 {connected_count}/{server_count} servers connected")
                else:
                    st.error(f"🔴 0/{server_count} servers connected")
                
                # Show server details
                with st.expander("Server Details", expanded=False):
                    if server_status:
                        for server_name, status in server_status.items():
                            st.text(f"{status} {server_name}")
                    else:
                        # Fallback to config servers
                        config_servers = getattr(mcp_client.config, 'servers', {})
                        for server_name in config_servers.keys():
                            st.text(f"🔄 {server_name} (Initializing)")
                            
                    # Show tools per server
                    tools = getattr(mcp_client, 'tools', {})
                    if tools:
                        st.text("")
                        st.text("🛠️ Tools by Server:")
                        servers = {}
                        for tool_name in tools.keys():
                            server_name = tool_name.split(':')[0] if ':' in tool_name else 'unknown'
                            if server_name not in servers:
                                servers[server_name] = 0
                            servers[server_name] += 1
                        
                        for server_name, tool_count in servers.items():
                            st.text(f"  📡 {server_name}: {tool_count} tools")
            else:
                # Check if we have config servers
                config_servers = getattr(mcp_client.config, 'servers', {})
                if config_servers:
                    st.info(f"⏳ Connecting to {len(config_servers)} servers...")
                    with st.expander("Configured Servers", expanded=False):
                        for server_name, server_config in config_servers.items():
                            st.text(f"🔄 {server_name}")
                            if 'command' in server_config:
                                st.caption(f"   Command: {server_config['command']}")
                else:
                    st.warning("⚠️ No servers configured")
        else:
            st.info("⏳ MCP client not initialized")
            
    def render_tools_compact(self):
        """Render available tools in compact format with server grouping."""
        st.subheader("🛠️ Available Tools")
        
        if hasattr(st.session_state, 'mcp_client') and st.session_state.mcp_client:
            tools = getattr(st.session_state.mcp_client, 'tools', {})
            
            if tools:
                # Group tools by server
                servers = {}
                for tool_name, tool_info in tools.items():
                    server_name = tool_name.split(':')[0] if ':' in tool_name else 'unknown'
                    if server_name not in servers:
                        servers[server_name] = []
                    servers[server_name].append((tool_name, tool_info))
                
                # Show summary
                total_tools = len(tools)
                server_count = len(servers)
                st.text(f"📊 {total_tools} tools from {server_count} servers")
                
                # Show tools by server
                with st.expander("View Tools by Server", expanded=False):
                    for server_name, server_tools in servers.items():
                        st.text(f"📡 {server_name} ({len(server_tools)} tools)")
                        for tool_name, tool_info in server_tools:
                            tool_display_name = tool_name.split(':')[1] if ':' in tool_name else tool_name
                            st.text(f"  • {tool_display_name}")
            else:
                st.text("⏳ Loading tools...")
        else:
            st.text("⏳ Initializing...")
            
    def logout_user(self):
        """Handle user logout."""
        # Logout from SSO
        self.sso_authenticator.logout_sso()
        
        # Clear environment variables
        for var in ["AWS_PROFILE", "AWS_REGION", "AWS_DEFAULT_REGION"]:
            if var in os.environ:
                del os.environ[var]
        
        # Clear session state
        for key in list(st.session_state.keys()):
            if key not in ["show_debug"]:  # Keep debug preference
                del st.session_state[key]
                
        st.session_state.authenticated = False
        st.success("✅ Logged out successfully!")
        st.rerun()
        
    def render_chat_interface(self):
        """Render the main chat interface."""
        st.title("💬 Chat with AWS")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about your AWS infrastructure..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        start_time = time.time()
                        
                        # Process with agent using async handler correctly
                        response = streamlit_async_handler.run_async(
                            st.session_state.agent.process_message(prompt),
                            timeout=120
                        )
                        
                        end_time = time.time()
                        response_time = end_time - start_time
                        
                        # Store debug information
                        debug_info = {
                            "request": prompt,
                            "raw_response": response,
                            "timing": response_time,
                            "errors": []
                        }
                        
                        # Try to get tool calls from agent if available
                        if hasattr(st.session_state.agent, '_last_tool_calls'):
                            debug_info["tool_calls"] = st.session_state.agent._last_tool_calls
                        
                        st.session_state.debug_info.append(debug_info)
                        
                        # Display response
                        st.markdown(response)
                        
                        # Add to messages
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response
                        })
                        
                    except Exception as e:
                        error_msg = f"Erreur: {str(e)}"
                        logger.error(f"💥 [APP] Request failed: {e}")
                        
                        # Store error in debug info
                        debug_info = {
                            "request": prompt,
                            "raw_response": "",
                            "timing": 0,
                            "errors": [str(e)]
                        }
                        st.session_state.debug_info.append(debug_info)
                        
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_msg
                        })
                        
    async def run(self):
        """Run the application."""
        try:
            # Check authentication
            if not self.sso_authenticator.is_authenticated():
                # Show SSO login UI in main area
                st.title("🔐 AWS SSO Authentication Required")
                authenticated = self.sso_authenticator.render_sso_login_ui()
                if not authenticated:
                    st.info("👆 Please authenticate with AWS SSO to continue")
                    return
                else:
                    st.session_state.authenticated = True
                    st.rerun()
                    
            # Initialize components
            with st.spinner("Initializing MCP servers..."):
                await self.initialize_components()
            
            # Render UI
            self.render_sidebar()
            
            # Main content area - only chat
            self.render_chat_interface()
            
        except Exception as e:
            st.error(f"Application error: {e}")
            logger.error(f"Application error: {e}")

async def main():
    """Main application entry point."""
    app = SimpleMCPApp()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
