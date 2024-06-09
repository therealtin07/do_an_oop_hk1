import csv
import os
import sys




# Read the CSV file
with open('level0_data.csv', mode='r') as file:
    reader = csv.reader(file)
    # Convert the reader object to a list of rows
    data = list(reader)

# Display the data
for row in data:
    print(row)
print(len(data[0]))