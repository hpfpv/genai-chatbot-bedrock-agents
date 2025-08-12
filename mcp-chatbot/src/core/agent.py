"""
Simple Agent - Direct Bedrock integration without LangChain
Implements the flow: User → Agent → MCP Client → MCP Server → AWS → Response
"""

import json
import logging
import re
import time
from typing import Dict, Any, List, Optional
import boto3

logger = logging.getLogger(__name__)


class SimpleAgent:
    """
    Simplified agent that directly uses Bedrock and MCP servers.
    """
    
    def __init__(self, app_config, mcp_client, aws_session=None):
        self.app_config = app_config
        self.mcp_client = mcp_client
        self.aws_session = aws_session or boto3.Session()
        self.bedrock_client = None
        self.conversation_history = []
        self._initialized = False
        self._last_tool_calls = []  # For debug tracking
        
    async def initialize(self):
        """Initialize the agent."""
        if self._initialized:
            return
            
        logger.info("Initializing Simple Agent...")
        
        # Initialize Bedrock client
        try:
            self.bedrock_client = self.aws_session.client(
                'bedrock-runtime',
                region_name=self.app_config.aws_region
            )
            
            # Test AWS credentials by making a simple call
            try:
                # Test with a simple STS call to verify credentials
                sts_client = self.aws_session.client('sts')
                identity = sts_client.get_caller_identity()
                logger.info(f"AWS credentials verified for: {identity.get('Arn', 'Unknown')}")
            except Exception as e:
                logger.warning(f"AWS credentials issue: {e}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
        
        # Initialize MCP client (synchronous since isolated client handles async internally)
        self.mcp_client.initialize()
        
        self._initialized = True
        logger.info("Simple Agent initialized successfully")
        
    async def process_message(self, user_message: str) -> str:
        """
        Process a user message and return a response.
        Implements the core flow: User → Agent → MCP → AWS → Response
        """
        if not self._initialized:
            await self.initialize()
            
        logger.info(f"🎯 Processing user message: '{user_message}'")
        
        # Clear previous debug info
        self._last_tool_calls = []
        
        try:
            # Step 1: Analyze user intent and determine if tools are needed
            logger.info("Step 1: Analyzing user intent...")
            intent_analysis = await self._analyze_intent(user_message)
            logger.info(f"Intent analysis result: {intent_analysis}")
            
            # Step 2: If tools are needed, execute them
            tool_results = []
            if intent_analysis.get("needs_tools", False):
                tool_calls = intent_analysis.get("tool_calls", [])
                logger.info(f"🛠️ Step 2: Executing {len(tool_calls)} tool calls...")
                
                for i, tool_call in enumerate(tool_calls, 1):
                    logger.info(f"🔧 Tool call {i}/{len(tool_calls)}: {tool_call['name']}")
                    logger.info(f"📋 Original arguments: {tool_call.get('arguments', {})}")
                    
                    # Store tool call for debug
                    self._last_tool_calls.append({
                        "name": tool_call['name'],
                        "arguments": tool_call.get('arguments', {})
                    })
                    
                    try:
                        # Validate and fix arguments
                        fixed_arguments = self._validate_and_fix_tool_arguments(
                            tool_call["name"], 
                            tool_call.get("arguments", {})
                        )
                        logger.info(f"✅ Fixed arguments: {fixed_arguments}")
                        
                        # Use synchronous call since isolated client handles async internally
                        result = self.mcp_client.call_tool(
                            tool_call["name"], 
                            fixed_arguments
                        )
                        
                        # Check if the result contains an error
                        if "error" in result:
                            logger.warning(f"⚠️ Tool call {i} returned error: {result['error']}")
                            
                            # For AWS CLI validation errors, suggest using suggest_aws_commands instead
                            if "validation" in result["error"].lower() or "parameters" in result["error"].lower():
                                logger.info(f"🔄 AWS CLI validation error detected, will suggest using suggest_aws_commands")
                                
                                # Extract the original intent for suggestion
                                if tool_call["name"] == "aws-api:call_aws" and "cli_command" in fixed_arguments:
                                    original_command = fixed_arguments["cli_command"]
                                    # Convert to a query for suggestions
                                    query = user_message  # Use original user message as query
                                    
                                    logger.info(f"🔄 Trying suggest_aws_commands with query: {query}")
                                    suggestion_result = self.mcp_client.call_tool(
                                        "aws-api:suggest_aws_commands",
                                        {"query": query}
                                    )
                                    
                                    if "result" in suggestion_result:
                                        logger.info(f"✅ Got command suggestions successfully")
                                        tool_results.append({
                                            "tool": "aws-api:suggest_aws_commands",
                                            "result": suggestion_result,
                                            "fallback_reason": f"Original command failed validation: {result['error']}"
                                        })
                                    else:
                                        tool_results.append({
                                            "tool": tool_call["name"],
                                            "result": result
                                        })
                                else:
                                    tool_results.append({
                                        "tool": tool_call["name"],
                                        "result": result
                                    })
                            else:
                                tool_results.append({
                                    "tool": tool_call["name"],
                                    "result": result
                                })
                        else:
                            logger.info(f"✅ Tool call {i} completed successfully")
                            tool_results.append({
                                "tool": tool_call["name"],
                                "result": result
                            })
                    except Exception as e:
                        logger.error(f"❌ Tool call {i} failed: {e}")
                        tool_results.append({
                            "tool": tool_call["name"],
                            "result": {"error": str(e)}
                        })
            else:
                logger.info("🚫 No tools needed for this request")
            
            # Step 3: Generate final response using Bedrock
            logger.info("🤖 Step 3: Generating final response with Bedrock...")
            final_response = await self._generate_response(
                user_message, 
                intent_analysis, 
                tool_results
            )
            logger.info(f"✅ Final response generated ({len(final_response)} chars)")
            
            # Step 4: Update conversation history
            self.conversation_history.append({
                "user": user_message,
                "assistant": final_response,
                "tools_used": [tr["tool"] for tr in tool_results]
            })
            logger.info(f"📚 Conversation history updated (total: {len(self.conversation_history)} messages)")
            
            return final_response
            
        except Exception as e:
            logger.error(f"💥 Error processing message: {e}")
            import traceback
            logger.error(f"📋 Full traceback: {traceback.format_exc()}")
            
            # Provide helpful error messages based on the error type
            if "Unable to locate credentials" in str(e):
                return """Je suis désolé, il y a un problème avec les identifiants AWS. 

Veuillez configurer vos identifiants AWS :
1. Utilisez `aws configure` pour configurer vos identifiants
2. Ou définissez les variables d'environnement AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY
3. Ou utilisez un profil AWS avec `export AWS_PROFILE=votre-profil`

Une fois configuré, redémarrez l'application."""
            
            elif "ValidationException" in str(e):
                return "Je suis désolé, il y a eu un problème avec la validation de la requête. Veuillez réessayer."
            
            elif "ThrottlingException" in str(e):
                return "Je suis désolé, il y a eu trop de requêtes. Veuillez attendre un moment et réessayer."
            
            elif "event loop" in str(e).lower() or "asyncio" in str(e).lower():
                return """Je suis désolé, il y a eu un problème technique avec les boucles d'événements asynchrones. 

Cela peut être résolu en redémarrant l'application. Veuillez :
1. Arrêter l'application (Ctrl+C)
2. Redémarrer avec ./run.sh

Si le problème persiste, il pourrait y avoir un conflit dans l'environnement d'exécution."""
            
            else:
                return f"Je suis désolé, une erreur s'est produite: {str(e)}"
            
    async def _analyze_intent(self, user_message: str) -> Dict[str, Any]:
        """Analyze user intent and determine what tools to use."""
        
        logger.info(f"[INTENT] Starting intent analysis for: '{user_message}'")
        
        # Get available tools
        available_tools = self.mcp_client.get_available_tools()
        tools_description = self._format_tools_for_prompt(available_tools)
        
        logger.info(f"[INTENT] Available tools count: {len(available_tools)}")
        
        # Create intent analysis prompt with improved context awareness
        prompt = f"""Analyze this user request and determine if AWS tools are needed.

User request: "{user_message}"

CONVERSATION CONTEXT: You are having an ongoing conversation about AWS infrastructure. Consider previous context when making decisions.

Available tools:
{tools_description}

IMPROVED DECISION MAKING:
1. PREFER call_aws when you know the exact command needed
2. Use suggest_aws_commands only when truly uncertain
3. For common operations (create/delete/list), use call_aws directly
4. Remember context from previous messages (VPC IDs, resource names, etc.)

CONTEXT-AWARE EXAMPLES:
- If user mentioned a VPC ID earlier, use it in subsequent commands
- If creating subnets, include --vpc-id parameter
- If user asks for "the same region", use ca-central-1
- For availability zones, use ca-central-1a, ca-central-1b, ca-central-1d

COMMON AWS OPERATIONS - USE call_aws DIRECTLY:
- Create subnet: aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block <cidr> --availability-zone <az>
- Delete VPC: aws ec2 delete-vpc --vpc-id <vpc-id>
- List instances: aws ec2 describe-instances
- List S3 buckets: aws s3 ls
- Create IAM role: Use suggest_aws_commands (complex multi-step)

IMPORTANT - Use these EXACT parameter names:
- For aws-api:call_aws → use "cli_command" (not "command")
- For aws-api:suggest_aws_commands → use "query" (not "command")
- For aws-docs:read_documentation → use "url", "max_length", "start_index"
- For aws-docs:search_documentation → use "search_phrase", "limit"
- For aws-docs:recommend → use "url"

CRITICAL AWS CLI RULES:
- For IAM role creation: Use ONLY aws iam create-role with --role-name and --assume-role-policy-document
- To attach policies: Use separate aws iam attach-role-policy command
- DO NOT use --managed-policy-arns with create-role (not supported)
- For complex operations requiring multiple steps, use suggest_aws_commands instead of call_aws

Examples of CORRECT IAM commands:
- Create role: aws iam create-role --role-name MyRole --assume-role-policy-document file://trust-policy.json
- Attach policy: aws iam attach-role-policy --role-name MyRole --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

Respond with JSON only:
{{
    "needs_tools": true/false,
    "reasoning": "explanation of why tools are/aren't needed and which tool is most appropriate",
    "tool_calls": [
        {{
            "name": "server_name:tool_name",
            "arguments": {{"correct_parameter_name": "value"}}
        }}
    ]
}}

IMPROVED EXAMPLES:
- "List my S3 buckets" → needs aws-api:call_aws with {{"cli_command": "aws s3 ls"}}
- "Create subnet in ca-central-1a" → needs aws-api:call_aws with {{"cli_command": "aws ec2 create-subnet --vpc-id <vpc-id> --cidr-block 10.0.1.0/24 --availability-zone ca-central-1a"}}
- "How do I create a VPC?" → needs aws-api:suggest_aws_commands with {{"query": "create a new VPC"}}
- "Create IAM role with permissions" → needs aws-api:suggest_aws_commands with {{"query": "create IAM role with specific permissions"}}
- "Search for Lambda docs" → needs aws-docs:search_documentation with {{"search_phrase": "Lambda", "limit": 5}}

JSON response:"""

        logger.info(f"[INTENT] Prompt length: {len(prompt)} chars")
        logger.info(f"[INTENT] Calling Bedrock for intent analysis...")

        try:
            response = await self._call_bedrock(prompt, max_tokens=500)
            
            logger.info(f"[INTENT] Raw Bedrock response: {response}")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                logger.info(f"[INTENT] Extracted JSON: {json_str}")
                
                parsed_intent = json.loads(json_str)
                logger.info(f"✅ [INTENT] Parsed intent successfully: {parsed_intent}")
                return parsed_intent
            else:
                logger.warning(f"⚠️ [INTENT] Could not extract JSON from response")
                return {"needs_tools": False, "reasoning": "Could not parse intent"}
                
        except json.JSONDecodeError as e:
            logger.error(f"💥 [INTENT] JSON decode error: {e}")
            return {"needs_tools": False, "reasoning": f"JSON parse error: {e}"}
        except Exception as e:
            logger.error(f"💥 [INTENT] Intent analysis failed: {e}")
            import traceback
            logger.error(f"📋 [INTENT] Full traceback: {traceback.format_exc()}")
            return {"needs_tools": False, "reasoning": f"Analysis error: {e}"}
            
    async def _generate_response(self, user_message: str, intent: Dict[str, Any], tool_results: List[Dict[str, Any]]) -> str:
        """Generate the final response using Bedrock."""
        
        # Build context
        context_parts = [f"User request: {user_message}"]
        
        if tool_results:
            context_parts.append("Tool results:")
            for result in tool_results:
                context_parts.append(f"- {result['tool']}: {json.dumps(result['result'], indent=2)}")
        
        context = "\n".join(context_parts)
        
        # Create response prompt
        prompt = f"""You are an AWS infrastructure assistant. Provide a helpful, clear response to the user.

{context}

RESPONSE GUIDELINES:
- Use French for the response (the user is French-speaking)
- Be specific and actionable - provide exact commands when possible
- If tool results show success, confirm what was accomplished
- If tool results show errors, explain them clearly and provide solutions
- Include relevant resource IDs, regions, and parameters
- For complex operations, break down into clear steps
- Be concise but informative

RESPONSE STRUCTURE:
1. Acknowledge what was requested
2. Explain what was done (if successful) or what went wrong (if error)
3. Provide next steps or additional commands if needed
4. Offer to help with related tasks

EXAMPLES OF GOOD RESPONSES:
- For successful VPC deletion: "✅ Le VPC vpc-xxx a été supprimé avec succès dans la région ca-central-1."
- For subnet creation: "Pour créer des sous-réseaux dans ca-central-1a, utilisez: aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24 --availability-zone ca-central-1a"
- For errors: "❌ Erreur: [explanation]. Pour résoudre: [solution steps]"

Response:"""

        try:
            response = await self._call_bedrock(prompt, max_tokens=1000)
            return response.strip()
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return f"Je suis désolé, je n'ai pas pu générer une réponse: {str(e)}"
            
    async def _call_bedrock(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call Bedrock to generate a response."""
        
        logger.info(f"🤖 [BEDROCK] Calling Bedrock with {len(prompt)} char prompt")
        logger.info(f"🤖 [BEDROCK] Model: {self.app_config.bedrock_model_id}")
        logger.info(f"🤖 [BEDROCK] Max tokens: {max_tokens}")
        logger.info(f"🤖 [BEDROCK] Temperature: {self.app_config.temperature}")
        
        # Use the correct format for Claude models
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": self.app_config.temperature,
            "top_p": self.app_config.top_p
        }
        
        logger.info(f"🤖 [BEDROCK] Request body: {json.dumps(body, indent=2)}")
        
        try:
            start_time = time.time()
            response = self.bedrock_client.invoke_model(
                modelId=self.app_config.bedrock_model_id,
                body=json.dumps(body)
            )
            end_time = time.time()
            
            logger.info(f"🤖 [BEDROCK] Response received in {end_time - start_time:.2f}s")
            
            response_body = json.loads(response['body'].read())
            logger.info(f"🤖 [BEDROCK] Response body: {json.dumps(response_body, indent=2)}")
            
            if 'content' in response_body and response_body['content']:
                result = response_body['content'][0]['text']
                logger.info(f"✅ [BEDROCK] Generated response ({len(result)} chars)")
                logger.info(f"📋 [BEDROCK] Response preview: {result[:200]}...")
                return result
            else:
                logger.error(f"❌ [BEDROCK] Invalid response format")
                raise Exception("Invalid response format from Bedrock")
                
        except Exception as e:
            logger.error(f"💥 [BEDROCK] Call failed: {e}")
            import traceback
            logger.error(f"📋 [BEDROCK] Full traceback: {traceback.format_exc()}")
            raise
            
    def _validate_and_fix_tool_arguments(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix tool arguments based on official MCP server schemas."""
        
        logger.info(f"🔧 [VALIDATE] Validating arguments for tool: {tool_name}")
        logger.info(f"🔧 [VALIDATE] Original arguments: {json.dumps(arguments, indent=2)}")
        
        # Get the tool schema
        if tool_name not in self.mcp_client.tools:
            logger.warning(f"⚠️ [VALIDATE] Tool {tool_name} not found in available tools")
            logger.info(f"📋 [VALIDATE] Available tools: {list(self.mcp_client.tools.keys())}")
            return arguments
            
        tool = self.mcp_client.tools[tool_name]
        logger.info(f"✅ [VALIDATE] Found tool schema for {tool_name}")
        
        # Common argument fixes based on official AWS Labs MCP servers
        fixed_arguments = arguments.copy()
        fixes_applied = []
        
        if tool_name == "aws-api:call_aws":
            # Fix: command → cli_command
            if "command" in fixed_arguments and "cli_command" not in fixed_arguments:
                fixed_arguments["cli_command"] = fixed_arguments.pop("command")
                fixes_applied.append("command → cli_command")
                
        elif tool_name == "aws-api:suggest_aws_commands":
            # Fix: command → query
            if "command" in fixed_arguments and "query" not in fixed_arguments:
                fixed_arguments["query"] = fixed_arguments.pop("command")
                fixes_applied.append("command → query")
                
        elif tool_name == "aws-docs:search_documentation":
            # Fix: search → search_phrase
            if "search" in fixed_arguments and "search_phrase" not in fixed_arguments:
                fixed_arguments["search_phrase"] = fixed_arguments.pop("search")
                fixes_applied.append("search → search_phrase")
                
        if fixes_applied:
            logger.info(f"🔧 [VALIDATE] Applied fixes: {', '.join(fixes_applied)}")
        else:
            logger.info(f"✅ [VALIDATE] No fixes needed - arguments already correct")
                
        # Validate against schema if available
        if hasattr(tool, 'input_schema') and tool.input_schema:
            schema = tool.input_schema
            logger.info(f"📋 [VALIDATE] Tool schema: {json.dumps(schema, indent=2)}")
            
            if 'properties' in schema:
                required_params = schema.get('required', [])
                available_params = list(schema['properties'].keys())
                
                logger.info(f"📋 [VALIDATE] Required params: {required_params}")
                logger.info(f"📋 [VALIDATE] Available params: {available_params}")
                
                # Check for missing required parameters
                missing_params = []
                for param in required_params:
                    if param not in fixed_arguments:
                        missing_params.append(param)
                        
                if missing_params:
                    logger.warning(f"⚠️ [VALIDATE] Missing required parameters: {missing_params}")
                else:
                    logger.info(f"✅ [VALIDATE] All required parameters present")
                        
                # Remove unknown parameters
                unknown_params = [p for p in fixed_arguments.keys() if p not in available_params]
                for param in unknown_params:
                    logger.warning(f"⚠️ [VALIDATE] Removing unknown parameter: {param}")
                    fixed_arguments.pop(param)
                    
                if unknown_params:
                    logger.info(f"🔧 [VALIDATE] Removed unknown parameters: {unknown_params}")
        else:
            logger.info(f"📋 [VALIDATE] No schema available for validation")
                    
        logger.info(f"✅ [VALIDATE] Final arguments: {json.dumps(fixed_arguments, indent=2)}")
        return fixed_arguments
        
    def _format_tools_for_prompt(self, tools: List[Dict[str, Any]]) -> str:
        """Format tools for inclusion in prompts."""
        if not tools:
            return "No tools available"
            
        formatted = []
        for tool in tools:
            formatted.append(f"- {tool['server_name']}:{tool['name']}: {tool['description']}")
            
        return "\n".join(formatted)
        
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
        
    async def cleanup(self):
        """Clean up resources."""
        self.mcp_client.cleanup()  # Synchronous cleanup
        logger.info("Simple Agent cleanup completed")
