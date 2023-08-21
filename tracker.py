####
# retrieve all EC2 instances from AWS account
# 1) list all running instnaces in all regions along with their owner and tags
# 2) list all running RDS databases with tags
# 3) write results to respective CSV files.

import configparser
import csv
import itertools
import os
import time
import json
import boto3
import jmespath

MAX_RESULTS = 10
PATH_TO_CREDENTIALS_JSON = '/Users/eran/projects/AWS/ERAN-AWS-cred'


def main():
    # Get list of profiles
    config = configparser.ConfigParser()
    path = os.path.join(os.path.expanduser('~'), PATH_TO_CREDENTIALS_JSON)
    config.read(path)
    profiles = config.sections()

    # look for EC2: 
    client_name = 'ec2'
    b_client = boto3.client(client_name)
    regions = get_list_of_regions(b_client)
    my_data = describe_ec2_instances(regions, profiles)

    # #prepare output file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    outputfile = f"ec2-inventory-{timestr}.csv"
    write_ec2_data_to_file(outputfile, my_data)

    # look for RDS: 
    my_data = describe_rds_instances(regions)

    #prepare output file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    outputfile = f"rds-inventory-{timestr}.csv"
    write_rds_data_to_file(outputfile, my_data)


def write_ec2_data_to_file(outputfile, my_data):
    # Write my_data to CSV file with headers
    output = list(itertools.chain(*my_data))
    with open(outputfile, "w", newline="", encoding="UTF") as f:
        writer = csv.writer(f)
        writer.writerow(['Type','State','Name','AZ','InstanceID','PublicIP','KeyPair', 'tags'])

        #Write each line to file.
        for line in output:
            if line[3] == 'running':
                newline2 = [line[2], line[3], line[8], line[4], line[6], line[7], "N/A"]
                writer.writerow(newline2)
    f.close

def write_rds_data_to_file(outputfile, my_data):
    # Write my_data to CSV file with headers
    with open(outputfile, "w", newline="", encoding="UTF") as f:
        f.write("AZ, InstanceID , TagList\n")
        for item in my_data:
            f.write(item + "\n")
    f.close


"""Use Boto3 to enumerate all regions"""
def get_list_of_regions(b_client):
    regions = [region['RegionName']
    for region in b_client.describe_regions()['Regions']]
    return regions


def describe_ec2_instances(regions, profiles):
    # Get list of EC2 attributes from all profiles and regions
    my_data = []
    for profile in profiles:
        for region in regions:
            current_session = boto3.Session(profile_name = profile, region_name = region)
            client = current_session.client('ec2')
            response = client.describe_instances()
            output = jmespath.search("Reservations[].Instances[].[NetworkInterfaces[0].OwnerId, InstanceId, InstanceType, \
                State.Name, Placement.AvailabilityZone, PrivateIpAddress, PublicIpAddress, KeyName, [Tags[?Key=='Name'].Value] [0][0]]", response)
            my_data.append(output)
    return my_data


def describe_rds_instances(regions):
    my_data = []

    # Loop through the regions and list the RDS instances in each region
    for region in regions:
        # Create a boto3 client for the region
        rds_client = boto3.client('rds', config=boto3.session.Config(region))

        # List the RDS instances in the region
        response = rds_client.describe_db_instances()
        if (len(response['DBInstances']) > 0 ):
            for instance in response['DBInstances']:
                line = region  + ',' + instance['DBInstanceIdentifier'] + ',' + json.dumps(instance['TagList'])
                my_data.append(line)
    return my_data


def get_regions_list():
    # Get list of regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName']
                for region in ec2_client.describe_regions()['Regions']]
    return regions


if __name__ == '__main__':
  main()