import csv
import boto3


def apply_tag():

#------------------------------------------------------------------------------------------
    instance_name= []
    instance_id = []
    count = 1
    try:
        session = boto3.Session(profile_name="interthinx") #you can change if you are using any other aws profile
        ec2client = session.client('ec2', region_name="us-west-2")

        response = ec2client.describe_instances()


        mytags = [{"Key": "Patch Group", "Value": "RC"}]

        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                inst_id = instance["InstanceId"]
                try:
                    existing_tags = instance["Tags"]
                    for tags in existing_tags:
                        if tags['Key'] == 'Environment':
                            if str(tags['Value']).endswith("RC"):
                                print(str(count)+ ": " + str(tags['Value']) + ": " + str(inst_id))
                                count+=1
                                ec2client.create_tags(DryRun=False, Resources=[inst_id], Tags=mytags)
                except Exception as e:
                    print("No tags associated with the instance: " + str(inst_id) + "\n" + str(e))

    except Exception as e:
        print("Something went wrong: " + str(e))
#------------------------------------------------------------------------------------------

if __name__ == "__main__":
    apply_tag()
