import pandas as pd
import numpy as np
from itertools import combinations


# ==============================================================================
# Step 1: Calculate Raw Co-occurrence
# ==============================================================================
def calculate_ena_cooccurrence(
        df: pd.DataFrame,
        unit_cols: list,
        convo_cols: list,
        code_cols: list,
        window_size: int
) -> pd.DataFrame:
"""Calculate raw ENA co-occurrence counts using sliding window."""
    df[code_cols] = df[code_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    code_pairs = list(combinations(sorted(code_cols), 2))
    pair_column_names = [f"{p[0]}.{p[1]}" for p in code_pairs]
    results = {}
    pair_to_index = {pair: i for i, pair in enumerate(code_pairs)}

    for _, conversation_df in df.groupby(convo_cols):
        for i in range(len(conversation_df)):
            start_index = max(0, i - window_size + 1)
            end_index = i + 1
            window_df = conversation_df.iloc[start_index:end_index]
            present_codes = [col for col in code_cols if window_df[col].sum() > 0]

            if len(present_codes) >= 2:
                current_unit = tuple(conversation_df.iloc[i][unit_cols])
                if current_unit not in results:
                    results[current_unit] = [0] * len(code_pairs)

                window_cooccurrences = combinations(sorted(present_codes), 2)
                for pair in window_cooccurrences:
                    if pair in pair_to_index:
                        idx = pair_to_index[pair]
                        results[current_unit][idx] += 1

    if not results:
        return pd.DataFrame(columns=unit_cols + pair_column_names)

    final_df = pd.DataFrame.from_dict(results, orient='index', columns=pair_column_names)
    final_df.index = pd.MultiIndex.from_tuples(final_df.index, names=unit_cols)
    final_df = final_df.reset_index()
    return final_df


# ==============================================================================
# Step 2: Normalize Connection Weights (Normalization)
# ==============================================================================
def normalize_ena_weights(cooccurrence_df: pd.DataFrame, unit_cols: list) -> pd.DataFrame:
    """
    Perform spherical normalization on co-occurrence counts, converting them to connection weights.
    This is the key step that transforms integer counts into decimal "coefficients".
    """
    # Identify all weight columns (non-unit columns)
    weight_cols = [col for col in cooccurrence_df.columns if col not in unit_cols]

    # Extract weight values as numpy array for easier computation
    weights = cooccurrence_df[weight_cols].values

    # Calculate L2 norm (square root of sum of squares) for each row (each unit)
    norms = np.linalg.norm(weights, axis=1)

    # Create copy to avoid modifying original data
    normalized_df = cooccurrence_df.copy()

    # Avoid division by zero: if a unit has no connections (norm is 0), weights remain 0
    # Otherwise, divide each weight by the row's norm
    with np.errstate(divide='ignore', invalid='ignore'):
        normalized_weights = np.where(norms[:, np.newaxis] == 0, 0, weights / norms[:, np.newaxis])

    normalized_df[weight_cols] = normalized_weights

    return normalized_df


# ==============================================================================
# Step 3: Calculate Group Average Networks (Generate Your Table)
# ==============================================================================
def get_group_average_network(
        normalized_df: pd.DataFrame,
        metadata_df: pd.DataFrame,
        unit_cols: list,
        group_col: str
) -> pd.DataFrame:
    """
    Calculate average connection weight network for each group.
    This function generates a table similar to the one shown in your image.
    """
    # Merge metadata with normalized weight data for group aggregation
    merged_df = pd.merge(metadata_df, normalized_df, on=unit_cols)

    # Identify weight columns
    weight_cols = [col for col in normalized_df.columns if col not in unit_cols]

    # Group by group column and calculate mean for all weight columns
    group_means = merged_df.groupby(group_col)[weight_cols].mean()

    return group_means


# ==============================================================================
# Step 4: SVD Dimensionality Reduction (Calculate point positions on plot)
# ==============================================================================
def perform_ena_svd(normalized_df: pd.DataFrame, unit_cols: list, dimensions: int = 2) -> pd.DataFrame:
    """
    Center and perform SVD on normalized connection weights to calculate
    coordinates for each unit in ENA space.
    """
    weight_cols = [col for col in normalized_df.columns if col not in unit_cols]
    weights = normalized_df[weight_cols].values

    # 1. Centering: subtract mean network across all units
    centered_weights = weights - np.mean(weights, axis=0)

    # 2. Perform SVD
    U, s, Vt = np.linalg.svd(centered_weights, full_matrices=False)

    # 3. Calculate projected point coordinates (U * s)
    points = U[:, :dimensions] * s[:dimensions]

    # 4. Organize results into DataFrame
    svd_df = normalized_df[unit_cols].copy()
    for i in range(dimensions):
        svd_df[f'SVD{i + 1}'] = points[:, i]

    return svd_df


# --- Example Run ---
if __name__ == "__main__":
    # Create richer sample data with grouping information
    data = {
        'UserName': ['Alice', 'Alice', 'Bob', 'Bob', 'Charlie', 'Charlie', 'David', 'David', 'Eve', 'Eve'],
        'Condition': ['G1', 'G1', 'G1', 'G1', 'G1', 'G2', 'G2', 'G2', 'G2', 'G2'],
        'Activity': ['A1', 'A1', 'A1', 'A1', 'A2', 'A2', 'A2', 'A2', 'A3', 'A3'],
        'CodeA': [1, 0, 1, 0, 1, 0, 0, 0, 1, 1],
        'CodeB': [1, 1, 0, 1, 0, 0, 1, 0, 0, 1],
        'CodeC': [0, 1, 1, 0, 0, 1, 1, 0, 1, 0],
        'CodeD': [0, 0, 0, 1, 1, 1, 0, 1, 0, 0]
    }
    sample_df = pd.DataFrame(data)

    # Define analysis parameters
    UNITS = ['UserName']
    CONVOS = ['Activity']
    CODES = ['CodeA', 'CodeB', 'CodeC', 'CodeD']
    GROUP_COL = 'Condition'
    WINDOW = 2

    print("=============== Raw Data ===============")
    print(sample_df)

    # Run Step 1
    cooccurrence_counts = calculate_ena_cooccurrence(sample_df, UNITS, CONVOS, CODES, WINDOW)
    print("\n\n=============== Step 1: Raw Co-occurrence Counts (Integers) ===============")
    print(cooccurrence_counts)

    # Run Step 2
    normalized_weights = normalize_ena_weights(cooccurrence_counts, UNITS)
    print("\n\n=============== Step 2: Normalized Connection Weights (Decimal Coefficients) ===============")
    print(normalized_weights)

    # Run Step 3
    # Need a separate metadata table for grouping
    metadata = sample_df[UNITS + [GROUP_COL]].drop_duplicates()
    group_average_networks = get_group_average_network(normalized_weights, metadata, UNITS, GROUP_COL)
    print("\n\n=============== Step 3: Group Average Networks (Table in Your Image) ===============")
    print(group_average_networks.T)  # Use .T to transpose, format closer to your image

    # Run Step 4
    svd_points = perform_ena_svd(normalized_weights, UNITS)
    print("\n\n=============== Step 4: Unit Coordinates After SVD Dimensionality Reduction ===============")
    print(svd_points)