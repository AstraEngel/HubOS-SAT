import time

import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="ReVora | HubOS-Sat Mission Intelligence", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")

# Strong contrast across Streamlit's built-in controls and the custom dashboard.
st.markdown("""<style>
:root { color-scheme: dark; }
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stSidebar"], [data-testid="stBottom"], [data-testid="stMain"] {
 background:#07111f !important; color:#edf5ff !important;
}
[data-testid="stSidebar"] {background:#101f31 !important;border-right:1px solid #30465d;}
.stApp p,.stApp span,.stApp label,.stApp small,.stApp li,.stApp h1,.stApp h2,.stApp h3,
.stApp h4,.stApp strong,[data-testid="stWidgetLabel"] *,[data-testid="stMarkdownContainer"] *,
[data-testid="stCaptionContainer"] *,[data-testid="stMetricLabel"] *,[data-testid="stMetricValue"] *,
[data-testid="stMetricDelta"] *,[data-testid="stSlider"] *,[data-testid="stToggle"] * {
 color:#edf5ff !important; opacity:1 !important;
}
[data-testid="stCaptionContainer"] *, .stApp .subtle {color:#b9d0e8 !important;}
[data-testid="stMetric"] {background:#12263b!important;border:1px solid #395672;border-radius:12px;padding:12px;}
[data-testid="stMetricLabel"] p{font-size:14px!important;font-weight:700!important;}
[data-testid="stMetricValue"] {color:#fff!important;}
[data-baseweb="select"]>div,[data-baseweb="popover"]>div,[role="listbox"],
[data-baseweb="input"]>div {background:#12263b!important;color:#fff!important;border-color:#42617d!important;}
[data-baseweb="select"] span,[role="option"] span,[role="listbox"] * {color:#f6faff!important;}
button[data-baseweb="tab"] {color:#d5e8fa!important;background:#101f31!important;border-radius:6px 6px 0 0;}
button[data-baseweb="tab"][aria-selected="true"] {color:#76f8dc!important;border-bottom:2px solid #3ce0c5!important;}
.stButton>button {background:#174b5c!important;color:#fff!important;border:1px solid #51a9b3!important;}
.stButton>button *{color:#fff!important;}
.stButton>button:hover{background:#206477!important;}
[data-testid="stAlert"] {background:#162b40!important;border:1px solid #466987!important;}
[data-testid="stAlert"] *{color:#f6faff!important;}
[data-testid="stExpander"] {background:#12263b!important;border:1px solid #42617d!important;}
[data-testid="stDataFrame"], [data-testid="stTable"] {background:#12263b!important;}
hr{border-color:#39516a!important;}
.hero {padding:21px 24px;border:1px solid #35647b;border-radius:15px;background:linear-gradient(110deg,#112f48,#0b2033);margin-bottom:10px;}
.kicker {font-size:11px;letter-spacing:2px;font-weight:800;color:#6ff0d6!important;}
.hero-title {font-size:30px;font-weight:800;color:white!important;margin:3px 0;}
.hero-sub{color:#d1e5f6!important;font-size:14px;}
.pill {display:inline-block;border-radius:20px;padding:5px 11px;font-size:12px;font-weight:800;border:1px solid #47748b;background:#152e46;color:#e9faff!important;}
.pill.good{background:#123b39;border-color:#249e86;color:#8ff7dc!important;}
.pill.warn{background:#45331d;border-color:#dba047;color:#ffe0a8!important;}
.pill.bad{background:#4b202d;border-color:#e37580;color:#ffd1d8!important;}
.panel {background:#10243a;border:1px solid #35536f;border-radius:12px;padding:14px 17px;margin-bottom:10px;}
.panel h4 {margin:0 0 7px;color:#fff!important;}
.panel p{color:#d8e9f8!important;margin:4px 0;font-size:13px;}
.mini {font-size:11px;color:#a9c3da!important;letter-spacing:.6px;}
.big {font-size:24px;font-weight:800;color:#fff!important;}
.log {font-family:monospace;font-size:12px;padding:9px 10px;margin-bottom:5px;background:#0a1b2c;border-left:3px solid #39b5ad;color:#e2f5ff!important;border-radius:4px;}
.flow {text-align:center;background:#132c44;border:1px solid #3d6781;border-radius:10px;padding:15px 8px;min-height:120px;}
.flow strong{display:block;color:#fff!important;font-size:15px;}
.flow small{color:#c1d6e8!important;font-size:12px;}
</style>""",unsafe_allow_html=True)

