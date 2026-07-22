#Test for Bulk Folio LCAP
import csv
import os
from pymarc import MARCReader, MARCWriter, Field, Subfield


def get_valid_input(prompt_text):
    """Prompt until a non-empty string is provided and strip surrounding quotes."""
    while True:
        value = input(prompt_text).strip().strip('"\'')
        if value:
            return value
        print("Input cannot be empty. Please try again.")


print("--- MARC 010 $a Population Utility ---\n")

# Get file paths from user
input_mrc_path = get_valid_input("Enter the path to your input MARC file (.mrc): ")
csv_file_path = get_valid_input("Enter the path to your CSV file (001, LCCN): ")
output_mrc_path = get_valid_input("Enter the path for the output MARC file (.mrc): ")

# Step 1: Load CSV mapping into a dictionary { "001_ID": "LCCN_VALUE" }
lccn_map = {}

try:
    with open(csv_file_path, mode="r", encoding="utf-8-sig") as csv_file:
        reader = csv.reader(csv_file)

        # Check for optional header
        first_row = next(reader, None)
        if first_row:
            # If the first row looks like a header (e.g., "001", "id", "lccn"), skip it
            if first_row[0].strip().lower() in ["001", "id", "control_number"]:
                pass  # Header skipped
            else:
                # First row is actual data
                lccn_map[first_row[0].strip()] = first_row[1].strip()

            for row in reader:
                if len(row) >= 2:
                    rec_id = row[0].strip()
                    lccn_val = row[1].strip()
                    if rec_id:
                        lccn_map[rec_id] = lccn_val

    print(f"Loaded {len(lccn_map)} record mappings from CSV.")

except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit(1)

# Step 2: Read MARC file, find matching 001, and insert LCCN into 010 $a
total_records = 0
updated_records = 0

try:
    with open(input_mrc_path, "rb") as input_file, \
            open(output_mrc_path, "wb") as output_file:

        reader = MARCReader(input_file)
        writer = MARCWriter(output_file)

        for record in reader:
            if record is None:
                print("Warning: Skipped a corrupted record.")
                continue

            total_records += 1

            # Get 001 ID
            control_num = record["001"].value().strip() if "001" in record else None

            # Check if this record is in our CSV mapping
            if control_num and control_num in lccn_map:
                new_lccn = "   " + lccn_map[control_num]  # Add two spaces prefix
                fields_010 = record.get_fields("010")

                if fields_010:
                    for old_field in fields_010:
                        new_subfields = []
                        for sf in old_field.subfields:
                            if sf.code == "a":
                                # Populate the blank $a with the prefixed LCCN
                                new_subfields.append(Subfield(code="a", value=new_lccn))
                            else:
                                new_subfields.append(Subfield(code=sf.code, value=sf.value))

                        new_field = Field(
                            tag="010",
                            indicators=old_field.indicators,
                            subfields=new_subfields
                        )
                        record.remove_field(old_field)
                        record.add_ordered_field(new_field)
                else:
                    # Fallback: If no 010 field existed at all, create one with $a
                    new_field = Field(
                        tag="010",
                        indicators=[" ", " "],
                        subfields=[Subfield(code="a", value=new_lccn)]
                    )
                    record.add_ordered_field(new_field)

                updated_records += 1

            writer.write(record)

        writer.close()

    print("\nProcessing complete!")
    print(f"  - Total records processed: {total_records}")
    print(f"  - Records updated with new LCCNs: {updated_records}")
    print(f"  - Output saved to: '{output_mrc_path}'")

except FileNotFoundError:
    print(f"Error: Could not find file '{input_mrc_path}'.")
except Exception as e:
    print(f"An error occurred: {e}")
