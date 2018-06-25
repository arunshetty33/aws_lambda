import boto3
import logging
from datetime import *
ec2 = boto3.resource('ec2',region_name='eu-west-1')
sns = boto3.resource('sns')
platform_endpoint = sns.PlatformEndpoint('add endpoint of your SNS topic'')

#set the date to today for the snapshot
today = datetime.now().date()

def lambda_handler(event, context):

    #report header (You can change it as per your requirement)
    VolumesReport = "The Following Volumes are Available State in us-east Region: \n"
    x = 0

    for vol in ec2.volumes.all():
        if  vol.state=='available':

		VolumesReport = VolumesReport + "- " + str(vol.id) + " - Size: " + str(vol.size) + " - Created: " + str(vol.create_time) + "\n"
        x= x + 1

    #only send a report if there are any available Volumes
    if x == 0:
        print "Nothing to Report"
    else:
        response = platform_endpoint.publish(
            Message=VolumesReport,
            #add subject for email body as per your requirement
            Subject='Volumes Available State Report for us-east Region: ' + str(today),
            MessageStructure='string',
        )

        print VolumesReport
