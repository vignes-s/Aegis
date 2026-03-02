import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Aegis · EV Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  APPLE-INSPIRED CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:      #F2F2F7;
    --bg2:     #FFFFFF;
    --bg3:     #E5E5EA;
    --surface: rgba(255,255,255,0.82);
    --border:  rgba(0,0,0,0.08);
    --text:    #1C1C1E;
    --text2:   #3A3A3C;
    --text3:   #8E8E93;
    --blue:    #007AFF;
    --green:   #34C759;
    --orange:  #FF9500;
    --red:     #FF3B30;
    --shadow:  0 2px 20px rgba(0,0,0,0.07);
    --shadow-md: 0 8px 40px rgba(0,0,0,0.11);
    --radius:  16px;
    --radius-sm: 10px;
    --radius-lg: 24px;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Nunito', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}
.stApp { background: var(--bg) !important; }

[data-testid="stSidebar"] {
    background: rgba(242,242,247,0.97) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text2) !important; }

.block-container { padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1400px; }

[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 18px 20px !important;
    box-shadow: var(--shadow) !important;
    transition: transform 0.2s, box-shadow 0.2s;
}
[data-testid="metric-container"]:hover { transform: translateY(-2px); box-shadow: var(--shadow-md) !important; }
[data-testid="stMetricValue"] { font-family: 'Nunito',sans-serif !important; font-weight: 800 !important; font-size: 1.9rem !important; color: var(--text) !important; }
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; font-weight: 600 !important; color: var(--text3) !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }

h1 { font-family: 'Nunito',sans-serif !important; font-weight: 800 !important; color: var(--text) !important; font-size: 1.9rem !important; }
h2 { font-family: 'Nunito',sans-serif !important; font-weight: 700 !important; color: var(--text) !important; font-size: 1.2rem !important; }
h3 { font-family: 'Nunito',sans-serif !important; font-weight: 600 !important; color: var(--text2) !important; }

.stButton > button {
    background: var(--blue) !important; color: white !important; border: none !important;
    border-radius: 12px !important; font-family: 'Nunito',sans-serif !important; font-weight: 600 !important;
    font-size: 0.85rem !important; padding: 10px 20px !important; transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(0,122,255,0.25) !important;
}
.stButton > button:hover { background: #0066DD !important; transform: translateY(-1px) !important; box-shadow: 0 4px 16px rgba(0,122,255,0.35) !important; }

.stSuccess { background: rgba(52,199,89,0.1) !important; border: 1px solid rgba(52,199,89,0.3) !important; border-radius: var(--radius-sm) !important; }
.stWarning { background: rgba(255,149,0,0.1) !important; border: 1px solid rgba(255,149,0,0.3) !important; border-radius: var(--radius-sm) !important; }
.stError   { background: rgba(255,59,48,0.1) !important; border: 1px solid rgba(255,59,48,0.3) !important; border-radius: var(--radius-sm) !important; }
.stInfo    { background: rgba(0,122,255,0.08) !important; border: 1px solid rgba(0,122,255,0.2) !important; border-radius: var(--radius-sm) !important; }

.stSelectbox > div > div, .stTextInput > div > div > input {
    background: var(--bg2) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important; color: var(--text) !important;
    font-family: 'Nunito',sans-serif !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--bg3) !important; border-radius: 12px !important; padding: 4px !important; gap: 2px !important; border: none !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 10px !important; color: var(--text3) !important;
    font-weight: 600 !important; font-size: 0.82rem !important; padding: 8px 16px !important;
    border: none !important; transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] { background: var(--bg2) !important; color: var(--text) !important; box-shadow: 0 1px 8px rgba(0,0,0,0.12) !important; }

[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: var(--radius) !important; box-shadow: var(--shadow) !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 24px 0 !important; }
.stCheckbox label { color: var(--text2) !important; font-size: 0.85rem !important; }

