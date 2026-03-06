# =============================================================================
#  AEGIS OS — EV Fleet Intelligence & Security Platform
#  Single-file Streamlit app | Python 3.10+ | Streamlit 1.30+
#  v3.3.0 — Fixed mediapipe API, Neural Core import, + Map Assistant terminal
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time
import datetime
import hashlib
import base64
import io
import warnings
warnings.filterwarnings("ignore")

# ── Optional heavy deps with graceful fallback ──────────────────────────────
CV2_AVAILABLE   = False
MP_AVAILABLE    = False
MP_LEGACY_API   = False   # True only if mp.solutions.hands exists (mediapipe <=0.10.3)
SR_AVAILABLE    = False
GTTS_AVAILABLE  = False
SCIPY_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    pass

try:
    import mediapipe as mp
    MP_AVAILABLE = True
    try:
        _ = mp.solutions.hands   # works on mediapipe <= 0.10.3
        MP_LEGACY_API = True
    except AttributeError:
        MP_LEGACY_API = False    # mediapipe 0.10.4+ dropped mp.solutions.*
except ImportError:
    pass

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    pass

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    pass

try:
    from scipy import stats
    from scipy.signal import savgol_filter
    SCIPY_AVAILABLE = True
except ImportError:
    pass

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AEGIS OS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
#  CLASS: AegisUI
# =============================================================================
class AegisUI:
    CYAN   = "#00d2ff"
    PINK   = "#ff00c1"
    CARD   = "rgba(15,15,30,0.75)"
    BORDER = "rgba(0,210,255,0.25)"

    @staticmethod
    def inject_css():
        st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Courier+Prime&display=swap');
        html, body, [data-testid="stAppViewContainer"] {{
            background: radial-gradient(ellipse at center, #0d0d1f 0%, #050510 100%) !important;
            color: #e0e8ff; font-family: 'Courier Prime', monospace;
        }}
        [data-testid="stSidebar"] {{
            background: rgba(5,5,20,0.92) !important;
            border-right: 1px solid {AegisUI.BORDER};
        }}
        .glitch-header {{
            font-family: 'Syncopate', sans-serif; font-size: 2rem; font-weight: 700;
            color: {AegisUI.CYAN};
            text-shadow: 0 0 8px {AegisUI.CYAN}, 0 0 20px {AegisUI.CYAN},
                         2px 0 {AegisUI.PINK}, -2px 0 {AegisUI.CYAN};
            letter-spacing: 4px; margin-bottom: 0.2rem;
        }}
        .sub-header {{
            font-family: 'Syncopate', sans-serif; font-size: 0.75rem;
            color: rgba(0,210,255,0.55); letter-spacing: 6px; margin-bottom: 1.5rem;
        }}
        .metric-card {{
            background: {AegisUI.CARD}; border: 1px solid {AegisUI.BORDER};
            border-radius: 12px; padding: 1.1rem 1.4rem;
            backdrop-filter: blur(12px); transition: box-shadow .25s;
        }}
        .metric-card:hover {{ box-shadow: 0 0 18px rgba(0,210,255,0.35); }}
        .metric-value {{
            font-family: 'Syncopate', sans-serif; font-size: 2rem;
            font-weight: 700; color: {AegisUI.CYAN};
        }}
        .metric-label {{
            font-size: 0.72rem; letter-spacing: 3px;
            color: rgba(224,232,255,0.55); text-transform: uppercase;
        }}
        .metric-delta-pos {{ color: #00ff9f; font-size: 0.8rem; }}
        .metric-delta-neg {{ color: {AegisUI.PINK}; font-size: 0.8rem; }}
        .log-block {{
            background: rgba(0,0,0,0.55); border-left: 3px solid {AegisUI.CYAN};
            border-radius: 4px; padding: 0.8rem 1rem;
            font-family: 'Courier Prime', monospace; font-size: 0.78rem;
            color: #a0ffcc; max-height: 280px; overflow-y: auto;
        }}
        .log-warn {{ color: #ffdd57; }}
        .log-crit {{ color: {AegisUI.PINK}; }}
        .sidebar-logo {{
            font-family: 'Syncopate', sans-serif; font-size: 1.4rem; font-weight: 700;
            color: {AegisUI.CYAN}; text-align: center; letter-spacing: 6px;
            padding: 1rem 0 0.3rem; text-shadow: 0 0 14px {AegisUI.CYAN};
        }}
        .stProgress > div > div > div > div {{
            background: linear-gradient(90deg, {AegisUI.CYAN}, {AegisUI.PINK});
        }}
        .stButton > button {{
            background: transparent; border: 1px solid {AegisUI.CYAN};
            color: {AegisUI.CYAN}; border-radius: 6px;
            font-family: 'Syncopate', sans-serif; font-size: 0.7rem;
            letter-spacing: 2px; transition: all .2s;
        }}
        .stButton > button:hover {{
            background: rgba(0,210,255,0.12); box-shadow: 0 0 12px {AegisUI.CYAN};
        }}
        #MainMenu, footer, header {{ visibility: hidden; }}
        </style>""", unsafe_allow_html=True)

    @staticmethod
    def header(title: str, sub: str = ""):
        st.markdown(f'<div class="glitch-header">{title}</div>', unsafe_allow_html=True)
        if sub:
            st.markdown(f'<div class="sub-header">{sub}</div>', unsafe_allow_html=True)

    @staticmethod
    def metric_card(col, label: str, value: str, delta: str = "", positive: bool = True):
        cls  = "metric-delta-pos" if positive else "metric-delta-neg"
        d_html = f'<div class="{cls}">{delta}</div>' if delta else ""
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {d_html}
        </div>""", unsafe_allow_html=True)

    @staticmethod
    def log_line(text: str, level: str = "info") -> str:
        ts  = datetime.datetime.now().strftime("%H:%M:%S")
        cls = {"warn": "log-warn", "crit": "log-crit"}.get(level, "")
        return f'<span class="{cls}">[{ts}] {text}</span><br>'

    @staticmethod
    def dark_fig(fig: go.Figure, title: str = "") -> go.Figure:
        fig.update_layout(
            title=dict(text=title, font=dict(family="Syncopate", size=13, color=AegisUI.CYAN)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(10,10,20,0.6)",
            font=dict(color="#a0b0d0", family="Courier Prime"),
            legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=AegisUI.BORDER),
            margin=dict(l=40, r=20, t=45, b=35),
        )
        fig.update_xaxes(gridcolor="rgba(0,210,255,0.07)", zerolinecolor="rgba(0,210,255,0.15)")
        fig.update_yaxes(gridcolor="rgba(0,210,255,0.07)", zerolinecolor="rgba(0,210,255,0.15)")
        return fig


# =============================================================================
#  CLASS: AegisData
# =============================================================================
class AegisData:
    VEHICLE_IDS = [f"EV-{100+i}" for i in range(20)]
    CITIES      = ["Chennai","Mumbai","Delhi","Bengaluru","Hyderabad","Pune","Kolkata","Ahmedabad"]
    COMPONENTS  = ["Battery Pack","Motor Drive","BMS","Inverter","Thermal Mgmt","Regen Brake"]
    ERRORS      = ["SOC_DRIFT","TEMP_SPIKE","CAN_TIMEOUT","BMS_FAULT","OTA_FAIL","SENSOR_ERR","OVERVOLT"]
    AI_RES      = ["Auto-Healed","Resolved via OTA","Flagged for Inspection","Thermal Reset","Ignored-Low","Escalated"]
    CITY_COORDS = {
        "Chennai":   (13.0827, 80.2707), "Mumbai":    (19.0760, 72.8777),
        "Delhi":     (28.6139, 77.2090), "Bengaluru": (12.9716, 77.5946),
        "Hyderabad": (17.3850, 78.4867), "Pune":      (18.5204, 73.8567),
        "Kolkata":   (22.5726, 88.3639), "Ahmedabad": (23.0225, 72.5714),
    }

    @staticmethod
    def fleet_snapshot(seed: int = 42):
        rng    = np.random.default_rng(seed)
        n      = 20
        lats   = rng.uniform(8.5, 28.5, n)
        lons   = rng.uniform(72.5, 88.5, n)
        soc    = rng.integers(15, 100, n)
        speed  = rng.integers(0, 120, n)
        status = rng.choice(["ACTIVE","IDLE","CHARGING","ALERT"], n, p=[0.50,0.25,0.18,0.07])
        cities = rng.choice(AegisData.CITIES, n)
        temps  = rng.uniform(28, 52, n).round(1)
        return pd.DataFrame({
            "vehicle": AegisData.VEHICLE_IDS, "lat": lats, "lon": lons,
            "soc": soc, "speed_kmh": speed, "city": cities,
            "status": status, "temp_c": temps,
        })

    @staticmethod
    def rul_data():
        records = []
        for comp in AegisData.COMPONENTS:
            days     = np.arange(0, 365)
            base_rul = random.randint(200, 365)
            noise    = np.random.normal(0, 8, len(days))
            stress   = np.clip(100 - (days / base_rul) * 100 + noise, 0, 100)
            stress_s = savgol_filter(stress, 21, 3) if SCIPY_AVAILABLE else stress
            for d, s in zip(days[::7], stress_s[::7]):
                records.append({"day": int(d), "health_%": round(float(s), 2), "component": comp})
        return pd.DataFrame(records)

    @staticmethod
    def cyber_events(n=18):
        types = ["PORT_SCAN","BRUTE_FORCE","MITM","REPLAY","DDOS","SQL_INJECT","ARP_SPOOF"]
        sevs  = ["LOW","MED","HIGH","CRITICAL"]
        rows  = []
        for _ in range(n):
            ts = datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0, 3600))
            rows.append({
                "timestamp": ts.strftime("%H:%M:%S"),
                "src_ip":    f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
                "event":     random.choice(types),
                "severity":  random.choice(sevs),
                "blocked":   random.choice(["YES","YES","YES","NO"]),
                "hash":      hashlib.md5(str(random.random()).encode()).hexdigest()[:12],
            })
        return pd.DataFrame(rows).sort_values("timestamp", ascending=False)

    @staticmethod
    def energy_data():
        hrs = list(range(24))
        grd = [round(random.uniform(20, 95), 1) for _ in hrs]
        sol = [round(max(0, random.gauss(60, 20)) if 6 <= h <= 18 else 0, 1) for h in hrs]
        reg = [round(random.uniform(5, 30), 1) for _ in hrs]
        dem = [round(g+s+r, 1) for g, s, r in zip(grd, sol, reg)]
        return pd.DataFrame({"hour": hrs, "grid_kw": grd, "solar_kw": sol, "regen_kw": reg, "demand_kw": dem})

    @staticmethod
    def blackbox_logs(n=40):
        rows = []
        for _ in range(n):
            ts = datetime.datetime.now() - datetime.timedelta(minutes=random.randint(0, 1440))
            rows.append({
                "timestamp":     ts.strftime("%Y-%m-%d %H:%M:%S"),
                "vehicle":       random.choice(AegisData.VEHICLE_IDS),
                "error_code":    random.choice(AegisData.ERRORS),
                "severity":      random.choice(["INFO","WARN","ERROR","CRITICAL"]),
                "ai_resolution": random.choice(AegisData.AI_RES),
                "duration_ms":   random.randint(50, 5000),
            })
        return pd.DataFrame(rows).sort_values("timestamp", ascending=False).reset_index(drop=True)

    @staticmethod
    def ota_packages():
        return [
            {"name":"Kernel v4.7.2",    "size":"128 MB","progress":random.randint(60,100),"status":"DEPLOYING"},
            {"name":"BMS Firmware 3.1", "size":"42 MB", "progress":100,                   "status":"COMPLETE"},
            {"name":"Telematics SDK",   "size":"18 MB", "progress":random.randint(0,80),  "status":"QUEUED"},
            {"name":"Thermal Model v2", "size":"9 MB",  "progress":100,                   "status":"COMPLETE"},
            {"name":"ALPR Engine 5.0",  "size":"256 MB","progress":random.randint(10,70), "status":"DEPLOYING"},
        ]

    @staticmethod
    def alpr_lookup(plate: str):
        random.seed(abs(hash(plate)) % (2**31))
        fn = ["Arjun","Priya","Ravi","Sunita","Mohammed","Deepa","Kiran","Anjali"]
        ln = ["Sharma","Patel","Kumar","Singh","Reddy","Nair","Iyer","Khan"]
        flag = random.choices(["CLEAR","CLEAR","CLEAR","WARNING","CRITICAL"],weights=[50,20,10,15,5])[0]
        fd   = {"CLEAR":"No outstanding issues.",
                "WARNING":"Unpaid challan / traffic violation detected.",
                "CRITICAL":"Vehicle reported STOLEN — contact law enforcement immediately."}
        return {
            "plate": plate.upper(),
            "owner": f"{random.choice(fn)} {random.choice(ln)}",
            "chassis": "MA3"+"".join(random.choices("ABCDEFGHJKLMNPRSTUVWXYZ0123456789",k=14)),
            "insurer": random.choice(["HDFC Ergo","Bajaj Allianz","New India","Star Health","ICICI Lombard"]),
            "valid_until": f"2025-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "flag": flag, "flag_detail": fd[flag],
            "rto": random.choice(AegisData.CITIES),
        }

    @staticmethod
    def route_history(vehicle_id: str):
        random.seed(abs(hash(vehicle_id)) % 9999)
        city = random.choice(AegisData.CITIES)
        base_lat, base_lon = AegisData.CITY_COORDS[city]
        n    = 25
        lats = [base_lat + random.uniform(-0.08, 0.08) for _ in range(n)]
        lons = [base_lon + random.uniform(-0.08, 0.08) for _ in range(n)]
        lats = [sum(lats[max(0,i-2):i+3])/len(lats[max(0,i-2):i+3]) for i in range(n)]
        lons = [sum(lons[max(0,i-2):i+3])/len(lons[max(0,i-2):i+3]) for i in range(n)]
        ts_list  = [datetime.datetime.now()-datetime.timedelta(minutes=(n-i)*4) for i in range(n)]
        soc_vals = list(np.clip(np.cumsum([-random.uniform(0,1.5) for _ in range(n)])+85, 10, 100).round(1))
        return pd.DataFrame({
            "lat": lats, "lon": lons,
            "timestamp": [t.strftime("%H:%M") for t in ts_list],
            "speed_kmh": [random.randint(0, 100) for _ in range(n)],
            "soc_%":     soc_vals,
            "city":      city,
        })


# =============================================================================
#  CLASS: AegisHardware
# =============================================================================
class AegisHardware:

    # ── GESTURE SECURITY — Fixed for mediapipe v0.10+ ────────────────────────
    @staticmethod
    def gesture_terminal():
        AegisUI.header("✋ GESTURE SECURITY", "BIOMETRIC HAND-VECTOR AUTHENTICATION")

        if not CV2_AVAILABLE or not MP_AVAILABLE:
            missing = "OpenCV" if not CV2_AVAILABLE else "MediaPipe"
            st.warning(f"⚠️  {missing} not installed — running in simulation mode.")
            AegisHardware._gesture_simulation()
            return

        if not MP_LEGACY_API:
            st.warning(
                "⚠️  **MediaPipe `mp.solutions.hands` not found.**\n\n"
                "Your MediaPipe version (0.10.4+) removed the legacy `solutions` API.\n\n"
                "**Fix:** `pip install mediapipe==0.10.3`\n\n"
                "Showing simulation mode in the meantime."
            )
            AegisHardware._gesture_simulation()
            return

        st.info("📷 Camera access required. Check the box below to begin.")
        run          = st.checkbox("🟢 Start Gesture Scan", key="gesture_run")
        FRAME_WINDOW = st.empty()
        status_box   = st.empty()

        if run:
            try:
                mp_hands = mp.solutions.hands       # safe — MP_LEGACY_API is True here
                mp_draw  = mp.solutions.drawing_utils

                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    st.error("❌ Camera not found — switching to simulation.")
                    AegisHardware._gesture_simulation()
                    return

                detector     = mp_hands.Hands(static_image_mode=False, max_num_hands=1,
                                               min_detection_confidence=0.7)
                frame_count  = 0
                access_ok    = False

                while st.session_state.get("gesture_run", False):
                    ret, frame = cap.read()
                    if not ret:
                        break
                    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    result = detector.process(rgb)

                    if result.multi_hand_landmarks:
                        for hl in result.multi_hand_landmarks:
                            mp_draw.draw_landmarks(rgb, hl, mp_hands.HAND_CONNECTIONS)
                        if not access_ok:
                            access_ok = True
                            status_box.success("🔓 ACCESS GRANTED — Hand biometric verified!")
                    else:
                        status_box.info("🔍 Scanning… show your hand to the camera.")
                        access_ok = False

                    FRAME_WINDOW.image(rgb, channels="RGB", use_container_width=True)
                    frame_count += 1
                    if frame_count > 300:
                        break

                cap.release()
                detector.close()
            except Exception as exc:
                st.error(f"Gesture module error: {exc}")
                AegisHardware._gesture_simulation()

    @staticmethod
    def _gesture_simulation():
        st.markdown("""
        <div style="background:rgba(0,210,255,0.06);border:1px solid rgba(0,210,255,0.3);
             border-radius:10px;padding:1.5rem;text-align:center;">
            <div style="font-size:5rem">🖐️</div>
            <div style="color:#00d2ff;font-family:Syncopate,sans-serif;
                        letter-spacing:4px;margin-top:.5rem;">SIMULATION MODE</div>
            <div style="color:#aaa;font-size:.8rem;margin-top:.4rem;">
                21-point MediaPipe hand skeleton — simulated landmarks
            </div>
        </div>""", unsafe_allow_html=True)

        lm_names = ["WRIST","THUMB_CMC","THUMB_MCP","THUMB_IP","THUMB_TIP",
                    "INDEX_MCP","INDEX_PIP","INDEX_DIP","INDEX_TIP",
                    "MIDDLE_MCP","MIDDLE_PIP","MIDDLE_DIP","MIDDLE_TIP"]
        cols = st.columns(4)
        for i, lm in enumerate(lm_names):
            x = round(random.uniform(0.15, 0.85), 3)
            y = round(random.uniform(0.10, 0.90), 3)
            z = round(random.uniform(-0.12, 0.12), 3)
            cols[i % 4].metric(lm, f"({x},{y})", f"z={z}")

        # Simulated skeleton scatter
        n_lm = 21
        lx = [random.uniform(0.2, 0.8) for _ in range(n_lm)]
        ly = [random.uniform(0.1, 0.9) for _ in range(n_lm)]
        fig = go.Figure()
        connections = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
                       (0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),
                       (0,17),(17,18),(18,19),(19,20),(5,9),(9,13),(13,17)]
        for a, b in connections:
            fig.add_trace(go.Scatter(x=[lx[a],lx[b]], y=[ly[a],ly[b]], mode="lines",
                                     line=dict(color="rgba(0,210,255,0.4)",width=2),
                                     showlegend=False))
        fig.add_trace(go.Scatter(x=lx, y=ly, mode="markers+text",
                                  marker=dict(size=10, color="#ff00c1",
                                              line=dict(color="#00d2ff",width=1)),
                                  text=[str(i) for i in range(n_lm)],
                                  textposition="top center",
                                  textfont=dict(size=8, color="#a0ffcc"),
                                  name="Landmarks"))
        AegisUI.dark_fig(fig, "HAND LANDMARK SKELETON — SIMULATED")
        fig.update_layout(height=320,
                          xaxis=dict(range=[0,1], showticklabels=False),
                          yaxis=dict(range=[0,1], showticklabels=False, autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"✅ SIMULATED ACCESS GRANTED | Hand: {random.choice(['Right','Left'])} "
                   f"| Confidence: {round(random.uniform(95,99.5),1)}%")

    # ── VOICE ASSISTANT ──────────────────────────────────────────────────────
    @staticmethod
    def voice_terminal():
        AegisUI.header("🎙️ VOICE ASSISTANT", "JARVIS — NEURAL LANGUAGE INTERFACE")
        queries = ["Fleet status report","Battery health overview","Active vehicle count",
                   "Cyber threat level","Latest OTA updates"]
        responses = {
            "Fleet status report":     "All 20 EVs online. 10 active, 5 idle, 3 charging, 2 alert.",
            "Battery health overview": "Avg SOC 68%. Three vehicles below 20% threshold.",
            "Active vehicle count":    "10 vehicles in active transit across 6 metros.",
            "Cyber threat level":      "ORANGE threat level. 3 intrusion attempts blocked.",
            "Latest OTA updates":      "Kernel v4.7.2 at 83%. BMS Firmware 3.1 complete.",
        }
        sel_q    = st.selectbox("🗣️ Select Query:", queries)
        custom_q = st.text_input("Custom query:", placeholder="Ask AEGIS anything…")
        active_q = custom_q.strip() if custom_q.strip() else sel_q

        if st.button("🔴 TRANSMIT"):
            resp = responses.get(active_q, f"Query '{active_q}' processed. All systems nominal.")
            st.markdown(f"""
            <div class="log-block">
                <span style="color:#00d2ff;">▶ USER:</span> {active_q}<br>
                <span style="color:#00ff9f;">◀ JARVIS:</span> {resp}
            </div>""", unsafe_allow_html=True)
            if GTTS_AVAILABLE:
                try:
                    tts = gTTS(text=resp, lang='en', slow=False)
                    buf = io.BytesIO()
                    tts.write_to_fp(buf); buf.seek(0)
                    a64 = base64.b64encode(buf.read()).decode()
                    st.markdown(f'<audio controls autoplay>'
                                f'<source src="data:audio/mp3;base64,{a64}" type="audio/mp3">'
                                f'</audio>', unsafe_allow_html=True)
                except Exception:
                    st.caption("_Audio synthesis unavailable._")
            else:
                st.caption("_gTTS not installed — text-only mode._")

        st.markdown("#### 📜 SESSION LOG")
        hist = [("Fleet status report","10 active, 5 idle, 3 charging, 2 alert.","09:14:02"),
                ("Battery health overview","Avg SOC 68%. 3 below threshold.","09:14:45"),
                ("Cyber threat level","ORANGE — 3 intrusion attempts blocked.","09:15:22")]
        log_html = '<div class="log-block">'
        for q, a, t in hist:
            log_html += f'[{t}] <span style="color:#00d2ff;">USER:</span> {q}<br>'
            log_html += f'[{t}] <span style="color:#00ff9f;">JARVIS:</span> {a}<br><br>'
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)


# =============================================================================
#  TERMINAL FUNCTIONS
# =============================================================================

def terminal_command_overview():
    AegisUI.header("⚡ COMMAND OVERVIEW", "GLOBAL FLEET INTELLIGENCE MATRIX")
    df = AegisData.fleet_snapshot()
    c1,c2,c3,c4,c5 = st.columns(5)
    AegisUI.metric_card(c1,"ACTIVE ASSETS", str(int((df.status=="ACTIVE").sum())),f"+{random.randint(0,3)} vs yesterday",True)
    AegisUI.metric_card(c2,"AVG SOC %",f"{df.soc.mean():.1f}","▲ 2.3%",True)
    AegisUI.metric_card(c3,"LATENCY",f"{random.randint(12,48)}ms","▼ 4ms",True)
    AegisUI.metric_card(c4,"ALERTS OPEN",str(int((df.status=="ALERT").sum())),"⚠",False)
    AegisUI.metric_card(c5,"FLEET LOAD",f"{random.randint(55,85)}%","▲ 1.1%",True)
    st.markdown("<br>", unsafe_allow_html=True)

    cmap = {"ACTIVE":"#00d2ff","IDLE":"#a0b0d0","CHARGING":"#00ff9f","ALERT":"#ff00c1"}
    col_map, col_right = st.columns([3,2])
    with col_map:
        fig = px.scatter_mapbox(df, lat="lat", lon="lon", color="status",
                                color_discrete_map=cmap, hover_name="vehicle",
                                hover_data={"soc":True,"speed_kmh":True,"temp_c":True,"lat":False,"lon":False},
                                size="soc", size_max=16, zoom=4,
                                center={"lat":20.5,"lon":80}, mapbox_style="carto-darkmatter")
        AegisUI.dark_fig(fig,"EV FLEET MAP — LIVE POSITIONS")
        fig.update_layout(height=420, margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with col_right:
        sc = df.status.value_counts().reset_index(); sc.columns=["status","count"]
        fig2 = px.pie(sc, names="status", values="count", color="status",
                      color_discrete_map=cmap, hole=0.55)
        AegisUI.dark_fig(fig2,"STATUS DISTRIBUTION")
        fig2.update_traces(textfont=dict(color="white"))
        st.plotly_chart(fig2, use_container_width=True)
        fig3 = px.histogram(df, x="soc", nbins=10, title="SOC DISTRIBUTION",
                             color_discrete_sequence=["#00d2ff"])
        AegisUI.dark_fig(fig3)
        fig3.update_layout(height=220, margin=dict(l=20,r=10,t=35,b=20))
        st.plotly_chart(fig3, use_container_width=True)
    st.markdown("#### FLEET TABLE")
    st.dataframe(df.style.applymap(
        lambda v: f"color: {'#00ff9f' if v=='ACTIVE' else '#ff00c1' if v=='ALERT' else '#a0b0d0'}",
        subset=["status"]), use_container_width=True, height=260)


def terminal_predictive_health():
    AegisUI.header("🔬 PREDICTIVE HEALTH","RUL ENGINE — COMPONENT STRESS ANALYTICS")
    rul_df   = AegisData.rul_data()
    comps    = rul_df.component.unique().tolist()
    selected = st.multiselect("Select components:", comps, default=comps[:3])
    filtered = rul_df[rul_df.component.isin(selected)] if selected else rul_df

    fig = px.line(filtered, x="day", y="health_%", color="component",
                  color_discrete_sequence=px.colors.qualitative.Bold)
    fig.add_hline(y=30, line_dash="dash", line_color="#ff00c1",
                  annotation_text="CRITICAL (30%)", annotation_font_color="#ff00c1")
    fig.add_hline(y=60, line_dash="dot",  line_color="#ffdd57",
                  annotation_text="WARNING (60%)",  annotation_font_color="#ffdd57")
    AegisUI.dark_fig(fig,"COMPONENT HEALTH DEGRADATION — 365-DAY RUL")
    fig.update_layout(height=380)
    st.plotly_chart(fig, use_container_width=True)

    c1,c2 = st.columns(2)
    latest = rul_df.groupby("component")["health_%"].last().reset_index()
    fig_b  = px.bar(latest, x="component", y="health_%", color="health_%",
                    color_continuous_scale=["#ff00c1","#ffdd57","#00ff9f"],
                    title="CURRENT HEALTH SNAPSHOT")
    AegisUI.dark_fig(fig_b)
    c1.plotly_chart(fig_b, use_container_width=True)

    if SCIPY_AVAILABLE and comps:
        vals  = rul_df[rul_df.component==comps[0]]["health_%"].values
        kde_x = np.linspace(vals.min(), vals.max(), 200)
        kde   = stats.gaussian_kde(vals)
        fk    = go.Figure()
        fk.add_trace(go.Scatter(x=kde_x, y=kde(kde_x), fill="tozeroy",
                                line_color="#00d2ff", name="KDE"))
        AegisUI.dark_fig(fk, f"HEALTH KDE — {comps[0]}")
        c2.plotly_chart(fk, use_container_width=True)
    else:
        c2.info("SciPy not installed — KDE unavailable.")


def terminal_financial_risk():
    AegisUI.header("💹 FINANCIAL RISK AI","ROI MODELLING & EXPOSURE ANALYTICS")
    c1,c2 = st.columns([1,2])
    with c1:
        fleet_size  = st.slider("Fleet Size",5,500,100)
        avg_km_day  = st.slider("Avg KM/day",50,500,200)
        fuel_saving = st.slider("Fuel saving $/km",0.05,0.30,0.12,0.01)
        ops_cost    = st.slider("Ops cost $/veh/day",5.0,50.0,18.0,0.5)
        risk_mult   = st.slider("Risk Multiplier",0.5,3.0,1.2,0.1)
        years       = st.slider("Projection Years",1,10,5)
    annual_saving = fleet_size*avg_km_day*fuel_saving*365
    annual_cost   = fleet_size*ops_cost*365
    net_annual    = annual_saving-annual_cost
    roi_pct       = (net_annual/max(fleet_size*800000,1))*100
    with c2:
        yrs = list(range(1,years+1))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=yrs,y=[net_annual*y for y in yrs],name="Gross Net",line=dict(color="#00d2ff",width=2)))
        fig.add_trace(go.Scatter(x=yrs,y=[net_annual*y/risk_mult for y in yrs],name="Risk-Adj",line=dict(color="#ff00c1",width=2,dash="dash")))
        fig.add_trace(go.Scatter(x=yrs,y=[-fleet_size*800000+net_annual*y for y in yrs],name="Payback",line=dict(color="#00ff9f",width=2,dash="dot")))
        fig.add_hline(y=0, line_color="rgba(255,255,255,0.2)")
        AegisUI.dark_fig(fig,"ROI PROJECTION")
        st.plotly_chart(fig, use_container_width=True)
    m1,m2,m3,m4 = st.columns(4)
    AegisUI.metric_card(m1,"ANNUAL SAVINGS",f"${annual_saving:,.0f}","",True)
    AegisUI.metric_card(m2,"OPS COST",f"${annual_cost:,.0f}","",False)
    AegisUI.metric_card(m3,"NET ANNUAL",f"${net_annual:,.0f}","",net_annual>0)
    AegisUI.metric_card(m4,"ROI %",f"{roi_pct:.2f}%","",roi_pct>0)
    st.markdown("<br>",unsafe_allow_html=True)
    st.markdown("#### RISK EXPOSURE HEATMAP")
    risk_cats = ["Battery Degrad.","Grid Depend.","Regulatory","Cyber Attack","Supply Chain","Driver Beh.","Market Vol."]
    scenarios = ["Base","Optimistic","Pessimistic","Stress Test","Black Swan"]
    fig_h = px.imshow(np.array([[random.uniform(0.1,1.0)*risk_mult for _ in range(7)] for _ in range(5)]),
                      x=risk_cats, y=scenarios,
                      color_continuous_scale=["#00d2ff","#ffdd57","#ff00c1"],
                      aspect="auto", title="RISK MATRIX")
    AegisUI.dark_fig(fig_h)
    st.plotly_chart(fig_h, use_container_width=True)


