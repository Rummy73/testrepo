import json
import csv
import os

# 1. Get the file names from the user
input_filename = input("Enter the name of the JSON file to read (e.g., Json_test.txt): ")
output_filename = input("Enter the name for the new CSV file (e.g., output.csv): ")

# Check if the input file actually exists before trying to open it
if not os.path.exists(input_filename):
    print(f"Error: The file '{input_filename}' was not found.")
else:
    # 2. Open and read the JSON file
    with open(input_filename, 'r', encoding='utf-8') as json_file:
        data_source = json.load(json_file)

    # 3. Open the output file to write into
    with open(output_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write the header row
        writer.writerow(['ID', 'Title'])
        
        # 4. Loop through the instances and extract 'id' and 'title'
        instances = data_source.get('instances', [])
        for item in instances:
            record_id = item.get('id')
            title = item.get('title')
            
            # Write the row to the CSV
            writer.writerow([record_id, title])

    print(f"Done! Data from {input_filename} has been converted to {output_filename}.")