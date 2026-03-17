import pandas as pd
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt
import matplotlib


def analyze_family_conflicts(filename="data_all.xlsx"):
    """
    Reads homework interaction data, calculates conflict frequencies for each family,
    and performs hierarchical clustering to group families with similar conflict profiles.
    """
    print(f"--- Starting Family Conflict Analysis ---")

    # --- 1. Read and Prepare Data ---
    try:
        print(f"Reading data from '{filename}'...")
        df = pd.read_excel(filename)
    except FileNotFoundError:
        print(f"Error: Could not find the file '{filename}'. Please make sure it's in the same directory.")
        return

    # Define the conflict columns based on your data structure
    conflict_columns = ['EC', 'CC', 'MC', 'RC', 'TC', 'KC', 'FC']

    # Check if all conflict columns are present in the dataframe
    if not all(col in df.columns for col in conflict_columns):
        print("Error: The Excel file is missing one or more required conflict columns.")
        print(f"Required columns: {conflict_columns}")
        return

    print("Data loaded successfully. Calculating conflict frequencies per family...")

    # --- 2. Calculate Conflict Frequencies per Family ---
    # Group by family_id and sum the occurrences of each conflict type
    family_conflict_freq = df.groupby('family_id')[conflict_columns].sum()

    print("\nConflict frequencies per family:")
    print(family_conflict_freq)

    # --- 3. Perform Hierarchical Clustering ---
    print("\nPerforming hierarchical clustering using the 'ward' method...")
    # The 'ward' method is a common choice that tries to minimize the variance within each cluster.
    # The result 'Z' is a linkage matrix that encodes the clustering hierarchy.
    Z = linkage(family_conflict_freq, method='ward')
    print("Clustering complete.")

    # --- 4. Visualize the Dendrogram ---
    print("Generating dendrogram plot...")

    # Set up matplotlib to handle potential Chinese characters in labels if needed
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # Example font, change if needed
    matplotlib.rcParams['axes.unicode_minus'] = False

    plt.figure(figsize=(15, 8))
    plt.title('Hierarchical Clustering of Families Based on Conflict Profiles', fontsize=16)
    plt.xlabel('Family ID', fontsize=12)
    plt.ylabel('Distance (Similarity)', fontsize=12)

    # The dendrogram function takes the linkage matrix 'Z' and plots the hierarchy
    dendrogram(
        Z,
        labels=family_conflict_freq.index.tolist(),  # Use family_id as labels
        leaf_rotation=90.,  # rotates the x axis labels
        leaf_font_size=10.  # font size for the x axis labels
    )

    # Save the plot to a file
    output_plot_filename = "family_conflict_clustering.png"
    plt.tight_layout()  # Adjust plot to ensure everything fits without overlapping
    plt.savefig(output_plot_filename)

    print(f"\n✅ Analysis complete! The clustering result has been saved as '{output_plot_filename}'.")


# --- Run the analysis ---
if __name__ == "__main__":
    analyze_family_conflicts()