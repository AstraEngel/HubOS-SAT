"""ReVora HubOS-Sat | Es'hailSat-context GEO Communications Intelligence DEMO.
All telemetry is synthetic, fictional and not calibrated to Es'hailSat spacecraft.
"""
import math
import time
from collections import deque
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title="ReVora | HubOS-Sat GEO Intelligence", page_icon="🛰️", layout="wide", initial_sidebar_state="expanded")

# Explicitly style common Streamlit components: no light panels with light text.
st.markdown('''<style>
:root {color-scheme:dark}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stSidebar"], [data-testid="stBottom"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"] {background:#071321 !important;color:#e8f3ff !important;}
.stApp, .stApp * {font-family:Inter, system-ui, -apple-system, "Segoe UI", sans-serif;}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp label,
.stApp span,.stApp small, .stApp li {color:#e8f3ff;}
[data-testid="stWidgetLabel"] p, [data-testid="stMetricLabel"] *,
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] *,
[data-testid="stMetricValue"], [data-testid="stMetricDelta"] *,
[data-testid="stCaptionContainer"] * {color:#ecf6ff !important;opacity:1 !important;}
[data-testid="stMetric"] {background:#10263b !important;border:1px solid #355775 !important;border-radius:12px;padding:13px 14px;}
[data-testid="stMetricLabel"] {font-weight:750 !important;}
[data-testid="stMarkdownContainer"] {color:#e8f3ff !important;}
[data-baseweb="select"] > div, [data-baseweb="popover"] > div,
[data-baseweb="menu"], [data-baseweb="input"] > div,
[data-baseweb="slider"] {background:#122a43 !important;color:#fff !important;}
[data-baseweb="select"] *, [data-baseweb="popover"] *, [data-baseweb="menu"] * {color:#fff !important;}
[data-testid="stAlert"] {background:#183148 !important;border-color:#40627f !important;}
[data-testid="stAlert"] * {color:#f6fbff !important;}
.stButton button, [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {
 background:#173a56 !important;color:#fff !important;border:1px solid #487b96 !important;font-weight:750 !important;
}
.stButton button:hover {background:#235573 !important;}
[data-testid="stTabs"] button {color:#eff8ff !important;}
hr {border-color:#304a61 !important;}
.hero {padding:22px 26px;border:1px solid #366987;border-radius:16px;background:linear-gradient(115deg,#123452,#0a2034 62%,#113b43);margin-bottom:14px;}
.hero .eyebrow {font-size:11px;font-weight:800;letter-spacing:2px;color:#64e1d2 !important;}
.hero .h {font-size:30px;line-height:1.2;font-weight:850;color:#fff !important;margin:7px 0;}
.hero .sub {font-size:14px;color:#c8e4ef !important;}
.notice {background:#253320;border:1px solid #8b914c;border-radius:8px;padding:9px 13px;color:#fff4c9 !important;font-size:12px;font-weight:700;margin:6px 0 16px;}
.panel {border:1px solid #345670;background:#10263b;border-radius:13px;padding:17px 18px;margin:5px 0 12px;}
.panel h3 {margin:0 0 9px 0;color:#f5fbff !important;font-size:17px;}
.panel p {font-size:13px;color:#d8e8f5 !important;line-height:1.65;margin:0;}
.chip {display:inline-block;border:1px solid #4c8294;background:#113c4b;border-radius:5px;padding:4px 9px;font-size:11px;font-weight:800;color:#d3faf2 !important;margin-right:6px;}
.chip.alert {background:#512e36;border-color:#bd6675;color:#ffe2e5 !important;}
.chip.warn {background:#554126;border-color:#b78a3e;color:#fff0cc !important;}
.console {background:#091a2a;border:1px solid #38566d;border-radius:10px;padding:12px 15px;font-family:ui-monospace, Consolas,monospace;font-size:12px;min-height:160px;}
.console .line {font-family:ui-monospace,Consolas,monospace;color:#d4e9f7 !important;padding:4px 0;border-bottom:1px solid #1d3449;}
.console .event {color:#6ce2cf !important;font-weight:800;}
.console .warn {color:#ffd083 !important;}
.console .error {color:#ff989f !important;}
.small {font-size:12px;color:#bcd3e7 !important;}
</style>''', unsafe_allow_html=True)

