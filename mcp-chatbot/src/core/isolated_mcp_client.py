"""
Event Loop Isolated MCP Client
Completely isolates MCP operations in their own event loop to avoid conflicts
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import queue

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str


class IsolatedMCPClient:
    """
    MCP client that runs in its own isolated event loop to avoid conflicts.
    All operations are thread-safe and isolated from the main application loop.
    """
    
    def __init__(self, config):
        self.config = config
        self.tools: Dict[str, MCPTool] = {}
        self._initialized = False
        self._loop_thread = None
        self._loop = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="mcp-isolated")
        self._server_data = {}  # Store server processes and data
        
        # UI compatibility attributes
        self.server_processes = {}  # For UI display compatibility
        
    @property
    def servers_count(self) -> int:
        """Get the number of active servers."""
        return len(self._server_data)
        
    def get_server_status(self) -> Dict[str, str]:
        """Get status of all servers for UI display."""
        status = {}
        for server_name, server_data in self._server_data.items():
            if server_data.get('initialized', False):
                status[server_name] = "🟢 Connected"
            else:
                status[server_name] = "🟡 Initializing"
        return status
        
    def _run_event_loop(self):
        """Run the isolated event loop in a separate thread."""
        logger.info("🔄 Starting isolated MCP event loop...")
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            self._loop.run_forever()
        except Exception as e:
            logger.error(f"💥 Event loop error: {e}")
        finally:
            logger.info("🛑 MCP event loop stopped")
            
    def _run_in_loop(self, coro):
        """Run a coroutine in the isolated event loop."""
        if not self._loop or not self._loop.is_running():
            raise RuntimeError("MCP event loop not running")
            
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=60)
        
    async def _async_initialize(self):
        """Initialize MCP servers in the isolated loop."""
        logger.info("🔧 Initializing MCP servers in isolated loop...")
        
        # Get enabled servers
        enabled_servers = self.config.get_enabled_servers()
        official_servers = {name: server for name, server in enabled_servers.items() 
                          if server.command == "uvx"}
        
        if not official_servers:
            logger.warning("No official MCP servers enabled")
            return
            
        logger.info(f"Found {len(official_servers)} official servers to initialize")
        
        # Initialize each official server
        for server_name, server_config in official_servers.items():
            try:
                await self._async_initialize_server(server_name, server_config)
            except Exception as e:
                logger.error(f"Failed to initialize {server_name}: {e}")
                continue
                
        logger.info(f"MCP client initialized with {len(self.tools)} tools")
        
    async def _async_initialize_server(self, server_name: str, server_config):
        """Initialize a server in the isolated loop."""
        logger.info(f"🔧 Initializing server: {server_name}")
        
        try:
            # Find uvx path
            import shutil
            uvx_path = shutil.which("uvx")
            if not uvx_path:
                for path in ["/opt/homebrew/bin/uvx", "/usr/local/bin/uvx", "/usr/bin/uvx"]:
                    if os.path.exists(path):
                        uvx_path = path
                        break
            
            if not uvx_path:
                raise Exception("uvx command not found")
                
            cmd = [uvx_path] + server_config.args
            
            # Set up environment
            env = os.environ.copy()
            if server_config.env:
                env.update(server_config.env)
                
            # Ensure AWS configuration is available to the MCP server
            aws_home = os.path.expanduser("~/.aws")
            if os.path.exists(aws_home):
                env["AWS_CONFIG_FILE"] = os.path.join(aws_home, "config")
                env["AWS_SHARED_CREDENTIALS_FILE"] = os.path.join(aws_home, "credentials")
                logger.info(f"🔐 [MCP] Set AWS config paths for {server_name}")
                
                # Try to read credentials directly from the default profile
                try:
                    import configparser
                    credentials_file = os.path.join(aws_home, "credentials")
                    if os.path.exists(credentials_file):
                        config_parser = configparser.ConfigParser()
                        config_parser.read(credentials_file)
                        
                        if 'default' in config_parser:
                            default_section = config_parser['default']
                            if 'aws_access_key_id' in default_section:
                                env["AWS_ACCESS_KEY_ID"] = default_section['aws_access_key_id']
                                logger.info(f"🔐 [MCP] Set AWS_ACCESS_KEY_ID from default profile")
                            if 'aws_secret_access_key' in default_section:
                                env["AWS_SECRET_ACCESS_KEY"] = default_section['aws_secret_access_key']
                                logger.info(f"🔐 [MCP] Set AWS_SECRET_ACCESS_KEY from default profile")
                except Exception as e:
                    logger.warning(f"⚠️ [MCP] Could not read credentials file: {e}")
                
            # Also pass through any existing AWS environment variables
            aws_env_vars = [
                "AWS_PROFILE", "AWS_REGION", "AWS_DEFAULT_REGION",
                "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"
            ]
            
            for var in aws_env_vars:
                if var in os.environ:
                    env[var] = os.environ[var]
                    logger.info(f"🔐 [MCP] Passed AWS env var: {var}")
                    
            # Don't set AWS_PROFILE explicitly - let AWS CLI use default resolution
            # This matches how AWS CLI works in the terminal
                    
            # Set default region if not specified
            if "AWS_REGION" not in env and "AWS_DEFAULT_REGION" not in env:
                env["AWS_DEFAULT_REGION"] = "ca-central-1"
                logger.info(f"🔐 [MCP] Set default region: ca-central-1")
                
            # Debug: Log AWS environment for troubleshooting
            logger.info(f"🔍 [MCP] AWS environment for {server_name}:")
            for key, value in env.items():
                if key.startswith("AWS_"):
                    # Don't log sensitive values, just show they exist
                    if "KEY" in key or "TOKEN" in key:
                        logger.info(f"🔍 [MCP]   {key}: [REDACTED]")
                    else:
                        logger.info(f"🔍 [MCP]   {key}: {value}")
            
            # Start server process
            logger.info(f"🚀 Starting server process: {' '.join(cmd)}")
            logger.info(f"🚀 Environment variables count: {len(env)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "isolated-mcp-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            # Send request
            request_json = json.dumps(init_request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            # Read response
            response_line = await asyncio.wait_for(
                process.stdout.readline(), 
                timeout=15
            )
            
            if not response_line:
                raise Exception("No response from server")
                
            response = json.loads(response_line.decode().strip())
            
            if "error" in response:
                raise Exception(f"Server initialization error: {response['error']}")
                
            logger.info(f"✅ Server {server_name} initialized successfully")
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            notification_json = json.dumps(initialized_notification) + "\n"
            process.stdin.write(notification_json.encode())
            await process.stdin.drain()
            
            await asyncio.sleep(1)
            
            # Get tools list
            await self._async_get_server_tools(server_name, process)
            
            # Store server data
            self._server_data[server_name] = {
                'process': process,
                'initialized': True
            }
            
            # Update UI compatibility attribute
            self.server_processes[server_name] = f"isolated-{server_name}"
            
        except Exception as e:
            logger.error(f"Failed to initialize server {server_name}: {e}")
            raise
            
    async def _async_get_server_tools(self, server_name: str, process):
        """Get available tools from a server in the isolated loop."""
        logger.info(f"🛠️ Getting tools from server: {server_name}")
        
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": None
        }
        
        try:
            request_json = json.dumps(tools_request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            response_line = await asyncio.wait_for(
                process.stdout.readline(), 
                timeout=15
            )
            
            if not response_line:
                logger.warning(f"No tools response from {server_name}")
                return
                
            response = json.loads(response_line.decode().strip())
            logger.info(f"📋 Tools response from {server_name}: received {len(str(response))} chars")
            
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                logger.info(f"✅ Server {server_name} provided {len(tools)} tools")
                
                for tool_data in tools:
                    tool = MCPTool(
                        name=tool_data["name"],
                        description=tool_data["description"],
                        input_schema=tool_data.get("inputSchema", {}),
                        server_name=server_name
                    )
                    self.tools[f"{server_name}:{tool.name}"] = tool
                    
            elif "error" in response:
                logger.error(f"❌ Error getting tools from {server_name}: {response['error']}")
            else:
                logger.warning(f"⚠️ Unexpected tools response from {server_name}")
                
        except Exception as e:
            logger.warning(f"Failed to get tools from {server_name}: {e}")
            
    async def _async_call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool in the isolated loop."""
        logger.info(f"🔧 [MCP] Calling tool: {tool_name}")
        logger.info(f"📋 [MCP] Arguments: {json.dumps(arguments, indent=2)}")
        
        if tool_name not in self.tools:
            logger.error(f"❌ [MCP] Tool {tool_name} not found in available tools")
            logger.info(f"📋 [MCP] Available tools: {list(self.tools.keys())}")
            return {"error": f"Tool {tool_name} not found"}
            
        tool = self.tools[tool_name]
        server_name = tool.server_name
        
        logger.info(f"📡 [MCP] Tool {tool_name} belongs to server: {server_name}")
        
        if server_name not in self._server_data:
            logger.error(f"❌ [MCP] Server {server_name} not available in active servers")
            logger.info(f"📋 [MCP] Active servers: {list(self._server_data.keys())}")
            return {"error": f"Server {server_name} not available"}
            
        process = self._server_data[server_name]['process']
        logger.info(f"✅ [MCP] Found active process for server: {server_name}")
        
        tool_request = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "tools/call",
            "params": {
                "name": tool.name,
                "arguments": arguments
            }
        }
        
        logger.info(f"[MCP] Sending tool request to {server_name}:")
        logger.info(f"[MCP] Request: {json.dumps(tool_request, indent=2)}")
        
        try:
            request_json = json.dumps(tool_request) + "\n"
            process.stdin.write(request_json.encode())
            await process.stdin.drain()
            
            logger.info(f"[MCP] Request sent to {server_name}, waiting for response...")
            
            response_line = await asyncio.wait_for(
                process.stdout.readline(), 
                timeout=30
            )
            
            if not response_line:
                logger.error(f"❌ [MCP] No response received from {server_name}")
                return {"error": "No response from server"}
            
            response = json.loads(response_line.decode().strip())
            logger.info(f"📥 [MCP] Received response from {server_name}:")
            logger.info(f"📥 [MCP] Response: {json.dumps(response, indent=2)}")
            
            # Handle different response types
            if "method" in response and response["method"] == "notifications/message":
                # This is a notification message (often an error)
                logger.warning(f"⚠️ [MCP] Received notification from {server_name}")
                
                if "params" in response and "level" in response["params"]:
                    level = response["params"]["level"]
                    data = response["params"].get("data", "No details provided")
                    
                    if level == "error":
                        logger.error(f"❌ [MCP] Server error notification: {data}")
                        
                        # Try to extract useful error information
                        try:
                            if "validation_failures" in data:
                                import json as json_lib
                                error_data = json_lib.loads(data)
                                if "validation_failures" in error_data:
                                    failure = error_data["validation_failures"][0]
                                    reason = failure.get("reason", "Unknown validation error")
                                    return {"error": f"AWS CLI validation error: {reason}"}
                        except:
                            pass
                            
                        return {"error": f"Server error: {data}"}
                    else:
                        logger.info(f"📋 [MCP] Server notification ({level}): {data}")
                        return {"error": f"Server notification ({level}): {data}"}
                        
                # Wait for the actual response after notification
                logger.info(f"📥 [MCP] Waiting for actual response after notification...")
                try:
                    response_line = await asyncio.wait_for(
                        process.stdout.readline(), 
                        timeout=10
                    )
                    
                    if response_line:
                        response = json.loads(response_line.decode().strip())
                        logger.info(f"📥 [MCP] Received actual response: {json.dumps(response, indent=2)}")
                    else:
                        return {"error": "No response after notification"}
                except asyncio.TimeoutError:
                    return {"error": "Timeout waiting for response after notification"}
            
            # Handle standard JSON-RPC response
            if "error" in response:
                logger.error(f"❌ [MCP] Server returned error: {response['error']}")
                error_message = response["error"].get("message", str(response["error"]))
                return {"error": error_message}
            elif "result" in response:
                result_size = len(str(response["result"]))
                logger.info(f"✅ [MCP] Tool call successful, result size: {result_size} chars")
                
                # Log a preview of the result
                result_preview = str(response["result"])[:200]
                logger.info(f"📋 [MCP] Result preview: {result_preview}...")
                
                return {"result": response["result"]}
            else:
                logger.warning(f"⚠️ [MCP] Unexpected response format from {server_name}")
                logger.info(f"📋 [MCP] Full response: {response}")
                return {"error": "Invalid response format"}
                
        except asyncio.TimeoutError:
            logger.error(f"⏰ [MCP] Tool call timeout for {tool_name} on {server_name} (30s)")
            return {"error": "Tool call timeout"}
        except json.JSONDecodeError as e:
            logger.error(f"💥 [MCP] JSON decode error for {tool_name}: {e}")
            logger.error(f"📋 [MCP] Raw response: {response_line}")
            return {"error": f"JSON decode error: {str(e)}"}
        except Exception as e:
            logger.error(f"💥 [MCP] Tool call exception for {tool_name}: {e}")
            import traceback
            logger.error(f"📋 [MCP] Full traceback: {traceback.format_exc()}")
            return {"error": str(e)}
            
    async def _async_cleanup(self):
        """Clean up servers in the isolated loop."""
        logger.info("🧹 Cleaning up MCP servers...")
        
        for server_name, server_data in self._server_data.items():
            try:
                process = server_data['process']
                if process.stdin and not process.stdin.is_closing():
                    process.stdin.close()
                process.terminate()
                await asyncio.wait_for(process.wait(), timeout=2)
                logger.info(f"✅ Cleaned up server: {server_name}")
            except Exception as e:
                logger.warning(f"Error cleaning up {server_name}: {e}")
                
        self._server_data.clear()
        self.server_processes.clear()  # Clear UI compatibility attribute
        self.tools.clear()
        
    # Public interface methods (thread-safe)
    
    def initialize(self):
        """Initialize the MCP client (thread-safe)."""
        if self._initialized:
            return
            
        logger.info("🚀 Starting isolated MCP client...")
        
        # Start the isolated event loop in a separate thread
        self._loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._loop_thread.start()
        
        # Wait for loop to start
        time.sleep(1)
        
        # Initialize servers in the isolated loop
        try:
            self._run_in_loop(self._async_initialize())
            self._initialized = True
            logger.info("✅ Isolated MCP client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize isolated MCP client: {e}")
            raise
            
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool (thread-safe)."""
        if not self._initialized:
            return {"error": "MCP client not initialized"}
            
        try:
            return self._run_in_loop(self._async_call_tool(tool_name, arguments))
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {"error": str(e)}
            
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools (thread-safe)."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "server_name": tool.server_name
            }
            for tool in self.tools.values()
        ]
        
    def cleanup(self):
        """Clean up resources (thread-safe)."""
        if not self._initialized:
            return
            
        logger.info("🛑 Shutting down isolated MCP client...")
        
        try:
            # Clean up servers
            self._run_in_loop(self._async_cleanup())
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
        
        # Stop the event loop
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
            
        # Wait for thread to finish
        if self._loop_thread and self._loop_thread.is_alive():
            self._loop_thread.join(timeout=5)
            
        # Shutdown executor
        self._executor.shutdown(wait=True)
        
        self._initialized = False
        logger.info("✅ Isolated MCP client shutdown complete")
