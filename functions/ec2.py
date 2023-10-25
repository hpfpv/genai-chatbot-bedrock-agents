import boto3
import json

client = boto3.client('ec2', region_name="us-east-1")

def search_ec2_instances_by_tag(tag_key: str):
    """Function to return the list of EC2 instances for a given tag"""
    try:
        if 'tag:' in tag_key:
            response = client.describe_instances(Filters=[{'Name': f'{tag_key}', 'Values': ['*']}])
        elif 'tag=' in tag_key:
            response = client.describe_instances(Filters=[{'Name': f"tag:{tag_key.split('=')[1]}", 'Values': ['*']}])
        else:
            response = client.describe_instances(Filters=[{'Name': f'tag:{tag_key}', 'Values': ['*']}])

        instances = []
        if response['Reservations'] == []:
            # print(f"no instances found with tag {tag_key}") 
            return None
        else:
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_state = instance['State']['Name']
                    private_ip = instance.get('PrivateIpAddress', 'N/A')
                    public_ip = instance.get('PublicIpAddress', 'N/A')

                    instances.append({
                        'Instance ID': instance_id,
                        'State': instance_state,
                        'Private IP': private_ip,
                        'Public IP': public_ip,
                    })
            # print(f"found instances with tag {tag_key}: {instances}") 
            return instances

    except Exception as e:
        return str(e)

def search_all_ec2_instances():
    """Function to return the list of all EC2 instances"""
    try:    
        response = client.describe_instances()

        instances = []
        if response['Reservations'] == []:
            # print(f"no instances found") 
            return None
        else:
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_state = instance['State']['Name']
                    private_ip = instance.get('PrivateIpAddress', 'N/A')
                    public_ip = instance.get('PublicIpAddress', 'N/A')

                    instances.append({
                        'Instance ID': instance_id,
                        'State': instance_state,
                        'Private IP': private_ip,
                        'Public IP': public_ip,
                    })
            # print(f"found instances : {instances}") 
            return instances

    except Exception as e:
        return str(e)
    
def start_ec2_instance(instance_id):
    """Function to start an instance given instance id"""
    try:
        ec2 = boto3.client('ec2', region_name="us-east-1")

        response = ec2.start_instances(InstanceIds=[instance_id])

        result = {
            'InstanceId': response["StartingInstances"][0]["InstanceId"],
            'CurrentState': response["StartingInstances"][0]["CurrentState"]["Name"]
        } 

        # print(f"started EC2 instance with ID: {instance_id}")
        return result

    except Exception as e:
        return str(e)
    
def stop_ec2_instance(instance_id):
    """Function to stop an instance given an instance id"""
    try:
        ec2 = boto3.client('ec2', region_name="us-east-1")

        response = ec2.stop_instances(InstanceIds=[instance_id])

        result = {
            'InstanceId': response["StoppingInstances"][0]["InstanceId"],
            'CurrentState': response["StoppingInstances"][0]["CurrentState"]["Name"]
        } 

        # print(f"stopped  EC2 instance with ID: {instance_id}")
        return result

    except Exception as e:
        return str(e)
    
def get_ec2_instance_launcher(instance_id):
    """Function to check who launched an EC2 instance """
    try:
        cloudtrail = boto3.client('cloudtrail', region_name="us-east-1")

        response = cloudtrail.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'ResourceName',
                    'AttributeValue': instance_id
                },
                {
                    'AttributeKey': 'EventName',
                    'AttributeValue': 'StartInstances'
                }
            ]
        )
        for event in response['Events']:
            username = None
            for resource in event['Resources']:
                if resource['ResourceName'] == instance_id:
                    username = event['Username']

            if username:
                result = {
                    'InstanceId': instance_id,
                    'Launched_By': username,
                    'Event_Time': event['EventTime']
                } 
                break

        # If 'username' is still None, no relevant events were found.
        if username is None:
            result = {
                    'InstanceId': instance_id,
                    'Launched_By': "No launch events found for instance"
                }

        return result

    except Exception as e:
        return str(e)
    
def get_ec2_instance_stopper(instance_id):
    """Function to check who stopped an EC2 instance """
    try:
        cloudtrail = boto3.client('cloudtrail', region_name="us-east-1")

        response = cloudtrail.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'ResourceName',
                    'AttributeValue': instance_id
                },
                {
                    'AttributeKey': 'EventName',
                    'AttributeValue': 'StartInstances'
                }
            ]
        )
        for event in response['Events']:
            username = None
            for resource in event['Resources']:
                if resource['ResourceName'] == instance_id:
                    username = event['Username']

            if username:
                result = {
                    'InstanceId': instance_id,
                    'Stopped_By': username,
                    'Event_Time': event['EventTime']
                } 
                break

        # If 'username' is still None, no relevant events were found.
        if username is None:
            result = {
                    'InstanceId': instance_id,
                    'Stopped_By': "No stop events found for instance"
                }

        return result

    except Exception as e:
        return str(e)


