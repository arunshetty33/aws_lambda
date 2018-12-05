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
SNS_TOPIC = 'arn:aws:sns:us-west-2:account-ID:TopicName'
SNS_SUBJECT = 'SBX Patch Compliance Update'

def lambda_handler(event, context):
    # Get compliance details
    non_compliant_detail = CONFIG_CLIENT.describe_instance_patch_states_for_patch_group(PatchGroup='SBX')
    resource_data = {}
    if len(non_compliant_detail['InstancePatchStates']) >= 0:
        for result in non_compliant_detail['InstancePatchStates']:
#            resource_data[result['InstanceId']] = 'PatchGroup: ' + result['PatchGroup'] + ', Patch-InstalledCount: ' + str(result['InstalledCount']) + ', Patch-MissingCount: ' + str(result['MissingCount']) + ', Patch-FailedCount: ' + str(result['FailedCount']) + ', Patch-InstalledCount: ' + str(result['InstalledCount']) + ', Time: ' + str(result['OperationStartTime']) 
            resource_data[result['InstanceId']] = 'PatchGroup: ' + result['PatchGroup'] + ', Patch-InstalledCount: ' + str(result['InstalledCount']) + ', Patch-MissingCount: ' + str(result['MissingCount']) + ', Patch-FailedCount: ' + str(result['FailedCount']) + ', Patch-InstalledCount: ' + str(result['InstalledCount']) + ', Time: ' + str(result['OperationStartTime']) + "\n"
        
        sns_message = 'AWS Config Compliance Update\n\n' \
     		    	+ 'The following resource(s) are not compliant:\n' \
     		    	+  str(resource_data)
        SNS_CLIENT.publish(TopicArn=SNS_TOPIC, Message=sns_message, Subject=SNS_SUBJECT)
        return resource_data
    
