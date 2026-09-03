import time
from scapy.all import IP, TCP, UDP
from typing import Dict, Any, Callable

class FlowTracker:
    def __init__(self, expiry_callback: Callable[[Dict[str, Any]], None], timeout_sec: int = 5):
        self.flows = {}
        self.expiry_callback = expiry_callback
        self.timeout_sec = timeout_sec

    def process_packet(self, pkt):
        try:
            if IP in pkt:
                src_ip = pkt[IP].src
                dst_ip = pkt[IP].dst
                proto = pkt[IP].proto
                
                src_port, dst_port = 0, 0
                syn_flag = 0
                ack_flag = 0
                rst_flag = 0
                fin_flag = 0
                
                if TCP in pkt:
                    src_port = pkt[TCP].sport
                    dst_port = pkt[TCP].dport
                    flags = pkt[TCP].flags
                    if 'S' in flags: syn_flag = 1
                    if 'A' in flags: ack_flag = 1
                    if 'R' in flags: rst_flag = 1
                    if 'F' in flags: fin_flag = 1
                elif UDP in pkt:
                    src_port = pkt[UDP].sport
                    dst_port = pkt[UDP].dport
                    
                # Canonical 5-tuple key to track bi-directional flows
                if src_ip < dst_ip:
                    flow_key = (src_ip, dst_ip, src_port, dst_port, proto)
                    is_fwd = True
                else:
                    flow_key = (dst_ip, src_ip, dst_port, src_port, proto)
                    is_fwd = False
                    
                pkt_len = len(pkt)
                current_time = time.time()
                
                if flow_key not in self.flows:
                    self.flows[flow_key] = {
                        'start_time': current_time,
                        'last_time': current_time,
                        'total_fwd_packets': 0,
                        'total_bwd_packets': 0,
                        'fwd_packet_length_max': 0,
                        'bwd_packet_length_max': 0,
                        'total_bytes': 0,
                        'syn_flag_count': 0,
                        'ack_flag_count': 0,
                        'rst_flag_count': 0,
                        'src_ip': src_ip if is_fwd else dst_ip,
                        'dst_ip': dst_ip if is_fwd else src_ip,
                        'finished': False
                    }
                    
                flow = self.flows[flow_key]
                flow['last_time'] = current_time
                flow['total_bytes'] += pkt_len
                flow['syn_flag_count'] += syn_flag
                flow['ack_flag_count'] += ack_flag
                flow['rst_flag_count'] += rst_flag
                
                if is_fwd:
                    flow['total_fwd_packets'] += 1
                    flow['fwd_packet_length_max'] = max(flow['fwd_packet_length_max'], pkt_len)
                else:
                    flow['total_bwd_packets'] += 1
                    flow['bwd_packet_length_max'] = max(flow['bwd_packet_length_max'], pkt_len)
                    
                if fin_flag or rst_flag:
                    flow['finished'] = True
                    
        except Exception:
            # Drop malformed packets gracefully
            pass

    def check_expired_flows(self):
        current_time = time.time()
        expired_keys = []
        for key, flow in self.flows.items():
            if flow['finished'] or (current_time - flow['last_time'] > self.timeout_sec):
                expired_keys.append(key)
                
        for key in expired_keys:
            flow = self.flows.pop(key)
            duration_sec = max(flow['last_time'] - flow['start_time'], 0.0001) # Avoid DivByZero
            total_packets = flow['total_fwd_packets'] + flow['total_bwd_packets']
            
            features = {
                'flow_duration': duration_sec * 1000000, # Convert to microseconds for ML model
                'total_fwd_packets': flow['total_fwd_packets'],
                'total_bwd_packets': flow['total_bwd_packets'],
                'fwd_packet_length_max': flow['fwd_packet_length_max'],
                'bwd_packet_length_max': flow['bwd_packet_length_max'],
                'flow_bytes_per_sec': flow['total_bytes'] / duration_sec,
                'flow_packets_per_sec': total_packets / duration_sec,
                'syn_flag_count': flow['syn_flag_count'],
                'ack_flag_count': flow['ack_flag_count'],
                'rst_flag_count': flow['rst_flag_count'],
                '_src_ip': flow['src_ip'],
                '_dst_ip': flow['dst_ip']
            }
            self.expiry_callback(features)