st.markdown('''<div class="hero"><div class="eyebrow">REVORA SPACE HUB · QATAR · CONCEPT TECHNOLOGY DEMONSTRATOR</div>
<div class="h">HubOS-Sat | GEO Communications Intelligence</div>
<div class="sub">Es’hailSat-context study • Ku/Ka communications • Al Ghuwariyah teleport • Mission intelligence beyond conventional alarms</div></div>''', unsafe_allow_html=True)
st.markdown('''<div class="notice">SYNTHETIC REAL-TIME SIMULATION — NOT CONNECTED TO ES’HAILSAT. The named spacecraft and 25.5°E / 26°E orbital neighborhood are public context only. All numeric measurements, engineering models, alarms and events are illustrative; no operational access, qualified AI or existing integration is claimed.</div>''', unsafe_allow_html=True)

# State: normalizes all values so the simulation can be run in an isolated Streamlit account.
if 'sim' not in st.session_state:
    st.session_state.sim = {
        'running': False, 'tick': 0, 'last_update': time.monotonic(),
        'temp': 35.0, 'soc': 90.0, 'baseline': 15.0,
        'history': [], 'events': [], 'previous': set(),
    }

sim = st.session_state.sim

with st.sidebar:
    st.markdown('## Mission scenario controls')
    st.caption('Change these during the live demonstration. One tick = one simulated minute.')
    spacecraft = st.selectbox('Public satellite context (no real telemetry)', ['Es’hail-1 | 25.5°E', 'Es’hail-2 | 26.0°E'])
    band = st.selectbox('Communications service scenario', ['Ka-band managed link', 'Ku-band broadcast link'])
    rain = st.slider('Ground-path rain attenuation (dB)', 0.0, 15.0, 0.0, .5)
    interference = st.slider('Additional RF interference (dB)', 0.0, 7.0, 0.0, .5)
    heat = st.slider('Modeled payload heat load (relative %)', 50, 170, 100, 5)
    radiator = st.slider('Thermal rejection effectiveness (%)', 55, 115, 100, 5)
    payload = st.slider('Payload electrical demand (relative %)', 50, 155, 100, 5)
    eclipse = st.toggle('GEO eclipse demonstration', value=False)
    st.divider()
    b1, b2, b3 = st.columns(3)
    if b1.button('▶ Start', use_container_width=True):
        sim['running'] = True
        sim['last_update'] = time.monotonic()
    if b2.button('Ⅱ Pause', use_container_width=True):
        sim['running'] = False
    if b3.button('↺ Reset', use_container_width=True):
        st.session_state.sim = {
            'running': False, 'tick': 0, 'last_update': time.monotonic(),
            'temp': 35.0, 'soc': 90.0, 'baseline': 15.0,
            'history': [], 'events': [], 'previous': set()
        }
        st.rerun()
    st.caption('A simplified conceptual model, not Es’hailSat engineering specifications. The satellite name is a scenario label only.')

