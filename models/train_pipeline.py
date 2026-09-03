import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import xgboost as xgb
import sys

def train_models():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'synthetic_traffic.csv')
    
    # Auto-generate data if it doesn't exist
    if not os.path.exists(data_path):
        print("Data file not found. Bootstrapping synthetic dataset...")
        sys.path.append(base_dir)
        from data.generate_synthetic_data import generate_data
        generate_data()
    
    df = pd.read_csv(data_path)
    y = df['Label']
    
    features = [
        'flow_duration', 'total_fwd_packets', 'total_bwd_packets', 
        'fwd_packet_length_max', 'bwd_packet_length_max', 
        'flow_bytes_per_sec', 'flow_packets_per_sec', 
        'syn_flag_count', 'ack_flag_count', 'rst_flag_count'
    ]
    X = df[features]
    
    print("1. Preprocessing data...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)
    
    print("2. Training Unsupervised Model (Isolation Forest)...")
    normal_mask = y == 'Normal'
    X_normal = X_scaled_df[normal_mask]
    
    if_model = IsolationForest(contamination=0.05, random_state=42)
    if_model.fit(X_normal)
    
    print("3. Training Supervised Model (XGBoost)...")
    label_mapping = {label: idx for idx, label in enumerate(y.unique())}
    y_encoded = y.map(label_mapping)
    
    # Calculate sample weights to correctly handle class imbalance (70/15/10/5)
    class_weights = len(y) / (len(label_mapping) * np.bincount(y_encoded))
    sample_weights = y_encoded.map(lambda x: class_weights[x])
    
    xgb_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
    xgb_model.fit(X_scaled, y_encoded, sample_weight=sample_weights)
    
    # Attach reverse mapping directly to the model object before serialization
    xgb_model.reverse_label_mapping = {idx: label for label, idx in label_mapping.items()}
    
    print("4. Serializing models...")
    models_dir = os.path.join(base_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))
    joblib.dump(if_model, os.path.join(models_dir, 'if_model.pkl'))
    joblib.dump(xgb_model, os.path.join(models_dir, 'xgb_model.pkl'))
    
    print(f"Models successfully trained and saved to {models_dir}")

if __name__ == "__main__":
    train_models()
