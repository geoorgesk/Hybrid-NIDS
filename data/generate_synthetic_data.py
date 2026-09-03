import pandas as pd
import numpy as np
import os

def generate_data(num_samples=10000):
    np.random.seed(42)
    
    # Define labels and distributions
    labels = ['Normal', 'DDoS', 'PortScan', 'BruteForce']
    probabilities = [0.70, 0.15, 0.10, 0.05]
    y = np.random.choice(labels, size=num_samples, p=probabilities)
    
    df = pd.DataFrame({'Label': y})
    
    # Initialize features with baseline benign traffic patterns
    df['flow_duration'] = np.random.uniform(0.1, 100, num_samples)
    df['total_fwd_packets'] = np.random.randint(1, 20, num_samples)
    df['total_bwd_packets'] = np.random.randint(1, 20, num_samples)
    df['fwd_packet_length_max'] = np.random.uniform(0, 1500, num_samples)
    df['bwd_packet_length_max'] = np.random.uniform(0, 1500, num_samples)
    df['flow_bytes_per_sec'] = np.random.uniform(100, 10000, num_samples)
    df['flow_packets_per_sec'] = np.random.uniform(1, 100, num_samples)
    df['syn_flag_count'] = np.random.randint(0, 3, num_samples)
    df['ack_flag_count'] = np.random.randint(0, 5, num_samples)
    df['rst_flag_count'] = np.random.randint(0, 2, num_samples)
    
    # Inject realistic statistical variance for specific attack classes
    
    # DDoS: Extremely high packet rates and large forward packet counts
    ddos_mask = df['Label'] == 'DDoS'
    df.loc[ddos_mask, 'flow_packets_per_sec'] = np.random.uniform(1000, 5000, ddos_mask.sum())
    df.loc[ddos_mask, 'total_fwd_packets'] = np.random.randint(50, 200, ddos_mask.sum())
    
    # PortScan: High SYN count, tiny packet sizes, negligible backward packets
    ps_mask = df['Label'] == 'PortScan'
    df.loc[ps_mask, 'syn_flag_count'] = np.random.randint(10, 50, ps_mask.sum())
    df.loc[ps_mask, 'fwd_packet_length_max'] = np.random.uniform(0, 100, ps_mask.sum())
    df.loc[ps_mask, 'bwd_packet_length_max'] = 0
    df.loc[ps_mask, 'total_bwd_packets'] = 0
    
    # BruteForce: Extended flow duration, very high ACK counts (data exchange)
    bf_mask = df['Label'] == 'BruteForce'
    df.loc[bf_mask, 'flow_duration'] = np.random.uniform(500, 3600, bf_mask.sum())
    df.loc[bf_mask, 'ack_flag_count'] = np.random.randint(20, 100, bf_mask.sum())
    
    # Save to disk
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(current_dir, exist_ok=True)
    out_path = os.path.join(current_dir, 'synthetic_traffic.csv')
    df.to_csv(out_path, index=False)
    print(f"Generated highly realistic synthetic dataset (N={num_samples}) at {out_path}")

if __name__ == "__main__":
    generate_data()
