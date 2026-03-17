import pandas as pd


def filter_and_save_excel(ids_to_keep):
    """
    Filter two Excel files based on given ID list and save as new files.

    Args:
        ids_to_keep (list): List of IDs to retain.
    """
    # Define files to process
    files_to_filter = {
        "Daily_Questionnaire.xlsx": "Daily_Questionnaire_filtered.xlsx",
        "Background_Questionnaire.xlsx": "Background_Questionnaire_filtered.xlsx"
    }

    print("Starting file processing...")

    for original_file, filtered_file in files_to_filter.items():
        try:
            # 1. Read original Excel file
            print(f"\nReading: '{original_file}'...")
            df = pd.read_excel(original_file)
            print(f"Original file has {len(df)} rows.")

            # 2. Check if 'id' column exists
            if 'id' not in df.columns:
                print(f"Error: Column 'id' not found in '{original_file}', skipping this file.")
                continue

            # 3. Perform filtering
            # Ensure matching by converting 'id' column and list to the same type
            # Assumes IDs are integers; code handles text IDs as well
            df['id'] = pd.to_numeric(df['id'], errors='coerce')  # Convert to numeric, invalid values become NaT

            # Use isin() to filter rows where 'id' is in the provided list
            filtered_df = df[df['id'].isin(ids_to_keep)]
            print(f"{len(filtered_df)} rows remaining after filtering.")

            # 4. Save filtered results to new Excel file if not empty
            if not filtered_df.empty:
                filtered_df.to_excel(filtered_file, index=False)
                print(f"Success! Filtered results saved to: '{filtered_file}'")
            else:
                print(f"Note: No matching IDs found in '{original_file}', no new file generated.")

        except FileNotFoundError:
            print(f"Error: File '{original_file}' not found. Please ensure it is in the correct directory.")
        except Exception as e:
            print(f"Error processing file '{original_file}': {e}")

if __name__ == "__main__":
    # List of 66 valid IDs provided
    valid_ids = [0, 1, 10, 104, 105, 12, 13, 15, 16, 18, 20, 21, 22, 24, 28, 3, 30, 32, 34, 35, 41, 45, 48, 5, 53, 57,
                 6, 62, 63, 66, 69, 74, 75, 76, 78, 79, 82, 85, 87, 9, 92, 95, 96, 97, 14, 19, 23, 47, 52, 80, 91, 17,
                 2, 25, 38, 77, 29, 71, 58, 65, 33, 90, 103, 4, 51, 68]

    # Call function to filter and save
    filter_and_save_excel(valid_ids)