# This model intentionally separates ground signal attenuation from spacecraft thermal and power behavior.
# Assumed baseline reference values are arbitrary but internally consistent for demonstration.
def compute_sample(s):
    s['tick'] += 1
    t = s['tick']
    # thermal lag: synthetic temperature responds smoothly to load and heat rejection.
    expected_temp = 35.0 + 0.6 * math.sin(t / 11)
    temp_target = 35.0 + 0.13 * (heat - 100) - 0.16 * (radiator - 100)
    s['temp'] += .13 * (temp_target - s['temp'])
    actual_temp = s['temp'] + 0.15 * math.sin(t / 4)
    # Only eclipse and power imbalance deplete battery in this simplified GEO scenario.
    solar_available = 0 if eclipse else 1.0
    demand_kw = 7.0 * (payload / 100)
    supply_kw = 9.0 * solar_available
    battery_delta = (supply_kw - demand_kw) / 25.0 * 100 / 60
    s['soc'] = min(99.0, max(0.0, s['soc'] + battery_delta))
    # Synthetic 'power balance' intentionally in kW rather than ungrounded bus voltage.
    # Rain attenuation is applied to a *ground path*, not spacecraft health.
    nominal_margin = 13.0 if band.startswith('Ka') else 10.0
    link_margin = nominal_margin - rain - interference + .15 * math.sin(t / 5)
    predicted = nominal_margin - rain + .15 * math.sin(t / 5) # weather-informed reference
    unexplained = link_margin - predicted # interference residual
    # A fictional received signal quality metric; modeled as margin, not fake RF health score.
    sample = {
        'Minute': t, 'Actual thermal °C': round(actual_temp, 3),
        'Reference thermal °C': round(expected_temp, 3),
        'GEO battery SOC %': round(s['soc'], 3),
        'Solar available kW': round(supply_kw, 3),
        'Payload demand kW': round(demand_kw, 3),
        'Observed link margin dB': round(link_margin, 3),
        'Weather-only expected margin dB': round(predicted, 3),
        'Unexplained RF residual dB': round(unexplained, 3),
        'Ground rain loss dB': rain,
        'Interference loss dB': interference,
    }
    s['history'].append(sample)
    s['history'] = s['history'][-180:]
    flags = []
    if link_margin < 3: flags.append(('RF LINK', 'Link margin below illustrative 3 dB review threshold', 'warn'))
    if abs(unexplained) > 1.5: flags.append(('CORRELATION', 'Observed RF loss exceeds weather-only prediction: check interference / ground chain', 'error'))
    if actual_temp - expected_temp > 5: flags.append(('THERMAL', 'Thermal residual exceeds illustrative 5°C threshold', 'warn'))
    if eclipse and s['soc'] < 65: flags.append(('ECLIPSE', 'Battery SOC below illustrative 65% review threshold', 'warn'))
    current = {item[0] for item in flags}
    for code, message, level in flags:
        if code not in s['previous']:
            s['events'].insert(0, (t, code, message, level))
    for old_code in s['previous'] - current:
        s['events'].insert(0, (t, 'RECOVERY', f'{old_code} condition cleared', 'event'))
    if t == 1: s['events'].insert(0, (t, 'START', 'Synthetic GEO communications telemetry initiated', 'event'))
    s['previous'] = current
    s['events'] = s['events'][:14]

