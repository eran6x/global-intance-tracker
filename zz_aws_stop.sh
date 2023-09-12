#!/bin/bash
PRPATH="/Users/eran/projects/AWS"
INSTANCES_LIST="$PRPATH/instances_list"
RDS_LIST="$PRPATH/rds_list"

echo "stop all AWS EC2 instances"
while read -r line
do
    #Split the line into fields
    # this doesn't work as the bash isn't splitting the line as needed.
    fields=($line)
    fields[0]=$(awk -F ',' '{print $1}' <<< "$line")
    fields[1]=$(awk -F ','  '{print $2}' <<< "$line")
    
    [[ -n "$line" ]] && aws ec2 stop-instances --instance-ids ${fields[0]} --region ${fields[1]}
done < $PRPATH/instances_list

echo "stop all AWS RDS instances"
while read -r line
do
    [[ -n "$line" ]] &&  aws rds stop-db-instance --db-instance-identifier  $line  --region ${fields[1]}   
done < $PRPATH/rds_list

echo "Done!"