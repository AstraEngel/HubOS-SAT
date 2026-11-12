import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import IsolationForest, RandomForestClassifier

st.set_page_config(page_title='ReVora | HubOS-Sat Sovereign Mission Intelligence', page_icon='🛰️', layout='wide', initial_sidebar_state='expanded')

st.markdown('''<style>
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"],
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {background-color:#071421 !important; color:#F2F7FF !important;}
[data-testid="stSidebar"] {background:#0C1D30 !important; border-right:1px solid #24445F !important;}
* {scrollbar-color:#365877 #071421;}
.stApp p, .stApp label, .stApp li, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stWidgetLabel"] *, [data-testid="stMarkdownContainer"] *, [data-testid="stCaptionContainer"] *,
[data-testid="stMetricLabel"] *, [data-testid="stMetricValue"] *, [data-testid="stMetricDelta"] * {
 color:#EAF3FF !important; opacity:1 !important;
}
[data-testid="stCaptionContainer"] * {color:#B6CDE2 !important;}
[data-testid="stMetric"] {background:#10283D !important; border:1px solid #315775 !important; border-radius:13px; padding:15px !important;}
[data-testid="stMetricLabel"] *, [data-testid="stMetricLabel"] {color:#C9E1F5 !important; font-weight:700 !important; font-size:0.9rem !important;}
[data-testid="stMetricValue"] *,[data-testid="stMetricValue"] {color:white !important; font-weight:800 !important;}
[data-baseweb="select"]>div, [data-baseweb="input"]>div, [data-baseweb="popover"] div,
[data-testid="stNumberInput"] input, [data-testid="stTextInput"] input {background:#10283D !important; color:#F2F7FF !important;}
[data-baseweb="select"] *, [data-baseweb="popover"] *, [data-baseweb="slider"] *, .stSlider * {color:#F2F7FF !important;}
.stButton button, [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {background:#173651 !important; color:#F2F7FF !important; border:1px solid #46728B !important; font-weight:700 !important;}
.stButton button:hover {background:#245473 !important; color:white !important;}
.stTabs [data-baseweb="tab-list"] {background:#0B2034 !important; border-radius:9px;}
.stTabs [data-baseweb="tab"] {color:#CBDFF1 !important;}
.stTabs [aria-selected="true"] {color:#6CE6D9 !important; border-bottom:2px solid #6CE6D9 !important;}
[data-testid="stAlert"] {background:#14293C !important; border:1px solid #315A75 !important;}
[data-testid="stAlert"] * {color:#EAF3FF !important;}
[data-testid="stDataFrame"] {background:#10283D !important;}
.hero {padding:20px 24px;border-radius:15px;border:1px solid #355E79;background:linear-gradient(115deg,#102F4A,#0A2338 70%,#0F3841);margin-bottom:12px;}
.eyebrow {color:#70E3D7;font-size:11px;font-weight:800;letter-spacing:2.4px;}
.headline {color:#FFFFFF;font-size:28px;font-weight:850;line-height:1.25;margin:5px 0;}
.subhead {color:#C8DEEF;font-size:13px;line-height:1.6;}
.pill {display:inline-block;background:#123D46;color:#97F8E0;border:1px solid #267D81;padding:6px 10px;border-radius:7px;font-size:12px;font-weight:800;margin:3px 6px 3px 0;}
.pill.warning {background:#493320;color:#FFE1A0;border-color:#91652E;}
.pill.danger {background:#4A2635;color:#FFD0D8;border-color:#985464;}
.panel {padding:18px 20px;background:#10283D;border-radius:13px;border:1px solid #315775;margin:10px 0 15px;}
.panel-title {font-size:16px;color:white;font-weight:800;margin-bottom:5px;}
.panel-body {font-size:13px;color:#C8DEEF;line-height:1.65;}
.console {font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px;line-height:1.75;white-space:pre-wrap;background:#06111C;border:1px solid #274865;border-radius:10px;padding:13px 16px;color:#BEEBDF;min-height:165px;}
.sov {padding:14px 16px;border:1px solid #3C6A86;background:#12314A;border-radius:11px;min-height:133px;margin-bottom:6px;}
.sov strong {color:white;display:block;margin-bottom:6px;font-size:14px;}
.sov span {color:#C9E0F0;font-size:12px;line-height:1.45;}
</style>''', unsafe_allow_html=True)

