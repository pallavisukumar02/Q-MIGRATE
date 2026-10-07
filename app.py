from pathlib import Path
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from scanner import scan_text
from risk_engine import score_assets, prioritize
from quantum_optimizer import run_qaoa_demo

st.set_page_config(page_title="Q-MIGRATE", page_icon="🔐", layout="wide")

st.title("🔐 Q-MIGRATE")
st.caption("Quantum-Safe Migration Intelligence for Enterprise Infrastructure")

st.info(
    "Prototype: discover cryptographic usage, estimate migration priority, "
    "visualize dependencies, and demonstrate a quantum optimization circuit."
)

uploaded = st.file_uploader("Upload source/config files", type=["py","js","java","txt","yaml","yml","json","conf","cfg"], accept_multiple_files=True)

if uploaded:
    records = []
    combined = ""
    for f in uploaded:
        text = f.read().decode("utf-8", errors="ignore")
        combined += f"\n# FILE: {f.name}\n{text}"
        records.extend(scan_text(text, f.name))
else:
    sample = Path("sample_project").glob("*")
    records = []
    combined = ""
    for p in sample:
        if p.is_file():
            text = p.read_text(errors="ignore")
            combined += f"\n# FILE: {p.name}\n{text}"
            records.extend(scan_text(text, p.name))

df = pd.DataFrame(records)

if df.empty:
    st.warning("No cryptographic patterns detected. Upload a source/config file.")
    st.stop()

scored = score_assets(df)
prioritized = prioritize(scored)

c1,c2,c3,c4 = st.columns(4)
c1.metric("Crypto assets", len(prioritized))
c2.metric("High priority", int((prioritized["priority"]=="CRITICAL").sum()))
c3.metric("Quantum-vulnerable", int(prioritized["quantum_vulnerable"].sum()))
c4.metric("Avg risk", f'{prioritized["risk_score"].mean():.1f}/100')

st.subheader("1. Cryptographic Inventory")
st.dataframe(
    prioritized[["asset","algorithm","file","category","quantum_vulnerable","risk_score","priority","recommended_action"]],
    use_container_width=True,
    hide_index=True
)

st.subheader("2. Migration Priority")
chart = go.Figure(go.Bar(
    x=prioritized["asset"],
    y=prioritized["risk_score"],
    text=prioritized["priority"],
    textposition="auto"
))
chart.update_layout(xaxis_title="Cryptographic asset", yaxis_title="Risk score")
st.plotly_chart(chart, use_container_width=True)

st.subheader("3. Migration Blast Radius")

st.write(
    "Estimate the downstream components that may be affected when "
    "a vulnerable cryptographic asset is migrated."
)

blast_radius = {
    "ECDH @ gateway.conf:4": [
        "API Gateway",
        "Payment Service",
        "Mobile Client",
    ],
    "ECDH @ payment_service.py:3": [
        "Payment Service",
        "Transaction API",
        "Database Connector",
    ],
    "RSA @ app.py:1": [
        "Authentication Service",
        "API Gateway",
    ],
    "RSA @ app.py:5": [
        "Authentication Service",
        "Certificate Service",
    ],
    "RSA @ app.py:7": [
        "Authentication Service",
        "Legacy Client",
    ],
}

selected_asset = st.selectbox(
    "Select a cryptographic asset",
    list(blast_radius.keys())
)

affected = blast_radius[selected_asset]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Migration Blast Radius", len(affected))

with col2:
    st.metric("Quantum Vulnerable", "YES")

with col3:
    st.metric("Priority", "P0")

st.subheader("Affected Components")

for component in affected:
    st.write(f"🔗 {component}")

st.info(
    "Migration recommendation: evaluate a validated post-quantum "
    "alternative such as ML-KEM for key establishment or ML-DSA "
    "for digital signatures, depending on the cryptographic role."
)

st.subheader("4. Quantum Optimization Demonstration")
st.write(
    "We formulate migration prioritization as a small binary optimization problem: "
    "select the most important vulnerable assets under a limited migration budget."
)
st.write(
    "The migration planner treats asset selection as a constrained "
    "optimization problem: maximize migration value while staying "
    "within a limited migration budget."
)

budget = st.slider(
    "Migration budget — assets to prioritize",
    min_value=1,
    max_value=min(5, len(prioritized)),
    value=min(3, len(prioritized)),
)

if st.button("Run quantum migration optimizer"):
    result = run_qaoa_demo(prioritized, budget)

    st.subheader("Quantum Circuit")
    st.code(result["circuit"])

    st.subheader("Optimization Result")

    st.success(
        f"Quantum simulation selected candidate assets: "
        f"{result['selection']}"
    )

    st.info(
        f"Migration budget: {budget} asset(s). "
        "In the production system, the optimization objective would "
        "combine quantum exposure, business criticality, dependency "
        "impact and migration cost."
    )