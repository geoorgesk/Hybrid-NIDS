import pandas as pd
from datasets import load_dataset
import os

print("Downloading real CICIDS-2017 dataset...")
# Load a subset of the dataset
ds = load_dataset('bvk/CICIDS-2017', split='train[:5%]')  # Get 5% (about 140k rows)
df = ds.to_pandas()

print(f"Loaded {len(df)} rows. Mapping features...")

# Map standard CICIDS column names to our expected feature names
column_mapping = {
    'Flow Duration': 'flow_duration',
    'Total Fwd Packet': 'total_fwd_packets',     # Note the singular 'Packet' in this dataset
    'Total Bwd packets': 'total_bwd_packets',    # Note the lowercase 'p' in 'packets'
    'Fwd Packet Length Max': 'fwd_packet_length_max',
    'Bwd Packet Length Max': 'bwd_packet_length_max',
    'Flow Bytes/s': 'flow_bytes_per_sec',
    'Flow Packets/s': 'flow_packets_per_sec',
    'SYN Flag Count': 'syn_flag_count',
    'ACK Flag Count': 'ack_flag_count',
    'RST Flag Count': 'rst_flag_count',
    'Label': 'label'
}

# Sometimes columns have leading/trailing spaces
df.columns = df.columns.str.strip()

# Check which mapped columns actually exist in the dataframe
available_cols = []
missing_cols = []
for k, v in column_mapping.items():
    # Attempt to find the column (case insensitive / stripped)
    found = False
    for actual_col in df.columns:
        if k.lower().replace(' ', '') in actual_col.lower().replace(' ', '') or k.lower() == actual_col.lower():
            df.rename(columns={actual_col: v}, inplace=True)
            available_cols.append(v)
            found = True
            break
    if not found:
        missing_cols.append(k)

print(f"Mapped columns: {available_cols}")
if missing_cols:
    print(f"WARNING: Could not find these columns: {missing_cols}")

# Filter down to just our required columns + label
required_cols = list(column_mapping.values())
df = df[[c for c in required_cols if c in df.columns]]

print("Normalizing labels...")
# Map CICIDS labels to our 4 categories
def map_label(l):
    l_str = str(l).upper()
    if 'BENIGN' in l_str or 'NORMAL' in l_str:
        return 'Normal'
    elif 'DOS' in l_str or 'DDOS' in l_str:
        return 'DDoS'
    elif 'PORTSCAN' in l_str:
        return 'PortScan'
    elif 'BRUTE' in l_str or 'PATATOR' in l_str or 'BOT' in l_str or 'INFILTRATION' in l_str or 'WEB' in l_str:
        # Grouping other attacks under BruteForce for the sake of our 4-class system
        return 'BruteForce'
    return 'Normal'

df['label'] = df['label'].apply(map_label)

print("Label distribution in dataset:")
print(df['label'].value_counts())

# Balance the dataset somewhat so it's not 99% Normal
df_normal = df[df['label'] == 'Normal'].sample(min(20000, len(df[df['label'] == 'Normal'])))
df_ddos = df[df['label'] == 'DDoS']
df_portscan = df[df['label'] == 'PortScan']
df_bruteforce = df[df['label'] == 'BruteForce']

df_balanced = pd.concat([df_normal, df_ddos, df_portscan, df_bruteforce])
df_balanced = df_balanced.sample(frac=1.0).reset_index(drop=True)

# Replace infinities/NaNs that sometimes appear in flow_bytes_per_sec
import numpy as np
df_balanced.replace([np.inf, -np.inf], np.nan, inplace=True)
df_balanced.fillna(0, inplace=True)

# Save to data/real_traffic.csv
os.makedirs('data', exist_ok=True)
out_path = 'data/real_traffic.csv'
df_balanced.to_csv(out_path, index=False)
print(f"Saved highly realistic dataset to {out_path} ({len(df_balanced)} rows)")