st.markdown("""<div class="hero"><div class="kicker">REVORA SPACE HUB · DOHA / QATAR · TECHNOLOGY CONCEPT</div>
<div class="hero-title">HubOS-Sat &nbsp; / &nbsp; Mission Intelligence</div>
<div class="hero-sub">Live engineering-style simulator for an Es’hailSat partnership discussion · Sovereign software development pathway</div></div>""",unsafe_allow_html=True)
st.caption("SYNTHETIC DATA ONLY · Fictional GEO communications platform · Illustrative models and alert rules · No connection to Es’hailSat systems · No onboard software or command authority")

DEFAULTS = {"tick": 0, "running": False, "thermal": 33.0, "soc": 86.0, "voltage": 28.2, "link": 11.8, "rf": 95.0, "history": [], "events": [], "last_wall": time.monotonic(), "last_alert": "", "playback": 1}
for k,v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v.copy() if isinstance(v,list) else v

with st.sidebar:
    st.markdown("### Mission controls")
    st.caption("Move controls during playback. Responses are calculated from the synthetic system model.")
    thermal_load = st.slider("Equipment heat load (W)", 40, 150, 60, 5)
    cooling = st.slider("Cooling effectiveness (%)", 20, 100, 85, 5)
    generation = st.slider("Solar power supply (W)", 250, 750, 550, 25)
    demand = st.slider("Electrical demand (W)", 250, 750, 470, 25)
    rain = st.slider("Ground terminal rain fade (dB)", 0.0, 12.0, 0.0, 0.5)
    st.divider()
    a,b=st.columns(2)
    if a.button("▶ Start / ❚❚ Pause",use_container_width=True):
        st.session_state.running=not st.session_state.running
        st.session_state.last_wall=time.monotonic()
    if b.button("↺ Reset",use_container_width=True):
        for k,v in DEFAULTS.items():
            st.session_state[k]=v.copy() if isinstance(v,list) else v
        st.rerun()
    speed = st.select_slider("Simulation speed",options=[1,2,5],value=1,format_func=lambda v:f"{v} simulated min / second")
    st.markdown("**Presentation suggestions**")
    st.markdown("1. Start with default settings.\n\n2. Increase heat load to **140 W**.\n\n3. Reduce solar power to **300 W**.\n\n4. Increase rain fade to **8 dB**.")
    st.caption("The simplified models are educational. Satellite requirements and response times are NOT calibrated to a real spacecraft.")

# A small, transparent demonstration model, not satellite flight dynamics.
def advance_step():
    s=st.session_state
    t=s.tick
    # First-order thermal relaxation with tunable load/cooling; stable at typical slider settings.
    target=23.0 + 0.22*thermal_load + 15.0*(1.0-cooling/100.0)
    s.thermal += 0.11*(target-s.thermal)
    net_power=generation-demand
    s.soc=float(np.clip(s.soc + net_power/450.0, 0,100))
    # Construct bus voltage as a bounded, illustrative function of charge and net power.
    v_target=26.2+0.023*s.soc+0.002*net_power
    s.voltage += 0.22*(v_target-s.voltage)
    # Rain fade impacts a downlink margin, not spacecraft onboard telemetry itself.
    target_link=11.8-rain
    s.link += 0.23*(target_link-s.link)
    # Secondary simulated RF-system health index.
    target_rf=95.0-max(0,42-s.link*3)*0.32
    s.rf += 0.12*(target_rf-s.rf)
    s.tick += 1
    s.history.append({"minute":s.tick,"temperature":s.thermal,"temp_expected":36.0,
                      "soc":s.soc,"voltage":s.voltage,"margin":s.link,"margin_expected":11.8,
                      "rf":s.rf})
    s.history=s.history[-100:]
    alerts=[]
    if s.thermal>=45: alerts.append("THERMAL TREND")
    if s.soc<30: alerts.append("LOW ENERGY RESERVE")
    if s.link<4: alerts.append("LINK MARGIN DEGRADATION")
    status=" / ".join(alerts) if alerts else "ALL PARAMETERS WITHIN DEMO LIMITS"
    if status != s.last_alert:
        s.events.insert(0,(s.tick,status))
        s.events=s.events[:20]
        s.last_alert=status

