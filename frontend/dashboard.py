import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
import requests

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="NIDS  |  Hybrid Intrusion Detection",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><text y='14' font-size='14'>&#x1f6e1;</text></svg>",
)

# ---------------------------------------------------------------------------
# PREMIUM DARK-TECH CSS (runs once, never reloads)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    .stApp {
        background: #050508;
        color: #e4e4e7;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp > header { background: transparent !important; }
    #MainMenu, footer, .stDeployButton { display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0a0a0f; }
    ::-webkit-scrollbar-thumb { background: #1c1c24; border-radius: 3px; }

    .section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px; font-weight: 600;
        letter-spacing: 0.2em; text-transform: uppercase;
        color: #10b981; margin-bottom: 4px; display: block;
    }
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 20px; font-weight: 600;
        color: #fafafa; letter-spacing: -0.02em; margin-bottom: 20px;
    }

    .badge-high {
        display: inline-block; background: rgba(239,68,68,0.12);
        color: #f87171; border: 1px solid rgba(239,68,68,0.2);
        border-radius: 999px; padding: 2px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    }
    .badge-low {
        display: inline-block; background: rgba(251,191,36,0.1);
        color: #fbbf24; border: 1px solid rgba(251,191,36,0.15);
        border-radius: 999px; padding: 2px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    }
    .badge-none {
        display: inline-block; background: rgba(16,185,129,0.1);
        color: #10b981; border: 1px solid rgba(16,185,129,0.15);
        border-radius: 999px; padding: 2px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    }

    .kpi-card {
        background: linear-gradient(145deg, #0d0d14 0%, #0a0a10 100%);
        border: 1px solid rgba(255,255,255,0.04); border-radius: 16px;
        padding: 28px 24px;
        box-shadow: 0 0 40px rgba(16,185,129,0.015), inset 0 1px 0 rgba(255,255,255,0.03);
        min-height: 130px;
    }
    .kpi-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px; font-weight: 500;
        letter-spacing: 0.14em; text-transform: uppercase;
        color: #71717a; margin-bottom: 12px;
    }
    .kpi-value {
        font-family: 'Inter', sans-serif;
        font-size: 36px; font-weight: 700;
        color: #fafafa; letter-spacing: -0.03em; line-height: 1;
    }
    .kpi-value.emerald { color: #10b981; }
    .kpi-value.red { color: #f87171; }
    .kpi-value.amber { color: #fbbf24; }

    .glass-panel {
        background: linear-gradient(145deg, #0d0d14 0%, #08080d 100%);
        border: 1px solid rgba(255,255,255,0.04); border-radius: 20px;
        padding: 28px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
        margin-bottom: 24px;
    }

    .alert-table {
        width: 100%; border-collapse: separate; border-spacing: 0 6px;
        font-family: 'JetBrains Mono', monospace; font-size: 12px;
    }
    .alert-table th {
        font-size: 9px; font-weight: 600;
        letter-spacing: 0.16em; text-transform: uppercase;
        color: #52525b; padding: 8px 16px; text-align: left; border: none;
    }
    .alert-table td { padding: 12px 16px; color: #d4d4d8; border: none; }
    .alert-table .row-high { background: rgba(239,68,68,0.06); border-left: 3px solid #ef4444; }
    .alert-table .row-high td:first-child { border-radius: 12px 0 0 12px; }
    .alert-table .row-high td:last-child { border-radius: 0 12px 12px 0; }
    .alert-table .row-low { background: rgba(251,191,36,0.04); border-left: 3px solid #f59e0b; }
    .alert-table .row-low td:first-child { border-radius: 12px 0 0 12px; }
    .alert-table .row-low td:last-child { border-radius: 0 12px 12px 0; }
    .alert-table .row-none { background: rgba(16,185,129,0.04); border-left: 3px solid #10b981; }
    .alert-table .row-none td:first-child { border-radius: 12px 0 0 12px; }
    .alert-table .row-none td:last-child { border-radius: 0 12px 12px 0; }

    .status-dot {
        display: inline-block; width: 8px; height: 8px; border-radius: 50%;
        background: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.5);
        animation: pulse-glow 2s ease-in-out infinite;
        margin-right: 8px; vertical-align: middle;
    }
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 8px rgba(16,185,129,0.4); }
        50% { box-shadow: 0 0 16px rgba(16,185,129,0.7); }
    }

    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.06) 50%, transparent 100%);
        margin: 32px 0;
    }

    div[data-testid="stHorizontalBlock"] { gap: 16px; }
    .stPlotlyChart { border-radius: 16px; overflow: hidden; }

    /* Aggressively disable Streamlit's native loading dim/opacity fade */
    .stApp * {
        transition: none !important;
    }
    [data-testid="stMain"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"] {
        background: #050508 !important;
        opacity: 1 !important;
        filter: none !important;
    }
    
    /* Hide the top right "Running..." indicator completely */
    [data-testid="stStatusWidget"] {
        display: none !important;
        opacity: 0 !important;
    }

    /* Premium Hardware-Accelerated Micro-Motion: Engine Scanner Line */
    .engine-scanner {
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #10b981 50%, transparent 100%);
        z-index: 999999;
        opacity: 0.8;
        transform-origin: left;
        animation: scan-line 2.5s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }
    @keyframes scan-line {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }

    .header-bar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 0 32px 0;
    }
    .header-title {
        font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 700;
        color: #fafafa; letter-spacing: -0.03em;
    }
    .header-subtitle {
        font-family: 'JetBrains Mono', monospace; font-size: 11px;
        color: #52525b; letter-spacing: 0.04em; margin-top: 4px;
    }
    .header-status {
        font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #71717a;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# STATIC HEADER (runs once, never flickers)
# ---------------------------------------------------------------------------
st.markdown("""
<div class="engine-scanner"></div>
<div class="header-bar">
    <div>
        <div class="header-title">Hybrid NIDS</div>
        <div class="header-subtitle">Real-Time Network Intrusion Detection System</div>
    </div>
    <div class="header-status">
        <span class="status-dot"></span> ENGINE ACTIVE
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# AUTO-REFRESH (zero-flicker native integration)
# ---------------------------------------------------------------------------
from streamlit_autorefresh import st_autorefresh
# Refresh every 3000 milliseconds (3 seconds) to avoid reload loops
st_autorefresh(interval=3000, key="data_refresh")

# ---------------------------------------------------------------------------
# LIVE DATA LOGIC
# ---------------------------------------------------------------------------
BACKEND_URL = "http://localhost:8000"
sev_badge = {'HIGH': 'badge-high', 'LOW': 'badge-low', 'NONE': 'badge-none'}

def live_dashboard():
    # Fetch fresh data from backend
    alerts = []
    metrics = {"total_packets": 0, "active_flows": 0, "total_threats": 0}

    # Extremely short timeouts (0.5s) to ensure Streamlit renders even if backend is offline
    try:
        res = requests.get(f"{BACKEND_URL}/metrics", timeout=0.5)
        if res.status_code == 200:
            data = res.json()
            metrics['total_packets'] = data.get('total_packets_analyzed', 0)
            metrics['active_flows'] = data.get('active_flows', 0)
            metrics['total_threats'] = data.get('total_threats_blocked', 0)
    except Exception:
        pass

    try:
        res = requests.get(f"{BACKEND_URL}/alerts", timeout=0.5)
        if res.status_code == 200:
            alerts = res.json()
            for a in alerts:
                if 'Timestamp' in a and 'Time' not in a:
                    a['Time'] = datetime.fromtimestamp(a['Timestamp']).strftime('%H:%M:%S')
    except Exception:
        pass

    highest_severity = "NONE"
    for a in alerts:
        if a.get('Severity') == 'HIGH':
            highest_severity = 'HIGH'
            break
        elif a.get('Severity') == 'LOW':
            highest_severity = 'LOW'

    # --- KPI ROW ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Packets Analyzed</div>
            <div class="kpi-value">{metrics['total_packets']:,}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Threats Blocked</div>
            <div class="kpi-value red">{metrics['total_threats']:,}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Active Flows</div>
            <div class="kpi-value emerald">{metrics['active_flows']:,}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Threat Level</div>
            <div style="margin-top: 8px;">
                <span class="{sev_badge[highest_severity]}">{highest_severity}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # --- THREAT FREQUENCY CHART ---
    st.markdown('<span class="section-label">Analytics</span>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Threat Frequency</div>', unsafe_allow_html=True)

    alerts_df = pd.DataFrame(alerts)

    if not alerts_df.empty and 'Timestamp' in alerts_df.columns:
        alerts_df['TimestampObj'] = pd.to_datetime(alerts_df['Timestamp'], unit='s')
        df_grouped = alerts_df.groupby(
            [pd.Grouper(key='TimestampObj', freq='10s'), 'Severity']
        ).size().reset_index(name='Count')

        color_map = {'HIGH': '#ef4444', 'LOW': '#f59e0b', 'NONE': '#10b981'}
        fig = go.Figure()
        for severity in ['HIGH', 'LOW', 'NONE']:
            subset = df_grouped[df_grouped['Severity'] == severity]
            if not subset.empty:
                fig.add_trace(go.Bar(
                    x=subset['TimestampObj'], y=subset['Count'],
                    name=severity, marker_color=color_map.get(severity, '#10b981'),
                    marker_line_width=0, opacity=0.85,
                ))

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='JetBrains Mono, monospace', size=11, color='#71717a'),
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10, color='#52525b')),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', zeroline=False, tickfont=dict(size=10, color='#52525b')),
            legend=dict(orientation='h', yanchor='bottom', y=1.04, xanchor='right', x=1, font=dict(size=10, color='#a1a1aa'), bgcolor='rgba(0,0,0,0)'),
            bargap=0.15, barmode='stack', margin=dict(l=0, r=0, t=20, b=0), height=320,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("""
        <div style="background: rgba(16,185,129,0.04); border: 1px solid rgba(16,185,129,0.08);
             border-radius: 16px; padding: 48px; text-align: center;">
            <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px;
                 letter-spacing: 0.1em; text-transform: uppercase; color: #10b981; margin-bottom: 8px;">
                Monitoring Active
            </div>
            <div style="font-family: 'Inter', sans-serif; font-size: 14px; color: #52525b;">
                Scanning network traffic. Threats will appear here in real-time.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # --- LIVE ALERT TABLE ---
    st.markdown('<span class="section-label">Live Feed</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Recent Alerts <span style="font-size:13px;color:#52525b;font-weight:400;">({len(alerts)} total)</span></div>', unsafe_allow_html=True)

    if alerts:
        rows_html = ""
        for alert in alerts[:100]:
            sev = alert.get('Severity', 'NONE')
            row_class = f"row-{sev.lower()}" if sev in ('HIGH', 'LOW') else 'row-none'
            conf = alert.get('Confidence', 0)
            conf_str = f"{conf:.1%}" if isinstance(conf, (int, float)) and conf <= 1 else str(conf)
            sev_badge_class = sev_badge.get(sev, 'badge-none')
            alert_time = alert.get('Time', datetime.fromtimestamp(alert.get('Timestamp', 0)).strftime('%H:%M:%S'))

            rows_html += f"""
            <tr class="{row_class}">
                <td style="color:#71717a;">{alert_time}</td>
                <td>{alert.get('Src IP', '—')}</td>
                <td>{alert.get('Dst IP', '—')}</td>
                <td style="color:#fafafa; font-weight:500;">{alert.get('Verdict', '—')}</td>
                <td><span class="{sev_badge_class}">{sev}</span></td>
                <td>{conf_str}</td>
            </tr>"""

        st.markdown(f"""
        <div class="glass-panel" style="padding: 16px 20px; overflow-x: auto;">
            <table class="alert-table">
                <thead><tr>
                    <th>Time</th><th>Source</th><th>Destination</th>
                    <th>Verdict</th><th>Severity</th><th>Confidence</th>
                </tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
             border-radius: 16px; padding: 48px; text-align: center;">
            <div style="font-family: 'Inter', sans-serif; font-size: 14px; color: #3f3f46;">
                No alerts recorded yet
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- FOOTER ---
    st.markdown(f"""
    <div class="divider"></div>
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0 4px;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #3f3f46; letter-spacing: 0.06em;">
            HYBRID NIDS v1.0  //  Isolation Forest + XGBoost Dual Engine
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #3f3f46; letter-spacing: 0.06em;">
            {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Run the live dashboard
live_dashboard()
