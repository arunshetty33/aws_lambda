'''
Lambda function to poll Config for noncompliant resources
'''

from __future__ import print_function

import boto3

# AWS Config settings
CONFIG_CLIENT = boto3.client('ssm')
MY_RULE = "Windows-Patch-Compliance"

# AWS SNS Settings
SNS_CLIENT = boto3.client('sns')
SNS_TOPIC = 'arn:aws:sns:us-west-2:666678657097:AWS-HEALTH-STATUS'
SNS_SUBJECT = 'SBX Patch Compliance Update'

def lambda_handler(event, context):
    # Get compliance details
    non_compliant_detail = CONFIG_CLIENT.describe_instance_patch_states_for_patch_group(PatchGroup='SBX')
    resource_data = {}
    if len(non_compliant_detail['InstancePatchStates']) >= 0:
        for result in non_compliant_detail['InstancePatchStates']:
            resource_data[result['InstanceId']] = 'PatchGroup: ' + result['PatchGroup'] + ', Patch-InstalledCount: ' + str(result['InstalledCount']) + ', Patch-MissingCount: ' + str(result['MissingCount']) + ', Patch-FailedCount: ' + str(result['FailedCount']) + ', Patch-InstalledCount: ' + str(result['InstalledCount']) + ', Time: ' + str(result['OperationStartTime']) 
    return resource_data
