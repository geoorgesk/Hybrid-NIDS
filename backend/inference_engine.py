import os
import joblib
import numpy as np

class InferenceEngine:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_dir = os.path.join(base_dir, 'models')
        
        self.scaler = joblib.load(os.path.join(models_dir, 'scaler.pkl'))
        self.if_model = joblib.load(os.path.join(models_dir, 'if_model.pkl'))
        self.xgb_model = joblib.load(os.path.join(models_dir, 'xgb_model.pkl'))
        
        self.feature_names = [
            'flow_duration', 'total_fwd_packets', 'total_bwd_packets', 
            'fwd_packet_length_max', 'bwd_packet_length_max', 
            'flow_bytes_per_sec', 'flow_packets_per_sec', 
            'syn_flag_count', 'ack_flag_count', 'rst_flag_count'
        ]

    def predict(self, flow_features: dict) -> dict:
        try:
            import pandas as pd
            # Extract dynamically built features in strictly the correct order
            feature_vals = [[flow_features.get(f, 0.0) for f in self.feature_names]]
            
            # Convert to DataFrame to match training data structure and prevent warnings
            X_df = pd.DataFrame(feature_vals, columns=self.feature_names)
            X_scaled = self.scaler.transform(X_df)
            X_scaled_df = pd.DataFrame(X_scaled, columns=self.feature_names)
            
            # Isolation Forest anomaly score (< -0.5 designates strong anomaly)
            if_score = self.if_model.decision_function(X_scaled_df)[0]
            is_anomaly = if_score < -0.5
            
            # XGBoost prediction
            xgb_probs = self.xgb_model.predict_proba(X_scaled)[0]
            xgb_pred_idx = np.argmax(xgb_probs)
            xgb_conf = float(xgb_probs[xgb_pred_idx])
            
            # Use reverse mapping stored during training, default to benign
            mapping = getattr(self.xgb_model, 'reverse_label_mapping', {0: 'Normal', 1: 'DDoS', 2: 'PortScan', 3: 'BruteForce'})
            xgb_class = mapping.get(xgb_pred_idx, 'Normal')
            
            verdict = 'Benign'
            threat_level = 'NONE'
            
            # Multi-layer Verdict Engine Logic
            if is_anomaly and xgb_class == 'Normal':
                verdict = 'Zero-Day Anomaly'
                threat_level = 'HIGH'
            elif xgb_class != 'Normal' and xgb_conf > 0.70:
                verdict = f'Known Attack: {xgb_class}'
                threat_level = 'HIGH' if xgb_class in ['DDoS', 'BruteForce'] else 'LOW'
                
            return {
                'verdict': verdict,
                'threat_level': threat_level,
                'confidence': round(xgb_conf, 4)
            }
        except Exception as e:
            return {
                'verdict': 'Engine Error',
                'threat_level': 'NONE',
                'confidence': 0.0,
                'error': str(e)
            }
