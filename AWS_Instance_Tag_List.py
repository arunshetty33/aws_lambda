#!/usr/bin/env python
#
#  Author: Nick Skitch (CAP team)
#  For Tagging Compliance.
prog_desc = "Generate CSV report of all instance tags"
 
import boto3
import json
import argparse
import csv
from collections import OrderedDict
import xlsxwriter
 
## ----------------------------------------------------
## Configuration variables (defaults)
##
 
required_fields = OrderedDict([('Name',''),('App',''),('AppOwner',''), ('Environment','')])
 
aws_profile_default = "SBX"
aws_region_default = "us-west-2"
## ----------------------------------------------------
 
aws_profile = "SBX"
aws_region = "us-west-2"
outputfile = "test"
 
 
def main():
    validate_script_inputs()
    #test()
    ec2 = connect_aws()
    query_name_tags(ec2, outputfile)
 
 
 
 
def connect_aws():
    print "connecting to aws using the {0} profile".format(aws_profile)
    boto3.setup_default_session(profile_name=aws_profile)
    ec2 = boto3.resource('ec2', region_name=aws_region)
    my_session = boto3.session.Session()
    my_region = my_session.region_name
    print "logged into {0} region".format(my_region)
    print "using {0} account.".format(boto3.client('sts').get_caller_identity()['Account'])
 
    return ec2
 
def query_name_tags(ec2, outputfile):
 
 
    with open(outputfile, 'wb') as outfh:
        writer = csv.writer(outfh)
 
        # header
        header = ["Instance ID", "Launch Time","Instance Type","Private IP Address"]
 
        # append required fields to header of report
        for key, value in required_fields.items():
 
            header.append(key + " tag")
 
        # write the header to report
        writer.writerow(header)
 
        print "Generating report ... "
        for instance in ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]):
            tags_message_leading_cols=[]
            tags_message=[]
 
            # The first few metadata items.
            tags_message_leading_cols.append(instance.id)
            tags_message_leading_cols.append(str(instance.launch_time))
            tags_message_leading_cols.append(instance.instance_type)
            tags_message_leading_cols.append(instance.private_ip_address)
 
 
 
            # some instances don't have ANY tags so this instance
            if instance.tags is None:
                continue
 
            # clear values from last run
            for key, value in required_fields.iteritems():
                required_fields[key] = ""
 
            # iterate through each tag to see if it's a required_field
            for tag in instance.tags:
                for key, value in required_fields.iteritems():
                    if tag['Key'].lower() == key.lower():
                        required_fields[key] = "{0} : {1} ".format(tag['Key'], tag['Value'])
 
 
 
 
            #print tags_message_leading_cols
            merged_tags = tags_message_leading_cols + required_fields.values()
 
            #print merged_tags
 
            writer.writerow(merged_tags)
 
def validate_script_inputs():
 
    parser = argparse.ArgumentParser(description=prog_desc)
    parser.add_argument("--profile", help="AWS profile: "+aws_profile_default, default=aws_profile_default)
    parser.add_argument("--region", help="AWS region: "+aws_region_default, default=aws_region_default)
    parser.add_argument("--output", help="Output filename", default="<profile>_tag_report.csv")
    args = parser.parse_args()
 
    global aws_profile
    aws_profile = args.profile
    if aws_profile == "":
        aws_profile = aws_profile_default
        print "-profile argument not provided, defaulting to "+aws_profile_default
 
    global aws_region
    aws_region = args.region
    if aws_region == "":
        aws_region = aws_region_default
        print "-region argument not provided, defaulting to "+aws_region_default
 
    global outputfile
    outputfile = args.output
    if outputfile == "<profile>_tag_report.csv":
        outputfile = aws_profile + "_tag_report.csv"
 
 
 
if __name__ == "__main__":
    main()