# The fragment makes the content automatically redraw while running; sliders trigger full reruns.
@st.fragment(run_every='1s')
def live_console():
    s = st.session_state.sim
    if s['running']:
        compute_sample(s)
    elif not s['history']:
        compute_sample(s)
    row = s['history'][-1]
    flags = list(s['previous'])
    status = 'INVESTIGATE' if flags else 'WITHIN ILLUSTRATIVE LIMITS'
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('SIMULATED MISSION TIME', f"T+{s['tick']:05d} min")
    c2.metric('LINK MARGIN', f"{row['Observed link margin dB']:.1f} dB")
    c3.metric('THERMAL DEVIATION', f"{row['Actual thermal °C']-row['Reference thermal °C']:+.1f} °C")
    c4.metric('ECLIPSE BATTERY SOC', f"{row['GEO battery SOC %']:.1f}%")
    if flags:
        st.error(f"HUBOS-SAT ANALYSIS • {status} • {', '.join(flags)}")
    else:
        st.success(f"HUBOS-SAT ANALYSIS • {status} • {'RUNNING' if s['running'] else 'PAUSED'}")
    hist = pd.DataFrame(s['history'])
    cfg = dict(displayModeBar=False, responsive=True)
    def make_chart(keys, title, unit, limits=None):
        fig = go.Figure()
        colors = ['#59dfce', '#81aefa', '#f6ca78', '#fc8d99']
        for j, key in enumerate(keys):
            fig.add_trace(go.Scatter(x=hist['Minute'], y=hist[key], mode='lines', name=key,
                                     line=dict(color=colors[j % len(colors)], width=2.8)))
        if limits is not None:
            fig.add_hline(y=limits, line=dict(color='#f6ca78', dash='dash', width=1),
                          annotation_text='Illustrative review threshold', annotation_font_color='#f6ca78')
        fig.update_layout(title=dict(text=title, font=dict(color='#ffffff', size=15)),
                          paper_bgcolor='#10263b', plot_bgcolor='#10263b',
                          font=dict(color='#eaf5ff', size=11), height=285,
                          margin=dict(l=15,r=20,t=45,b=10),
                          xaxis=dict(title='Simulated elapsed minutes', gridcolor='#2a435b', color='#dceeff'),
                          yaxis=dict(title=unit, gridcolor='#2a435b', color='#dceeff'),
                          legend=dict(orientation='h', y=-.38, font=dict(color='#eaf5ff')))
        return fig
    graph_left, graph_right = st.columns(2)
    with graph_left:
        st.plotly_chart(make_chart(['Observed link margin dB','Weather-only expected margin dB'],
                                  'Ku/Ka ground-path margin | observed vs weather model', 'dB'),
                        use_container_width=True, config=cfg)
        st.plotly_chart(make_chart(['Actual thermal °C','Reference thermal °C'],
                                  'Spacecraft thermal | modeled vs reference', '°C'),
                        use_container_width=True, config=cfg)
    with graph_right:
        st.plotly_chart(make_chart(['Unexplained RF residual dB'],
                                  'Cross-source intelligence | unexplained RF loss', 'dB'),
                        use_container_width=True, config=cfg)
        st.plotly_chart(make_chart(['GEO battery SOC %'],
                                  'GEO eclipse demonstration | battery SOC', '%'),
                        use_container_width=True, config=cfg)
    st.markdown('### Live analysis: what an additional intelligence layer could contribute')
    if abs(row['Unexplained RF residual dB']) > 1.5:
        st.markdown('''<div class="panel"><h3>RF loss not fully explained by weather</h3><p>The model compares a weather-adjusted expectation against the combined observed link impairment. An extra residual is visible. In a real pilot, an operator would validate whether interference, antenna pointing, equipment faults, or measurement uncertainty explain it. <b>This is not a real cause diagnosis.</b></p></div>''', unsafe_allow_html=True)
    elif row['Observed link margin dB'] < 3:
        st.markdown('''<div class="panel"><h3>Weather-correlated link degradation</h3><p>Rain attenuation explains most of the modeled reduction. A possible next step is combining measured RF metrics with local weather observations, SLA information and ground-station history to support service-impact analysis.</p></div>''', unsafe_allow_html=True)
    elif row['Actual thermal °C']-row['Reference thermal °C'] > 5:
        st.markdown('''<div class="panel"><h3>Thermal residual requires engineering review</h3><p>The actual modeled temperature is above its synthetic expected baseline. An operator could review payload operating mode, heater states, radiation exposure and redundant sensors. HubOS-Sat would present evidence, not issue spacecraft commands.</p></div>''', unsafe_allow_html=True)
    elif eclipse:
        st.markdown('''<div class="panel"><h3>GEO eclipse power-balance watch</h3><p>Solar generation is zero in this scenario. Modeled battery state-of-charge declines as the spacecraft supplies payload demand. This is a simplified demonstration of an eclipse period, not an actual Es’hailSat power-system model.</p></div>''', unsafe_allow_html=True)
    else:
        st.markdown('''<div class="panel"><h3>Baseline relationship is consistent</h3><p>The weather-adjusted link margin and observed synthetic telemetry align within the model. Test a rain fade event, then add RF interference. The key distinction is that the software distinguishes an expected weather-related change from an additional unexplained loss.</p></div>''', unsafe_allow_html=True)
    st.markdown('### Mission event console')
    logs = []
    for t, code, msg, level in s['events'][:8]:
        logs.append(f'<div class="line"><span class="{level}">T+{t:05d} [{code}]</span> — {msg}</div>')
    if not logs: logs.append('<div class="line">No events recorded</div>')
    st.markdown('<div class="console">'+''.join(logs)+'</div>', unsafe_allow_html=True)
    st.caption('All data, model values, event timings, thresholds and analytics are synthetic. Live means the demo computes new values while running, not a live satellite feed.')

