# Hybrid Real-Time Network Intrusion Detection System (NIDS)

A production-ready, AI-powered Network Intrusion Detection System that combines **unsupervised anomaly detection** (Isolation Forest) with **supervised multi-class classification** (XGBoost) to detect both known cyberattacks and zero-day threats in real-time.

Built with Scapy for live packet capture, FastAPI for the backend engine, and Streamlit for a dark-themed cybersecurity dashboard.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        NETWORK INTERFACE                         │
└──────────────┬───────────────────────────────────────────────────┘
               │ Raw Packets
               ▼
┌──────────────────────────┐
│   Scapy AsyncSniffer     │  Real-time packet capture
│   (packet_listener.py)   │  Non-blocking background thread
└──────────────┬───────────┘
               │ Individual Packets
               ▼
┌──────────────────────────┐
│   Flow Tracker           │  Groups packets into bidirectional flows
│   (feature_extractor.py) │  using canonical 5-tuple keys
│                          │  (SrcIP, DstIP, SrcPort, DstPort, Proto)
│                          │  Expires flows after 5s idle or FIN/RST
└──────────────┬───────────┘
               │ 10 Extracted Features per Flow
               ▼
┌──────────────────────────────────────────────────────┐
│              DUAL AI ENGINE                           │
│                                                       │
│  ┌─────────────────────┐  ┌────────────────────────┐ │
│  │  Isolation Forest   │  │  XGBoost Classifier    │ │
│  │  (Unsupervised)     │  │  (Supervised)          │ │
│  │                     │  │                        │ │
│  │  Trained on Normal  │  │  Trained on all 4      │ │
│  │  traffic only       │  │  classes with sample   │ │
│  │                     │  │  weight balancing      │ │
│  │  Detects: Zero-Day  │  │  Detects: DDoS,       │ │
│  │  anomalies          │  │  PortScan, BruteForce  │ │
│  └────────┬────────────┘  └───────────┬────────────┘ │
│           │                           │               │
│           └───────────┬───────────────┘               │
│                       ▼                               │
│            ┌─────────────────────┐                    │
│            │   Verdict Engine    │                    │
│            │                     │                    │
│            │  IF anomaly + XGB   │                    │
│            │  says Normal →      │                    │
│            │  "Zero-Day Anomaly" │                    │
│            │                     │                    │
│            │  XGB attack class   │                    │
│            │  with >70% conf →   │                    │
│            │  "Known Attack"     │                    │
│            └────────┬────────────┘                    │
└─────────────────────┼────────────────────────────────┘
                      │ Verdict + Severity
                      ▼
┌──────────────────────────────────────────────────────┐
│                 FastAPI Backend                        │
│                                                       │
│  WebSocket /ws/alerts    GET /metrics                 │
│  (real-time broadcast)   (system stats)               │
└──────────────┬───────────────────────────────────────┘
               │ JSON Alerts via WebSocket
               ▼
┌──────────────────────────────────────────────────────┐
│              Streamlit Dashboard                      │
│                                                       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐ │
│  │ Packets │ │ Threats │ │ Active  │ │  Threat   │ │
│  │Analyzed │ │ Blocked │ │  Flows  │ │  Level    │ │
│  └─────────┘ └─────────┘ └─────────┘ └───────────┘ │
│                                                       │
│  ┌───────────────────────────────────────────────┐   │
│  │     Threat Frequency Chart (Plotly)           │   │
│  └───────────────────────────────────────────────┘   │
│                                                       │
│  ┌───────────────────────────────────────────────┐   │
│  │     Live Alert Table (color-coded severity)   │   │
│  └───────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

---

## Features

- **Dual-Engine AI Detection** — Combines Isolation Forest (unsupervised) with XGBoost (supervised) for comprehensive threat coverage
- **Zero-Day Detection** — Identifies previously unseen attack patterns that don't match any known signature
- **Multi-Class Classification** — Classifies attacks into DDoS, PortScan, and BruteForce with confidence scores
- **Real-Time Packet Capture** — Uses Scapy's AsyncSniffer for non-blocking live traffic interception
- **Bidirectional Flow Tracking** — Groups packets into flows using canonical 5-tuple keys with automatic expiration
- **WebSocket Broadcasting** — Pushes alerts instantly to all connected dashboard clients
- **Dark-Themed Dashboard** — Premium cybersecurity aesthetic with OLED-black design, emerald accents, and JetBrains Mono typography
- **Docker Support** — Full containerization with docker-compose for one-command deployment

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Networking | Scapy | Real-time packet sniffing and flow state tracking |
| ML (Unsupervised) | scikit-learn (Isolation Forest) | Zero-day anomaly detection |
| ML (Supervised) | XGBoost | Multi-class attack classification |
| Preprocessing | scikit-learn (StandardScaler) | Feature normalization |
| Backend | FastAPI + Uvicorn | REST API + WebSocket server |
| Frontend | Streamlit + Plotly | Real-time dashboard |
| Infrastructure | Docker + docker-compose | Containerized deployment |

---

## Project Structure

