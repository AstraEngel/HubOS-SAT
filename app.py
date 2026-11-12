import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ReVora HubOS-Sat | Concept Demonstrator", page_icon="🛰️", layout="wide")
st.markdown('''<style>
.stApp {background: #091522; color: #e8f1fa}
[data-testid="stMetric"] {background:#14283b; border:1px solid #28455b; padding:14px; border-radius:12px}
[data-testid="stAlert"] {border-radius:10px}
</style>''', unsafe_allow_html=True)

st.title("🛰️ ReVora | HubOS-Sat")
st.caption("SATELLITE INTELLIGENCE CONCEPT DEMONSTRATOR • SYNTHETIC DATA ONLY • NO LIVE SPACECRAFT CONNECTION")
st.info("Illustrative concept for discussions with a satellite operator. Not integrated, flight-qualified, AI-validated, or authorized to control a spacecraft.")

left, right = st.columns([2,1])
with left:
    scenario = st.radio("Operational scenario", ["Nominal operations", "Developing thermal anomaly", "Communications degradation"], horizontal=True)
with right:
    st.selectbox("Demo spacecraft", ["Illustrative GEO communications satellite"], help="Fictional reference model; not an Es'hailSat spacecraft")

rng = np.random.default_rng(21)
minutes = np.arange(0, 90)
thermal = 33 + 0.6*np.sin(minutes/8) + rng.normal(0,.3,len(minutes))
voltage = 28.2 + 0.08*np.sin(minutes/7) + rng.normal(0,.045,len(minutes))
link = 98.7 + .3*np.sin(minutes/12) + rng.normal(0,.12,len(minutes))
if scenario == "Developing thermal anomaly":
    thermal += np.clip((minutes-48)*0.32,0,None)
    voltage -= np.clip((minutes-60)*0.009,0,None)
elif scenario == "Communications degradation":
    link -= np.clip((minutes-42)*0.37,0,None)

critical_temp = 42.0
warning_temp = 39.0
warning_link = 92.0
critical_link = 87.0
last_temp,last_volt,last_link = thermal[-1],voltage[-1],link[-1]
status = "CRITICAL" if last_temp>=critical_temp or last_link<critical_link else "ATTENTION" if last_temp>=warning_temp or last_link<warning_link else "NOMINAL"

cols = st.columns(4)
for c, label, val in zip(cols,["Thermal sensor", "Bus voltage", "Link quality", "Rule-based health"],[f"{last_temp:.1f} °C",f"{last_volt:.2f} V",f"{last_link:.1f}%",status]):
    c.metric(label, val)

st.subheader("Telemetry trend (synthetic, last 90 minutes)")
a,b = st.columns(2)
with a:
    st.markdown("**Thermal monitoring (°C)**")
    st.line_chart(pd.DataFrame({"Temperature":thermal,"Warning threshold":np.full(len(minutes), warning_temp),"Critical threshold":np.full(len(minutes), critical_temp)},index=minutes),height=245)
with b:
    st.markdown("**Communications link quality (%)**")
    st.line_chart(pd.DataFrame({"Link quality":link,"Warning threshold":np.full(len(minutes),warning_link)},index=minutes),height=245)

st.subheader("HubOS-Sat concept: interpretation and human decision support")
if scenario == "Nominal operations":
    st.success("NORMAL: All simulated monitored parameters remain within illustrative ranges.")
    st.write("**Suggested operator view:** Continue monitoring. No action recommended.")
elif scenario == "Developing thermal anomaly":
    st.error("THERMAL ALERT: Temperature has exceeded an illustrative operational threshold and continues to rise.")
    st.write("**Rule-based interpretation:** Sustained warming appears from minute 48. The pattern warrants human review; its cause cannot be determined from this simulation.")
    st.write("**Suggested operator checks:** Compare sensor redundancy; review thermal-control commands and heater states; inspect correlated power data; follow the operator's approved anomaly-response procedure.")
else:
    st.error("LINK ALERT: The simulated communications quality index shows persistent deterioration.")
    st.write("**Rule-based interpretation:** Decline begins near minute 42. This does not identify the cause or imply loss of the spacecraft.")
    st.write("**Suggested operator checks:** Correlate antenna pointing, weather at ground facilities, link budgets, and ground equipment alarms under established procedures.")

with st.expander("Conceptual digital twin and integration boundary"):
    st.markdown("""
    **Illustrative digital twin:** compare actual telemetry against a simplified baseline model to flag deviations. A genuine operational twin would require spacecraft-specific models, engineering calibration, validation, configuration management and operator approval.

    **Proposed integration:** operator-controlled ground systems → authorized read-only telemetry export/API → isolated HubOS-Sat analysis environment → engineer dashboard.

    **Not included:** real telemetry, actual machine learning, autonomous spacecraft control, command uplink, validated fault diagnosis or predictive maintenance.
    """)

st.divider()
st.markdown("**Proposed joint evaluation:** (1) select one operator-relevant use case → (2) obtain approved historical or simulated data → (3) test detection and false alarms → (4) review cybersecurity, data rights and software IP → (5) decide whether to pilot.")
st.caption("ReVora • For concept discussion only • Values, spacecraft and incidents are fictional")