st.markdown('''<div class="hero"><div class="eyebrow">REVORA SPACE HUB · DOHA TO THE WORLD</div>
<div class="headline">HubOS-Sat | Sovereign Mission Intelligence</div>
<div class="subhead">GEO communications • AI-assisted incident correlation • Satellite + ground context • Qatar-based IP development<br>
PROTOTYPE DEMONSTRATION — a fictional Ku/Ka communications service, not Es’hailSat's telemetry or flight software.</div></div>''', unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def make_models():
    r=np.random.default_rng(2026)
    rows=[]; labels=[]
    # Features: observed weather fade, measured ground pointing, unexpected RF residual,
    # spacecraft thermal deviation, battery discharge / minute, link margin.
    cases=['Nominal','Weather attenuation','Unexplained RF impairment','Ground pointing issue','Spacecraft thermal excursion','GEO eclipse / power stress']
    for label in cases:
        for _ in range(390):
            weather=max(0,r.normal(.8,.55)); pointing=max(0,r.normal(.12,.11)); rf=max(0,r.normal(.12,.13)); thermal=r.normal(0,.45); discharge=max(0,r.normal(.03,.07))
            if label=='Weather attenuation': weather=r.uniform(3.6,9.8)
            if label=='Unexplained RF impairment': rf=r.uniform(2.5,6.5)
            if label=='Ground pointing issue': pointing=r.uniform(1.1,3.5)
            if label=='Spacecraft thermal excursion': thermal=r.uniform(6.5,17)
            if label=='GEO eclipse / power stress': discharge=r.uniform(.35,1.35)
            margin=13-weather-pointing-rf+r.normal(0,.20)
            rows.append([weather,pointing,rf,thermal,discharge,margin]);labels.append(label)
    X=np.array(rows);y=np.array(labels)
    clf=RandomForestClassifier(n_estimators=90,max_depth=11,random_state=12,n_jobs=-1)
    clf.fit(X,y)
    normal=X[y=='Nominal']
    detector=IsolationForest(n_estimators=110,contamination=.035,random_state=13,n_jobs=-1)
    detector.fit(normal)
    return detector,clf

anomaly_model, triage_model = make_models()

if 'history' not in st.session_state:
    st.session_state.history=[]
    st.session_state.events=[]
    st.session_state.tick=0
    st.session_state.running=False
    st.session_state.soc=94.0
    st.session_state.last_alert='Nominal'
    st.session_state.last_ai='Nominal'

with st.sidebar:
    st.markdown('### MISSION INJECTION CONTROLS')
    st.caption('All values are synthetic. Change a slider while the simulation runs.')
    c1,c2=st.columns(2)
    with c1:
        if st.button('▶ Start' if not st.session_state.running else 'Ⅱ Pause',use_container_width=True):
            st.session_state.running=not st.session_state.running
    with c2:
        if st.button('↺ Reset',use_container_width=True):
            st.session_state.history=[];st.session_state.events=[];st.session_state.tick=0
            st.session_state.soc=94.0;st.session_state.last_alert='Nominal';st.session_state.last_ai='Nominal'
            st.session_state.running=False
            st.rerun()
    st.markdown('#### Ground and RF environment')
    weather=st.slider('Ground-path rain fade (dB)',0.0,10.0,0.5,.5)
    interference=st.slider('Extra unexplained RF loss (dB)',0.0,7.0,0.0,.5)
    pointing=st.slider('Ground antenna pointing loss (dB)',0.0,3.5,0.1,.1)
    st.markdown('#### Spacecraft environment')
    payload=st.slider('Payload utilization (%)',20,100,55,5)
    thermal_fault=st.slider('Extra equipment thermal load (°C equivalent)',0.0,15.0,0.0,.5)
    eclipse=st.toggle('GEO eclipse / solar generation unavailable',value=False)
    st.divider()
    st.caption('The AI algorithms run locally in this Streamlit application. The data is synthetic and not connected to Es’hailSat.')


def push_tick():
    ss=st.session_state; t=ss.tick; r=np.random.default_rng(1091+t)
    # illustrative physics; NOT fitted to any Es'hailSat spacecraft or RF link.
    predicted_cn0=79.0-weather-pointing
    observed_cn0=predicted_cn0-interference+r.normal(0,.12)
    rf_residual=max(0,predicted_cn0-observed_cn0)
    link_margin=13.0-weather-pointing-rf_residual
    temp=31.0+payload*.085+thermal_fault+r.normal(0,.14)
    thermal_dev=temp-(31.0+payload*.085)
    power_load=5.1+payload*.060 # kW, illustrative, not a fleet specification
    solar=0.0 if eclipse else 13.2
    net=solar-power_load
    # 32 kWh fictional battery: % per simulated minute.
    soc_before=ss.soc
    ss.soc=float(np.clip(ss.soc+(net/60/32)*100,0,100))
    discharge=max(0,soc_before-ss.soc)
    feature=np.array([[weather,pointing,rf_residual,thermal_dev,discharge,link_margin]])
    outlier=anomaly_model.predict(feature)[0]==-1
    raw=anomaly_model.decision_function(feature)[0]
    probs=triage_model.predict_proba(feature)[0]
    label=str(triage_model.classes_[np.argmax(probs)])
    model_probability=float(np.max(probs))
    # No claim of statistically calibrated confidence: scores only on simulated scenarios.
    status='REVIEW' if outlier else 'NOMINAL'
    if outlier and label=='Nominal':label='Unclassified deviation'
    record=dict(t=t,cn0=observed_cn0,expected_cn0=predicted_cn0,margin=link_margin,
                thermal=temp,thermal_expected=31+payload*.085,soc=ss.soc,
                power_load=power_load,solar=solar,weather=weather,pointing=pointing,
                rf_residual=rf_residual,thermal_dev=thermal_dev,discharge=discharge,
                anomaly=outlier,score=raw,classification=label,probability=model_probability,
                status=status)
    ss.history.append(record);ss.history=ss.history[-180:]
    if t==0:
        ss.events.append(f'T+{t:04d}  SESSION INITIALIZED / simulated GEO communications service')
        ss.events.append(f'T+{t:04d}  ISOLATION FOREST + RANDOM FOREST initialized on synthetic training data')
    if outlier and (ss.last_alert!='REVIEW' or ss.last_ai!=label):
        ss.events.append(f'T+{t:04d}  AI FLAG → {label.upper()} | investigate cross-source evidence')
    elif not outlier and ss.last_alert=='REVIEW':
        ss.events.append(f'T+{t:04d}  AI FLAG CLEARED → returned to simulated baseline')
    if t>0 and t%15==0: ss.events.append(f'T+{t:04d}  MONITORING → {status} | link margin {link_margin:.1f} dB')
    ss.events=ss.events[-14:]
    ss.last_alert=status;ss.last_ai=label;ss.tick+=1


def make_chart(df,cols,title,unit,limits=None):
    colors=['#59E0D4','#63BDF4','#FFB969']
    fig=go.Figure()
    for i,(key,name) in enumerate(cols):
        fig.add_trace(go.Scatter(x=df.t,y=df[key],name=name,mode='lines',
            line=dict(color=colors[i%len(colors)],width=2.6),
            hovertemplate='T+%{x} min<br>%{y:.2f} '+unit+'<extra>'+name+'</extra>'))
    if limits is not None:
        fig.add_hline(y=limits,line_dash='dot',line_color='#FFAA75',annotation_text='Example review threshold',annotation_font_color='#FFD39A')
    fig.update_layout(height=267,margin=dict(l=10,r=12,t=24,b=7),
        paper_bgcolor='#10283D',plot_bgcolor='#10283D',font=dict(color='#EAF3FF',size=11),
        xaxis=dict(title='Simulated elapsed minutes',gridcolor='#29475F',zeroline=False),
        yaxis=dict(title=unit,gridcolor='#29475F',zeroline=False),
        legend=dict(orientation='h',y=1.20,x=0,bgcolor='#10283D'),hovermode='x unified')
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False},key='plot_'+title.replace(' ','_'))


