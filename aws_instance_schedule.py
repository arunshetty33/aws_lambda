from __future__ import print_function # Python 2/3 compatibility
import boto3
import datetime
import sys

def lambda_handler(event, context):
    schedule_tag = 'Running Schedule' #Tag name of instance
    max_delta = 12
    now = datetime.datetime.now()
    ec2 = boto3.resource('ec2')
    client = boto3.client('ec2')
    scheduled_instances = []
    processed_instances = []
    #filter for instances with the correct tag
    instances = ec2.instances.filter(Filters=[{'Name': 'tag:Opt Out', 'Values': ['false',""]}])

    #{'Name':'tag:role', 'Values':[Role]}

    #grab the scheduler string
    for instance in instances:
        for tag in instance.tags:
            if tag['Key'] == 'Running Schedule':
                scheduled_instances.append({'instance':instance, 'schedule':tag['Value']})

    def parse_schedule(instance_hold):
        day = now.strftime('%a').lower()
        current_time = datetime.datetime.strptime(now.strftime("%H%M"), "%H%M")
        instance_hold['disabled'] = False
        #parse the schedule string into seperate tokens
        tokenized_schedule = instance_hold['schedule'].split(';')
        #make sure the schedule string contains either 4 or 5 parameters.
        if len(tokenized_schedule) < 4:
            try:
                instance_hold['disabled'] = True
            except:
                pass
        if len(tokenized_schedule) > 6:
            try:
                instance_hold['disabled'] = True
            except:
                pass
        #check to make sure today is the day to execute an on action
        if day in tokenized_schedule[0]:
            try:
                #check to make sure 24 hour string parses correctly
                scheduled_time_for_on = datetime.datetime.strptime(tokenized_schedule[1], "%H%M")
                #as long as not outside of the window of execution
                delta = scheduled_time_for_on - current_time
                margin = datetime.timedelta(minutes=max_delta)
                if(current_time - margin <= scheduled_time_for_on <= current_time):
                    instance_hold['on'] = True
                else:
                    instance_hold['on'] = False
            except Exception as e:
                print(e)
                instance_hold['disabled'] = True
                sys.exit('Time string for the on action improperly formed. Ensure in HHMM format.')
        else:
            instance_hold['on'] = False

        #check to make sure today is the day to execute an off action
        if day in tokenized_schedule[2]:
            try:
                #check to make sure 24 hour string parses correctly
                scheduled_time_for_off = datetime.datetime.strptime(tokenized_schedule[3], "%H%M")
                delta = scheduled_time_for_off - current_time
                margin = datetime.timedelta(minutes=max_delta)
                if(current_time - margin <= scheduled_time_for_off <= current_time):
                   instance_hold['off'] = True
                else:
                    instance_hold['off'] = False
            except Exception as e:
                print(e)
                instance_hold['disabled'] = True
                sys.exit('Time string for the on action improperly formed. Ensure in HHMM format.')
        else:
            instance_hold['off'] = False

        #check for disabled string
        if len(tokenized_schedule) > 4:
            if '24by7' in tokenized_schedule[4]:
                instance_hold['disabled'] = True
        return instance_hold

    for instance_hold in scheduled_instances:
        try:
            processed_instances.append(parse_schedule(instance_hold))
        except:
            pass

    for instance_hold in processed_instances:
        if(instance_hold['disabled']==False):
            try:
                if(instance_hold['off']==True and instance_hold['on']==True):
                   print('Both on and off actions specified for this time window. Doing nothing.')
                if(instance_hold['off']==True and instance_hold['on']==False):
                   print('Turning instance off: ' + instance_hold['instance'].id + ' ' + instance_hold['instance'].instance_type)
                   client.stop_instances(InstanceIds=[instance_hold['instance'].id])
                if(instance_hold['off']==False and instance_hold['on']==True):
                   print('Turning instance on: ' + instance_hold['instance'].id + ' ' + instance_hold['instance'].instance_type)
                   client.start_instances(InstanceIds=[instance_hold['instance'].id])
                if(instance_hold['off']==False and instance_hold['on']==False):
                   print('No action on instance: ' + instance_hold['instance'].id + ' ' + instance_hold['instance'].instance_type)
            except:
                 print ('Schedule disabled: ' + instance_hold['instance'].id + ' ' + instance_hold['instance'].instance_type)
