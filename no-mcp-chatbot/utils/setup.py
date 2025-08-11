import warnings
warnings.filterwarnings('ignore')

import json
import os
import sys
import boto3

module_path = ".."
sys.path.append(os.path.abspath(module_path))
from utils import bedrock, print_ww

os.environ["AWS_PROFILE"] = "bedrock-agent"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["BEDROCK_ASSUME_ROLE"] = "arn:aws:iam::655843031706:role/iamrole-bedrock"
os.environ["SERPAPI_API_KEY"] = "68d2242a277053d3655cfd28afee8b5e80fb559c3d4991586f34760634ff4a69"


boto3_bedrock = bedrock.get_bedrock_client(
    assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
    region=os.environ.get("AWS_DEFAULT_REGION", None),
)

model_parameter = {"temperature": 0.0, "top_p": .5, "max_tokens_to_sample": 2000}