def terminal_cyber_shield():
    AegisUI.header("🛡️ CYBER-SHIELD","ZERO-TRUST BLOCKCHAIN PERIMETER")
    c1,c2,c3,c4 = st.columns(4)
    AegisUI.metric_card(c1,"THREATS BLOCKED",str(random.randint(320,850)),"▲ today",False)
    AegisUI.metric_card(c2,"NODES VALIDATED",str(random.randint(12,20)),"blockchain",True)
    AegisUI.metric_card(c3,"FIREWALL",f"{random.randint(95,100)}%","integrity",True)
    AegisUI.metric_card(c4,"ENCRYPTION","AES-256","active",True)
    st.markdown("<br>",unsafe_allow_html=True)
    col_log,col_stats = st.columns([3,2])
    cyber_df = AegisData.cyber_events(20)
    def cs(val):
        return f"color:{'#a0b0d0' if val=='LOW' else '#ffdd57' if val=='MED' else '#ff8800' if val=='HIGH' else '#ff00c1'};font-weight:bold"
    with col_log:
        st.markdown("#### 🔴 LIVE INTRUSION LOG")
        st.dataframe(cyber_df.style.applymap(cs,subset=["severity"]),
                     use_container_width=True,height=320)
    with col_stats:
        ev = cyber_df.event.value_counts().reset_index(); ev.columns=["event","count"]
        fig_ev = px.bar(ev,x="count",y="event",orientation="h",color="count",
                        color_continuous_scale=["#00d2ff","#ff00c1"],title="ATTACK VECTORS")
        AegisUI.dark_fig(fig_ev)
        st.plotly_chart(fig_ev,use_container_width=True)
    st.markdown("#### ⛓️ BLOCKCHAIN NODES")
    nodes = [f"NODE-{chr(65+i)}" for i in range(8)]
    st.dataframe(pd.DataFrame({
        "node":nodes,
        "hash":[hashlib.sha256(n.encode()).hexdigest()[:20] for n in nodes],
        "latency_ms":[random.randint(2,45) for _ in nodes],
        "status":[random.choice(["VALID","VALID","VALID","SYNCING"]) for _ in nodes],
        "block_height":[random.randint(98000,100000) for _ in nodes],
    }),use_container_width=True)
    st.markdown("#### FIREWALL LAYERS")
    for lyr in ["L1 Physical","L2 DataLink","L3 Network","L4 Transport","L7 Application"]:
        st.markdown(f"`{lyr}`")
        st.progress(random.randint(87,100)/100)


