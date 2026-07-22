import csv
import os
from pymarc import MARCReader, MARCWriter

def get_valid_input(prompt_text):
    """Prompt until a non-empty string is provided."""
    while True:
        value = input(prompt_text).strip().strip('"\'')
        if value:
            return value
        print("Input cannot be empty. Please try again.")

print("--- MARC File Cut & Paste Utility ---\n")

# Get user inputs for file paths
input_mrc_path = get_valid_input("Enter the path to your source MARC file (.mrc): ")
csv_file_path = get_valid_input("Enter the path to your CSV file with 001 IDs: ")
selected_mrc_path = get_valid_input("Enter the name/path for the NEW file (cut records): ")

# Ask if they want to keep the remaining records in a separate file or overwrite
remaining_mrc_path = get_valid_input("Enter the name/path for the REMAINING records file: ")

print("\nProcessing...")

# Step 1: Read control numbers from CSV into a set for fast lookup
target_ids = set()

try:
    with open(csv_file_path, mode="r", encoding="utf-8-sig") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if row:
                target_ids.add(row[0].strip())
    print(f"Loaded {len(target_ids)} control numbers from '{csv_file_path}'.")
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit(1)

# Step 2: Stream through original MRC file and filter
cut_count = 0
kept_count = 0

try:
    with open(input_mrc_path, "rb") as input_file, \
         open(selected_mrc_path, "wb") as selected_file, \
         open(remaining_mrc_path, "wb") as remaining_file:

        reader = MARCReader(input_file)
        selected_writer = MARCWriter(selected_file)
        remaining_writer = MARCWriter(remaining_file)

        for record in reader:
            if record is None:
                print("Warning: Skipped a corrupted record.")
                continue

            control_number = record["001"].value().strip() if "001" in record else None

            if control_number and control_number in target_ids:
                selected_writer.write(record)
                cut_count += 1
            else:
                remaining_writer.write(record)
                kept_count += 1

        selected_writer.close()
        remaining_writer.close()

    print("\nProcessing complete!")
    print(f"  - Extracted records saved to: '{selected_mrc_path}' ({cut_count} records)")
    print(f"  - Remaining records saved to: '{remaining_mrc_path}' ({kept_count} records)")

except FileNotFoundError:
    print(f"Error: Could not find the input MARC file '{input_mrc_path}'.")
except Exception as e:
    print(f"An error occurred while processing MARC files: {e}")