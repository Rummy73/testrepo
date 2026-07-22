import csv
import io
import os
from pymarc import MARCMakerReader, MARCReader


def extract_marc_fields():
    # 1. User inputs for the files
    input_file = input("Enter the path to the .mrk file: ").strip()
    output_file = input("Enter the desired CSV output file name: ").strip()

    # File validation
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        return

    if not output_file.lower().endswith(".csv"):
        output_file += ".csv"

    print("\nProcessing records with MARCReader... Please wait.")

    try:
        # Step A: Convert the text .mrk format into a binary MARC stream
        # This gives MARCReader the raw bytes it needs to see data.
        binary_stream = io.BytesIO()
        with open(input_file, "r", encoding="utf-8") as txt_fh:
            maker_reader = MARCMakerReader(txt_fh)
            for record in maker_reader:
                if record is not None:
                    binary_stream.write(record.as_marc())

        # Reset stream pointer back to the beginning
        binary_stream.seek(0)

        # 2. Open CSV for writing
        with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["ID", "LCCN"])  # Required headers

            # 3. Read using standard MARCReader as requested
            reader = MARCReader(binary_stream)
            record_count = 0

            for record in reader:
                if record is None:
                    continue

                # Extract 001 (Control Field - uses .data string)
                if record["001"] is not None:
                    id_value = record["001"].data.strip()
                else:
                    id_value = ""

                # Extract 010$a (Variable Field) using your target logic checking pattern
                if record["010"] is not None:
                    if record["010"]["a"] is not None:
                        lccn_value = record["010"]["a"].strip()
                    else:
                        lccn_value = ""
                else:
                    lccn_value = ""

                # Write row to CSV
                writer.writerow([id_value, lccn_value])
                record_count += 1

        print(f"\nSuccess! Successfully processed {record_count} records.")
        print(f"Data saved to: {os.path.abspath(output_file)}")

    except Exception as e:
        print(f"\nAn error occurred during processing: {e}")


if __name__ == "__main__":
    extract_marc_fields()
