'''
Lambda function to poll Config for noncompliant resources
'''
from __future__ import print_function
import boto3
# AWS Config settings
CONFIG_CLIENT = boto3.client('config')
MY_RULE = "Windows-Patch-Compliance"

# AWS SNS Settings
SNS_CLIENT = boto3.client('sns')
SNS_TOPIC = 'arn:aws:sns:us-west-2:666678657097:AWS-HEALTH-STATUS'
SNS_SUBJECT = 'SBX Patch Compliance Update'

def lambda_handler(event, context):
    # Get compliance details
    non_compliant_detail = CONFIG_CLIENT.get_compliance_details_by_config_rule(\
    						ConfigRuleName=MY_RULE, ComplianceTypes=['NON_COMPLIANT'])

    if len(non_compliant_detail['EvaluationResults']) > 0:
        print('The following resource(s) are not compliant with AWS Config rule: ' + MY_RULE)
        non_complaint_resources = ''
        for result in non_compliant_detail['EvaluationResults']:
            print(result['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId'])
            non_complaint_resources = non_complaint_resources + \
    	    				result['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId'] + '\n'

        sns_message = 'AWS Config Compliance Update\n\n Rule: ' \
    				+ MY_RULE + '\n\n' \
     				+ 'The following resource(s) are not compliant:\n' \
     				+ non_complaint_resources

        SNS_CLIENT.publish(TopicArn=SNS_TOPIC, Message=sns_message, Subject=SNS_SUBJECT)

    else:
<<<<<<< HEAD
        print('No noncompliant resources detected.')
=======
        print('No noncompliant resources detected.')
>>>>>>> a29664c900cbbaadbe71ae359bb6562f42ed949a
