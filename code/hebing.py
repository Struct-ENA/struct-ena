import pandas as pd

# Read two Excel files
df_conflict = pd.read_excel("family_conflict_groups_clustered.xlsx")
df_data_all = pd.read_excel("data_all.xlsx")

# Merge 'cluster' column from df_conflict into df_data_all based on 'family_id'
# Only select 'family_id' and 'cluster' columns from df_conflict for the merge
df_merged = pd.merge(df_data_all, df_conflict[['family_id', 'cluster']], on='family_id', how='left')

# Save the merged DataFrame to a new Excel file
# index=False excludes the DataFrame index column from the output
df_merged.to_excel("data_all_with_cluster.xlsx", index=False)

print("Merge complete! New file saved as data_all_with_cluster.xlsx")