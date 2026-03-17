import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def create_simplified_plot(excel_filename="Dialogue_Analysis(Turns_and_Duration)_Sorted.xlsx"):
    """
    Read data from the specified Excel file and generate a monochrome scatter plot
    without legend to display the overall trend.

    Args:
        excel_filename (str): Name of the Excel file containing analysis data.
    """
    try:
        # 1. Read data from Excel file
        print(f"Reading file: '{excel_filename}'...")
        df = pd.read_excel(excel_filename)
        print("File read successfully.")

    except FileNotFoundError:
        print(f"Error: File '{excel_filename}' not found.")
        print("Please ensure this script is in the same directory as your Excel file.")
        return
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # 2. Create scatter plot
    print("Generating simplified chart...")
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 8))

    # Removed hue='id' and palette parameters from scatterplot function
    # Added fixed color parameter instead
    scatter_plot = sns.scatterplot(
        data=df,
        x='Total_Duration(min)',
        y='Turn_Rate(turns/min)',
        color='royalblue',  # Unified color for all data points
        s=80,  # Data point size
        alpha=0.7  # Data point transparency
    )

    # 3. Set chart title and axis labels
    plt.title('Interaction Rate vs. Total Duration of Tutoring Sessions (Overall Trend)', fontsize=16,
              fontweight='bold')
    plt.xlabel('Total Duration (minutes)', fontsize=12)
    plt.ylabel('Turn Rate (turns/minute)', fontsize=12)

    # 4. Refine chart details
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    # 5. Display chart (legend not created as hue parameter is not used)
    print("Chart generated!")
    plt.show()

if __name__ == "__main__":
    create_simplified_plot()