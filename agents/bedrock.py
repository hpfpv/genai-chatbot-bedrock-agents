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


os.environ["AWS_PROFILE"] = "bedrock-agent"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
# os.environ["BEDROCK_ASSUME_ROLE"] = "arn:aws:iam::655843031706:role/iamrole-bedrock"
os.environ["SERPAPI_API_KEY"] = "68d2242a277053d3655cfd28afee8b5e80fb559c3d4991586f34760634ff4a69"

def bedrock_chain():
    profile = os.environ["AWS_PROFILE"]

    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
    )
    
    llm = Bedrock(
        model_id="anthropic.claude-v2", client=bedrock_runtime, credentials_profile_name=profile
        # model_id="anthropic.claude-instant-v1", client=bedrock_runtime, credentials_profile_name=profile
    )
    llm.model_kwargs = {"temperature": 0.0, "top_p": .5, "max_tokens_to_sample": 2000}

    search = SerpAPIWrapper()

    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="useful for when you need to answer questions about current events. "
                        "You should ask targeted questions"
        )
    ]

    tools.append(tool_search_ec2_instances_by_tag())
    tools.append(tool_search_all_ec2_instances())
    tools.append(tool_start_ec2_instance())
    tools.append(tool_stop_ec2_instance())
    tools.append(tool_stop_ec2_instance())
    tools.append(tool_get_ec2_instance_launcher())
    tools.append(tool_get_ec2_instance_stopper())
    tools.append(tool_list_s3_buckets())
    
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        k=5,
        return_messages=True)
    
    react_agent = initialize_agent(
        tools, 
        llm, 
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        # agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, CHAT_ZERO_SHOT_REACT_DESCRIPTION 
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