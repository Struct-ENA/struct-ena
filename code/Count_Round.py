import os
import json
import pandas as pd


def analyze_turn_taking_and_export(root_directory="."):
    """
    Traverse date folders in the specified directory, calculate dialogue turn counts
    for each JSON file, and save results to an Excel file.
    """
    # List to store all analysis results
    results_list = []

    print(f"Starting scan and analysis of directory: {os.path.abspath(root_directory)}")

    # 1. Get all folder names in root directory
    try:
        all_items = os.listdir(root_directory)
    except FileNotFoundError:
        print(f"Error: Directory '{root_directory}' not found.")
        return

    # 2. Filter date folders
    date_folders = [item for item in all_items if
                    os.path.isdir(os.path.join(root_directory, item)) and re.match(r'^\d{8}', item)]

    if not date_folders:
        print("No date-formatted folders (YYYYMMDD) found in root directory.")
        return

    # 3. Iterate through each date folder
    for folder_name in sorted(date_folders):
        folder_path = os.path.join(root_directory, folder_name)

        # 4. Get all JSON files in the folder
        try:
            json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
            if not json_files:
                continue

            # 5. Iterate through and analyze each JSON file
            for json_file in sorted(json_files):
                file_path = os.path.join(folder_path, json_file)

                # Extract ID "0" from filename "0.json"
                file_id = os.path.splitext(json_file)[0]

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        transcript_data = json.load(f)

                        # --- Core analysis logic: calculate turn count ---
                        turn_count = 0
                        last_speaker = None
                        if isinstance(transcript_data, list) and transcript_data:
                            # Iterate through dialogue records
                            for entry in transcript_data:
                                current_speaker = entry.get("speaker")
                                # If current speaker differs from last (and not first record), increment turn count
                                if last_speaker is not None and current_speaker != last_speaker:
                                    turn_count += 1
                                # Update "last speaker"
                                last_speaker = current_speaker

                        # Store result in list
                        results_list.append({
                            'Date': folder_name,
                            'ID': file_id,
                            'Count': turn_count
                        })
                        print(f"Analysis complete: {file_path} -> Turn count: {turn_count}")

                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Skipping file {file_path}: format error or missing 'speaker' field: {e}")
                except Exception as e:
                    print(f"Unknown error processing file {file_path}: {e}")

    except Exception as e:
        print(f"Error accessing folder {folder_name}: {e}")

    # 6. Convert all results from list to DataFrame and save to Excel
    if not results_list:
        print("No analysis results generated.")
        return

    df = pd.DataFrame(results_list)
    output_filename = "对话轮转次数分析.xlsx"

    try:
        # Use to_excel method to save, index=False prevents writing DataFrame row index to Excel
        df.to_excel(output_filename, index=False, engine='openpyxl')
        print(f"\n🎉 Analysis complete! Results successfully saved to: {os.path.abspath(output_filename)}")
    except Exception as e:
        print(f"\nError saving Excel file: {e}")


if __name__ == "__main__":
    # Assumes date folders are in the same directory as this script; run directly
    analyze_turn_taking_and_export()