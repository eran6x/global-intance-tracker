####
# retrieve all instances from AWS account
# 1) list all running instnaces in all regions along with their owner and tags
# 2) list all running databases, 
# 3) list all used EBS, and then other resources.

# import boto3

# ec2 = boto3.client('ec2')
# regions = ec2.describe_regions()
# print(regions)

import csv
import itertools
import configparser
import os
import time
import jmespath
import boto3

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

##ec2_id = output[0][]
with open(outpufile, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(['Type','State','Name','AZ','InstanceID','PublicIP','KeyPair'])
    for line in output:
        if line[3] == 'running':
            #if row status is Running
            #   write to list only: (['Type','State','Name','AZ','InstanceID','PublicIP','KeyPair'])
            #newline = f"{line[2]}, {line[3]}, {line[8]}, {line[4]}, {line[6]}, {line[7]}"
            #print(newline)
            newline2 = [line[2], line[3], line[8], line[4], line[6], line[7]]
            writer.writerow(newline2)
            
    #writer.writerow(['AccountID','InstanceID','Type','State','AZ','PrivateIP','PublicIP','KeyPair','Name'])
    #writer.writerows(output)

def get_regions_list():
    # Get list of regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName']
                for region in ec2_client.describe_regions()['Regions']]
    return regions