@st.fragment(run_every='1s')
def mission_view():
    if st.session_state.running or not st.session_state.history:
        push_tick()
    df=pd.DataFrame(st.session_state.history)
    current=df.iloc[-1]
    live='LIVE SYNTHETIC STREAM' if st.session_state.running else 'PAUSED / SYNTHETIC STREAM'
    pill='danger' if bool(current.anomaly) else ''
    st.markdown(f'''<span class="pill">{live}</span><span class="pill">MET T+{int(current.t):05d} min</span>
    <span class="pill {pill}">AI {str(current.status)}</span><span class="pill">READ-ONLY CONCEPT</span>''',unsafe_allow_html=True)
    m1,m2,m3,m4,m5=st.columns(5)
    m1.metric('Observed C/N₀',f'{current.cn0:.1f} dB-Hz')
    m2.metric('Link margin',f'{current.margin:.1f} dB')
    m3.metric('RF residual',f'{current.rf_residual:.2f} dB')
    m4.metric('Equipment temperature',f'{current.thermal:.1f} °C')
    m5.metric('Battery state of charge',f'{current.soc:.1f}%')
    tab1,tab2,tab3=st.tabs(['MISSION CONSOLE','AI INTELLIGENCE','QATAR SOVEREIGN CAPABILITY'])
    with tab1:
        a,b=st.columns(2)
        with a:
            st.markdown('#### Ku/Ka ground-link signal behaviour')
            make_chart(df,[('cn0','Observed C/N₀'),('expected_cn0','Weather/pointing expected')],'rf_link','dB-Hz')
            st.markdown('#### Spacecraft equipment thermal response')
            make_chart(df,[('thermal','Modeled observed'),('thermal_expected','Expected baseline')],'thermal','°C')
        with b:
            st.markdown('#### Available link margin')
            make_chart(df,[('margin','Calculated margin')],'link_margin','dB',limits=3)
            st.markdown('#### Spacecraft battery & power')
            make_chart(df,[('soc','Battery state of charge')],'battery','%')
        left,right=st.columns([1.2,1])
        with left:
            st.markdown('#### Mission event console')
            logs='\n'.join(reversed(st.session_state.events[-9:]))
            st.markdown('<div class="console">'+logs.replace('&','&amp;').replace('<','&lt;')+'</div>',unsafe_allow_html=True)
        with right:
            st.markdown('#### Cross-system state')
            st.dataframe(pd.DataFrame([
                ['Ground weather',f'{current.weather:.1f} dB attenuation'],
                ['Pointing',f'{current.pointing:.1f} dB measured loss'],
                ['RF unexplained residual',f'{current.rf_residual:.2f} dB'],
                ['Payload power',f'{current.power_load:.1f} kW model'],
                ['Solar power',f'{current.solar:.1f} kW model'],
                ['Power balance',f'{current.solar-current.power_load:+.1f} kW model'],
            ],columns=['Source','Current reading']),hide_index=True,use_container_width=True)
    with tab2:
        st.markdown('### AI layer: what the operating console does not tell you by itself')
        x,y=st.columns([1,1])
        with x:
            st.metric('Isolation Forest anomaly score',f'{current.score:+.3f}',help='Negative is unusual relative to synthetic nominal training data; not a real mission risk score.')
            st.metric('Synthetic scenario classification',str(current.classification))
            st.metric('Model vote share',f'{current.probability*100:.0f}%',help='Share of random-forest votes on synthetic patterns, NOT calibrated confidence on real Es’hailSat data.')
            st.markdown('''<div class="panel"><div class="panel-title">Two actual ML components</div>
                <div class="panel-body"><b>Isolation Forest</b> tests whether the latest multi-source state differs from a synthetic nominal baseline.<br>
                <b>Random Forest</b> sorts abnormal states into synthetic weather, interference, pointing, thermal, or eclipse patterns.<br><br>
                Neither model is trained on Es’hailSat data. All outputs require engineering validation before operational use.</div></div>''',unsafe_allow_html=True)
        with y:
            explanation=[]
            if current.weather>=3:explanation.append(f'Ground-path weather attenuation is elevated ({current.weather:.1f} dB).')
            if current.rf_residual>=1.6:explanation.append(f'Observed signal is {current.rf_residual:.1f} dB worse than weather/pointing model predicts: review additional RF causes.')
            if current.pointing>=1:explanation.append(f'Ground antenna pointing-loss proxy is elevated ({current.pointing:.1f} dB).')
            if current.thermal_dev>=5:explanation.append('Spacecraft thermal reading diverges from the payload-dependent reference.')
            if current.discharge>=.35:explanation.append('Battery is discharging rapidly in the simulated power model; check eclipse and net load.')
            if not explanation:explanation=['Measured values remain close to the simplified reference model.']
            st.markdown('#### Cross-source reasoning')
            for item in explanation:st.markdown('• '+item)
            st.markdown('#### Operator-facing next step')
            st.info('Compare the flagged sources with existing RF/TT&C alarms, weather logs and engineering procedures. Preserve operator control; do not uplink commands.')
            st.markdown('''<div class="panel"><div class="panel-title">Potential value beyond current monitoring</div>
            <div class="panel-body">One incident context that combines <b>ground weather + RF measurements + engineering reference models + spacecraft health</b>.
            The commercial test is whether this reduces investigation time or improves triage versus Es’hailSat's existing tools.</div></div>''',unsafe_allow_html=True)
        st.markdown('#### Observed vs expected: explanation of an apparent link fault')
        c1,c2,c3=st.columns(3)
        c1.metric('Expected C/N₀',f'{current.expected_cn0:.2f} dB-Hz')
        c2.metric('Observed C/N₀',f'{current.cn0:.2f} dB-Hz')
        c3.metric('Unexplained difference',f'{current.rf_residual:.2f} dB')
    with tab3:
        st.markdown('### Software sovereignty is built through capability, control and IP — not through a dashboard')
        st.write('HubOS-Sat is proposed as a Qatar-developed, operator-validated software product. This demonstration shows the *types* of capability ReVora could build; it does not establish national sovereignty by itself.')
        q1,q2,q3=st.columns(3)
        with q1:
            st.markdown('<div class="sov"><strong>01 · Local engineering and IP</strong><span>Build the telemetry normalization, anomaly models, test harness and application source code through a Qatar-based development team. Define background and foreground IP by contract.</span></div>',unsafe_allow_html=True)
        with q2:
            st.markdown('<div class="sov"><strong>02 · Qatar-controlled deployment</strong><span>Offer an Es’hailSat-approved isolated or on-premises deployment, with access logs, data residency and operator-managed permissions. No telemetry leaves its approved boundary.</span></div>',unsafe_allow_html=True)
        with q3:
            st.markdown('<div class="sov"><strong>03 · Independent technical capability</strong><span>Document interfaces, train engineers, support local maintainability and test interoperability. Sovereignty requires operational competence and contractual control, not just asset location.</span></div>',unsafe_allow_html=True)
        st.markdown('### Complementing Es’hailSat, not replacing it')
        st.dataframe(pd.DataFrame([
            ['Existing TT&C, RF/baseband/transport monitoring','Established operator capability','Read-only, cross-source analytics evaluated beside existing tools'],
            ['Fleet service operations and incident response','Es’hailSat-led operational decisions','AI-assisted triage and evidence summarization for operator review'],
            ['Secure ground infrastructure','Es’hailSat defines cyber/data controls','Qatar-hosted, access-controlled software product if approved'],
            ['Future communications expansion','Operator/partners define real mission needs','Qatar-built software modules and possible future partner-led missions'],
        ],columns=['Area','Operator role','Proposed ReVora contribution']),hide_index=True,use_container_width=True)
        st.markdown('''<div class="panel"><div class="panel-title">A concrete, testable partnership request</div>
        <div class="panel-body">Select one existing operational problem. Jointly agree a <b>read-only test dataset</b>, compare HubOS-Sat against current triage processes and set measurable acceptance criteria (false positives, incident classification, time to root-cause hypothesis, engineer utility).<br><br>
        If validated: agree licensing, Qatar-based engineering and IP boundaries before any production deployment.</div></div>''',unsafe_allow_html=True)
    st.caption('All readings, model training examples, thresholds, mission time, and recommendations are synthetic. This is a demonstrator of feasible ML techniques, not an operationally validated Es’hailSat system. Real outcomes and integration depend on Es’hailSat requirements and authorization.')

mission_view()
