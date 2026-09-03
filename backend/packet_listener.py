import threading
import time
from scapy.all import AsyncSniffer
from backend.feature_extractor import FlowTracker
from backend.inference_engine import InferenceEngine

class PacketListener:
    def __init__(self, alert_callback):
        self.alert_callback = alert_callback
        self.engine = InferenceEngine()
        self.tracker = FlowTracker(expiry_callback=self.on_flow_expired, timeout_sec=5)
        self.sniffer = None
        self.running = False
        
        # Metrics
        self.total_packets_analyzed = 0
        self.total_threats = 0
        
    def start(self):
        if self.running: return
        self.running = True
        
        # Non-blocking async packet sniffer
        self.sniffer = AsyncSniffer(prn=self.on_packet, store=False)
        self.sniffer.start()
        
        # Background cleanup thread
        self.cleanup_thread = threading.Thread(target=self._flow_cleanup_loop, daemon=True)
        self.cleanup_thread.start()

    def stop(self):
        self.running = False
        if self.sniffer:
            self.sniffer.stop()

    def on_packet(self, pkt):
        self.total_packets_analyzed += 1
        self.tracker.process_packet(pkt)
        
    def _flow_cleanup_loop(self):
        while self.running:
            self.tracker.check_expired_flows()
            time.sleep(1)
            
    def on_flow_expired(self, flow_features):
        result = self.engine.predict(flow_features)
        
        if result['verdict'] != 'Benign':
            self.total_threats += 1
            alert = {
                'Timestamp': time.time(),
                'Src IP': flow_features.get('_src_ip', '0.0.0.0'),
                'Dst IP': flow_features.get('_dst_ip', '0.0.0.0'),
                'Verdict': result['verdict'],
                'Severity': result['threat_level'],
                'Confidence': result['confidence']
            }
            if self.alert_callback:
                self.alert_callback(alert)