# Seed with synthetic normal telemetry so charts have useful context before Start.
if not st.session_state.history:
    for _ in range(18): advance_step()


def graph(df,fields,title,units,limit=None):
    fig=go.Figure()
    palette=["#56e1d0","#65adff","#ffc47a"]
    for i,(field,label) in enumerate(fields):
        fig.add_trace(go.Scatter(x=df.minute,y=df[field],mode="lines",name=label,
                    line=dict(color=palette[i%len(palette)],width=3 if i==0 else 2,
                              dash="solid" if i==0 else "dot"),
                    hovertemplate="Minute %{x}<br>%{y:.2f} "+units+"<extra>"+label+"</extra>"))
    if limit is not None:
        fig.add_hline(y=limit,line_dash="dash",line_color="#f6a95e",
                      annotation_text="Illustrative limit",annotation_font_color="#ffd49c")
    fig.update_layout(title=dict(text=title,font=dict(color="#f3faff",size=14)),
        paper_bgcolor="#10243a",plot_bgcolor="#10243a",font=dict(color="#eaf5ff",size=11),height=260,
        margin=dict(l=35,r=15,t=42,b=22),legend=dict(orientation="h",y=1.12,x=0,font=dict(color="#d9edff")),
        xaxis=dict(title="Simulated minute",gridcolor="#2b4660",zeroline=False),
        yaxis=dict(title=units,gridcolor="#2b4660",zeroline=False),
        hovermode="x unified")
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

