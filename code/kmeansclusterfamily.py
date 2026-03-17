import pandas as pd
from sklearn.cluster import KMeans
import numpy as np


def classify_families_by_conflict_clustering(filename="data_all.xlsx",
                                             output_filename="family_conflict_groups_clustered.xlsx",
                                             num_clusters=2):
    """
    Group families using K-Means clustering based on "conflict event proportion".
    - Conflict event: Consecutive conflict dialogue rows are counted as one event.
    - Proportion denominator: Only counts rows with valid codes.
    """
    print(f"--- Starting K-Means clustering to group families ---")

    # 1. Read data
    try:
        print(f"Reading data file: '{filename}'...")
        df = pd.read_excel(filename)
        # Ensure data is sorted by family and dialogue ID for correct consecutive conflict calculation
        df = df.sort_values(by=['family_id', 'dialogue_id']).reset_index(drop=True)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Please ensure the script is in the same directory.")
        return

    # 2. Identify behavior columns and conflict columns
    # This logic robustly finds all B_ and C_ columns, as well as the alternate EN, LP, etc. format.
    behavior_columns = [col for col in df.columns if
                        col.startswith('B_') or col in ['EN', 'LP', 'UP', 'GI', 'RU', 'RE', 'DI', 'IT', 'CO', 'MO',
                                                        'DC', 'IC', 'CB', 'FT', 'NI', 'BD', 'FD', 'II']]
    conflict_columns = [col for col in df.columns if
                        col.startswith('C_') or col in ['EC', 'CC', 'MC', 'RC', 'TC', 'KC', 'FC']]
    all_code_columns = behavior_columns + conflict_columns

    print("Data loaded successfully. Calculating numerator and denominator...")

    # 3. Calculate denominator: total "active interaction" rows per family
    df['is_active_turn'] = df[all_code_columns].sum(axis=1) > 0
    active_turns_per_family = df.groupby('family_id')['is_active_turn'].sum()

    # 4. Calculate numerator: number of "conflict events" per family
    df['is_conflict_turn'] = df[conflict_columns].sum(axis=1) > 0
    # An event starts when a conflict turn appears and the previous turn was NOT a conflict
    df['is_event_start'] = df['is_conflict_turn'] & (
                df.groupby('family_id')['is_conflict_turn'].shift(1).fillna(False) == False)
    conflict_events_per_family = df.groupby('family_id')['is_event_start'].sum()

    # 5. Merge results and calculate "conflict event proportion"
    summary_df = pd.DataFrame({
        'active_turns': active_turns_per_family,
        'conflict_events': conflict_events_per_family
    }).reset_index()

    summary_df['conflict_proportion'] = summary_df.apply(
        lambda row: row['conflict_events'] / row['active_turns'] if row['active_turns'] > 0 else 0,
        axis=1
    )

    # 6. Perform K-Means clustering
    print(f"\nPreparing to perform K-Means clustering on conflict proportions for {len(summary_df)} families (K={num_clusters})...")

    # K-Means requires a 2D array, even for 1D data
    proportions_for_clustering = summary_df[['conflict_proportion']].values

    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init='auto')
    summary_df['cluster'] = kmeans.fit_predict(proportions_for_clustering)

    print("Clustering complete.")

    # 7. Identify high/low conflict clusters and assign labels
    cluster_centers = summary_df.groupby('cluster')['conflict_proportion'].mean().sort_values(ascending=False)
    high_conflict_cluster_id = cluster_centers.index[0]

    summary_df['conflict_group'] = np.where(
        summary_df['cluster'] == high_conflict_cluster_id,
        'High_Conflict',
        'Low_Conflict'
    )

    summary_df = summary_df.sort_values(by='conflict_proportion', ascending=False)

    # 8. Output and save results
    print("\n--- Family Grouping Results (Based on Clustering) ---")
    print(summary_df[['family_id', 'active_turns', 'conflict_events', 'conflict_proportion', 'conflict_group']])

    print("\n--- Group Statistics ---")
    print(summary_df['conflict_group'].value_counts())

    try:
        summary_df.to_excel(output_filename, index=False)
        print(f"\n✅ Grouping results successfully saved to: '{output_filename}'")
    except Exception as e:
        print(f"\n❌ Error saving file: {e}")


if __name__ == "__main__":
    # We will cluster families into 2 groups (High vs. Low)
    classify_families_by_conflict_clustering(num_clusters=2)