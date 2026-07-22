import os
from pymarc import MARCReader, MARCWriter, Field, Subfield

def get_valid_input(prompt_text):
    """Prompt until a non-empty string is provided and strip surrounding quotes."""
    while True:
        value = input(prompt_text).strip().strip('"\'')
        if value:
            return value
        print("Input cannot be empty. Please try again.")

print("--- MARC Cut 010 $a to $z (Keep Blank $a) ---\n")

input_mrc_path = get_valid_input("Enter the path to your source MARC file (.mrc): ")
output_mrc_path = get_valid_input("Enter the path for the modified output MARC file (.mrc): ")

modified_records_count = 0
total_records_count = 0

try:
    with open(input_mrc_path, "rb") as input_file, \
         open(output_mrc_path, "wb") as output_file:

        reader = MARCReader(input_file)
        writer = MARCWriter(output_file)

        for record in reader:
            if record is None:
                print("Warning: Skipped a corrupted record.")
                continue

            total_records_count += 1
            record_modified = False

            # Get all 010 fields in the record
            fields_010 = record.get_fields("010")

            for old_field in fields_010:
                # Check if $a exists in this field
                has_a = any(sf.code == "a" for sf in old_field.subfields)

                if has_a:
                    record_modified = True
                    new_subfields = []

                    for sf in old_field.subfields:
                        if sf.code == "a":
                            # CUT step: extract the string data inside $a
                            extracted_data = sf.value

                            # KEEP $a (blank) for future data entry
                            new_subfields.append(Subfield(code="a", value=""))

                            # PASTE step: create new $z with the cut data
                            new_subfields.append(Subfield(code="z", value=extracted_data))
                        else:
                            # Keep other subfields (like existing $z or $b) untouched
                            new_subfields.append(Subfield(code=sf.code, value=sf.value))

                    # Reconstruct the 010 Field with preserved indicators
                    new_field = Field(
                        tag="010",
                        indicators=old_field.indicators,
                        subfields=new_subfields
                    )

                    # Swap old field for updated field
                    record.remove_field(old_field)
                    record.add_ordered_field(new_field)

            if record_modified:
                modified_records_count += 1

            writer.write(record)

        writer.close()

    print("\nProcessing complete!")
    print(f"  - Total records processed: {total_records_count}")
    print(f"  - Records where 010 $a was cut to $z and left blank: {modified_records_count}")
    print(f"  - Modified MARC file saved to: '{output_mrc_path}'")

except FileNotFoundError:
    print(f"Error: Could not find the input MARC file '{input_mrc_path}'.")
except Exception as e:
    print(f"An error occurred while processing: {e}")