import os
import json
import pandas as pd
from datetime import datetime


def analyze_interaction_and_export(root_directory="."):
    """
    Traverse directory, analyze turn count, total duration, and turn rate
    for each JSON file, and save results to Excel file.
    """
    results_list = []

    print(f"Starting deep analysis of directory: {os.path.abspath(root_directory)}")

    # 1. Filter date folders
    try:
        all_items = os.listdir(root_directory)
        date_folders = [item for item in all_items if
                        os.path.isdir(os.path.join(root_directory, item)) and re.match(r'^\d{8}', item)]
    except FileNotFoundError:
        print(f"Error: Directory '{root_directory}' not found.")
        return

    # 2. Iterate through folders and files
    for folder_name in sorted(date_folders):
        folder_path = os.path.join(root_directory, folder_name)
        try:
            json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
            for json_file in sorted(json_files):
                file_path = os.path.join(folder_path, json_file)
                file_id = os.path.splitext(json_file)[0]

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        transcript_data = json.load(f)

                        # --- Initialize analysis variables ---
                        turn_count = 0
                        total_duration_seconds = 0
                        last_speaker = None

                        if not isinstance(transcript_data, list) or not transcript_data:
                            print(f"Skipping empty or malformed file: {file_path}")
                            continue

                        # --- Analysis Logic ---
                        # 1. Calculate turn count
                        for entry in transcript_data:
                            current_speaker = entry.get("speaker")
                            if last_speaker is not None and current_speaker != last_speaker:
                                turn_count += 1
                            last_speaker = current_speaker

                        # 2. Calculate total duration
                        try:
                            time_format = "%H:%M:%S.%f"
                            start_time_str = transcript_data[0].get("start_time")
                            end_time_str = transcript_data[-1].get("end_time")

                            start_time = datetime.strptime(start_time_str, time_format)
                            end_time = datetime.strptime(end_time_str, time_format)

                            delta = end_time - start_time
                            total_duration_seconds = delta.total_seconds()
                        except (ValueError, TypeError, IndexError):
                            print(f"Warning: Unable to calculate duration for {file_path}, time format may be incorrect or data incomplete.")
                            total_duration_seconds = 0

                        total_duration_minutes = total_duration_seconds / 60

                        # 3. Calculate turn rate (turns/minute)
                        if total_duration_minutes > 0:
                            turn_rate = turn_count / total_duration_minutes
                        else:
                            turn_rate = 0

                        # --- Store Results ---
                        results_list.append({
                            'Date': folder_name,
                            'ID': file_id,
                            'Turn_Count': turn_count,
                            'Total_Duration(min)': round(total_duration_minutes, 2),
                            'Turn_Rate(turns/min)': round(turn_rate, 2)
                        })
                        print(
                            f"Analysis complete: {file_path} | Duration: {round(total_duration_minutes, 2)}min | Turn rate: {round(turn_rate, 2)}turns/min")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

        except Exception as e:
            print(f"Error accessing folder {folder_name}: {e}")

    # 3. Save to Excel
    if not results_list:
        print("No analysis results generated.")
        return

    df = pd.DataFrame(results_list)
    output_filename = "Dialogue_Analysis(Turns_and_Duration).xlsx"

    try:
        df.to_excel(output_filename, index=False)
        print(f"\n✅ Analysis complete! Results successfully saved to: {os.path.abspath(output_filename)}")
    except Exception as e:
        print(f"\nError saving Excel file: {e}. Please ensure 'pandas' and 'openpyxl' are installed.")

import os
import json
import pandas as pd
from datetime import datetime

