####
# retrieve all instances from AWS account
# 1) list all running instnaces in all regions along with their owner and tags
# 2) list all running databases, 
# 3) list all used EBS, and then other resources.

import csv
import itertools
import configparser
import os
import time
import jmespath
import boto3
import html

max_results = 10 

# Get list of profiles
config = configparser.ConfigParser()
path = os.path.join(os.path.expanduser('~'), '/Users/eran/projects/AWS/ERAN-AWS-cred')
config.read(path)
profiles = config.sections()

# Get list of regions
ec2_client = boto3.client('ec2')
regions = [region['RegionName']
            for region in ec2_client.describe_regions()['Regions']]

# Get list of EC2 attributes from all profiles and regions
myData = []
for profile in profiles:
    for region in regions:
        current_session = boto3.Session(profile_name = profile, region_name = region)
        client = current_session.client('ec2')
        response = client.describe_instances()
        output = jmespath.search("Reservations[].Instances[].[NetworkInterfaces[0].OwnerId, InstanceId, InstanceType, \
            State.Name, Placement.AvailabilityZone, PrivateIpAddress, PublicIpAddress, KeyName, [Tags[?Key=='Name'].Value] [0][0]]", response)
        myData.append(output)

#prepare output file
timestr = time.strftime("%Y%m%d-%H%M%S")
outpufile = f"ec2-inventory-{timestr}.csv"

# Write myData to CSV file with headers
output = list(itertools.chain(*myData))
with open(outpufile, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(['Type','State','Name','AZ','InstanceID','PublicIP','KeyPair', 'tags'])

    #Write each line to file.
    for line in output:
        if line[3] == 'running':
            #if row status is Running
            #   write to list only: (['Type','State','Name','AZ','InstanceID','PublicIP','KeyPair'])
            #   newline = f"{line[2]}, {line[3]}, {line[8]}, {line[4]}, {line[6]}, {line[7]}"
            #print(newline)
            # get the tags:
            # Call the describe_tags method to retrieve the tags for the specified instance
            response = get_instance_tags(current_session, line[4],line[1])
            client = current_session.client('ec2', region_name=line[4])
            instance_id = line[1]
            response = client.describe_tags(InstanceId=instance_id)
            response = client.describe_tags(
                InstanceId=instance_id,
                Filters={
                    'key': {'FilterType': 'KeyEquals', 'Value': 'owner'},
                    'value': {'FilterType': 'StringLike', 'Value': '%myTagValue%'}
                },
                MaxResults=max_results
            )
            
            response = "no tags"
            print(response)
            newline2 = [line[2], line[3], line[8], line[4], line[6], line[7], response]
            writer.writerow(newline2)

create_html_file(output)

def get_regions_list():
    # Get list of regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName']
                for region in ec2_client.describe_regions()['Regions']]
    return regions

def create_html_file(lst):
    # Get the maximum widths for each column
    max_widths = {}
    for i, item in enumerate(lst):
        for key, value in item.items():
            if key not in max_widths:
                max_widths[key] = len(str(value))
            else:
                max_widths[key] = max(max_widths[key], len(str(value)))
    
    # Create the table header row
    header_row = "<tr>" + "".join([f"<th style='{k}: {max_widths[k]}px'>{k}</th>" for k in lst[0].keys()]) + "</tr>"
    
    # Create the body rows
    body_rows = []
    for row in range(1, len(lst)):
        body_row = "<tr>" + "".join([f"<td style='{k}: {max_widths[k]}px'>{item[k]}]</td>" for k in lst[0].keys()]) + "</tr>"
        body_rows.append(body_row)
    
    # Combine everything into one string
    return f"<table>{header_row}<tbody>{ (',').join(body_rows)}</tbody></table>"



def get_instance_tags(current_session, line[4],line[1]):
    client = current_session.client('ec2', region_name=line[4])
    instance_id = line[1]
    response = client.describe_tags(InstanceId=instance_id)
    response = client.describe_tags(
        InstanceId=instance_id,
        Filters={
            'key': {'FilterType': 'KeyEquals', 'Value': 'owner'},
            'value': {'FilterType': 'StringLike', 'Value': '%myTagValue%'}
        },
        MaxResults=max_results
    )

def describe_instance_tags(ec2client, instance_id):
   response = ec2client.describe_tags(InstanceId=instance_id)
    ##ec2_id = output[0][]
    ec2client = boto3.client('ec2')
    instance_id = output[0][1]
    tagstring = describe_instance_tags(instance_id)