```
hybrid-nids/
├── data/
│   └── generate_synthetic_data.py    # Generates 10,000 realistic network flows
├── models/
│   └── train_pipeline.py             # Trains Isolation Forest + XGBoost
├── backend/
│   ├── main.py                       # FastAPI app with WebSocket broadcasting
│   ├── packet_listener.py            # Scapy AsyncSniffer integration
│   ├── feature_extractor.py          # Flow tracking and feature extraction
│   └── inference_engine.py           # Dual-engine AI prediction logic
├── frontend/
│   └── dashboard.py                  # Streamlit real-time dashboard
├── test_attacks.py                   # Attack simulation test suite
├── requirements.txt
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

---

## Dataset

Since the original CICIDS-2017 dataset is 1GB+, this project uses a synthetic data generator that creates **10,000 realistic network flow records** with statistically accurate distributions per attack class:

| Class | Distribution | Key Characteristics |
|-------|-------------|-------------------|
| Normal | 70% | Baseline traffic patterns |
| DDoS | 15% | High `flow_packets_per_sec` (1000-5000), high `total_fwd_packets` (50-200) |
| PortScan | 10% | High `syn_flag_count` (10-50), zero `bwd_packet_length_max`, zero `total_bwd_packets` |
| BruteForce | 5% | Long `flow_duration` (500-3600s), high `ack_flag_count` (20-100) |

### Extracted Features (10)

| Feature | Description |
|---------|-------------|
| `flow_duration` | Duration of the flow in seconds |
| `total_fwd_packets` | Total packets in the forward direction |
| `total_bwd_packets` | Total packets in the backward direction |
| `fwd_packet_length_max` | Maximum packet size in forward direction |
| `bwd_packet_length_max` | Maximum packet size in backward direction |
| `flow_bytes_per_sec` | Flow throughput in bytes per second |
| `flow_packets_per_sec` | Flow rate in packets per second |
| `syn_flag_count` | Number of SYN flags observed |
| `ack_flag_count` | Number of ACK flags observed |
| `rst_flag_count` | Number of RST flags observed |

---

## ML Pipeline

### Preprocessing
- **Scaling:** `StandardScaler` (mean=0, std=1) fitted on all feature columns
- **Class Imbalance:** Handled via dynamically calculated `sample_weight` during XGBoost training

### Model 1: Isolation Forest (Unsupervised)
- Trained exclusively on `Normal` traffic
- `contamination=0.05`, `random_state=42`
- Detects anomalies via decision function score < -0.5

### Model 2: XGBoost Classifier (Supervised)
- Trained on entire dataset (all 4 classes)
- `eval_metric='mlogloss'`, `random_state=42`
- Outputs predicted class + confidence probability

### Verdict Logic
```
IF Isolation Forest flags anomaly AND XGBoost predicts Normal:
    → "Zero-Day Anomaly" (HIGH severity)

ELIF XGBoost predicts attack class with >70% confidence:
    → "Known Attack: {class}" (HIGH/LOW severity)

ELSE:
    → "Benign" (no alert)
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- [Npcap](https://npcap.com/#download) (Windows only — check "Install in WinPcap API-compatible Mode")

### Option A: Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/hybrid-nids.git
cd hybrid-nids

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate data and train models
python models/train_pipeline.py

# 4. Start the backend (Terminal 1)
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 5. Start the dashboard (Terminal 2)
streamlit run frontend/dashboard.py
```

Open **http://localhost:8501** to view the dashboard.

### Option B: Run with Docker

```bash
docker-compose up --build
```

- Dashboard: **http://localhost:8501**
- Backend API: **http://localhost:8000**

---

## Testing

Run the attack simulation test suite to verify the detection engine:

```bash
python test_attacks.py
```

This simulates 6 realistic attack scenarios:
- 2x DDoS (Volumetric Flood + SYN Flood)
- 2x Port Scan (SYN Sweep + Stealth Scan)
- 2x Brute Force (SSH + FTP)

Results appear in the terminal and are pushed to the live dashboard.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/metrics` | Returns total packets analyzed, threats blocked, active flows, uptime |
| WebSocket | `/ws/alerts` | Real-time alert stream (JSON) |
| POST | `/test_alert` | Inject test alerts into the dashboard |

### Sample `/metrics` Response
```json
{
  "uptime_seconds": 342.5,
  "total_packets_analyzed": 4821,
  "total_threats_blocked": 12,
  "active_flows": 3
}
```

### Sample WebSocket Alert
```json
{
  "Timestamp": 1693612345.67,
  "Src IP": "192.168.1.105",
  "Dst IP": "10.0.0.50",
  "Verdict": "Known Attack: DDoS",
  "Severity": "HIGH",
  "Confidence": 0.9847
}
```

---

## Dashboard

The frontend features a premium dark-tech cybersecurity aesthetic:

- **OLED-black** background with emerald accent color
- **JetBrains Mono** for data typography, **Inter** for headings
- **Glass-panel** KPI cards with hover glow effects
- **Color-coded** severity badges (RED = HIGH, AMBER = LOW, EMERALD = NONE)
- **Plotly** stacked bar chart for threat frequency over time
- **Custom HTML** alert table with left-border severity indicators
- **Pulsing status dot** indicating active monitoring
- **Auto-refresh** every 1.5 seconds

---

## License

This project is built for educational and research purposes. Use responsibly and only on networks you own or have explicit permission to monitor.
#   H y b r i d - N I D S  
 