@st.fragment(run_every="1s")
def live_dashboard():
    s=st.session_state
    now=time.monotonic()
    if s.running:
        # One simulation step per rendered second, with adjustable speed.
        for _ in range(speed): advance_step()
    s.last_wall=now
    thermal_alert=s.thermal>=45
    energy_alert=s.soc<30
    link_alert=s.link<4
    alert_count=sum([thermal_alert,energy_alert,link_alert])
    state="ATTENTION" if alert_count else "NOMINAL"
    pill="bad" if alert_count>1 else "warn" if alert_count==1 else "good"
    st.markdown(f'<span class="pill {pill}">● {state}</span> &nbsp; '
                f'<span class="pill">MISSION ELAPSED T+{s.tick:05d} MIN</span> &nbsp; '
                f'<span class="pill">{"LIVE SIMULATION" if s.running else "PAUSED"}</span> &nbsp; '
                f'<span class="pill">READ-ONLY CONCEPT · HUMAN DECISIONS</span>',unsafe_allow_html=True)
    st.write("")
    cols=st.columns(6)
    entries=[("THERMAL SENSOR",f"{s.thermal:.1f} °C",thermal_alert),
             ("BUS VOLTAGE",f"{s.voltage:.2f} V",False),
             ("BATTERY CHARGE",f"{s.soc:.1f}%",energy_alert),
             ("LINK MARGIN",f"{s.link:.1f} dB",link_alert),
             ("RF HEALTH INDEX",f"{s.rf:.0f}/100",False),
             ("ACTIVE RULE ALERTS",str(alert_count),bool(alert_count))]
    for col,(lab,value,is_bad) in zip(cols,entries):
        with col:
            st.markdown(f'<div class="panel"><div class="mini">{lab}</div>'
                        f'<div class="big">{value}</div>'
                        f'<span class="pill {"warn" if is_bad else "good"}">'
                        f'{"REVIEW" if is_bad else "MONITORED"}</span></div>',unsafe_allow_html=True)
    tab1,tab2,tab3=st.tabs(["MISSION CONSOLE","INTELLIGENCE & DIGITAL TWIN","PARTNERSHIP / INTEGRATION"])
    import pandas as pd
    frame=pd.DataFrame(s.history)
    with tab1:
        l,r=st.columns([1.65,1])
        with l:
            graph(frame,[("temperature","Observed model"),("temp_expected","Expected baseline")],"THERMAL | Actual model vs expected", "°C",45)
            graph(frame,[("margin","Calculated margin"),("margin_expected","Expected baseline")],"GROUND LINK | Rain fade response", "dB",4)
        with r:
            st.markdown("#### Subsystem states")
            statuses=[("SPACECRAFT THERMAL",thermal_alert),("ELECTRICAL POWER",energy_alert),
                     ("DOWNLINK / GROUND SEGMENT",link_alert),("OPERATIONAL CONTROL",False)]
            for lab,bad in statuses:
                st.markdown(f'<div class="panel"><span class="mini">{lab}</span> &nbsp; '
                            f'<span class="pill {"warn" if bad else "good"}">'
                            f'{"INVESTIGATE" if bad else "NOMINAL"}</span></div>',unsafe_allow_html=True)
            st.markdown("#### Mission event feed")
            if s.events:
                for minute,msg in s.events[:6]:
                    st.markdown(f'<div class="log">T+{minute:05d} | {msg}</div>',unsafe_allow_html=True)
            else:
                st.markdown('<div class="log">No rule transitions yet. Change controls while running.</div>',unsafe_allow_html=True)
        a,b=st.columns(2)
        with a:graph(frame,[("soc","Battery charge")],"POWER | Stored energy model","%",30)
        with b:graph(frame,[("voltage","Bus voltage")],"POWER | Bus response","V")
    with tab2:
        a,b=st.columns([1,1])
        with a:
            st.markdown("### Model-to-telemetry comparison")
            diff=s.thermal-36.0
            margin_dev=s.link-11.8
            st.metric("Thermal deviation from reference",f"{diff:+.1f} °C")
            st.metric("Ground-link margin deviation",f"{margin_dev:+.1f} dB")
            st.markdown('<div class="panel"><h4>Digital-twin concept</h4><p>Reference curves are illustrative benchmarks. A future validated twin would use spacecraft-specific engineering models, calibration data and operator-approved telemetry.</p></div>',unsafe_allow_html=True)
        with b:
            st.markdown("### Cross-system investigation")
            if thermal_alert:
                conclusion="THERMAL: inspect heater states, equipment modes and correlated power trends."
            elif link_alert:
                conclusion="LINK: inspect ground weather, antenna pointing and RF equipment metrics."
            elif energy_alert:
                conclusion="POWER: review net electrical load, generation and reserve trends."
            else:
                conclusion="No demo limits exceeded; continue trend monitoring and compare against reference behaviour."
            st.markdown(f'<div class="panel"><h4>Rule-based assessment</h4><p>{conclusion}</p><p>Operator action: review evidence; no autonomous spacecraft command is generated.</p></div>',unsafe_allow_html=True)
            st.markdown('<div class="panel"><h4>Proposed differentiator</h4><p>Combine historical telemetry, spacecraft engineering models and ground-segment conditions to investigate cross-system patterns. Measure any benefit against Es’hailSat’s existing operations tools in a controlled pilot.</p></div>',unsafe_allow_html=True)
            st.caption("No machine-learning model is trained or validated in this demo; no fault probabilities or confidence percentages are claimed.")
    with tab3:
        st.markdown("### Designed to complement existing Es’hailSat operations")
        c1,c2,c3=st.columns(3)
        for c,hd,sub in [(c1,"ES’HAILSAT SYSTEMS","Current TT&C, telemetry archives and ground operations"),
                         (c2,"SECURE DATA INTERFACE","Operator-approved filtered, read-only export into isolated test environment"),
                         (c3,"REVORA HUBOS-SAT","Proposed cross-system analytics, digital-twin comparison and operator decision support")]:
            with c:st.markdown(f'<div class="flow"><strong>{hd}</strong><small>{sub}</small></div>',unsafe_allow_html=True)
        st.markdown("### Credible next steps")
        st.markdown("**1.** Select an operational problem not adequately addressed by existing tools.  \n**2.** Agree a secure dataset, governance and evaluation criteria.  \\n**3.** Build an isolated proof of concept in Qatar.  \\n**4.** Benchmark accuracy, false alarms, engineering usefulness and security.  \\n**5.** Discuss licensing, local IP and broader cooperation if value is demonstrated.")
        st.markdown('<div class="panel"><h4>Technical boundary</h4><p>This simulator does not use operational data and is not connected to satellite or ground networks. Any real-data integration must be approved and tested with Es’hailSat engineers and cybersecurity teams.</p></div>',unsafe_allow_html=True)

live_dashboard()
st.divider()
st.caption("REVORA / HUBOS-SAT · Concept demonstrator only · All parameters, limits, and telemetry are synthetic. This is not a satellite qualification, a validated digital twin, or evidence of integration with Es’hailSat.")
