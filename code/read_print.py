import os
import json

def read_and_print_transcripts(root_directory="."):
    """
    Traverse all date folders in the specified root directory, read JSON files within,
    and print contents entry by entry.

    Args:
        root_directory (str): Path to the root directory containing date folders. Defaults to current directory.
    """
    print(f"Starting directory scan: {os.path.abspath(root_directory)}")

    # 1. Get all files and folder names in root directory
    try:
        all_items = os.listdir(root_directory)
    except FileNotFoundError:
        print(f"Error: Directory '{root_directory}' not found. Please ensure the script and data folders are in the correct location.")
        return

    # 2. Filter date folders (expected format: YYYYMMDD)
    date_folders = [item for item in all_items if os.path.isdir(os.path.join(root_directory, item)) and re.match(r'^\d{8}', item)]

    if not date_folders:
        print("No date-formatted folders (YYYYMMDD) found in root directory.")
        return

    print(f"Found date folders: {date_folders}")

    # 3. Iterate through each date folder
    for folder_name in sorted(date_folders):  # Sort folders
        folder_path = os.path.join(root_directory, folder_name)
        print(f"\n{'='*20} Entering folder: {folder_name} {'='*20}")

        # 4. Get all JSON files in the folder
        try:
            json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
            if not json_files:
                print(f"No .json files found in folder '{folder_name}'.")
                continue

            # 5. Iterate through and read each JSON file
            for json_file in sorted(json_files):  # Sort files
                file_path = os.path.join(folder_path, json_file)
                print(f"\n--- Reading file: {file_path} ---")

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                         # Load JSON file content
                        transcript_data = json.load(f)

                        # Check if data is in list format
                        # if isinstance(transcript_data, list):
                        #     # Print each dialogue entry
                        #     for entry in transcript_data:
                        #         print(entry)
                        # else:
                        #     print(f"Warning: Content in {json_file} is not in expected list format.")

                except json.JSONDecodeError:
                    print(f"Error: File {json_file} has invalid format and cannot be parsed.")
                except Exception as e:
                    print(f"Unknown error occurred while reading file {json_file}: {e}")

        except Exception as e:
            print(f"Error accessing folder {folder_name}: {e}")

if __name__ == "__main__":
    # Assumes date folders are in the same directory as this script.
    # Modify the path below if located elsewhere.
    # Example: read_and_print_transcripts("/path/to/your/data")
    read_and_print_transcripts()