from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

from functions.ec2 import search_ec2_instances_by_tag, start_ec2_instance, search_all_ec2_instances, stop_ec2_instance, get_ec2_instance_stopper, get_ec2_instance_launcher
from functions.s3 import list_s3_buckets

class input_search_ec2_instances_by_tag(BaseModel):
    """Inputs for search_ec2_instances_by_tag function"""

    attribute: str = Field(description="A tag key to search for")

class tool_search_ec2_instances_by_tag(BaseTool):
    name = "search_ec2_instances_by_tag"
    description = """
        Useful when you want to lists EC2 Instances by tag key.
        You should enter the tag key you want to search for.
        """
    args_schema: Type[BaseModel] = input_search_ec2_instances_by_tag

    def _run(self, attribute: str):
        response = search_ec2_instances_by_tag(attribute)
        return response

    def _arun(self, attribute: str):
        raise NotImplementedError(
            "search_ec2_instances_by_tag does not support async calls")
    
################################################################

# class input_search_all_ec2_instances(BaseModel):
#     """Inputs for search_all_ec2_instances function"""
#     attribute: str = None


class tool_search_all_ec2_instances(BaseTool):
    name = "search_all_ec2_instances"
    description = """
        Useful when you want to lists all EC2 Instances.
        No input needed.
        """
    args_schema: Type[BaseModel] = None

    def _run(self):
        response = search_all_ec2_instances()
        return response

    def _arun(self):
        raise NotImplementedError(
            "search_all_ec2_instances does not support async calls")
    
################################################################

class input_start_ec2_instance(BaseModel):
    """Inputs for start_ec2_instance function"""

    attribute: str = Field(description="The instance id to start")

class tool_start_ec2_instance(BaseTool):
    name = "start_ec2_instance"
    description = """
        Useful when you want to start an EC2 Instance.
        You should enter the instance id you want to start.
        Returns a map of instance id with the current state.
        """
    args_schema: Type[BaseModel] = input_start_ec2_instance

    def _run(self, attribute: str):
        response = start_ec2_instance(attribute)
        return response

    def _arun(self, attribute: str):
        raise NotImplementedError(
            "start_ec2_instance not support async calls")
    
################################################################

class input_stop_ec2_instance(BaseModel):
    """Inputs for stop_ec2_instance function"""

    attribute: str = Field(description="The instance id to stop")

class tool_stop_ec2_instance(BaseTool):
    name = "stop_ec2_instance"
    description = """
        Useful when you want to stop an EC2 Instance.
        You should enter the instance id you want to stop.
        Returns a map of instance id with the current state.
        """
    args_schema: Type[BaseModel] = input_stop_ec2_instance

    def _run(self, attribute: str):
        response = stop_ec2_instance(attribute)
        return response

    def _arun(self, attribute: str):
        raise NotImplementedError(
            "stop_ec2_instance not support async calls")

################################################################

# class input_list_s3_buckets(BaseModel):
#     """Inputs for list_s3_buckets function"""
#     attribute: str = None

class tool_list_s3_buckets(BaseTool):
    name = "list_s3_buckets"
    description = """
        Useful when you want to lists all S3 Buckets.
        No input needed.
        """
    args_schema: Type[BaseModel] = None

    def _run(self):
        response = list_s3_buckets()
        return response

    def _arun(self):
        raise NotImplementedError(
            "list_s3_buckets does not support async calls")
    
################################################################

class input_get_ec2_instance_launcher(BaseModel):
    """Inputs for get_ec2_instance_launcher function"""

    attribute: str = Field(description="The instance id to check for")

class tool_get_ec2_instance_launcher(BaseTool):
    name = "get_ec2_instance_launcher"
    description = """
        Useful when you want to check who launched an EC2 Instance.
        You should enter the instance id to check for.
        Returns a map of instance id with the username who launched the instance and the time of the event.
        """
    args_schema: Type[BaseModel] = input_get_ec2_instance_launcher

    def _run(self, attribute: str):
        response = get_ec2_instance_launcher(attribute)
        return response

    def _arun(self, attribute: str):
        raise NotImplementedError(
            "get_ec2_instance_launcher not support async calls")
    
################################################################

class input_get_ec2_instance_stopper(BaseModel):
    """Inputs for get_ec2_instance_stopper function"""

    attribute: str = Field(description="The instance id to check for")

class tool_get_ec2_instance_stopper(BaseTool):
    name = "get_ec2_instance_stopper"
    description = """
        Useful when you want to check who stopped an EC2 Instance.
        You should enter the instance id to check for.
        Returns a map of instance id with the username who stopped the instance and the time of the event.
        """
    args_schema: Type[BaseModel] = input_get_ec2_instance_stopper

    def _run(self, attribute: str):
        response = get_ec2_instance_stopper(attribute)
        return response

    def _arun(self, attribute: str):
        raise NotImplementedError(
            "get_ec2_instance_stopper not support async calls")