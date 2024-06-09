import csv

# Define the data
data = [
    ['Name', 'Age', 'City'],
    ['Alice', 24, 'New York'],
    ['Bob', 27, 'Los Angeles'],
    ['Charlie', 22, 'Chicago'],
    ['David', 32, 'Houston'],
    ['Eva', 29, 'Phoenix']
]

# Write data to CSV file
with open('example.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)
