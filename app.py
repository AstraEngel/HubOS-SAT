import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="ReVora | HubOS-Sat Mission Intelligence",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""<style>
:root {color-scheme:dark}
.stApp, [data-testid="stAppViewContainer"] {
    background: #07111e;
    color: #eff6ff;
}
[data-testid="stHeader"] {background: #07111e;}
[data-testid="stSidebar"] {background:#102338;}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,
.stApp p,.stApp label,.stApp small {
    color:#eff6ff !important;
}
[data-testid="stWidgetLabel"] p,
[data-testid="stMarkdownContainer"] p {
    color:#e5eefb !important;
}
[data-testid="stMetric"] {
    background:#10243b;
    border:1px solid #325573;
    padding:17px;
    border-radius:14px;
}
[data-testid="stMetricLabel"] *,
[data-testid="stMetricLabel"] {
    color:#f0f7ff !important;
    font-size:1rem !important;
    font-weight:650 !important;
    opacity:1 !important;
}
[data-testid="stMetricValue"] *,
[data-testid="stMetricValue"] {
    color:#ffffff !important;
    opacity:1 !important;
}
[data-testid="stMetricDelta"] * {
    color:#bdebdc !important;
}
[data-testid="stCaptionContainer"] *,
.stApp [data-testid="stCaptionContainer"] {
    color:#b9cde5 !important;
}
[data-testid="stRadio"] label,
[data-testid="stRadio"] p,
[data-testid="stSelectbox"] label {
    color:#f1f6ff !important;
}
.stTabs [data-baseweb="tab"] {
    color:#d8e7f7 !important;
    font-weight:600;
}
.stTabs [aria-selected="true"] {
    color:#68e1da !important;
}
div[data-baseweb="select"] > div {
    background-color:#142a42 !important;
    color:#fff !important;
}
.hero {
    background:linear-gradient(115deg,#123250,#0b2337 65%,#123a45);
    border:1px solid #2b5670;
    border-radius:16px;
    padding:22px 27px;
    margin-bottom:13px;
}
.eyebrow {
    letter-spacing:2px;
    font-size:11px;
    color:#6ce6d4;
    font-weight:750;
}
.hero-title {
    font-size:30px;
    font-weight:800;
    color:#fff;
    margin:4px 0 5px 0;
}
.hero-sub {
    color:#ccdeef;
    font-size:15px;
}
.status {
    border-radius:9px;
    padding:10px 14px;
    font-size:14px;
    font-weight:800;
    border:1px solid #2a6e6c;
    background:#103e44;
    color:#a5f3e5;
    margin:8px 0 14px;
}
.status.warn {
    border-color:#9a6b27;
    background:#392e21;
    color:#ffe2a2;
}
.status.alert {
    border-color:#aa5254;
    background:#43272e;
    color:#ffd1d4;
}
.panel {
    border:1px solid #294863;
    background:#102238;
    border-radius:13px;
    padding:18px 19px;
    margin:8px 0 13px;
}
.panel-title {
    color:#f3f8ff;
    font-size:17px;
    font-weight:750;
    margin:0 0 8px;
}
.panel-copy {
    color:#d3e1ef;
    font-size:14px;
    line-height:1.65;
}
.tag {
    display:inline-block;
    border:1px solid #4f7384;
    border-radius:7px;
    padding:3px 8px;
    color:#c9e9fa;
    font-size:11px;
    font-weight:700;
    margin-right:6px;
}
.diagram-node {
    background:#142e47;
    padding:15px;
    border-radius:12px;
    border:1px solid #366783;
    text-align:center;
    min-height:92px;
}
.diagram-node strong {
    display:block;
    color:#fff;
    margin-bottom:5px;
}
.diagram-node span {
    font-size:12px;
    color:#c9dcea;
}
.step {
    background:#10263d;
    border-left:3px solid #3bc5b8;
    padding:13px 17px;
    margin-bottom:10px;
    border-radius:5px;
}
.step strong {color:#fff}
.step span {
    color:#c6dae9;
    font-size:13px;
}
</style>""", unsafe_allow_html=True)

st.markdown(
    '''<div class="hero">
    <div class="eyebrow">REVORA SPACE HUB · QATAR</div>
    <div class="hero-title">HubOS-Sat | Mission Intelligence</div>
    <div class="hero-sub">
    Proposed satellite operations intelligence layer ·
    Interactive technical concept for an Es’hailSat discussion
    </div></div>''',
    unsafe_allow_html=True
)

st.warning(
    "CONCEPT DEMONSTRATOR — fictional GEO communications satellite, "
    "synthetic telemetry, illustrative thresholds. No Es’hailSat data, "
    "real AI, satellite integration, spacecraft command or validated prediction."
)

left, right = st.columns([2.25, 1])

with left:
    scenario = st.radio(
        "DEMONSTRATION SCENARIO",
        [
            "Nominal operations",
            "Thermal anomaly",
            "Communications degradation"
        ],
        horizontal=True
    )

with right:
    show_baseline = st.toggle(
        "Show baseline and warning limits",
        value=True
    )

# SYNTHETIC SATELLITE TELEMETRY

x = np.arange(90)
rng = np.random.default_rng(14)

temp = (
    33
    + .55 * np.sin(x / 9)
    + rng.normal(0, .20, len(x))
)

volt = (
    28.2
    + .09 * np.sin(x / 11)
    + rng.normal(0, .035, len(x))
)

link = (
    98.4
    + .35 * np.sin(x / 12)
    + rng.normal(0, .16, len(x))
)

rf = (
    72
    + 1.2 * np.sin(x / 8)
    + rng.normal(0, .35, len(x))
)

if scenario == "Thermal anomaly":
    temp += np.maximum(x - 43, 0) * .27
    volt -= np.maximum(x - 60, 0) * .012

elif scenario == "Communications degradation":
    link -= np.maximum(x - 39, 0) * .34
    rf -= np.maximum(x - 44, 0) * .23

last_temp, last_volt, last_link, last_rf = [
    a[-1] for a in (temp, volt, link, rf)
]

health = (
    "CRITICAL"
    if last_temp >= 42 or last_link < 87
    else "ATTENTION"
    if last_temp >= 39 or last_link < 92
    else "NOMINAL"
)

css_status = (
    "alert" if health == "CRITICAL"
    else "warn" if health == "ATTENTION"
    else ""
)

st.markdown(
    f'<div class="status {css_status}">'
    f'● MISSION HEALTH: {health} &nbsp; | &nbsp; '
    f'SIMULATED GEO COMMUNICATIONS SPACECRAFT &nbsp; | &nbsp; '
    f'NO COMMAND AUTHORITY'
    f'</div>',
    unsafe_allow_html=True
)

# SATELLITE HEALTH METRICS

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Thermal sensor",
    f"{last_temp:.1f} °C",
    help="Fictional equipment temperature, synthetic"
)

m2.metric(
    "Bus voltage",
    f"{last_volt:.2f} V",
    help="Synthetic DC bus voltage"
)

m3.metric(
    "Link quality",
    f"{last_link:.1f}%",
    help="Illustrative composite index, NOT a physical RF measure"
)

m4.metric(
    "RF chain health index",
    f"{last_rf:.1f}/100",
    help="Synthetic monitoring score"
)

BLUE = "#58c6f4"
TEAL = "#55e0cd"
GOLD = "#ffc36b"
RED = "#ff737d"

def chart(
    y,
    name,
    unit,
    threshold=None,
    baseline=None,
    reverse=False
):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            name=name,
            mode="lines",
            line=dict(
                color=TEAL if not reverse else BLUE,
                width=3
            ),
            fill="tozeroy",
            fillcolor="rgba(56,189,203,.06)",
            hovertemplate=(
                "Minute %{x}<br>%{y:.2f} "
                + unit
                + "<extra></extra>"
            )
        )
    )

    if show_baseline and baseline is not None:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=np.full(len(x), baseline),
                name="Nominal reference",
                line=dict(
                    color=BLUE,
                    dash="dot",
                    width=1.6
                )
            )
        )

    if show_baseline and threshold is not None:
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color=GOLD,
            annotation_text="Illustrative warning limit",
            annotation_font_color=GOLD
        )

    fig.update_layout(
        height=285,
        margin=dict(l=10, r=15, t=30, b=10),
        paper_bgcolor="#102238",
        plot_bgcolor="#102238",
        font=dict(color="#e9f4ff", size=12),
        xaxis=dict(
            title="Elapsed minutes",
            gridcolor="#25405b",
            zeroline=False
        ),
        yaxis=dict(
            title=unit,
            gridcolor="#25405b",
            zeroline=False
        ),
        legend=dict(
            orientation="h",
            y=1.20,
            x=0
        ),
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


live_tab, analysis_tab, architecture_tab, roadmap_tab = st.tabs(
    [
        "01 · Operations",
        "02 · HubOS-Sat Analysis",
        "03 · Secure Integration",
        "04 · Partnership Roadmap"
    ]
)

# TAB 1: SATELLITE OPERATIONS

with live_tab:

    a, b = st.columns(2)

    with a:
        st.markdown("### Thermal subsystem")
        chart(
            temp,
            "Equipment temperature",
            "°C",
            39,
            33
        )
        st.caption(
            "Temperature profile is simulated. Actual safe ranges "
            "depend on spacecraft design and sensor placement."
        )

    with b:
        st.markdown("### Communications link health")
        chart(
            link,
            "Link quality index",
            "%",
            92,
            98.4,
            reverse=True
        )
        st.caption(
            "Link quality is a fictional demonstration index, "
            "not Es’hailSat link-margin data."
        )

    c, d = st.columns(2)

    with c:
        st.markdown("### Power bus")
        chart(
            volt,
            "Bus voltage",
            "V",
            None,
            28.2
        )

    with d:
        st.markdown("### RF chain health")
        chart(
            rf,
            "RF health index",
            "points",
            None,
            72,
            reverse=True
        )


# TAB 2: HUBOS-SAT ANALYSIS

with analysis_tab:

    if scenario == "Nominal operations":

        st.success(
            "NO TRIGGER: All monitored demo parameters remain "
            "within illustrative limits."
        )

        headline = "Continue routine monitoring"

        details = (
            "No rule-based alert is triggered. "
            "The fictional telemetry shows small expected fluctuations."
        )

        checks = [
            "Review normal watch list",
            "Retain telemetry history for trend comparisons",
            "Operator keeps full decision authority"
        ]

    elif scenario == "Thermal anomaly":

        st.error(
            "THERMAL RULE TRIGGERED: A sustained temperature rise "
            "crosses the simulated warning limit."
        )

        headline = "Review thermal-control behaviour"

        details = (
            "The simulated rise starts at minute 43. "
            "A threshold violation is visible, but cause and "
            "severity cannot be established from this demonstration."
        )

        checks = [
            "Check redundant temperature measurements",
            "Correlate heater states, sun exposure and power telemetry",
            "Follow Es’hailSat-approved anomaly response procedures"
        ]

    else:

        st.error(
            "LINK RULE TRIGGERED: The composite link-health indicator "
            "deteriorates below the simulated warning limit."
        )

        headline = "Investigate communications degradation"

        details = (
            "A synthetic decline starts at minute 39. "
            "Possible causes cannot be diagnosed without actual RF "
            "measurements, ground information and approved engineering models."
        )

        checks = [
            "Compare real link budget and RF equipment trends",
            "Check ground-terminal weather, pointing and modem alarms",
            "Follow Es’hailSat-approved communications incident procedures"
        ]

    st.markdown(
        f'<div class="panel">'
        f'<div class="panel-title">'
        f'Suggested operator investigation: {headline}'
        f'</div>'
        f'<div class="panel-copy">{details}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("#### Human-in-the-loop checklist")

    for check in checks:
        st.checkbox(
            check,
            key=f"{scenario}-{check}"
        )

    st.markdown(
        '''<div class="panel">
        <div class="panel-title">From concept to actual AI</div>
        <div class="panel-copy">
        <span class="tag">NOW: SIMPLE RULES</span>
        <span class="tag">FUTURE: VALIDATED MODELS</span>
        <p>
        Today’s dashboard uses simple transparent thresholds.
        ReVora proposes to research anomaly detection,
        trend forecasting and digital-twin comparison only
        after obtaining authorized datasets, engineering
        baselines and operator-defined validation criteria.
        </p>
        <p><strong>Measures for a pilot:</strong>
        detection latency, false-alarm rate, engineer
        usefulness, cybersecurity review and reproducibility.
        </p>
        </div></div>''',
        unsafe_allow_html=True
    )


# TAB 3: SECURE SATELLITE INTEGRATION

with architecture_tab:

    st.markdown(
        "### Proposed integration — read-only first"
    )

    p, q, r = st.columns(3)

    with p:
        st.markdown(
            '''<div class="diagram-node">
            <strong>Es’hailSat systems</strong>
            <span>
            Operator-controlled telemetry and ground infrastructure
            </span></div>''',
            unsafe_allow_html=True
        )

    with q:
        st.markdown(
            '''<div class="diagram-node">
            <strong>Approved data boundary</strong>
            <span>
            Permissioned, filtered exports / secure test environment
            </span></div>''',
            unsafe_allow_html=True
        )

    with r:
        st.markdown(
            '''<div class="diagram-node">
            <strong>ReVora HubOS-Sat</strong>
            <span>
            Analytics, visualization and engineer-reviewed recommendations
            </span></div>''',
            unsafe_allow_html=True
        )

    st.info(
        "No uplink path, no spacecraft commands, no assumed "
        "production-network access. Integration subject to "
        "Es’hailSat security and operational approval."
    )

    st.markdown(
        "### Potential co-development modules"
    )

    modules = pd.DataFrame([
        {
            "Module": "Telemetry analytics",
            "Potential objective": (
                "Consolidate historical data and identify trend shifts"
            ),
            "Initial requirement": "Representative authorized dataset"
        },
        {
            "Module": "Anomaly investigation",
            "Potential objective": (
                "Prioritize exceptions and evidence for operator review"
            ),
            "Initial requirement": "Agreed event labels and thresholds"
        },
        {
            "Module": "Digital twin concept",
            "Potential objective": (
                "Compare measured vs modelled thermal or power behaviour"
            ),
            "Initial requirement": (
                "Engineering models and calibration data"
            )
        },
        {
            "Module": "Intelligent operations UI",
            "Potential objective": (
                "Unified operator visualization and decision support"
            ),
            "Initial requirement": (
                "Workflow and cybersecurity requirements"
            )
        },
    ])

    st.dataframe(
        modules,
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Potential capabilities, not integrated or proven deployed "
        "features. Existing spacecraft IP and data remain with their "
        "owners; new software/IP terms require negotiation."
    )


# TAB 4: PARTNERSHIP ROADMAP

with roadmap_tab:

    st.markdown(
        "### Build in Qatar, validate with operators"
    )

    stages = [
        (
            "0–6 months · Scope and technical validation",
            "Select one narrow use case; evaluate HubOS code readiness; "
            "agree NDA, telemetry governance and success criteria."
        ),
        (
            "6–18 months · Isolated pilot",
            "Develop software module; test with historical or simulated "
            "data; measure false alarms and operator utility."
        ),
        (
            "18–36 months · Product qualification",
            "Subject to positive results, advance security review, "
            "integration testing, operating support and commercialization."
        ),
        (
            "36+ months · Broader Qatar capabilities",
            "Explore partner-led mission participation and satellite "
            "subsystems only with confirmed funding, customer demand "
            "and experienced engineering teams."
        ),
    ]

    for title, desc in stages:

        st.markdown(
            f'<div class="step">'
            f'<strong>{title}</strong><br>'
            f'<span>{desc}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        "#### Proposed outcome from today's discussion"
    )

    st.markdown(
        "**Nominate technical counterparts and schedule a workshop "
        "to scope one proof of concept.**"
    )

    st.markdown(
        "**Key questions:** Which operational problem matters most? "
        "What dataset could be shared in a secure evaluation? "
        "What performance criteria would justify a pilot?"
    )


st.divider()

st.caption(
    "ReVora | HubOS-Sat • Concept demonstration for partner discussion "
    "• No proprietary operator data is displayed "
    "• All scenarios and spacecraft are fictional"
)
