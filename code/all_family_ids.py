import pandas as pd

def print_unique_ids_from_excel(filename="Dialogue_Turn_Analysis.xlsx"):
    """
    Read the specified Excel file and print the unique values from the 'id' column.

    Args:
        filename (str): Name of the Excel file to read.
    """
    try:
        # Read Excel file using pandas
        df = pd.read_excel(filename)

        # Check if 'id' column exists
        if 'id' not in df.columns:
            print(f"Error: Column 'id' not found in file '{filename}'.")
            print(f"Available columns: {df.columns.tolist()}")
            return

        # Get 'id' column and remove duplicates using .unique()
        # Convert result to standard Python list using .tolist()
        unique_ids = df['id'].unique().tolist()

        # Print results
        print(f"Unique IDs in file '{filename}':")
        print(unique_ids)
        print(f"\nTotal: {len(unique_ids)} unique IDs.")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        print("Please ensure the file exists in the current directory with the correct name.")
    except Exception as e:
        print(f"An unknown error occurred while reading or processing the file: {e}")

if __name__ == "__main__":
    print_unique_ids_from_excel()