def analyze_and_sort_interaction(root_directory="."):
    """
    Traverse directory, analyze dialogue data, sort by correct date order, and save to Excel.
    """
    results_list = []

    print(f"Starting deep analysis of directory: {os.path.abspath(root_directory)}")

    # 1. Get folder list (no pre-sorting here)
    try:
        all_items = os.listdir(root_directory)
        date_folders = [item for item in all_items if os.path.isdir(os.path.join(root_directory, item)) and re.match(r'^\d{8}', item)]
    except FileNotFoundError:
        print(f"Error: Directory '{root_directory}' not found.")
        return

    # 2. Traverse and process data (same as before）
    for folder_name in date_folders:
        folder_path = os.path.join(root_directory, folder_name)
        try:
            json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
            for json_file in json_files:
                file_path = os.path.join(folder_path, json_file)
                file_id = os.path.splitext(json_file)[0]

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        transcript_data = json.load(f)

                        # ... (analysis logic same as previous version omitted here) ...
                        turn_count = 0
                        total_duration_seconds = 0
                        last_speaker = None
                        if not isinstance(transcript_data, list) or not transcript_data:
                            continue
                        for entry in transcript_data:
                            current_speaker = entry.get("speaker")
                            if last_speaker is not None and current_speaker != last_speaker:
                                turn_count += 1
                            last_speaker = current_speaker
                        try:
                            time_format = "%H:%M:%S.%f"
                            start_time_str = transcript_data[0].get("start_time")
                            end_time_str = transcript_data[-1].get("end_time")
                            start_time = datetime.strptime(start_time_str, time_format)
                            end_time = datetime.strptime(end_time_str, time_format)
                            delta = end_time - start_time
                            total_duration_seconds = delta.total_seconds()
                        except (ValueError, TypeError, IndexError):
                            total_duration_seconds = 0
                        total_duration_minutes = total_duration_seconds / 60
                        if total_duration_minutes > 0:
                            turn_rate = turn_count / total_duration_minutes
                        else:
                            turn_rate = 0

    # 3. Convert results list to DataFrame
    df = pd.DataFrame(results_list)

    # --- Core Sorting Logic ---
    print("\nSorting data by correct date order...")
    # a. Convert "Date" column (e.g., "20250410") to pandas datetime format
    #    Using format='%Y%m%d' for YYYYMMDD format
    #    errors='coerce' returns NaT for invalid formats
    df['sort_key_date'] = pd.to_datetime(df['Date'], format='%Y%m%d', errors='coerce')

    # b. Sort using new datetime column and 'ID' column
    df.sort_values(by=['sort_key_date', 'ID'], inplace=True)

    # c. Drop auxiliary sorting column, keep original "Date" column format
    df.drop(columns=['sort_key_date'], inplace=True)
    # --- Sorting Complete ---

    # 4. Save to Excel
    output_filename = "Dialogue_Analysis(Turns_and_Duration)_Sorted.xlsx"
    try:
        df.to_excel(output_filename, index=False)
        print(f"✅ Analysis and sorting complete! Results successfully saved to: {os.path.abspath(output_filename)}")
    except Exception as e:
        print(f"\nError saving Excel file: {e}.")

    # 3. Convert results list to DataFrame
    df = pd.DataFrame(results_list)

    # --- Core Sorting Logic ---
    print("\nSorting data by correct date order...")
    # a. Convert "Date" column (e.g., "20250410") to pandas datetime format
    #    Using format='%Y%m%d' for YYYYMMDD format
    #    errors='coerce' returns NaT for invalid formats
    df['sort_key_date'] = pd.to_datetime(df['Date'], format='%Y%m%d', errors='coerce')

    # b. Sort using new datetime column and 'ID' column
    df.sort_values(by=['sort_key_date', 'ID'], inplace=True)

    # c. Drop auxiliary sorting column, keep original "Date" column format
    df.drop(columns=['sort_key_date'], inplace=True)
    # --- Sorting Complete ---

    # 4. Save to Excel
    output_filename = "Dialogue_Analysis(Turns_and_Duration)_Sorted.xlsx"
    try:
        df.to_excel(output_filename, index=False)
        print(f"✅ Analysis and sorting complete! Results successfully saved to: {os.path.abspath(output_filename)}")
    except Exception as e:
        print(f"\nError saving Excel file: {e}.")


if __name__ == "__main__":
    analyze_interaction_and_export()
    analyze_and_sort_interaction()


