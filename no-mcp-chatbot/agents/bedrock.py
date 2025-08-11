import os
import boto3

from langchain.chains import ConversationChain
from langchain.llms.bedrock import Bedrock
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from langchain.agents import AgentType, ZeroShotAgent, Tool, AgentExecutor, initialize_agent, load_tools

# Import Search Tool
from langchain.utilities import SerpAPIWrapper

# Import Custom Tools
from agents.tools import tool_search_ec2_instances_by_tag, tool_start_ec2_instance, tool_stop_ec2_instance, tool_search_all_ec2_instances, tool_get_ec2_instance_launcher, tool_get_ec2_instance_stopper, tool_list_s3_buckets

# Import configuration
try:
    from config import set_environment, AWS_PROFILE, AWS_DEFAULT_REGION, BEDROCK_MODEL_ID, TEMPERATURE, TOP_P, MAX_TOKENS
    set_environment()
except ImportError:
    print("⚠️  Configuration file not found. Please copy config.py.template to config.py and update with your values.")
    print("Using default values for now...")
    AWS_PROFILE = "default"
    AWS_DEFAULT_REGION = "us-east-1"
    BEDROCK_MODEL_ID = "anthropic.claude-v2"
    TEMPERATURE = 0.0
    TOP_P = 0.5
    MAX_TOKENS = 2000
    os.environ["AWS_PROFILE"] = AWS_PROFILE
    os.environ["AWS_DEFAULT_REGION"] = AWS_DEFAULT_REGION

def bedrock_chain():
    profile = os.environ.get("AWS_PROFILE", "default")

    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
    )
    
    llm = Bedrock(
        model_id=BEDROCK_MODEL_ID, 
        client=bedrock_runtime, 
        credentials_profile_name=profile
    )
    llm.model_kwargs = {
        "temperature": TEMPERATURE, 
        "top_p": TOP_P, 
        "max_tokens_to_sample": MAX_TOKENS
    }

    # Initialize tools list
    tools = []
    
    # Add web search tool if SerpAPI key is available
    if os.environ.get("SERPAPI_API_KEY") and os.environ.get("SERPAPI_API_KEY") != "your-serpapi-key-here":
        search = SerpAPIWrapper()
        tools.append(Tool(
            name="Search",
            func=search.run,
            description="useful for when you need to answer questions about current events. "
                        "You should ask targeted questions"
        ))

    # Add AWS tools
    tools.extend([
        tool_search_ec2_instances_by_tag(),
        tool_search_all_ec2_instances(),
        tool_start_ec2_instance(),
        tool_stop_ec2_instance(),
        tool_get_ec2_instance_launcher(),
        tool_get_ec2_instance_stopper(),
        tool_list_s3_buckets()
    ])
    
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        k=5,
        return_messages=True)
    
    react_agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        max_iteration=2,
        return_intermediate_steps=False,
        handle_parsing_errors=True
    )

    return react_agent

def run_chain(chain, prompt):
    # num_tokens = chain.llm.get_num_tokens(prompt)
    num_tokens = 2
    return chain({"input": prompt}), num_tokens

def clear_memory(chain):
    return chain.memory.clear()
