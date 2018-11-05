import boto3
import json
from bson import json_util
# Health constant
REGION = 'us-west-1'
# Function for describe_event (Specify desired information and acquire event.)


def get_describe_event(services, event_status_codes):
    health = boto3.client('health', region_name=REGION)
    response = health.describe_events(
       filter={
          'services': services,
          'eventStatusCodes': event_status_codes
       }
    )
    return response


def get_describe_event_details(event_arns):
    health = boto3.client('health', region_name=REGION)
    response = health.describe_event_details(eventArns=event_arns)
    return response


def get_describe_affected_entities(event_arns):
    health = boto3.client('health', region_name=REGION)
    response = health.describe_affected_entities(
       filter={
           'eventArns': event_arns
        }
    )
    return response


def main():
    services = ['VPN']
    event_status_codes = ['open', 'upcoming']
    result = get_describe_event(services, event_status_codes)
    print("starting describe event")
    print(json.dumps(result, default=json_util.default, sort_keys=True, indent=4))
    print("end of describe event")
    event_arns = []
    for event in result['events']:
        event_arns.append(event['arn'])
    result = get_describe_event_details(event_arns)
    print("starting describe event details")
    print(json.dumps(result, default=json_util.default, sort_keys=True, indent=4))
    print("end of describe event details")
    result = get_describe_affected_entities(event_arns)
    print("starting describe affected entities")
    print(json.dumps(result, default=json_util.default, sort_keys=True, indent=4))
    print("end of describe affected entities")


if __name__ == '__main__':
    main()