def terminal_energy_telemetry():
    AegisUI.header("⚡ ENERGY TELEMETRY","SMART GRID POWER DISTRIBUTION")
    ed = AegisData.energy_data()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ed.hour,y=ed.grid_kw, name="Grid kW", marker_color="#00d2ff"))
    fig.add_trace(go.Bar(x=ed.hour,y=ed.solar_kw,name="Solar kW",marker_color="#00ff9f"))
    fig.add_trace(go.Bar(x=ed.hour,y=ed.regen_kw,name="Regen kW",marker_color="#ff00c1"))
    fig.add_trace(go.Scatter(x=ed.hour,y=ed.demand_kw,name="Demand",line=dict(color="#ffdd57",width=2)))
    fig.update_layout(barmode="stack")
    AegisUI.dark_fig(fig,"24H POWER DISTRIBUTION — kW")
    fig.update_layout(height=380)
    st.plotly_chart(fig,use_container_width=True)
    c1,c2 = st.columns(2)
    mix = pd.DataFrame({"source":["Grid","Solar","Regen"],"kwh":[ed.grid_kw.sum(),ed.solar_kw.sum(),ed.regen_kw.sum()]})
    fm = px.pie(mix,names="source",values="kwh",hole=0.5,color_discrete_sequence=["#00d2ff","#00ff9f","#ff00c1"],title="ENERGY MIX")
    AegisUI.dark_fig(fm)
    c1.plotly_chart(fm,use_container_width=True)
    eff = random.uniform(78,95)
    fg = go.Figure(go.Indicator(
        mode="gauge+number+delta",value=eff,delta={"reference":80},
        gauge={"axis":{"range":[0,100]},"bar":{"color":"#00d2ff"},
               "steps":[{"range":[0,50],"color":"rgba(255,0,193,0.15)"},
                        {"range":[50,75],"color":"rgba(255,221,87,0.12)"},
                        {"range":[75,100],"color":"rgba(0,255,159,0.12)"}],
               "threshold":{"value":80,"line":{"color":"#ff00c1","width":2}}},
        title={"text":"GRID EFFICIENCY %","font":{"color":"#00d2ff","size":13}},
        number={"font":{"color":"#00d2ff"}},
    ))
    AegisUI.dark_fig(fg)
    fg.update_layout(height=320)
    c2.plotly_chart(fg,use_container_width=True)


