#!/bin/bash
# read CSV from file.csv and print 2 entries line by line
# use while loop
# parameter is CSV file name. (needs an empty line at the end)
#
#


# Get the name of the CSV file from the command line
file=$1

# Open the CSV file for reading
while read line; do

  # Split the line into fields
  fields=($line)

  # Print the first two fields
  echo "${fields[0]} ${fields[1]}"

done < "$file"