main, project, next_steps = st.tabs(['01  •  LIVE GEO OPERATIONS', '02  •  SECURE CO-DEVELOPMENT', '03  •  VALIDATION ROADMAP'])
with main:
    st.markdown('#### Suggested demonstration: Start → add rain fade → add interference → observe the unexplained RF residual. Then enable GEO eclipse to see battery response.')
    live_console()
with project:
    st.markdown('### Es’hailSat already monitors and controls its spacecraft. What would ReVora add?')
    a, b, c = st.columns(3)
    with a:
        st.markdown('''<div class="panel"><h3>1 · Existing operator systems</h3><p>Es’hailSat operates spacecraft TT&C, capacity management and satellite services. Its teleport provides monitored RF, baseband and transport-stream services. This demonstration does not imply any capability gap.</p></div>''', unsafe_allow_html=True)
    with b:
        st.markdown('''<div class="panel"><h3>2 · Proposed read-only bridge</h3><p>Subject to Es’hailSat approval, obtain selected historical telemetry, weather records and link-quality signals through a filtered dataset or isolated interface. No spacecraft commands or production-network access.</p></div>''', unsafe_allow_html=True)
    with c:
        st.markdown('''<div class="panel"><h3>3 · HubOS-Sat intelligence</h3><p>Develop cross-source correlation, anomalies against engineering baselines, explainable events and operator investigation evidence. Demonstrate measurable benefit over existing tools before discussing deployment.</p></div>''', unsafe_allow_html=True)
    st.markdown('**Proposed evaluation use case:** weather-correlated RF degradation versus additional unexplained impairment on an approved Ku/Ka service dataset.')
    st.info('Not an installed product. This proof of concept uses synthetic data and transparent rules; any ML, digital twin, live interface or predictive accuracy would require engineering and commercial validation.')
    st.markdown('**Data boundary**  •  Es’hailSat controls access and data rights  •  ReVora develops a test module  •  Human operators remain responsible  •  Background IP and new IP terms require a separate agreement')
with next_steps:
    st.markdown('### From interactive concept to a practical engineering pilot')
    steps = [
        ('01  Technical alignment', 'Select a real operator pain point and nominate Es’hailSat / ReVora technical counterparts.'),
        ('02  Data feasibility & security', 'Agree scope of read-only historical RF, weather and/or spacecraft telemetry and the evaluation environment.'),
        ('03  Limited proof of concept', 'Build a transparent baseline; test anomaly correlation with labeled incidents and known false positives.'),
        ('04  Measured evaluation', 'Compare with existing workflows using precision, false-alert rate, time to investigation and engineer acceptance.'),
        ('05  Conditional product discussion', 'If useful, negotiate pilot integration, support model, commercial licensing and Qatar-based IP development.'),
    ]
    for heading, desc in steps:
        st.markdown(f'<div class="panel"><h3>{heading}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
    st.markdown('**Proposed meeting ask:** “Could we hold a joint technical workshop to assess a read-only, securely scoped data pilot for cross-source link-health analytics?”')
    st.markdown('#### Public context behind the tailored scenario')
    st.markdown('- [Es’hailSat satellites: Es’hail-1 and Es’hail-2, Ku/Ka payloads](https://www.eshailsat.qa/satellites/)')
    st.markdown('- [Es’hailSat teleport services including TT&C and capacity management](https://www.eshailsat.qa/wp-content/uploads/2025/04/Teleport-Services.pdf)')
    st.markdown('- [Es’hailSat products and services](https://www.eshailsat.qa/products-services/)')

st.divider()
st.caption('© ReVora — HubOS-Sat prototype concept. Synthetic data only. Es’hailSat is a prospective technical collaboration partner; no affiliation, endorsement or access is implied.')