def terminal_digital_twin():
    AegisUI.header("🔮 DIGITAL TWIN","3D PHYSICS ENGINE — EV REPLICA")
    st.info("Full 3D physics rendering requires NVIDIA Omniverse / Unity WebGL context. "
            "Showing live parameter telemetry feed.")
    vehicle = st.selectbox("Select twin vehicle:", AegisData.VEHICLE_IDS)
    random.seed(hash(vehicle)%9999)
    params = {"Motor RPM":random.randint(0,8500),"Torque Nm":round(random.uniform(0,400),1),
              "Slip Ratio":round(random.uniform(0,0.15),3),"Yaw Rate °/s":round(random.uniform(-30,30),2),
              "Susp FL mm":round(random.uniform(80,120),1),"Susp FR mm":round(random.uniform(80,120),1),
              "Susp RL mm":round(random.uniform(80,120),1),"Susp RR mm":round(random.uniform(80,120),1),
              "Aero Drag N":round(random.uniform(50,400),1),"Roll Resist N":round(random.uniform(20,150),1)}
    cols = st.columns(5)
    for i,(k,v) in enumerate(params.items()):
        cols[i%5].metric(k,v)
    cats  = ["Battery","Motor","Brakes","Suspension","Thermal","Aero","Electrical"]
    vals  = [random.randint(60,100) for _ in cats]
    fr    = go.Figure(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],
                                      fill="toself",line_color="#00d2ff",
                                      fillcolor="rgba(0,210,255,0.12)",name="Health"))
    fr.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                radialaxis=dict(visible=True,range=[0,100],gridcolor="rgba(0,210,255,0.15)",color="#00d2ff"),
                                angularaxis=dict(gridcolor="rgba(0,210,255,0.15)",color="#a0b0d0")))
    AegisUI.dark_fig(fr,f"TWIN HEALTH RADAR — {vehicle}")
    st.plotly_chart(fr,use_container_width=True)


