import pandas as pd
import re

# Read Excel file
df = pd.read_excel('data.xlsx')

# Define mapping from provinces to region names
region_map = {
    'Beijing': 'North', 'Tianjin': 'North', 'Hebei': 'North', 'Shanxi': 'Central', 'Inner Mongolia': 'North',
    'Liaoning': 'North', 'Jilin': 'North', 'Heilongjiang': 'North',
    'Shanghai': 'East', 'Jiangsu': 'East', 'Zhejiang': 'East', 'Anhui': 'East', 'Fujian': 'East', 'Jiangxi': 'East', 'Shandong': 'East',
    'Henan': 'Central', 'Hubei': 'Central', 'Hunan': 'Central',
    'Guangdong': 'South', 'Guangxi': 'South', 'Hainan': 'South',
    'Chongqing': 'West', 'Sichuan': 'West', 'Guizhou': 'West', 'Yunnan': 'West', 'Tibet': 'West',
    'Shaanxi': 'West', 'Gansu': 'West', 'Qinghai': 'West', 'Ningxia': 'West', 'Xinjiang': 'West',
    'Hong Kong': 'South', 'Macao': 'South', 'Taiwan': 'East'
}

# Define mapping from region names to codes
encoding_map = {
    'East': 1,
    'West': 2,
    'Central': 3,
    'North': 4,
    'South': 5
}


def get_province(ip_string):
    """Extract province from 'from IP' column"""
    match = re.search(r'\((.*?)-', ip_string)
    if match:
        return match.group(1)
    return None

# 1. Extract province
df['province'] = df['from IP'].apply(get_province)

# 2. Map province to region name
df['region name'] = df['province'].map(region_map)

# 3. Map region name to code, and name the column 'region'
df['region'] = df['region name'].map(encoding_map)

# Select and rearrange final columns
df_final = df[['from IP', 'region']]

# Export to new Excel file
df_final.to_excel('data_with_region_encoded.xlsx', index=False)

print("Processing complete! Generated 'data_with_region_encoded.xlsx' file.")