/* ── Apple Cards ── */
.apple-card {
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
    padding: 20px 24px; margin: 8px 0; box-shadow: var(--shadow);
    transition: transform 0.2s, box-shadow 0.2s;
}
.apple-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.apple-card-sm {
    background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm);
    padding: 12px 16px; margin: 5px 0; box-shadow: var(--shadow);
}
.status-pill {
    display: inline-flex; align-items: center; gap: 5px; padding: 4px 12px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;
}
.pill-green  { background: rgba(52,199,89,0.12);  color: #1A7A33; border: 1px solid rgba(52,199,89,0.3); }
.pill-orange { background: rgba(255,149,0,0.12);  color: #7A4A00; border: 1px solid rgba(255,149,0,0.3); }
.pill-red    { background: rgba(255,59,48,0.12);  color: #8A1A14; border: 1px solid rgba(255,59,48,0.3); }
.pill-dark   { background: rgba(255,59,48,0.2);   color: #5A0A08; border: 1px solid rgba(255,59,48,0.5); animation: blink 1.2s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* ── Hero ── */
.hero-wrap {
    background: linear-gradient(145deg, #FFFFFF 0%, #F2F2F7 100%);
    border: 1px solid var(--border); border-radius: var(--radius-lg);
    padding: 32px 40px; margin-bottom: 24px; box-shadow: var(--shadow-md);
    position: relative; overflow: hidden;
}
.hero-wrap::before {
    content:''; position:absolute; top:-60px; right:-60px;
    width:220px; height:220px;
    background: radial-gradient(circle, rgba(0,122,255,0.08) 0%, transparent 70%);
    border-radius:50%; pointer-events:none;
}
.brand-name { font-family:'Nunito',sans-serif; font-weight:800; font-size:2.2rem; color:#1C1C1E; letter-spacing:-0.02em; }
.brand-name span { color:#007AFF; }
.brand-tag  { font-size:0.75rem; font-weight:600; color:#8E8E93; letter-spacing:0.12em; text-transform:uppercase; margin-top:4px; }
.live-badge {
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(52,199,89,0.1); border:1px solid rgba(52,199,89,0.3);
    border-radius:20px; padding:5px 12px; font-size:0.72rem; font-weight:700; color:#1A7A33;
}
.live-dot { width:7px; height:7px; background:#34C759; border-radius:50%; animation:livepulse 1.8s ease-in-out infinite; box-shadow:0 0 6px rgba(52,199,89,0.6); }
@keyframes livepulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.6;transform:scale(0.8)} }

.section-title { font-family:'Nunito',sans-serif; font-weight:800; font-size:1.15rem; color:#1C1C1E; margin:0 0 4px 0; }
.section-sub   { font-size:0.78rem; color:#8E8E93; margin:0 0 16px 0; }

.progress-bar-wrap { background:#E5E5EA; border-radius:6px; height:7px; overflow:hidden; margin:4px 0; }
.progress-bar-fill { height:7px; border-radius:6px; transition:width 0.6s cubic-bezier(0.4,0,0.2,1); }

.chat-user {
    background:#007AFF; color:white; border-radius:18px 18px 4px 18px;
    padding:10px 16px; margin:6px 0; max-width:72%;
    font-size:0.88rem; line-height:1.4; box-shadow:0 2px 8px rgba(0,122,255,0.2);
}
.chat-ai {
    background:white; color:#1C1C1E; border:1px solid var(--border);
    border-radius:18px 18px 18px 4px; padding:10px 16px; margin:6px 0; max-width:78%;
    font-size:0.88rem; line-height:1.4; box-shadow:var(--shadow);
}
.log-entry {
    font-family:'DM Mono',monospace; font-size:0.73rem; color:#8E8E93;
    background:rgba(0,0,0,0.03); border-left:3px solid #E5E5EA;
    padding:5px 10px; margin:3px 0; border-radius:0 6px 6px 0;
}

/* ── Aegis AI head SVG icon ── */
.aegis-ai-head {
    width:38px; height:38px; border-radius:50%;
    background: radial-gradient(circle at 35% 35%, #5AC8FA, #007AFF 60%, #0040AA);
    box-shadow: 0 0 0 4px rgba(0,122,255,0.15), 0 2px 10px rgba(0,122,255,0.3);
    display:flex; align-items:center; justify-content:center;
    animation: robopulse 2.5s ease-in-out infinite;
    flex-shrink:0;
}
@keyframes robopulse {
    0%,100%{box-shadow:0 0 0 4px rgba(0,122,255,0.15),0 2px 10px rgba(0,122,255,0.3);}
    50%{box-shadow:0 0 0 9px rgba(0,122,255,0.2),0 2px 18px rgba(0,122,255,0.45);}
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY HELPER
# ─────────────────────────────────────────────
PLOT_BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(255,255,255,0)"
GRID_COLOR = "#F2F2F7"
TICK_COLOR = "#8E8E93"
FONT = "Nunito, sans-serif"

def apple_layout(fig, height=300, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(family=FONT,size=14,color="#1C1C1E"), x=0, xanchor="left") if title else None,
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        font=dict(family=FONT, color=TICK_COLOR),
        height=height, margin=dict(t=44 if title else 20, b=20, l=10, r=10),
        legend=dict(bgcolor="rgba(255,255,255,0.85)", bordercolor="#E5E5EA", borderwidth=1, font=dict(size=11)),
    )
    fig.update_xaxes(showgrid=False, color=TICK_COLOR, linecolor="#E5E5EA", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR, color=TICK_COLOR, linecolor="#E5E5EA", zeroline=False)
    return fig

# ─────────────────────────────────────────────
#  DATA & LOGIC
# ─────────────────────────────────────────────
DRIVER_NAMES  = ["Arjun Sharma","Priya Nair","Ravi Kumar","Sneha Pillai","Vikram Reddy",
                 "Ananya Iyer","Siddharth Rao","Kavya Menon","Aditya Joshi","Meera Krishnan"]
VEHICLE_MODELS= ["BYD Atto 3","Tata Nexon EV","MG ZS EV","Ola S1 Pro","Ather 450X",
                 "Tata Tigor EV","Hyundai Kona","Kia EV6","BMW iX","Tesla Model 3"]

def generate_vehicle_data(n=10):
    data = []
    for i in range(n):
        data.append({
            "vehicle_id":        f"EV-{str(i+1).zfill(3)}",
            "model":             VEHICLE_MODELS[i % len(VEHICLE_MODELS)],
            "driver":            DRIVER_NAMES[i % len(DRIVER_NAMES)],
            "speed":             int(np.clip(np.random.normal(65,25),0,130)),
            "battery":           int(np.clip(np.random.normal(55,25),5,100)),
            "soc_degradation":   round(random.uniform(0,15),1),
            "brake_temp":        int(np.clip(np.random.normal(160,40),80,260)),
            "motor_temp":        int(np.clip(np.random.normal(80,20),40,130)),
            "regen_efficiency":  round(random.uniform(0.1,0.95),2),
            "tire_pressure":     round(random.uniform(28,38),1),
            "cabin_temp":        round(random.uniform(18,35),1),
            "vibration":         round(random.uniform(0.1,2.5),2),
            "mileage":           random.randint(5000,95000),
            "last_service_days": random.randint(0,180),
            "trips_today":       random.randint(1,12),
            "harsh_braking":     random.randint(0,8),
            "rapid_accel":       random.randint(0,6),
            "overspeed_events":  random.randint(0,5),
            "network_status":    random.choices([1,0],weights=[0.85,0.15])[0],
            "gps_status":        random.choices([1,0],weights=[0.92,0.08])[0],
        })
    return pd.DataFrame(data)

def detect_faults(row):
    f=[]
    if row["battery"]<15:           f.append("⚡ Critical Low Battery")
    elif row["battery"]<25:         f.append("⚡ Low Battery")
    if row["brake_temp"]>220:       f.append("🔥 Critical Brake Overheat")
    elif row["brake_temp"]>195:     f.append("🌡 Brake Overheat")
    if row["motor_temp"]>110:       f.append("🔥 Critical Motor Overheat")
    elif row["motor_temp"]>95:      f.append("🌡 Motor Overheat")
    if row["speed"]>110:            f.append("🚨 Dangerous Overspeed")
    elif row["speed"]>95:           f.append("⚠️ Overspeed")
    if row["network_status"]==0:    f.append("📡 Network Failure")
    if row["gps_status"]==0:        f.append("🛰 GPS Signal Lost")
    if row["regen_efficiency"]<0.2: f.append("🔋 Regen Brake Issue")
    if row["tire_pressure"]<30:     f.append("🔘 Low Tire Pressure")
    if row["vibration"]>2.0:        f.append("📳 Abnormal Vibration")
    if row["last_service_days"]>150:f.append("🔧 Overdue Service")
    if row["soc_degradation"]>12:   f.append("🔋 Battery Degradation")
    return f

def calculate_safety_score(row):
    mech=100.;elec=100.;digi=100.;therm=100.;drv=100.
    if row["brake_temp"]>220:       mech-=35
    elif row["brake_temp"]>195:     mech-=18
    if row["speed"]>110:            mech-=20
    elif row["speed"]>95:           mech-=10
    if row["vibration"]>2.0:        mech-=15
    if row["tire_pressure"]<30:     mech-=10
    if row["battery"]<15:           elec-=45
    elif row["battery"]<25:         elec-=25
    if row["regen_efficiency"]<0.2: elec-=15
    if row["soc_degradation"]>12:   elec-=10
    if row["network_status"]==0:    digi-=40
    if row["gps_status"]==0:        digi-=30
    if row["motor_temp"]>110:       therm-=40
    elif row["motor_temp"]>95:      therm-=20
    if row["cabin_temp"]>32:        therm-=5
    drv-=min(row["harsh_braking"]*5,30)
    drv-=min(row["rapid_accel"]*4,20)
    drv-=min(row["overspeed_events"]*6,30)
    mech=max(mech,0);elec=max(elec,0);digi=max(digi,0);therm=max(therm,0);drv=max(drv,0)
    overall=0.25*mech+0.25*elec+0.15*digi+0.20*therm+0.15*drv
    return mech,elec,digi,therm,drv,round(overall,1)

def classify_safety(s):
    if s>=82: return "Healthy"
    elif s>=63: return "At Risk"
    elif s>=42: return "Critical"
    return "Emergency"

def driver_score(row):
    b=100-min(row["harsh_braking"]*6,36)-min(row["rapid_accel"]*5,25)-min(row["overspeed_events"]*7,35)
    return max(b,0)

def predict_failure_prob(row):
    r=0.
    r+=max(0,(100-row["battery"])/100)*0.2
    r+=max(0,(row["brake_temp"]-150)/110)*0.25
    r+=max(0,(row["motor_temp"]-70)/60)*0.2
    r+=(1-row["regen_efficiency"])*0.1
    r+=max(0,row["soc_degradation"]/15)*0.1
    r+=(1-row["network_status"])*0.1
    r+=max(0,(row["vibration"]-1.0)/1.5)*0.05
    return round(min(r,1.0)*100,1)

def maintenance_window(p):
    if p>70: return "< 48 hrs"
    elif p>45: return "3–7 days"
    elif p>25: return "2–4 weeks"
    return "> 1 month"

def generate_recs(faults):
    MAP={
        "Critical Low Battery":    "⚡ URGENT: Route to charging station now",
        "Low Battery":             "⚡ Schedule charging within 20 km",
        "Critical Brake Overheat": "🔥 STOP: Brake inspection required immediately",
        "Brake Overheat":          "🌡 Reduce braking intensity; inspect pads",
        "Critical Motor Overheat": "🔥 Reduce load, allow cooling",
        "Motor Overheat":          "🌡 Check motor cooling system",
        "Dangerous Overspeed":     "🚨 Alert driver; apply speed limiter",
        "Overspeed":               "⚠️ Issue speed warning to driver",
        "Network Failure":         "📡 Diagnose V2X communication module",
        "GPS Signal Lost":         "🛰 Switch to DR navigation; check antenna",
        "Regen Brake Issue":       "🔋 Calibrate regenerative braking system",
        "Low Tire Pressure":       "🔘 Inflate to 32–35 PSI",
        "Abnormal Vibration":      "📳 Check wheel balance & suspension",
        "Overdue Service":         "🔧 Schedule preventive maintenance",
        "Battery Degradation":     "🔋 Battery health check required",
    }
    recs=[]
    for fault in faults:
        clean=fault.split(" ",1)[1] if len(fault)>0 and not fault[0].isalpha() else fault
        for k,v in MAP.items():
            if k.lower() in clean.lower():
                recs.append(v); break
    return recs

def fleet_ai_response(query, df):
    q=query.lower()
    if any(w in q for w in ["how many","count","total"]):
        if "critical" in q or "emergency" in q:
            n=len(df[df["status"].isin(["Critical","Emergency"])])
            return f"🔴 **{n}** vehicles are in Critical or Emergency status."
        if "healthy" in q: return f"✅ **{len(df[df['status']=='Healthy'])}** vehicles are Healthy."
        return f"📊 Fleet has **{len(df)}** total vehicles."
    if any(w in q for w in ["worst","dangerous","most risk","lowest"]):
        w=df.loc[df["safety_index"].idxmin()]
        return f"⚠️ **{w['vehicle_id']}** ({w['model']}) has the lowest score: **{w['safety_index']}** — driven by {w['driver']}."
    if any(w in q for w in ["best","safest","highest"]):
        b=df.loc[df["safety_index"].idxmax()]
        return f"✅ **{b['vehicle_id']}** ({b['model']}) is safest: **{b['safety_index']}** — driven by {b['driver']}."
    if "battery" in q:
        low=df[df["battery"]<25]
        if len(low): return f"⚡ **{len(low)}** vehicles have low battery: {', '.join(low['vehicle_id'].tolist())}."
        return "⚡ All vehicles have adequate battery (>25%)."
    if any(w in q for w in ["driver","behavior","score"]):
        df2=df.copy(); df2["ds"]=df2.apply(driver_score,axis=1)
        return f"🏆 Best driver: **{df2.loc[df2['ds'].idxmax(),'driver']}** | ⚠️ Needs coaching: **{df2.loc[df2['ds'].idxmin(),'driver']}**"
    if any(w in q for w in ["fleet","average","overall","index"]):
        return f"📈 Fleet Safety Index: **{round(df['safety_index'].mean(),1)}/100**"
    if any(w in q for w in ["maintenance","service","repair"]):
        overdue=df[df["last_service_days"]>150]
        ids=', '.join(overdue["vehicle_id"].tolist()) if len(overdue) else "None"
        return f"🔧 **{len(overdue)}** vehicles overdue for service: {ids}"
    if any(w in q for w in ["recommend","action","urgent","what should"]):
        crit=df[df["status"].isin(["Critical","Emergency"])]
        if not len(crit): return "✅ Fleet in good condition. Continue regular monitoring."
        top=crit.iloc[0]
        recs=generate_recs(top["faults"])
        return f"🎯 Priority — **{top['vehicle_id']}**: "+" | ".join(recs[:3])
    return "🤖 Try: 'Which vehicle needs urgent attention?', 'Who is the safest driver?', 'How many have low battery?', or 'What is the fleet index?'"

def gen_telemetry():
    now=datetime.now()
    times=[now-timedelta(minutes=30*i) for i in range(48,0,-1)]
    return pd.DataFrame({
        "time":times,
        "speed":    [max(0,min(120,60+30*np.sin(i/8)+random.gauss(0,10))) for i in range(48)],
        "battery":  [max(10,80-i*0.5+random.gauss(0,2)) for i in range(48)],
        "brake_temp":[max(100,160+30*np.sin(i/6)+random.gauss(0,15)) for i in range(48)],
    })

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "fleet_data"   not in st.session_state: st.session_state.fleet_data=generate_vehicle_data(10)
if "chat_history" not in st.session_state: st.session_state.chat_history=[{"role":"ai","text":"Hi! I'm Aegis AI. Ask me anything about your fleet — safety scores, driver behavior, or maintenance alerts."}]
if "sim_log"      not in st.session_state: st.session_state.sim_log=[]
if "mute_alerts"  not in st.session_state: st.session_state.mute_alerts=False

# ─────────────────────────────────────────────
#  COMPUTE DF
# ─────────────────────────────────────────────
df=st.session_state.fleet_data.copy()
df["faults"]         =df.apply(detect_faults,axis=1)
df["recommendations"]=df["faults"].apply(generate_recs)
df[["mech","elec","digi","therm","drv_score","safety_index"]]=df.apply(lambda r:pd.Series(calculate_safety_score(r)),axis=1)
df["status"]         =df["safety_index"].apply(classify_safety)
df["fail_prob"]      =df.apply(predict_failure_prob,axis=1)
df["maint_window"]   =df["fail_prob"].apply(maintenance_window)
df["driver_score"]   =df.apply(driver_score,axis=1)

FSI        =round(df["safety_index"].mean(),1)
n_healthy  =len(df[df["status"]=="Healthy"])
n_risk     =len(df[df["status"]=="At Risk"])
n_critical =len(df[df["status"]=="Critical"])
n_emergency=len(df[df["status"]=="Emergency"])

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 12px 0;'>
        <div style='display:flex;align-items:center;gap:8px;'>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="4" width="18" height="14" rx="3" fill="#007AFF"/>
              <circle cx="8.5" cy="9" r="1.5" fill="white"/>
              <circle cx="15.5" cy="9" r="1.5" fill="white"/>
              <rect x="9" y="13" width="6" height="1.5" rx="0.75" fill="white"/>
              <rect x="10" y="2" width="4" height="3" rx="1" fill="#007AFF"/>
              <rect x="11.25" y="18" width="1.5" height="2" rx="0.75" fill="#007AFF"/>
              <rect x="8" y="19.5" width="8" height="1.2" rx="0.6" fill="#007AFF"/>
            </svg>
            <div style='font-family:Nunito,sans-serif;font-weight:800;font-size:1.2rem;color:#1C1C1E;'>Aegis</div>
        </div>
        <div style='font-size:0.7rem;color:#8E8E93;letter-spacing:0.1em;margin-top:4px;text-transform:uppercase;'>EV Safety Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("**Fleet Config**")
    num_v=st.slider("Vehicles",5,20,10)
    if st.button("🔄 Refresh Fleet Data"):
        st.session_state.fleet_data=generate_vehicle_data(num_v)
        st.session_state.sim_log=[]
        st.rerun()
    st.divider()
    st.markdown("**Display**")
    show_raw  =st.checkbox("Raw Telemetry Table",False)
    show_tele =st.checkbox("Historical Telemetry Charts",False)
    mute_alerts=st.checkbox("Mute Alerts",False)
    st.divider()
    st.markdown("**Fleet Health**")
    for label,val,color in [("🟢 Healthy",n_healthy,"#34C759"),("🟡 At Risk",n_risk,"#FF9500"),
                             ("🔴 Critical",n_critical,"#FF3B30"),("🆘 Emergency",n_emergency,"#FF3B30")]:
        st.markdown(f"""<div style='display:flex;justify-content:space-between;padding:4px 0;font-size:0.83rem;'>
            <span style='color:#3A3A3C;'>{label}</span>
            <span style='font-weight:700;color:{color};'>{val}</span></div>""",unsafe_allow_html=True)
    st.divider()
    st.caption("VIT Smart Mobility · Team Aegis · 2026")

# ─────────────────────────────────────────────
#  HERO  (FIX 1: Aegis name | FIX 2: proper AI robot SVG head)
# ─────────────────────────────────────────────
fsi_color=("#34C759" if FSI>=80 else "#FF9500" if FSI>=60 else "#FF3B30")
fsi_label=("Fleet is Stable" if FSI>=80 else "Moderate Risk" if FSI>=60 else "High Risk — Action Required")

st.markdown(f"""
<div class="hero-wrap">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:20px;">
    <div>
      <div style="display:flex;align-items:center;gap:14px;">
        <!-- FIX 2: Proper AI robot head SVG — not emoji -->
        <div class="aegis-ai-head" title="Jarvis AI Active">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="5" width="18" height="13" rx="3.5" fill="white" fill-opacity="0.95"/>
            <circle cx="8.5" cy="10" r="2" fill="#007AFF"/>
            <circle cx="9.2" cy="9.3" r="0.6" fill="white"/>
            <circle cx="15.5" cy="10" r="2" fill="#007AFF"/>
            <circle cx="16.2" cy="9.3" r="0.6" fill="white"/>
            <rect x="9.5" y="13.5" width="5" height="1.2" rx="0.6" fill="#34C759"/>
            <rect x="10.5" y="2.5" width="3" height="3" rx="1" fill="white" fill-opacity="0.8"/>
            <rect x="11.75" y="18" width="0.5" height="0.5" rx="0.25" fill="white"/>
            <rect x="0" y="9" width="3" height="1.5" rx="0.75" fill="white" fill-opacity="0.6"/>
            <rect x="21" y="9" width="3" height="1.5" rx="0.75" fill="white" fill-opacity="0.6"/>
          </svg>
        </div>
        <!-- FIX 1: Brand name changed to Aegis -->
        <div class="brand-name">Aegi<span>s</span></div>
      </div>
      <div class="brand-tag">Smart EV Fleet Safety Intelligence Platform</div>
      <div style="margin-top:14px;">
        <span class="live-badge"><span class="live-dot"></span>LIVE &nbsp;·&nbsp; {datetime.now().strftime("%d %b %Y, %H:%M")}</span>
        &nbsp;
        <span style="font-size:0.7rem;font-weight:600;color:#007AFF;background:rgba(0,122,255,0.08);border:1px solid rgba(0,122,255,0.2);border-radius:20px;padding:4px 10px;">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="#007AFF" style="vertical-align:middle;margin-right:3px;" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="5" width="18" height="13" rx="3.5" fill="#007AFF"/>
            <circle cx="8.5" cy="10" r="2" fill="white"/>
            <circle cx="15.5" cy="10" r="2" fill="white"/>
            <rect x="9.5" y="13.5" width="5" height="1.2" rx="0.6" fill="#34C759"/>
          </svg>
          Jarvis Active
        </span>
      </div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:0.72rem;font-weight:600;color:#8E8E93;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">Fleet Safety Index</div>
      <div style="font-family:Nunito,sans-serif;font-weight:800;font-size:3rem;color:{fsi_color};line-height:1;">
        {FSI}<span style="font-size:1rem;color:#8E8E93;">/100</span>
      </div>
      <div style="font-size:0.78rem;font-weight:600;color:{fsi_color};margin-top:2px;">{fsi_label}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── GLOBAL JARVIS AUTO-ALERT ──
_emg_ids   = [str(r['vehicle_id']) for _,r in df[df["status"]=="Emergency"].iterrows()]
_emg_names = [str(r['driver'])     for _,r in df[df["status"]=="Emergency"].iterrows()]
_risk_ids  = [str(r['vehicle_id']) for _,r in df[df["status"]=="At Risk"].iterrows()]
_banner_h  = 0 if (not _emg_ids and not _risk_ids) else (100 if not _emg_ids else 130)

st.components.v1.html(f"""
<!DOCTYPE html><html><head>
<style>
body{{margin:0;padding:0;font-family:'Nunito',sans-serif;}}
#emg-banner{{display:none;background:linear-gradient(135deg,#FF3B30,#CC1A10);color:white;border-radius:14px;padding:14px 18px;margin:4px 0;animation:epulse 0.7s ease-in-out infinite;box-shadow:0 4px 24px rgba(255,59,48,0.5);}}
#risk-banner{{display:none;background:linear-gradient(135deg,#FF9500,#CC7700);color:white;border-radius:14px;padding:12px 18px;margin:4px 0;box-shadow:0 4px 16px rgba(255,149,0,0.35);}}
@keyframes epulse{{0%,100%{{box-shadow:0 4px 24px rgba(255,59,48,0.5);}}50%{{box-shadow:0 4px 44px rgba(255,59,48,0.85);}}}}
.b-title{{font-weight:800;font-size:0.95rem;}}.b-sub{{font-size:0.8rem;opacity:0.93;margin-top:3px;}}
</style></head><body>
<div id="emg-banner"><div class="b-title">🚨 JARVIS EMERGENCY ALERT</div><div class="b-sub" id="emg-text"></div></div>
<div id="risk-banner"><div class="b-title">⚠️ JARVIS — VEHICLES AT RISK</div><div class="b-sub" id="risk-text"></div></div>
<script>
const EMG_IDS={_emg_ids};const EMG_NAMES={_emg_names};const RISK_IDS={_risk_ids};
const synth=window.speechSynthesis;
function getVoice(){{const vv=synth.getVoices();return vv.find(v=>v.name.includes('Daniel')||v.name.includes('Google UK')||v.name.includes('British'))||null;}}
function speak(text,rate=0.87,pitch=0.78){{synth.cancel();const u=new SpeechSynthesisUtterance(text);u.rate=rate;u.pitch=pitch;u.volume=1.0;const v=getVoice();if(v)u.voice=v;synth.speak(u);}}
function buzz(){{try{{const ctx=new(window.AudioContext||window.webkitAudioContext)();[[880,0.00],[660,0.22],[880,0.44],[660,0.66],[880,0.88]].forEach(([f,t])=>{{const o=ctx.createOscillator(),g=ctx.createGain();o.connect(g);g.connect(ctx.destination);o.type='square';o.frequency.value=f;g.gain.setValueAtTime(0.7,ctx.currentTime+t);g.gain.exponentialRampToValueAtTime(0.001,ctx.currentTime+t+0.18);o.start(ctx.currentTime+t);o.stop(ctx.currentTime+t+0.22);}})}}catch(e){{}}}}
function runAlerts(){{
  if(EMG_IDS.length>0){{
    document.getElementById('emg-banner').style.display='block';
    document.getElementById('emg-text').innerText='Vehicles '+EMG_IDS.join(', ')+' ('+EMG_NAMES.join(', ')+') — EMERGENCY! Immediate action required.';
    setTimeout(()=>{{buzz();setTimeout(()=>{{speak('Alert! Alert! Sir, '+EMG_IDS.length+' vehicle'+(EMG_IDS.length>1?'s are':' is')+' in emergency status. '+EMG_IDS.join(', ')+'. Driver'+(EMG_NAMES.length>1?'s ':' ')+EMG_NAMES.join(' and ')+' require'+(EMG_NAMES.length>1?'':'s')+' immediate assistance. I strongly urge you to act now, Sir!');}},1300);}},600);
  }} else if(RISK_IDS.length>0){{
    document.getElementById('risk-banner').style.display='block';
    document.getElementById('risk-text').innerText=RISK_IDS.length+' vehicle(s) at risk: '+RISK_IDS.join(', ')+'. Monitoring closely.';
    setTimeout(()=>{{speak('Sir, '+RISK_IDS.length+' vehicle'+(RISK_IDS.length>1?'s are':' is')+' currently at risk: '+RISK_IDS.join(', ')+'. I recommend reviewing the fleet at your earliest convenience.');}},1000);
  }}
}}
if(synth.getVoices().length>0){{runAlerts();}}else{{synth.onvoiceschanged=runAlerts;setTimeout(runAlerts,2200);}}
</script></body></html>
""", height=_banner_h)

# ─────────────────────────────────────────────
#  KPI ROW
# ─────────────────────────────────────────────
k1,k2,k3,k4,k5,k6=st.columns(6)
with k1: st.metric("🚗 Total",len(df))
with k2: st.metric("✅ Healthy",n_healthy)
with k3: st.metric("⚠️ At Risk",n_risk)
with k4: st.metric("🔴 Critical",n_critical)
with k5: st.metric("🆘 Emergency",n_emergency)
with k6: st.metric("🔮 Avg Fail Risk",f"{round(df['fail_prob'].mean(),1)}%")

# ─────────────────────────────────────────────
#  ALERTS
# ─────────────────────────────────────────────
if not mute_alerts:
    for _,ev in df[df["status"]=="Emergency"].iterrows():
        st.error(f"🚨 EMERGENCY — {ev['vehicle_id']} ({ev['driver']}) | Score: {ev['safety_index']} | {', '.join(ev['faults'])}")
    crit_df=df[df["status"]=="Critical"]
    if len(crit_df):
        st.warning(f"⚠️ CRITICAL — {len(crit_df)} vehicle(s): {', '.join(crit_df['vehicle_id'].tolist())}")

st.divider()

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tabs=st.tabs(["📡 Fleet Overview","🔮 Predictive AI","👤 Driver Analytics","🧬 Digital Twin","💬 AI Assistant","📈 Analytics","🎙️ Jarvis"])

# ══════════════════════════════════════════
#  TAB 1 — FLEET OVERVIEW
# ══════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="section-title">Vehicle Safety Dashboard</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Real-time telemetry and fault monitoring across all EVs</div>',unsafe_allow_html=True)
    for _,row in df.iterrows():
        pill={"Healthy":"pill-green","At Risk":"pill-orange","Critical":"pill-red","Emergency":"pill-dark"}.get(row["status"],"pill-orange")
        # FIX 4: healthy vehicles show no faults cleanly, no code leakage
        fault_str=" &nbsp;·&nbsp; ".join(row["faults"]) if row["faults"] else "✅ No faults detected"
        rec_str="<br>".join([f"<span style='color:#007AFF;'>→</span> {r}" for r in row["recommendations"][:3]]) if row["recommendations"] else ""
        sc="#34C759" if row["safety_index"]>=82 else "#FF9500" if row["safety_index"]>=63 else "#FF3B30"
        fc="#FF3B30" if row["fail_prob"]>60 else "#FF9500" if row["fail_prob"]>30 else "#34C759"
        # FIX 4: icon tied to status not threshold
        risk_icon="✅" if row["status"]=="Healthy" else "⚠️"
        rec_block=f"<div style='margin-top:8px;font-size:0.75rem;color:#8E8E93;line-height:1.7;'>{rec_str}</div>" if rec_str else ""
        st.markdown(f"""
        <div class="apple-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;">
            <div style="flex:1;min-width:260px;">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <span style="font-family:Nunito,sans-serif;font-weight:800;font-size:1rem;color:#1C1C1E;">{row['vehicle_id']}</span>
                <span class="status-pill {pill}">{row['status']}</span>
              </div>
              <div style="font-size:0.78rem;color:#8E8E93;margin-bottom:8px;">{row['model']} &nbsp;·&nbsp; 👤 {row['driver']} &nbsp;·&nbsp; {row['mileage']:,} km</div>
              <div style="font-size:0.79rem;color:#3A3A3C;">{fault_str}</div>
              {rec_block}
            </div>
            <div style="text-align:right;min-width:180px;">
              <div style="font-family:Nunito,sans-serif;font-weight:800;font-size:2rem;color:{sc};line-height:1.1;">
                {row['safety_index']}<span style="font-size:0.8rem;color:#8E8E93;font-weight:400;">/100</span>
              </div>
              <div style="font-size:0.65rem;color:#8E8E93;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Safety Index</div>
              <div style="font-size:0.77rem;margin-bottom:4px;">
                <span style="color:{fc};font-weight:600;">{risk_icon} {row['fail_prob']}% failure risk</span>
              </div>
              <div style="font-size:0.73rem;color:#8E8E93;">🔧 {row['maint_window']}</div>
              <div style="margin-top:8px;font-size:0.72rem;color:#8E8E93;">⚡{row['battery']}% &nbsp;|&nbsp; 🌡{row['brake_temp']}°C &nbsp;|&nbsp; 🏎 {row['speed']}km/h</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
    if show_raw:
        st.markdown("**Raw Telemetry Data**")
        cols=["vehicle_id","model","driver","speed","battery","brake_temp","motor_temp","regen_efficiency","vibration","network_status","safety_index","status"]
        st.dataframe(df[cols].set_index("vehicle_id"),use_container_width=True)

# ══════════════════════════════════════════
#  TAB 2 — PREDICTIVE AI
# ══════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-title">Predictive Maintenance Intelligence</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-sub">AI-simulated failure probabilities based on multi-parameter telemetry analysis</div>',unsafe_allow_html=True)
    c1,c2=st.columns([2,1])
    with c1:
        bar_colors=["#FF3B30" if p>60 else "#FF9500" if p>30 else "#34C759" for p in df["fail_prob"]]
        fig_pred=go.Figure()
        fig_pred.add_trace(go.Bar(x=df["vehicle_id"],y=df["fail_prob"],marker_color=bar_colors,
            text=[f"{p}%" for p in df["fail_prob"]],textposition="outside",
            textfont=dict(family="DM Mono",size=10,color="#3A3A3C")))
        fig_pred.add_hline(y=60,line_dash="dot",line_color="rgba(255,59,48,0.5)",
                           annotation_text="High Risk",annotation_font_color="#FF3B30",annotation_font_size=11)
        fig_pred.add_hline(y=30,line_dash="dot",line_color="rgba(255,149,0,0.5)",
                           annotation_text="Moderate Risk",annotation_font_color="#FF9500",annotation_font_size=11)
        apple_layout(fig_pred,height=320,title="Failure Probability by Vehicle (%)")
        fig_pred.update_layout(yaxis=dict(range=[0,115]))
        st.plotly_chart(fig_pred,use_container_width=True)
    with c2:
        st.markdown("**Maintenance Schedule**")
        for _,r in df[["vehicle_id","fail_prob","maint_window"]].sort_values("fail_prob",ascending=False).iterrows():
            dot="🔴" if r["fail_prob"]>60 else "🟡" if r["fail_prob"]>30 else "🟢"
            st.markdown(f"""<div class="apple-card-sm">
                <div style="font-weight:700;font-size:0.85rem;color:#1C1C1E;">{dot} {r['vehicle_id']}</div>
                <div style="font-size:0.73rem;color:#8E8E93;margin-top:2px;">{r['maint_window']} &nbsp;·&nbsp; {r['fail_prob']}% risk</div>
            </div>""",unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="section-title">Multi-Dimensional Safety Analysis</div>',unsafe_allow_html=True)
    sel_v=st.selectbox("Select Vehicle",df["vehicle_id"].tolist(),key="pred_sel")
    vrow=df[df["vehicle_id"]==sel_v].iloc[0]
    cats=["Mechanical","Electrical","Digital","Thermal","Driver"]
    vals=[vrow["mech"],vrow["elec"],vrow["digi"],vrow["therm"],vrow["drv_score"]]
    ra1,ra2=st.columns([1,1])
    with ra1:
        fig_radar=go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=vals+[vals[0]],theta=cats+[cats[0]],fill='toself',
            fillcolor='rgba(0,122,255,0.1)',line=dict(color='#007AFF',width=2.5)))
        fig_radar.update_layout(
            polar=dict(bgcolor="rgba(242,242,247,0.6)",
                radialaxis=dict(visible=True,range=[0,100],color="#8E8E93",gridcolor="#E5E5EA",tickfont=dict(size=9)),
                angularaxis=dict(color="#3A3A3C",tickfont=dict(size=11,family="Nunito"))),
            paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,height=320,margin=dict(t=20,b=20,l=30,r=30))
        st.plotly_chart(fig_radar,use_container_width=True)
    with ra2:
        st.markdown(f"**{sel_v} Health Breakdown**")
        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        for cat,val in zip(cats,vals):
            bc="#34C759" if val>=80 else "#FF9500" if val>=60 else "#FF3B30"
            st.markdown(f"""<div style="margin:10px 0;">
                <div style="display:flex;justify-content:space-between;font-size:0.82rem;color:#3A3A3C;margin-bottom:4px;font-weight:600;">
                    <span>{cat}</span><span style="color:{bc};font-family:'DM Mono',monospace;">{val:.0f}</span>
                </div>
                <div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:{val}%;background:{bc};"></div></div>
            </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════
#  TAB 3 — DRIVER ANALYTICS
# ══════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="section-title">Driver Behavior & Safety Leaderboard</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Ranked by driving score — braking, acceleration, and speed compliance</div>',unsafe_allow_html=True)
    drv_df=df[["vehicle_id","driver","driver_score","harsh_braking","rapid_accel","overspeed_events","trips_today"]].sort_values("driver_score",ascending=False).reset_index(drop=True)
    medals=["🥇","🥈","🥉"]+[f"#{i+4}" for i in range(len(drv_df)-3)]
    for i,(_,r) in enumerate(drv_df.iterrows()):
        sc="#34C759" if r["driver_score"]>=80 else "#FF9500" if r["driver_score"]>=60 else "#FF3B30"
        st.markdown(f"""<div class="apple-card" style="padding:16px 24px;">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
                <div style="display:flex;align-items:center;gap:16px;">
                    <div style="font-size:1.6rem;min-width:36px;text-align:center;">{medals[i]}</div>
                    <div>
                        <div style="font-weight:700;font-size:0.95rem;color:#1C1C1E;">{r['driver']}</div>
                        <div style="font-size:0.75rem;color:#8E8E93;margin-top:2px;">{r['vehicle_id']} &nbsp;·&nbsp; {r['trips_today']} trips today</div>
                    </div>
                </div>
                <div style="display:flex;gap:24px;align-items:center;flex-wrap:wrap;">
                    <div style="text-align:center;">
                        <div style="font-size:0.62rem;color:#8E8E93;text-transform:uppercase;letter-spacing:0.06em;">Harsh Brake</div>
                        <div style="font-family:'DM Mono',monospace;font-weight:600;color:#FF9500;">{r['harsh_braking']}x</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:0.62rem;color:#8E8E93;text-transform:uppercase;letter-spacing:0.06em;">Rapid Accel</div>
                        <div style="font-family:'DM Mono',monospace;font-weight:600;color:#FF9500;">{r['rapid_accel']}x</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:0.62rem;color:#8E8E93;text-transform:uppercase;letter-spacing:0.06em;">Overspeed</div>
                        <div style="font-family:'DM Mono',monospace;font-weight:600;color:#FF3B30;">{r['overspeed_events']}x</div>
                    </div>
                    <div style="text-align:center;min-width:70px;">
                        <div style="font-family:Nunito,sans-serif;font-weight:800;font-size:1.8rem;color:{sc};line-height:1;">{r['driver_score']}</div>
                        <div style="font-size:0.62rem;color:#8E8E93;text-transform:uppercase;letter-spacing:0.06em;">Score</div>
                    </div>
                </div>
            </div>
        </div>""",unsafe_allow_html=True)
    st.divider()
    d1,d2=st.columns(2)
    with d1:
        fig_ds=px.bar(drv_df,x="driver",y="driver_score",color="driver_score",
                      color_continuous_scale=["#FF3B30","#FF9500","#34C759"],range_color=[0,100])
        apple_layout(fig_ds,height=280,title="Driver Score Comparison")
        fig_ds.update_layout(xaxis=dict(tickangle=30),coloraxis_showscale=False,margin=dict(t=44,b=80,l=10,r=10))
        st.plotly_chart(fig_ds,use_container_width=True)
    with d2:
        fig_events=go.Figure()
        fig_events.add_trace(go.Bar(name="Harsh Braking",x=drv_df["driver"],y=drv_df["harsh_braking"],marker_color="#FF3B30"))
        fig_events.add_trace(go.Bar(name="Rapid Accel",  x=drv_df["driver"],y=drv_df["rapid_accel"],  marker_color="#FF9500"))
        fig_events.add_trace(go.Bar(name="Overspeed",    x=drv_df["driver"],y=drv_df["overspeed_events"],marker_color="#FF6B35"))
        fig_events.update_layout(barmode="group")
        apple_layout(fig_events,height=280,title="Risk Events by Driver")
        fig_events.update_layout(xaxis=dict(tickangle=30),margin=dict(t=44,b=80,l=10,r=10))
        st.plotly_chart(fig_events,use_container_width=True)

# ══════════════════════════════════════════
#  TAB 4 — DIGITAL TWIN
# ══════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-title">Digital Twin Simulation Lab</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Inject real-world fault scenarios and observe live safety impact</div>',unsafe_allow_html=True)
    col_info,col_sim=st.columns([1,2])
    with col_info:
        sim_v=st.selectbox("Select Vehicle",df["vehicle_id"].tolist(),key="twin_sel")
        sv=st.session_state.fleet_data[st.session_state.fleet_data["vehicle_id"]==sim_v].iloc[0]
        rows_html="".join([
            f"<div style='display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #F2F2F7;font-size:0.82rem;'>"
            f"<span style='color:#8E8E93;'>{k}</span>"
            f"<span style='font-family:DM Mono,monospace;font-weight:600;color:#1C1C1E;'>{v}</span></div>"
            for k,v in [("Battery",f"{sv['battery']}%"),("Brake Temp",f"{sv['brake_temp']}°C"),
                        ("Motor Temp",f"{sv['motor_temp']}°C"),("Speed",f"{sv['speed']} km/h"),
                        ("Network","OK ✅" if sv['network_status']==1 else "FAULT ❌")]
        ])
        st.markdown(f"""<div class="apple-card">
            <div style="font-size:0.68rem;font-weight:700;color:#8E8E93;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px;">Current State</div>
            {rows_html}
        </div>""",unsafe_allow_html=True)
    with col_sim:
        st.markdown("**Inject Fault Scenario**")
        fc1,fc2,fc3=st.columns(3)
        with fc1:
            if st.button("🔥 Brake Failure"):
                st.session_state.fleet_data.loc[st.session_state.fleet_data["vehicle_id"]==sim_v,"brake_temp"]=255
                st.session_state.sim_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {sim_v} → Brake failure (255°C)")
                st.rerun()
            if st.button("⚡ Battery Drop"):
                st.session_state.fleet_data.loc[st.session_state.fleet_data["vehicle_id"]==sim_v,"battery"]=8
                st.session_state.sim_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {sim_v} → Battery drop (8%)")
                st.rerun()
        with fc2:
            if st.button("🌡 Motor Overheat"):
                st.session_state.fleet_data.loc[st.session_state.fleet_data["vehicle_id"]==sim_v,"motor_temp"]=125
                st.session_state.sim_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {sim_v} → Motor overheat")
                st.rerun()
            if st.button("📡 Network Cut"):
                st.session_state.fleet_data.loc[st.session_state.fleet_data["vehicle_id"]==sim_v,"network_status"]=0
                st.session_state.sim_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {sim_v} → Network failure")
                st.rerun()
        with fc3:
            if st.button("🚨 Overspeed"):
                st.session_state.fleet_data.loc[st.session_state.fleet_data["vehicle_id"]==sim_v,"speed"]=125
                st.session_state.sim_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {sim_v} → Overspeed (125 km/h)")
                st.rerun()
            if st.button("✅ Reset"):
                st.session_state.fleet_data.loc[st.session_state.fleet_data["vehicle_id"]==sim_v,
                    ["battery","brake_temp","motor_temp","speed","network_status"]]=[
                    random.randint(40,90),random.randint(120,175),random.randint(60,88),random.randint(40,80),1]
                st.session_state.sim_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {sim_v} → Reset to nominal")
                st.rerun()
        st.markdown("**Simulation Log**")
        if st.session_state.sim_log:
            for entry in reversed(st.session_state.sim_log[-8:]):
                st.markdown(f'<div class="log-entry">{entry}</div>',unsafe_allow_html=True)
        else:
            st.caption("No events logged yet. Inject a fault above.")
    if show_tele:
        st.divider()
        st.markdown(f'<div class="section-title">24-Hour Telemetry — {sim_v}</div>',unsafe_allow_html=True)
        hist=gen_telemetry()
        fig_tele=make_subplots(rows=3,cols=1,shared_xaxes=True,
                               subplot_titles=["Speed (km/h)","Battery (%)","Brake Temp (°C)"],vertical_spacing=0.1)
        for i,(col,color) in enumerate(zip(["speed","battery","brake_temp"],["#007AFF","#34C759","#FF3B30"]),1):
            r_hex=color.lstrip('#')
            r_int=tuple(int(r_hex[j:j+2],16) for j in (0,2,4))
            fill_color=f"rgba({r_int[0]},{r_int[1]},{r_int[2]},0.07)"
            fig_tele.add_trace(go.Scatter(x=hist["time"],y=hist[col],mode="lines",
                line=dict(color=color,width=2),fill="tozeroy",fillcolor=fill_color),row=i,col=1)
        fig_tele.update_layout(height=380,showlegend=False,plot_bgcolor=PLOT_BG,paper_bgcolor=PAPER_BG,
                               font=dict(family=FONT,color=TICK_COLOR),margin=dict(t=30,b=20,l=10,r=10))
        for i in range(1,4):
            fig_tele.update_xaxes(showgrid=False,color=TICK_COLOR,row=i,col=1)
            fig_tele.update_yaxes(showgrid=True,gridcolor=GRID_COLOR,color=TICK_COLOR,row=i,col=1)
        st.plotly_chart(fig_tele,use_container_width=True)

# ══════════════════════════════════════════
#  TAB 5 — AI ASSISTANT
# ══════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="section-title">Aegis AI Assistant</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Ask anything about your fleet in plain English</div>',unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"]=="user":
            st.markdown(f'<div style="display:flex;justify-content:flex-end;"><div class="chat-user">{msg["text"]}</div></div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="display:flex;justify-content:flex-start;"><div class="chat-ai">🤖 {msg["text"]}</div></div>',unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)
    st.markdown("**Quick Questions**")
    qqs=["Which vehicle needs urgent attention?","Who is the safest driver?",
         "What is the fleet safety index?","How many have low battery?","Which need maintenance?"]
    qcols=st.columns(len(qqs))
    for i,(q,col) in enumerate(zip(qqs,qcols)):
        with col:
            if st.button(q,key=f"qq_{i}"):
                st.session_state.chat_history.append({"role":"user","text":q})
                st.session_state.chat_history.append({"role":"ai","text":fleet_ai_response(q,df)})
                st.rerun()
    user_input=st.text_input("Type your question...",placeholder="e.g. Which vehicle has the worst brake health?",key="chat_inp")
    cs,cc=st.columns([1,5])
    with cs:
        if st.button("Send ➤") and user_input.strip():
            st.session_state.chat_history.append({"role":"user","text":user_input})
            st.session_state.chat_history.append({"role":"ai","text":fleet_ai_response(user_input,df)})
            st.rerun()
    with cc:
        if st.button("🗑 Clear Chat"):
            st.session_state.chat_history=[{"role":"ai","text":"Hi! I'm Aegis AI. Ask me anything about your EV fleet."}]
            st.rerun()

# ══════════════════════════════════════════
#  TAB 6 — ANALYTICS
# ══════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="section-title">Fleet Analytics & Intelligence</div>',unsafe_allow_html=True)
    a1,a2=st.columns(2)
    with a1:
        status_counts=df["status"].value_counts().reset_index()
        status_counts.columns=["Status","Count"]
        fig_pie=px.pie(status_counts,values="Count",names="Status",hole=0.5,
                       color="Status",color_discrete_map={"Healthy":"#34C759","At Risk":"#FF9500","Critical":"#FF3B30","Emergency":"#AC1A14"})
        apple_layout(fig_pie,height=300,title="Fleet Status Distribution")
        st.plotly_chart(fig_pie,use_container_width=True)
    with a2:
        fig_scat=px.scatter(df,x="battery",y="safety_index",color="status",size="fail_prob",
                            hover_data=["vehicle_id","driver","model"],
                            color_discrete_map={"Healthy":"#34C759","At Risk":"#FF9500","Critical":"#FF3B30","Emergency":"#AC1A14"})
        apple_layout(fig_scat,height=300,title="Battery Level vs Safety Index")
        st.plotly_chart(fig_scat,use_container_width=True)
    a3,a4=st.columns(2)
    with a3:
        fig_hist_chart=px.histogram(df,x="safety_index",nbins=10,color_discrete_sequence=["#007AFF"])
        fig_hist_chart.add_vline(x=FSI,line_dash="dash",line_color="#34C759",
                                  annotation_text=f"Fleet Avg: {FSI}",annotation_font_color="#34C759",annotation_font_size=11)
        apple_layout(fig_hist_chart,height=280,title="Safety Score Distribution")
        st.plotly_chart(fig_hist_chart,use_container_width=True)
    with a4:
        fig_temp=go.Figure()
        fig_temp.add_trace(go.Scatter(x=df["vehicle_id"],y=df["brake_temp"],mode="lines+markers",name="Brake Temp",
                           line=dict(color="#FF3B30",width=2),marker=dict(size=6)))
        fig_temp.add_trace(go.Scatter(x=df["vehicle_id"],y=df["motor_temp"],mode="lines+markers",name="Motor Temp",
                           line=dict(color="#FF9500",width=2),marker=dict(size=6)))
        fig_temp.add_hline(y=200,line_dash="dot",line_color="rgba(255,59,48,0.45)",
                           annotation_text="Brake Limit",annotation_font_color="#FF3B30",annotation_font_size=10)
        fig_temp.add_hline(y=100,line_dash="dot",line_color="rgba(255,149,0,0.45)",
                           annotation_text="Motor Limit",annotation_font_color="#FF9500",annotation_font_size=10)
        apple_layout(fig_temp,height=280,title="Thermal Profile Across Fleet")
        st.plotly_chart(fig_temp,use_container_width=True)
    st.divider()
    st.markdown('<div class="section-title">Fleet Risk Pattern Detection</div>',unsafe_allow_html=True)
    brake_n  =df["faults"].apply(lambda x:any("Brake" in f for f in x)).sum()
    network_n=df["faults"].apply(lambda x:any("Network" in f for f in x)).sum()
    battery_n=df["faults"].apply(lambda x:any("Battery" in f for f in x)).sum()
    motor_n  =df["faults"].apply(lambda x:any("Motor" in f for f in x)).sum()
    rp1,rp2,rp3,rp4=st.columns(4)
    for col,label,count,thr in [(rp1,"🛞 Brake Risk",brake_n,3),(rp2,"📡 Network Risk",network_n,3),
                                 (rp3,"⚡ Battery Risk",battery_n,3),(rp4,"🌡 Thermal Risk",motor_n,3)]:
        with col:
            if count>=thr: st.error(f"**{label}**\n{count} vehicles affected")
            else:          st.success(f"**{label}**\n{count} affected — OK")

# ══════════════════════════════════════════
#  TAB 7 — JARVIS VOICE + GESTURE ASSISTANT
# ══════════════════════════════════════════
with tabs[6]:
    st.markdown('<div class="section-title">🤖 Jarvis — Voice & Gesture Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Choose your interaction mode — voice for general users, hand gestures for differently abled users</div>', unsafe_allow_html=True)

    # ── Mode Selector ──
    st.markdown("""
    <div style="display:flex;gap:12px;margin:16px 0 24px 0;flex-wrap:wrap;">
        <div style="font-size:0.78rem;font-weight:700;color:#8E8E93;align-self:center;text-transform:uppercase;letter-spacing:0.08em;">Select Mode:</div>
    </div>
    """, unsafe_allow_html=True)

    mode_col1, mode_col2, mode_col3 = st.columns([1, 1, 4])
    with mode_col1:
        general_btn = st.button("🎙️ General User", key="mode_general", use_container_width=True)
    with mode_col2:
        special_btn = st.button("🤟 Differently Abled", key="mode_special", use_container_width=True)

    if "jarvis_mode" not in st.session_state:
        st.session_state.jarvis_mode = "general"
    if general_btn:
        st.session_state.jarvis_mode = "general"
    if special_btn:
        st.session_state.jarvis_mode = "special"

    current_mode = st.session_state.jarvis_mode

    # mode pill indicator
    pill_color = "#007AFF" if current_mode == "general" else "#34C759"
    pill_label = "🎙️ General User — Voice Mode" if current_mode == "general" else "🤟 Differently Abled — Hand Gesture Mode"
    st.markdown(f"""
    <div style="display:inline-flex;align-items:center;gap:8px;background:rgba({('0,122,255' if current_mode=='general' else '52,199,89')},0.1);
        border:1px solid rgba({('0,122,255' if current_mode=='general' else '52,199,89')},0.3);
        border-radius:20px;padding:6px 16px;margin-bottom:20px;font-size:0.82rem;font-weight:700;color:{pill_color};">
        {pill_label}
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ═══════════════════════════════════════
    #  GENERAL MODE — Voice (existing)
    # ═══════════════════════════════════════
    if current_mode == "general":
        jarvis_commands=[
            ("Hello Jarvis","Auto full fleet briefing"),
            ("Fleet status","Overall health summary"),
            ("Which vehicle is critical?","Most dangerous vehicle"),
            ("Who is the best driver?","Top driver leaderboard"),
            ("Battery report","Low battery vehicles"),
            ("Maintenance alert","Overdue service vehicles"),
            ("Safety index","Current fleet safety score"),
            ("Failure risk","Highest breakdown probability"),
        ]

        jc1, jc2 = st.columns([1.2, 1])

        with jc1:
            st.components.v1.html(f"""
            <!DOCTYPE html><html><head>
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
            *{{box-sizing:border-box;margin:0;padding:0;}}
            body{{font-family:'Nunito',sans-serif;background:transparent;padding:8px 0;}}
            .jarvis-card{{background:rgba(255,255,255,0.92);border:1px solid rgba(0,0,0,0.08);border-radius:20px;padding:22px 20px;box-shadow:0 2px 20px rgba(0,0,0,0.07);}}
            .j-header{{display:flex;align-items:center;gap:12px;margin-bottom:18px;}}
            .j-robo{{width:48px;height:48px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#5AC8FA,#007AFF 60%,#003A99);box-shadow:0 0 0 4px rgba(0,122,255,0.12),0 3px 12px rgba(0,122,255,0.3);display:flex;align-items:center;justify-content:center;animation:jpulse 2.5s ease-in-out infinite;flex-shrink:0;}}
            @keyframes jpulse{{0%,100%{{box-shadow:0 0 0 4px rgba(0,122,255,0.12),0 3px 12px rgba(0,122,255,0.3);}}50%{{box-shadow:0 0 0 9px rgba(0,122,255,0.18),0 3px 22px rgba(0,122,255,0.45);}}}}
            .j-title{{font-weight:800;font-size:1rem;color:#1C1C1E;}}.j-sub{{font-size:0.72rem;color:#8E8E93;margin-top:1px;}}
            .touch-btn{{width:100%;padding:14px;border:none;border-radius:14px;cursor:pointer;font-family:'Nunito',sans-serif;font-weight:800;font-size:0.95rem;transition:all 0.2s;outline:none;background:linear-gradient(135deg,#007AFF,#0055CC);color:white;box-shadow:0 3px 14px rgba(0,122,255,0.35);display:flex;align-items:center;justify-content:center;gap:8px;}}
            .touch-btn:hover{{transform:translateY(-2px);box-shadow:0 5px 20px rgba(0,122,255,0.45);}}
            .touch-btn.listening{{background:linear-gradient(135deg,#34C759,#1A8A35);animation:lp 0.9s ease-in-out infinite;}}
            .touch-btn.speaking{{background:linear-gradient(135deg,#5AC8FA,#007AFF);}}
            @keyframes lp{{0%,100%{{opacity:1}}50%{{opacity:0.75}}}}
            .status-row{{display:flex;align-items:center;gap:8px;margin:12px 0;padding:8px 14px;background:#F2F2F7;border-radius:10px;}}
            .s-dot{{width:8px;height:8px;border-radius:50%;background:#C7C7CC;flex-shrink:0;}}
            .s-dot.on-listen{{background:#34C759;animation:dp 0.8s ease-in-out infinite;}}
            .s-dot.on-speak{{background:#007AFF;animation:dp 0.6s ease-in-out infinite;}}
            .s-dot.on-think{{background:#FF9500;animation:dp 1s ease-in-out infinite;}}
            @keyframes dp{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
            .s-label{{font-size:0.8rem;font-weight:600;color:#3A3A3C;}}
            #transcript-box{{background:rgba(0,122,255,0.04);border:1px solid rgba(0,122,255,0.14);border-radius:12px;padding:11px 14px;font-size:0.84rem;color:#3A3A3C;font-style:italic;margin:10px 0;min-height:42px;line-height:1.5;}}
            #response-box{{background:rgba(52,199,89,0.04);border:1px solid rgba(52,199,89,0.18);border-radius:12px;padding:13px 14px;font-size:0.86rem;color:#1C1C1E;font-weight:600;min-height:58px;line-height:1.6;margin:10px 0;}}
            .btn-row2{{display:flex;gap:8px;margin-top:10px;}}
            .mini-btn{{flex:1;padding:8px;border:1px solid #E5E5EA;border-radius:10px;background:#F2F2F7;color:#3A3A3C;font-family:'Nunito',sans-serif;font-weight:700;font-size:0.78rem;cursor:pointer;transition:all 0.18s;}}
            .mini-btn:hover{{background:#E5E5EA;}}.mini-btn.red{{color:#FF3B30;border-color:rgba(255,59,48,0.3);}}
            </style></head><body>
            <div class="jarvis-card">
              <div class="j-header">
                <div class="j-robo">
                  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="5" width="18" height="13" rx="3.5" fill="white" fill-opacity="0.95"/>
                    <circle cx="8.5" cy="10" r="2" fill="#007AFF"/><circle cx="9.2" cy="9.3" r="0.65" fill="white"/>
                    <circle cx="15.5" cy="10" r="2" fill="#007AFF"/><circle cx="16.2" cy="9.3" r="0.65" fill="white"/>
                    <rect x="9.5" y="13.5" width="5" height="1.2" rx="0.6" fill="#34C759"/>
                    <rect x="10.5" y="2.5" width="3" height="3" rx="1" fill="white" fill-opacity="0.7"/>
                    <rect x="0.5" y="9" width="2.5" height="1.5" rx="0.75" fill="white" fill-opacity="0.5"/>
                    <rect x="21" y="9" width="2.5" height="1.5" rx="0.75" fill="white" fill-opacity="0.5"/>
                  </svg>
                </div>
                <div>
                  <div class="j-title">Jarvis — Voice Intelligence</div>
                  <div class="j-sub">Touch to speak &nbsp;·&nbsp; "Hello Jarvis" for full fleet briefing</div>
                </div>
              </div>
              <button class="touch-btn" id="touchBtn" onclick="toggleListen()">
                <span id="btnIcon">🎙️</span><span id="btnText">Touch to Speak</span>
              </button>
              <div class="status-row"><div class="s-dot" id="sDot"></div><div class="s-label" id="sLabel">Ready, Sir</div></div>
              <div id="transcript-box">Your voice input will appear here...</div>
              <div id="response-box">Awaiting your command, Sir.</div>
              <div class="btn-row2">
                <button class="mini-btn red" onclick="stopSpeaking()">⏹ Stop</button>
                <button class="mini-btn" onclick="clearAll()">🗑 Clear</button>
                <button class="mini-btn" onclick="sayFleetBrief()">📊 Fleet Brief</button>
              </div>
            </div>
            <script>
            const synth=window.speechSynthesis;let recognition=null,isListening=false;
            const FSI={FSI};const N_HEALTHY={n_healthy},N_RISK={n_risk},N_CRITICAL={n_critical},N_EMERGENCY={n_emergency};
            const WORST_VEH="{df.loc[df['safety_index'].idxmin(),'vehicle_id']}";
            const BEST_DRV="{df.loc[df['driver_score'].idxmax(),'driver']}";
            const WORST_DRV="{df.loc[df['driver_score'].idxmin(),'driver']}";
            const LOW_BAT=`{', '.join(df[df['battery']<25]['vehicle_id'].tolist()) or 'None'}`;
            const OVERDUE=`{', '.join(df[df['last_service_days']>150]['vehicle_id'].tolist()) or 'None'}`;
            const HIGH_RISK_VEH="{df.loc[df['fail_prob'].idxmax(),'vehicle_id']}";
            const HIGH_RISK_PROB={round(df['fail_prob'].max(),1)};
            function getVoice(){{const vv=synth.getVoices();return vv.find(v=>v.name.includes('Daniel')||v.name.includes('Google UK')||v.name.includes('British'))||null;}}
            function speak(text,rate=0.9,pitch=0.82){{synth.cancel();const u=new SpeechSynthesisUtterance(text);u.rate=rate;u.pitch=pitch;u.volume=1.0;const v=getVoice();if(v)u.voice=v;u.onstart=()=>setStatus("Speaking...","on-speak");u.onend=()=>{{setStatus("Ready, Sir","");setBtn("idle");}};synth.speak(u);setBtn("speaking");}}
            function fleetBriefText(){{
              const cond=FSI>=80?"running at peak efficiency, Sir. Splendid.":FSI>=60?"showing moderate stress. I am watching closely.":"in quite a concerning state. Immediate attention advised, Sir.";
              let b=`Sir, here is your Aegis fleet briefing. Safety Index stands at ${{FSI}} out of 100. The fleet is ${{cond}} `;
              b+=`We have ${{N_HEALTHY}} healthy, ${{N_RISK}} at risk, ${{N_CRITICAL}} critical`;
              if(N_EMERGENCY>0)b+=`, and ${{N_EMERGENCY}} in emergency — which is frankly alarming`;b+=`. `;
              if(LOW_BAT!=='None')b+=`Vehicles ${{LOW_BAT}} have low battery. `;
              if(OVERDUE!=='None')b+=`${{OVERDUE}} overdue for service. `;
              b+=`Best driver is ${{BEST_DRV}}. ${{HIGH_RISK_VEH}} carries ${{HIGH_RISK_PROB}}% failure risk. That concludes your briefing, Sir.`;
              return b;
            }}
            function sayFleetBrief(){{const t=fleetBriefText();document.getElementById('response-box').innerText=t;speak(t,0.88,0.8);}}
            function processCommand(cmd){{
              setStatus("Processing...","on-think");let r='';
              if(cmd.match(/hello|hi jarvis|hey jarvis|good morning|good evening|jarvis/))r=fleetBriefText();
              else if(cmd.match(/fleet status|overall|fleet health/))r=fleetBriefText();
              else if(cmd.match(/critical|dangerous|worst vehicle|urgent/)){{const c=N_CRITICAL+N_EMERGENCY;r=c===0?"No critical vehicles, Sir.":`${{c}} vehicle${{c>1?'s are':' is'}} demanding attention. ${{WORST_VEH}} is the most concerning.`;}}
              else if(cmd.match(/emergency/))r=N_EMERGENCY===0?"No emergencies, Sir.":`${{N_EMERGENCY}} in emergency status. Act immediately, Sir!`;
              else if(cmd.match(/best driver|top driver|leaderboard/))r=`${{BEST_DRV}} leads the leaderboard, Sir. ${{WORST_DRV}} needs coaching.`;
              else if(cmd.match(/battery|charge|low power/))r=LOW_BAT==='None'?"All batteries adequate, Sir.":`Vehicles ${{LOW_BAT}} are low, Sir.`;
              else if(cmd.match(/maintenance|service|overdue/))r=OVERDUE==='None'?"All within service intervals.":`${{OVERDUE}} overdue for service.`;
              else if(cmd.match(/safety index|safety score/))r=`Fleet Safety Index is ${{FSI}} out of 100.`;
              else if(cmd.match(/failure|risk|breakdown/))r=`${{HIGH_RISK_VEH}} carries ${{HIGH_RISK_PROB}}% failure risk, Sir.`;
              else if(cmd.match(/thank/))r="You are most welcome, Sir.";
              else r="I did not catch that, Sir. Try: Hello Jarvis, Fleet status, Battery report, or Best driver.";
              document.getElementById('response-box').innerText=r;speak(r);
            }}
            function initRecognition(){{
              if(!('webkitSpeechRecognition' in window)&&!('SpeechRecognition' in window)){{setStatus("Voice not supported — use Chrome","");return null;}}
              const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
              const rec=new SR();rec.continuous=false;rec.interimResults=true;rec.lang='en-US';
              rec.onstart=()=>{{setStatus("Listening, Sir...","on-listen");setBtn("listening");}};
              rec.onresult=(e)=>{{let interim='',final='';for(let i=e.resultIndex;i<e.results.length;i++){{if(e.results[i].isFinal)final+=e.results[i][0].transcript;else interim+=e.results[i][0].transcript;}}document.getElementById('transcript-box').innerText=(final||interim)||'...';if(final)processCommand(final.toLowerCase().trim());}};
              rec.onerror=(e)=>{{setStatus("Error: "+e.error,"");resetBtn();}};rec.onend=()=>{{isListening=false;resetBtn();}};return rec;
            }}
            function toggleListen(){{if(isListening){{recognition.stop();return;}}recognition=initRecognition();if(!recognition)return;isListening=true;recognition.start();}}
            function setBtn(state){{const btn=document.getElementById('touchBtn'),icon=document.getElementById('btnIcon'),txt=document.getElementById('btnText');btn.className='touch-btn';if(state==='listening'){{btn.classList.add('listening');icon.innerText='🔴';txt.innerText='Listening...';}}else if(state==='speaking'){{btn.classList.add('speaking');icon.innerText='🔊';txt.innerText='Speaking...';}}else{{icon.innerText='🎙️';txt.innerText='Touch to Speak';}}}}
            function resetBtn(){{isListening=false;setBtn('idle');setStatus("Ready, Sir","");}}
            function stopSpeaking(){{synth.cancel();setStatus("Ready, Sir","");setBtn('idle');}}
            function clearAll(){{synth.cancel();document.getElementById('transcript-box').innerText='Your voice input will appear here...';document.getElementById('response-box').innerText='Awaiting your command, Sir.';setStatus("Ready, Sir","");setBtn('idle');}}
            function setStatus(msg,cls){{document.getElementById('sLabel').innerText=msg;const d=document.getElementById('sDot');d.className='s-dot'+(cls?' '+cls:'');}}
            speechSynthesis.onvoiceschanged=()=>speechSynthesis.getVoices();
            </script></body></html>
            """, height=440)

        with jc2:
            st.markdown("""<div class="apple-card" style="margin-bottom:12px;">
                <div style="font-size:0.68rem;font-weight:700;color:#8E8E93;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">🎙️ Voice Commands</div>
            """, unsafe_allow_html=True)
            for cmd, desc in jarvis_commands:
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #F2F2F7;">
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#1C1C1E;">"{cmd}"</div>
                        <div style="font-size:0.72rem;color:#8E8E93;margin-top:1px;">{desc}</div>
                    </div>
                    <div style="font-size:0.7rem;background:rgba(0,122,255,0.08);color:#007AFF;padding:3px 9px;border-radius:8px;font-weight:600;white-space:nowrap;margin-left:8px;">Say it</div>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="apple-card">
                <div style="font-size:0.68rem;font-weight:700;color:#8E8E93;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">⚡ Live Fleet Briefing</div>
                <div style="font-size:0.82rem;color:#3A3A3C;line-height:1.8;">
                    <div>🚗 <b>Fleet:</b> {len(df)} vehicles online</div>
                    <div>📊 <b>Safety Index:</b> <span style="color:{fsi_color};font-weight:700;">{FSI}/100</span></div>
                    <div>✅ <b>Healthy:</b> {n_healthy} &nbsp;|&nbsp; ⚠️ <b>At Risk:</b> {n_risk}</div>
                    <div>🔴 <b>Critical:</b> {n_critical} &nbsp;|&nbsp; 🆘 <b>Emergency:</b> {n_emergency}</div>
                    <div>🏆 <b>Best Driver:</b> {df.loc[df['driver_score'].idxmax(),'driver']}</div>
                    <div>⚡ <b>Low Battery:</b> {len(df[df['battery']<25])} vehicle(s)</div>
                    <div>🔧 <b>Overdue Service:</b> {len(df[df['last_service_days']>150])} vehicle(s)</div>
                </div>
            </div>
            <div class="apple-card" style="margin-top:0;">
                <div style="font-size:0.68rem;font-weight:700;color:#8E8E93;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">ℹ️ How It Works</div>
                <div style="font-size:0.77rem;color:#8E8E93;line-height:1.7;">
                    • Touch the button and speak your command<br>
                    • Say <b style="color:#007AFF;">"Hello Jarvis"</b> for full auto briefing<br>
                    • <b>No API keys</b> — works on any device<br>
                    • Responses spoken aloud in Jarvis voice<br>
                    • Works best in <b>Chrome or Edge</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ═══════════════════════════════════════
    #  SPECIAL MODE — Hand Gesture (Pure OpenCV, no mediapipe solutions needed)
    # ═══════════════════════════════════════
    else:
        import cv2

        gc1, gc2 = st.columns([1.3, 1])

        with gc1:
            st.markdown("""
            <div class="apple-card" style="margin-bottom:16px;">
              <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
                <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#34C759,#1A8A35);
                    display:flex;align-items:center;justify-content:center;font-size:1.5rem;
                    box-shadow:0 0 0 4px rgba(52,199,89,0.15),0 3px 12px rgba(52,199,89,0.3);">🤟</div>
                <div>
                  <div style="font-weight:800;font-size:1rem;color:#1C1C1E;">Hand Gesture Control</div>
                  <div style="font-size:0.72rem;color:#8E8E93;margin-top:1px;">Camera-based · No speech needed · Pure OpenCV finger detection</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Pure OpenCV finger counting — skin color + convex hull ──
            # No mediapipe, no model file, works on ANY version installed
            def get_skin_mask(frame):
                hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                ycr  = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
                m1 = cv2.inRange(hsv, (0,15,60),  (20,170,255))
                m2 = cv2.inRange(ycr, (0,133,77), (255,173,127))
                mask = cv2.bitwise_and(m1, m2)
                k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k, iterations=2)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=3)
                mask = cv2.GaussianBlur(mask, (5,5), 0)
                return mask

            def count_fingers_opencv(frame):
                """Returns (finger_count, annotated_frame, found_hand)"""
                h, w = frame.shape[:2]
                # Focus on right side of frame (where hand usually is)
                roi = frame[60:h-20, w//4:]
                mask = get_skin_mask(roi)
                cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if not cnts:
                    return 0, frame, False
                cnt = max(cnts, key=cv2.contourArea)
                if cv2.contourArea(cnt) < 4000:
                    return 0, frame, False
                # Draw contour on frame
                cnt_shifted = cnt + np.array([w//4, 60])
                cv2.drawContours(frame, [cnt_shifted], -1, (0,122,255), 2)
                # Convex hull + defects for finger counting
                hull_idx = cv2.convexHull(cnt, returnPoints=False)
                if hull_idx is None or len(hull_idx) < 3:
                    return 0, frame, True
                try:
                    defects = cv2.convexityDefects(cnt, hull_idx)
                except:
                    return 0, frame, True
                if defects is None:
                    return 1, frame, True
                finger_count = 1
                for i in range(defects.shape[0]):
                    s,e,f,d = defects[i,0]
                    start  = tuple(cnt[s][0] + np.array([w//4, 60]))
                    end    = tuple(cnt[e][0] + np.array([w//4, 60]))
                    far    = tuple(cnt[f][0] + np.array([w//4, 60]))
                    # Angle at defect point
                    a = np.array(start, dtype=float) - np.array(far, dtype=float)
                    b = np.array(end,   dtype=float) - np.array(far, dtype=float)
                    angle = np.degrees(np.arccos(
                        np.clip(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-6), -1, 1)
                    ))
                    # Valid finger gap: angle < 90°, defect depth > threshold
                    if angle < 88 and d > 8000:
                        finger_count += 1
                        cv2.circle(frame, far,   6, (255,100,0), -1)
                        cv2.circle(frame, start, 4, (52,199,89), -1)
                        cv2.circle(frame, end,   4, (52,199,89), -1)
                finger_count = min(finger_count, 5)
                return finger_count, frame, True

            def classify_by_count(n):
                if n == 0: return "fist",  "✊ Fist (0)",        "Stop / Clear"
                if n == 1: return "one",   "☝️ 1 Finger",       "Emergency Alert"
                if n == 2: return "two",   "✌️ 2 Fingers",      "Battery Report"
                if n == 3: return "three", "🤟 3 Fingers",       "Best Driver"
                if n == 4: return "four",  "🖖 4 Fingers",       "Maintenance Alert"
                if n == 5: return "open",  "✋ Open Hand (5)",   "Fleet Status Briefing"
                return "unknown","🖐 Other","Unrecognised"

            _low_bat_str = ', '.join(df[df['battery']<25]['vehicle_id'].tolist()) or 'None'
            _overdue_str = ', '.join(df[df['last_service_days']>150]['vehicle_id'].tolist()) or 'None'
            _best_drv_g  = df.loc[df['driver_score'].idxmax(),'driver']

            def get_response(key):
                return {
                    "open":  f"Fleet briefing: Safety Index {FSI}/100. {n_healthy} healthy, {n_risk} at risk, {n_critical} critical, {n_emergency} emergency.",
                    "one":   f"EMERGENCY! {n_emergency} vehicle(s) need immediate help!" if n_emergency>0 else "No emergencies right now, Sir.",
                    "two":   f"Low battery vehicles: {_low_bat_str}." if _low_bat_str!='None' else "All batteries adequate, Sir.",
                    "three": f"{_best_drv_g} leads the driver leaderboard, Sir.",
                    "four":  f"Overdue service: {_overdue_str}." if _overdue_str!='None' else "All vehicles within service intervals.",
                    "fist":  "Display cleared, Sir.",
                }.get(key, "Gesture not recognised, Sir.")

            # ── Camera controls ──
            if "gesture_running" not in st.session_state: st.session_state.gesture_running = False
            if "gesture_result"  not in st.session_state: st.session_state.gesture_result  = None

            cam_col1, cam_col2 = st.columns(2)
            with cam_col1:
                if st.button("📷 Turn Camera ON",  key="cam_on",  use_container_width=True):
                    st.session_state.gesture_running = True
                    st.session_state.gesture_result  = None
            with cam_col2:
                if st.button("⏹ Turn Camera OFF", key="cam_off", use_container_width=True):
                    st.session_state.gesture_running = False

            cam_status = "🟢 Camera Active — Show your hand in good light" if st.session_state.gesture_running else "⚫ Camera Off — Press Turn Camera ON"
            st.markdown(f'<div style="background:#F2F2F7;border-radius:10px;padding:10px 16px;margin:10px 0;font-size:0.82rem;font-weight:600;color:#3A3A3C;">{cam_status}</div>', unsafe_allow_html=True)

            FRAME_WINDOW     = st.empty()
            gesture_display  = st.empty()
            response_display = st.empty()

            if st.session_state.gesture_running:
                cap = cv2.VideoCapture(0)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
                hold_counts    = {}
                CONFIRM_FRAMES = 20
                last_confirmed = None
                frame_count    = 0
                try:
                    while st.session_state.gesture_running and frame_count < 500:
                        ret, frame = cap.read()
                        if not ret: break
                        frame = cv2.flip(frame, 1)

                        n_fingers, frame, found = count_fingers_opencv(frame)
                        gkey, glabel, gaction = classify_by_count(n_fingers) if found else ("unknown","No hand detected","—")

                        if found and gkey != "unknown":
                            hold_counts[gkey] = hold_counts.get(gkey, 0) + 1
                            for k in list(hold_counts):
                                if k != gkey: hold_counts[k] = 0
                            pct = min(int(hold_counts[gkey] / CONFIRM_FRAMES * 100), 100)
                        else:
                            hold_counts = {}
                            pct = 0

                        # Draw HUD overlay
                        ov = frame.copy()
                        cv2.rectangle(ov, (0,0), (frame.shape[1], 76), (20,20,24), -1)
                        cv2.addWeighted(ov, 0.72, frame, 0.28, 0, frame)
                        cv2.putText(frame, f"{glabel}  ->  {gaction}", (10,27), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,255), 2)
                        bw = int((frame.shape[1]-20) * pct / 100)
                        cv2.rectangle(frame, (10,40), (10+bw, 56), (52,199,89), -1)
                        cv2.rectangle(frame, (10,40), (frame.shape[1]-10, 56), (80,80,80), 1)
                        cv2.putText(frame, f"Hold: {pct}%", (10,72), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180,180,180), 1)
                        cv2.putText(frame, f"Fingers: {n_fingers}", (frame.shape[1]-130,27), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,200,0), 2)

                        # Confirm gesture when held long enough
                        if found and hold_counts.get(gkey,0) >= CONFIRM_FRAMES and gkey != last_confirmed and gkey != "unknown":
                            last_confirmed = gkey
                            st.session_state.gesture_result = {
                                "key": gkey, "label": glabel,
                                "action": gaction, "response": get_response(gkey)
                            }
                            hold_counts = {}

                        FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

                        if st.session_state.gesture_result:
                            r = st.session_state.gesture_result
                            gesture_display.markdown(
                                f'<div style="background:rgba(52,199,89,0.08);border:1px solid rgba(52,199,89,0.25);border-radius:12px;padding:10px 14px;margin:8px 0;">'
                                f'<b style="color:#1A7A33;">✅ Confirmed: {r["label"]}</b><br>'
                                f'<span style="font-size:0.78rem;color:#3A3A3C;">{r["action"]}</span></div>',
                                unsafe_allow_html=True)
                            response_display.markdown(
                                f'<div style="background:rgba(0,122,255,0.05);border:1px solid rgba(0,122,255,0.18);border-radius:12px;padding:12px 14px;font-size:0.86rem;font-weight:600;color:#1C1C1E;">'
                                f'🤖 {r["response"]}</div>',
                                unsafe_allow_html=True)
                        frame_count += 1

                except Exception as cam_err:
                    st.error(f"Camera error: {cam_err}")
                finally:
                    cap.release()
                st.session_state.gesture_running = False
                st.rerun()

            elif st.session_state.gesture_result:
                r = st.session_state.gesture_result
                gesture_display.markdown(
                    f'<div style="background:rgba(52,199,89,0.08);border:1px solid rgba(52,199,89,0.25);border-radius:12px;padding:10px 14px;margin:8px 0;">'
                    f'<b style="color:#1A7A33;">✅ Last Gesture: {r["label"]}</b><br>'
                    f'<span style="font-size:0.78rem;color:#3A3A3C;">{r["action"]}</span></div>',
                    unsafe_allow_html=True)
                response_display.markdown(
                    f'<div style="background:rgba(0,122,255,0.05);border:1px solid rgba(0,122,255,0.18);border-radius:12px;padding:12px 14px;font-size:0.86rem;font-weight:600;color:#1C1C1E;">'
                    f'🤖 {r["response"]}</div>',
                    unsafe_allow_html=True)

        with gc2:
            st.markdown("""
            <div class="apple-card" style="margin-bottom:12px;">
              <div style="font-size:0.68rem;font-weight:700;color:#8E8E93;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">🤟 Gesture Commands</div>
            """, unsafe_allow_html=True)
            gestures = [
                ("✋", "Open Hand (5 fingers)", "Fleet Status Briefing", "#007AFF"),
                ("☝️", "One Finger (index)", "Emergency Alert", "#FF3B30"),
                ("✌️", "Two Fingers", "Battery Report", "#FF9500"),
                ("🤟", "Three Fingers", "Best Driver", "#34C759"),
                ("🖖", "Four Fingers", "Maintenance Alert", "#007AFF"),
                ("🤙", "Shaka (thumb + pinky)", "Safety Index", "#5AC8FA"),
                ("✊", "Fist (0 fingers)", "Stop / Clear", "#8E8E93"),
            ]
            for icon, label, action, color in gestures:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid #F2F2F7;">
                    <div style="font-size:1.4rem;min-width:32px;text-align:center;">{icon}</div>
                    <div style="flex:1;">
                        <div style="font-size:0.82rem;font-weight:700;color:#1C1C1E;">{label}</div>
                        <div style="font-size:0.72rem;color:#8E8E93;margin-top:1px;">{action}</div>
                    </div>
                    <div style="font-size:0.68rem;background:rgba(0,0,0,0.04);color:{color};
                        padding:3px 8px;border-radius:8px;font-weight:700;white-space:nowrap;
                        border:1px solid rgba(0,0,0,0.06);">Hold 1s</div>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="apple-card">
              <div style="font-size:0.68rem;font-weight:700;color:#8E8E93;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px;">⚡ Live Fleet Status</div>
              <div style="font-size:0.82rem;color:#3A3A3C;line-height:1.8;">
                <div>🚗 <b>Fleet:</b> {len(df)} vehicles</div>
                <div>📊 <b>Safety Index:</b> <span style="color:{fsi_color};font-weight:700;">{FSI}/100</span></div>
                <div>✅ {n_healthy} Healthy &nbsp;|&nbsp; ⚠️ {n_risk} At Risk</div>
                <div>🔴 {n_critical} Critical &nbsp;|&nbsp; 🆘 {n_emergency} Emergency</div>
              </div>
            </div>
            <div class="apple-card" style="margin-top:0;">
              <div style="font-size:0.68rem;font-weight:700;color:#8E8E93;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">ℹ️ How to Use</div>
              <div style="font-size:0.77rem;color:#8E8E93;line-height:1.8;">
                1. Click <b style="color:#34C759;">Turn Camera ON</b><br>
                2. Hold your hand clearly in front of camera<br>
                3. <b>Hold the gesture for ~1 second</b> to confirm<br>
                4. Jarvis reads the result aloud<br>
                5. Works with <b>MediaPipe + OpenCV</b><br>
                6. No ML training — pure hand landmark detection
              </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FOOTER  (FIX 3: 2026)
# ─────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center;padding:16px 0 8px;color:#C7C7CC;font-size:0.75rem;font-weight:500;letter-spacing:0.04em;">
    Aegis · EV Safety Intelligence Platform &nbsp;·&nbsp; VIT Smart Mobility Competition 2026 &nbsp;·&nbsp; Team Aegis
</div>
""", unsafe_allow_html=True)