def terminal_ota():
    AegisUI.header("🚀 OTA DEPLOYMENT","OVER-THE-AIR KERNEL & FIRMWARE MATRIX")
    for pkg in AegisData.ota_packages():
        sc = {"COMPLETE":"#00ff9f","DEPLOYING":"#00d2ff","QUEUED":"#a0b0d0"}.get(pkg["status"],"#fff")
        st.markdown(f"""<div class="metric-card" style="margin-bottom:.7rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div><span style="color:#00d2ff;font-family:Syncopate,sans-serif;font-size:.85rem;letter-spacing:2px;">{pkg['name']}</span>
                <span style="color:#a0b0d0;font-size:.72rem;margin-left:1rem;">{pkg['size']}</span></div>
                <span style="color:{sc};font-size:.75rem;letter-spacing:3px;font-family:Syncopate,sans-serif;">{pkg['status']}</span>
            </div></div>""",unsafe_allow_html=True)
        st.progress(pkg["progress"]/100,text=f"{pkg['progress']}%")
        st.markdown("<div style='margin-bottom:.4rem'></div>",unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    cov = random.randint(68,95)
    AegisUI.metric_card(c1,"COVERAGE",f"{cov}%","of fleet",True)
    AegisUI.metric_card(c2,"PENDING",str(20-int(20*cov/100)),"",False)
    AegisUI.metric_card(c3,"AVG DEPLOY","4m 32s","▼ 12s faster",True)
    st.markdown("<br>",unsafe_allow_html=True)
    hist = pd.DataFrame({"date":pd.date_range(end=datetime.date.today(),periods=14,freq="D"),
                         "deployed":[random.randint(0,5) for _ in range(14)],
                         "failed":[random.randint(0,2) for _ in range(14)]})
    fig = px.bar(hist,x="date",y=["deployed","failed"],barmode="group",title="14-DAY OTA ACTIVITY",
                 color_discrete_map={"deployed":"#00d2ff","failed":"#ff00c1"})
    AegisUI.dark_fig(fig)
    st.plotly_chart(fig,use_container_width=True)


def terminal_blackbox():
    AegisUI.header("📦 BLACKBOX LOGS","IMMUTABLE EVENT RECORDER")
    logs = AegisData.blackbox_logs(50)
    f1,f2,f3 = st.columns(3)
    sf = f1.multiselect("Severity:",logs.severity.unique().tolist(),default=logs.severity.unique().tolist())
    vf = f2.multiselect("Vehicle:",["ALL"]+AegisData.VEHICLE_IDS,default=["ALL"])
    ef = f3.multiselect("Error:",["ALL"]+AegisData.ERRORS,default=["ALL"])
    flt = logs[logs.severity.isin(sf)]
    if "ALL" not in vf: flt=flt[flt.vehicle.isin(vf)]
    if "ALL" not in ef: flt=flt[flt.error_code.isin(ef)]
    def sc2(val):
        return {"INFO":"color:#a0b0d0","WARN":"color:#ffdd57","ERROR":"color:#ff8800","CRITICAL":"color:#ff00c1"}.get(val,"")
    st.dataframe(flt.style.applymap(sc2,subset=["severity"]),use_container_width=True,height=380)
    c1,c2 = st.columns(2)
    sv = flt.severity.value_counts().reset_index(); sv.columns=["severity","count"]
    fs = px.bar(sv,x="severity",y="count",color="severity",
                color_discrete_map={"INFO":"#a0b0d0","WARN":"#ffdd57","ERROR":"#ff8800","CRITICAL":"#ff00c1"},
                title="SEVERITY BREAKDOWN")
    AegisUI.dark_fig(fs); c1.plotly_chart(fs,use_container_width=True)
    rv = flt.ai_resolution.value_counts().reset_index(); rv.columns=["resolution","count"]
    fr = px.pie(rv,names="resolution",values="count",hole=0.5,title="AI RESOLUTION TYPES",
                color_discrete_sequence=px.colors.qualitative.Bold)
    AegisUI.dark_fig(fr); c2.plotly_chart(fr,use_container_width=True)


def terminal_neural_core():
    """
    Neural Core terminal.
    PyTorch is NOT imported at module level (it's 700 MB+).
    Architecture is shown as a runnable code block.
    Training metrics are simulated with NumPy — no torch required to run this app.
    """
    AegisUI.header("🧠 NEURAL CORE","DEEP LEARNING TOPOLOGY & TRAINING METRICS")

    # Attempt local import — does NOT crash if torch absent
    TORCH_OK = False
    try:
        import torch          # noqa: F401
        import torch.nn as nn # noqa: F401
        TORCH_OK = True
    except ImportError:
        pass

    tab1, tab2, tab3 = st.tabs(["🏗️ Architecture","📈 Training","🔬 Inference"])

    with tab1:
        st.markdown("#### AEGIS-NET v3.2 — Transformer-GNN Hybrid")
        if TORCH_OK:
            st.success("✅ PyTorch detected — model is runnable on this machine.")
        else:
            st.info("ℹ️  PyTorch not installed. Code below is reference only.\n\n"
                    "Install: `pip install torch`")

        st.dataframe(pd.DataFrame({
            "Layer":      ["Input","Embedding","Transformer×6","GNN","Attn Pool","Dense(512)","Dense(128)","Output"],
            "Shape":      ["(B,T,F)","(B,T,256)","(B,T,256)","(B,N,256)","(B,256)","(B,512)","(B,128)","(B,C)"],
            "Params":     ["—","1.3M","24.6M","8.2M","0.5M","131k","65k","16k"],
            "Activation": ["—","—","GELU","ReLU","Softmax","GELU","ReLU","Sigmoid"],
        }), use_container_width=True)

        # Pure display code block — no live import, will never raise ImportError
        st.code(
"""\
# ── AEGIS-NET v3.2 ── requires: pip install torch ────────────────
import torch
import torch.nn as nn

class AegisNet(nn.Module):
    def __init__(self, input_dim=128, hidden=256,
                 heads=8, layers=6, num_classes=10):
        super().__init__()
        self.embed = nn.Linear(input_dim, hidden)
        enc_layer  = nn.TransformerEncoderLayer(
            d_model=hidden, nhead=heads,
            dim_feedforward=1024,
            activation='gelu',
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(enc_layer, num_layers=layers)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.head = nn.Sequential(
            nn.Linear(hidden, 512), nn.GELU(), nn.Dropout(0.3),
            nn.Linear(512, 128),   nn.ReLU(),
            nn.Linear(128, num_classes), nn.Sigmoid(),
        )

    def forward(self, x):
        # x: (batch, seq_len, input_dim)
        x = self.embed(x)                           # (B, T, 256)
        x = self.transformer(x)                     # (B, T, 256)
        x = self.pool(x.permute(0, 2, 1)).squeeze(-1)  # (B, 256)
        return self.head(x)                         # (B, num_classes)

# ── Sanity check ─────────────────────────────────────────────────
if __name__ == "__main__":
    model  = AegisNet()
    dummy  = torch.randn(4, 32, 128)   # batch=4, seq=32, features=128
    output = model(dummy)
    print("Output shape:", output.shape)  # -> torch.Size([4, 10])
""",
            language="python",
        )

    with tab2:
        rng    = np.random.default_rng(7)
        epochs = list(range(1, 51))
        t_loss = [max(0.001, 1.8*np.exp(-0.07*e) + rng.uniform(-0.02, 0.02)) for e in epochs]
        v_loss = [max(0.001, 2.0*np.exp(-0.065*e)+ rng.uniform(-0.03, 0.04)) for e in epochs]
        t_acc  = [min(99, max(0, 100*(1-np.exp(-0.09*e))  + rng.uniform(-1,   1))) for e in epochs]
        v_acc  = [min(98, max(0, 100*(1-np.exp(-0.082*e)) + rng.uniform(-1.5, 1.5))) for e in epochs]

        fig = make_subplots(rows=1, cols=2, subplot_titles=("LOSS","ACCURACY (%)"))
        fig.add_trace(go.Scatter(x=epochs,y=t_loss,name="Train Loss",line=dict(color="#00d2ff")),row=1,col=1)
        fig.add_trace(go.Scatter(x=epochs,y=v_loss,name="Val Loss",  line=dict(color="#ff00c1",dash="dash")),row=1,col=1)
        fig.add_trace(go.Scatter(x=epochs,y=t_acc, name="Train Acc", line=dict(color="#00ff9f")),row=1,col=2)
        fig.add_trace(go.Scatter(x=epochs,y=v_acc, name="Val Acc",   line=dict(color="#ffdd57",dash="dash")),row=1,col=2)
        AegisUI.dark_fig(fig,"TRAINING CURVES — SIMULATED")
        fig.update_layout(height=370)
        st.plotly_chart(fig,use_container_width=True)
        m1,m2,m3,m4 = st.columns(4)
        AegisUI.metric_card(m1,"BEST VAL ACC",f"{max(v_acc):.1f}%",f"epoch {v_acc.index(max(v_acc))+1}",True)
        AegisUI.metric_card(m2,"TRAIN LOSS",  f"{t_loss[-1]:.4f}","",True)
        AegisUI.metric_card(m3,"TOTAL PARAMS","34.8M","",True)
        AegisUI.metric_card(m4,"INFERENCE",   "12ms","A100",True)

    with tab3:
        st.markdown("#### REAL-TIME INFERENCE FEED")
        vehs = AegisData.VEHICLE_IDS[:8]
        st.dataframe(pd.DataFrame({
            "vehicle":       vehs,
            "fault_class":   [random.choice(["NORMAL","BATTERY_DRIFT","MOTOR_STRESS","THERMAL_EVENT"]) for _ in vehs],
            "confidence":    [round(random.uniform(0.75,0.99),4) for _ in vehs],
            "latency_ms":    [random.randint(8,22) for _ in vehs],
            "anomaly_score": [round(random.uniform(0,1),4) for _ in vehs],
        }), use_container_width=True)
        fh = px.histogram(pd.DataFrame({"confidence":[round(random.uniform(0.75,0.99),4) for _ in range(40)]}),
                          x="confidence",nbins=12,title="INFERENCE CONFIDENCE DISTRIBUTION",
                          color_discrete_sequence=["#00d2ff"])
        AegisUI.dark_fig(fh)
        st.plotly_chart(fh,use_container_width=True)


def terminal_alpr():
    AegisUI.header("🚔 ALPR POLICE DB","AUTOMATED LICENSE PLATE RECOGNITION — LAW ENFORCEMENT UPLINK")
    st.markdown("""<div style="background:rgba(255,0,193,0.06);border:1px solid rgba(255,0,193,0.3);
         border-radius:8px;padding:.8rem 1.2rem;margin-bottom:1rem;">
        <span style="color:#ff00c1;font-family:Syncopate,sans-serif;font-size:.75rem;
                     letter-spacing:3px;">⚠ RESTRICTED ACCESS — AUTHORISED PERSONNEL ONLY</span>
    </div>""",unsafe_allow_html=True)
    plate_in = st.text_input("🔍 Enter Vehicle Registration Number:",
                              placeholder="e.g. TN01AB1234",max_chars=12)
    if st.button("🔗 INITIATE DB HANDSHAKE") and plate_in.strip():
        with st.spinner("Connecting to National Vehicle Registry…"):
            time.sleep(1.2)
        rec = AegisData.alpr_lookup(plate_in.strip())
        fs  = {"CLEAR":("✅ CLEAR","#00ff9f","rgba(0,255,159,0.08)"),
               "WARNING":("⚠️ WARNING","#ffdd57","rgba(255,221,87,0.1)"),
               "CRITICAL":("🚨 CRITICAL","#ff00c1","rgba(255,0,193,0.1)")}[rec["flag"]]
        st.markdown(f"""<div style="background:{fs[2]};border:1px solid {fs[1]};
             border-radius:10px;padding:1.2rem 1.6rem;margin-bottom:1rem;">
            <div style="font-family:Syncopate,sans-serif;font-size:1.3rem;
                        color:{fs[1]};letter-spacing:3px;">{fs[0]}</div>
            <div style="color:#ccc;margin-top:.3rem;">{rec['flag_detail']}</div>
        </div>""",unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        c1.markdown("#### VEHICLE RECORD")
        c1.table(pd.DataFrame({"Field":["Plate","Owner","Chassis No.","Insurer","Policy Valid Until","RTO"],
                                "Value":[rec["plate"],rec["owner"],rec["chassis"],rec["insurer"],rec["valid_until"],rec["rto"]]}))
        c2.markdown("#### FORENSIC METADATA")
        meta={"Query Time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              "DB Node":f"NVR-{random.choice(['MUM','DEL','CHN','BLR'])}",
              "Ping ms":random.randint(12,80),"TLS Cipher":"TLS_AES_256_GCM_SHA384",
              "Response Hash":hashlib.sha256(rec["chassis"].encode()).hexdigest()[:32],"Encryption":"AES-256-GCM"}
        c2.table(pd.DataFrame({"Key":list(meta.keys()),"Value":list(meta.values())}))
        log_html = '<div class="log-block">'
        log_html += AegisUI.log_line(f"ALPR query — plate: {rec['plate']}")
        log_html += AegisUI.log_line("Secure channel OK — NVR handshake complete")
        log_html += AegisUI.log_line(f"Owner: {rec['owner']} | RTO: {rec['rto']}")
        log_html += AegisUI.log_line(f"Insurer: {rec['insurer']} valid until {rec['valid_until']}")
        log_html += AegisUI.log_line(f"FLAG: {rec['flag']} — {rec['flag_detail']}",
                                     {"CLEAR":"info","WARNING":"warn","CRITICAL":"crit"}[rec["flag"]])
        log_html += AegisUI.log_line("Logged to immutable blockchain ledger.")
        log_html += '</div>'
        st.markdown(log_html,unsafe_allow_html=True)


# =============================================================================
#  NEW — MAP ASSISTANT TERMINAL
# =============================================================================
def terminal_map_assistant():
    AegisUI.header("🗺️ MAP ASSISTANT","LIVE VEHICLE TRACKING & ROUTE INTELLIGENCE")
    df = AegisData.fleet_snapshot()

    c1,c2,c3,c4 = st.columns(4)
    AegisUI.metric_card(c1,"TRACKED VEHICLES","20","all cities",True)
    AegisUI.metric_card(c2,"AVG SPEED km/h",f"{df.speed_kmh.mean():.1f}","fleet",True)
    AegisUI.metric_card(c3,"GEOFENCE ALERTS",str(random.randint(0,3)),"last 30 min",False)
    AegisUI.metric_card(c4,"COVERAGE km²",str(random.randint(2800,4200)),"active zones",True)
    st.markdown("<br>",unsafe_allow_html=True)

    tab_fleet, tab_route, tab_heat, tab_geo = st.tabs([
        "🌍 Fleet Overview","📍 Route Replay","🔥 Density Heatmap","⛔ Geofence Monitor"
    ])

    cmap = {"ACTIVE":"#00d2ff","IDLE":"#a0b0d0","CHARGING":"#00ff9f","ALERT":"#ff00c1"}

    # ── Fleet Overview ────────────────────────────────────────────────────────
    with tab_fleet:
        col_map, col_side = st.columns([3,2])
        with col_map:
            f_stat = st.multiselect("Status filter:", df.status.unique().tolist(),
                                    default=df.status.unique().tolist(), key="ma_stat")
            f_city = st.multiselect("City filter:",   df.city.unique().tolist(),
                                    default=df.city.unique().tolist(), key="ma_city")
            fdf = df[df.status.isin(f_stat) & df.city.isin(f_city)]
            fig_fm = px.scatter_mapbox(fdf, lat="lat", lon="lon", color="status",
                                       color_discrete_map=cmap, hover_name="vehicle",
                                       hover_data={"soc":True,"speed_kmh":True,"temp_c":True,
                                                   "city":True,"lat":False,"lon":False},
                                       size="soc", size_max=18, zoom=4,
                                       center={"lat":20.5,"lon":80}, mapbox_style="carto-darkmatter")
            AegisUI.dark_fig(fig_fm,"LIVE FLEET POSITIONS")
            fig_fm.update_layout(height=500, margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig_fm, use_container_width=True)

        with col_side:
            st.markdown("#### VEHICLE QUICK-LOOK")
            sel_v = st.selectbox("Select vehicle:", fdf["vehicle"].tolist(), key="ma_vsel")
            if not fdf.empty:
                vrow  = fdf[fdf.vehicle==sel_v].iloc[0]
                sc_c  = cmap.get(vrow["status"],"#fff")
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:1rem;">
                    <div style="font-family:Syncopate,sans-serif;font-size:1.1rem;
                                color:#00d2ff;letter-spacing:3px;">{vrow['vehicle']}</div>
                    <div style="margin-top:.5rem;font-size:.85rem;line-height:1.8;">
                        <span style="color:{sc_c};">● {vrow['status']}</span><br>
                        🏙️ {vrow['city']}<br>🔋 SOC: {vrow['soc']}%<br>
                        🚗 {vrow['speed_kmh']} km/h<br>🌡️ {vrow['temp_c']} °C<br>
                        📍 {vrow['lat']:.4f}, {vrow['lon']:.4f}
                    </div>
                </div>""", unsafe_allow_html=True)

                fig_sg = go.Figure(go.Indicator(
                    mode="gauge+number", value=int(vrow["soc"]),
                    gauge={"axis":{"range":[0,100]},
                           "bar":{"color":"#00ff9f" if vrow["soc"]>40 else "#ff00c1"},
                           "steps":[{"range":[0,20],"color":"rgba(255,0,193,0.2)"},
                                    {"range":[20,50],"color":"rgba(255,221,87,0.1)"},
                                    {"range":[50,100],"color":"rgba(0,255,159,0.1)"}],
                           "threshold":{"value":20,"line":{"color":"#ff00c1","width":2}}},
                    title={"text":"SOC %","font":{"color":"#00d2ff","size":12}},
                    number={"font":{"color":"#00d2ff","size":36}},
                ))
                AegisUI.dark_fig(fig_sg)
                fig_sg.update_layout(height=240)
                st.plotly_chart(fig_sg, use_container_width=True)

            cc = df.city.value_counts().reset_index(); cc.columns=["city","count"]
            fig_cc = px.bar(cc, x="city", y="count", title="VEHICLES PER CITY",
                            color="count", color_continuous_scale=["#00d2ff","#ff00c1"])
            AegisUI.dark_fig(fig_cc)
            fig_cc.update_layout(height=230, margin=dict(l=20,r=10,t=35,b=60))
            st.plotly_chart(fig_cc, use_container_width=True)

    # ── Route Replay ──────────────────────────────────────────────────────────
    with tab_route:
        st.markdown("#### 📍 GPS ROUTE HISTORY & REPLAY")
        rv    = st.selectbox("Select vehicle:", AegisData.VEHICLE_IDS, key="ma_rv")
        rdf   = AegisData.route_history(rv)

        fig_rt = go.Figure()
        fig_rt.add_trace(go.Scattermapbox(lat=rdf.lat, lon=rdf.lon, mode="lines",
                                           line=dict(color="#00d2ff",width=3), name="Route"))
        fig_rt.add_trace(go.Scattermapbox(lat=rdf.lat, lon=rdf.lon, mode="markers+text",
                                           marker=dict(size=8, color="#ff00c1"),
                                           text=rdf.timestamp, textposition="top right",
                                           textfont=dict(size=8, color="#ffdd57"),
                                           name="Waypoints",
                                           hovertemplate="<b>%{text}</b><br>Speed:%{customdata[0]}km/h<br>SOC:%{customdata[1]}%<extra></extra>",
                                           customdata=list(zip(rdf.speed_kmh, rdf["soc_%"]))))
        fig_rt.add_trace(go.Scattermapbox(lat=[rdf.lat.iloc[0]], lon=[rdf.lon.iloc[0]],
                                           mode="markers", marker=dict(size=16,color="#00ff9f"), name="Start"))
        fig_rt.add_trace(go.Scattermapbox(lat=[rdf.lat.iloc[-1]], lon=[rdf.lon.iloc[-1]],
                                           mode="markers", marker=dict(size=16,color="#ff00c1"), name="End"))
        fig_rt.update_layout(
            mapbox=dict(style="carto-darkmatter",
                        center=dict(lat=rdf.lat.mean(),lon=rdf.lon.mean()),zoom=12),
            height=480, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#a0b0d0")),
        )
        st.plotly_chart(fig_rt, use_container_width=True)

        c1,c2 = st.columns(2)
        fs = px.line(rdf, x="timestamp", y="speed_kmh", title=f"SPEED — {rv}",
                     color_discrete_sequence=["#00d2ff"])
        AegisUI.dark_fig(fs); fs.update_layout(height=240); c1.plotly_chart(fs,use_container_width=True)
        fs2= px.line(rdf, x="timestamp", y="soc_%", title=f"SOC — {rv}",
                     color_discrete_sequence=["#00ff9f"])
        fs2.add_hline(y=20,line_dash="dash",line_color="#ff00c1",
                      annotation_text="LOW SOC",annotation_font_color="#ff00c1")
        AegisUI.dark_fig(fs2); fs2.update_layout(height=240); c2.plotly_chart(fs2,use_container_width=True)
        st.dataframe(rdf, use_container_width=True, height=200)

    # ── Density Heatmap ───────────────────────────────────────────────────────
    with tab_heat:
        st.markdown("#### 🔥 VEHICLE DENSITY HEATMAP")
        hlat, hlon = [], []
        for city in AegisData.CITIES:
            blat, blon = AegisData.CITY_COORDS[city]
            n = random.randint(30,80)
            hlat.extend(np.random.normal(blat,0.05,n).tolist())
            hlon.extend(np.random.normal(blon,0.05,n).tolist())
        fig_hm = px.density_mapbox(pd.DataFrame({"lat":hlat,"lon":hlon}),
                                   lat="lat",lon="lon",radius=18,zoom=4,
                                   center={"lat":20.5,"lon":80},mapbox_style="carto-darkmatter",
                                   color_continuous_scale=["#050510","#00d2ff","#ff00c1","#ffffff"])
        AegisUI.dark_fig(fig_hm,"FLEET DENSITY — ALL CITIES")
        fig_hm.update_layout(height=520, margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_hm, use_container_width=True)

        ca = pd.DataFrame({"city":AegisData.CITIES,
                           "vehicles":[random.randint(5,35) for _ in AegisData.CITIES],
                           "alerts":[random.randint(0,5) for _ in AegisData.CITIES]})
        fig_ca = px.bar(ca,x="city",y=["vehicles","alerts"],barmode="group",title="CITY ACTIVITY",
                        color_discrete_map={"vehicles":"#00d2ff","alerts":"#ff00c1"})
        AegisUI.dark_fig(fig_ca)
        st.plotly_chart(fig_ca,use_container_width=True)

    # ── Geofence Monitor ──────────────────────────────────────────────────────
    with tab_geo:
        st.markdown("#### ⛔ GEOFENCE MONITOR")
        geofences = [
            {"name":"DEPOT ALPHA", "city":"Chennai",   "lat":13.0827,"lon":80.2707,"radius_km":5.0, "type":"ALLOWED"},
            {"name":"DEPOT BETA",  "city":"Mumbai",    "lat":19.0760,"lon":72.8777,"radius_km":4.5, "type":"ALLOWED"},
            {"name":"ZONE GAMMA",  "city":"Delhi",     "lat":28.6139,"lon":77.2090,"radius_km":6.0, "type":"ALLOWED"},
            {"name":"RESTRICT-1",  "city":"Bengaluru", "lat":12.9716,"lon":77.5946,"radius_km":2.0, "type":"RESTRICTED"},
            {"name":"RESTRICT-2",  "city":"Hyderabad", "lat":17.3850,"lon":78.4867,"radius_km":1.5, "type":"RESTRICTED"},
        ]
        gf_df = pd.DataFrame(geofences)
        violations = []
        for _, veh in df.iterrows():
            for _, gf in gf_df[gf_df.type=="RESTRICTED"].iterrows():
                dist = ((veh.lat-gf.lat)**2+(veh.lon-gf.lon)**2)**0.5*111
                if dist < gf.radius_km:
                    violations.append({"vehicle":veh.vehicle,"zone":gf["name"],"city":gf.city,
                                        "distance":f"{dist:.2f}km","soc":veh.soc,"status":"🚨 VIOLATION"})
        if violations:
            st.error(f"🚨 {len(violations)} GEOFENCE VIOLATION(S) DETECTED!")
            st.dataframe(pd.DataFrame(violations),use_container_width=True)
        else:
            st.success("✅ No geofence violations. All vehicles within authorised zones.")

        fig_gf = px.scatter_mapbox(df,lat="lat",lon="lon",color="status",
                                   color_discrete_map=cmap,hover_name="vehicle",
                                   size="soc",size_max=14,zoom=4,
                                   center={"lat":20.5,"lon":80},mapbox_style="carto-darkmatter")
        fig_gf.add_trace(go.Scattermapbox(
            lat=gf_df.lat,lon=gf_df.lon,mode="markers+text",
            marker=dict(size=20,color=["#00ff9f" if t=="ALLOWED" else "#ff00c1" for t in gf_df.type],opacity=0.6),
            text=gf_df["name"],textposition="top right",textfont=dict(size=10,color="#ffdd57"),name="Geofences"))
        AegisUI.dark_fig(fig_gf,"GEOFENCE ZONES")
        fig_gf.update_layout(height=460,margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_gf,use_container_width=True)
        st.dataframe(gf_df, use_container_width=True)

        st.markdown("#### 📋 GEOFENCE EVENT LOG")
        log_html = '<div class="log-block">'
        for _ in range(8):
            ts  = (datetime.datetime.now()-datetime.timedelta(minutes=random.randint(1,120))).strftime("%H:%M:%S")
            gf  = random.choice(geofences)
            evt = random.choice(["ENTERED","EXITED","DWELL","SPEEDING"])
            lvl = "crit" if gf["type"]=="RESTRICTED" and evt=="ENTERED" else "info"
            log_html += AegisUI.log_line(
                f"{random.choice(AegisData.VEHICLE_IDS)} {evt} [{gf['name']}] @ {gf['city']}", lvl)
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)


# =============================================================================
#  MAIN
# =============================================================================
def main():
    AegisUI.inject_css()

    TERMINALS = [
        "⚡ Command Overview",
        "🎙️ Voice Assistant",
        "✋ Gesture Security",
        "🔬 Predictive Health",
        "💹 Financial Risk AI",
        "🛡️ Cyber-Shield",
        "⚡ Energy Telemetry",
        "🔮 Digital Twin",
        "🚀 OTA Deployment",
        "📦 BlackBox Logs",
        "🧠 Neural Core",
        "🚔 ALPR Police DB",
        "🗺️ Map Assistant",
    ]

    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🛡 AEGIS OS</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:.62rem;letter-spacing:3px;color:rgba(0,210,255,0.4);'
                    'text-align:center;margin-bottom:1rem;">EV FLEET INTELLIGENCE</div>',
                    unsafe_allow_html=True)
        st.markdown("---")
        now = datetime.datetime.now().strftime("%H:%M:%S")
        st.markdown(f"""<div style="font-size:.72rem;color:#a0b0d0;letter-spacing:2px;padding:.3rem 0;">
            🟢 SYSTEM ONLINE<br>🔵 {now} IST<br>🟡 20 VEHICLES TRACKED</div>""",
            unsafe_allow_html=True)
        st.markdown("---")
        selected = st.radio("SATELLITE UPLINK", TERMINALS, label_visibility="visible")
        st.markdown("---")
        st.markdown('<div style="font-size:.62rem;color:rgba(0,210,255,0.35);letter-spacing:2px;'
                    'text-align:center;">AEGIS OS v3.3.0<br>© 2025 AEGIS INTELLIGENCE</div>',
                    unsafe_allow_html=True)

    dispatch = {
        TERMINALS[0]:  terminal_command_overview,
        TERMINALS[1]:  AegisHardware.voice_terminal,
        TERMINALS[2]:  AegisHardware.gesture_terminal,
        TERMINALS[3]:  terminal_predictive_health,
        TERMINALS[4]:  terminal_financial_risk,
        TERMINALS[5]:  terminal_cyber_shield,
        TERMINALS[6]:  terminal_energy_telemetry,
        TERMINALS[7]:  terminal_digital_twin,
        TERMINALS[8]:  terminal_ota,
        TERMINALS[9]:  terminal_blackbox,
        TERMINALS[10]: terminal_neural_core,
        TERMINALS[11]: terminal_alpr,
        TERMINALS[12]: terminal_map_assistant,
    }
    dispatch[selected]()


if __name__ == "__main__":
    main()
