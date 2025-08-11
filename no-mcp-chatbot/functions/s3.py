import boto3
import json

client = boto3.client('s3', region_name="us-east-1")

def list_s3_buckets() :
    """Function to list all S3 buckets"""
    try:
        response = client.list_buckets()
        buckets = []
        for bucket in response['Buckets']:
            buckets.append(bucket['Name'])

        return response

    except Exception as e:
        return str(e)