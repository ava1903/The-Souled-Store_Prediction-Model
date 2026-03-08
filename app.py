# ─────────────────────────────────────────────────────────────────────────────
#  The Souled Store — Data-Driven Growth Dashboard
#  Single self-contained file. No local imports. No src/ folder needed.
#  Dependencies: streamlit, pandas, numpy, plotly  (all in requirements.txt)
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Souled Store — Growth Dashboard",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand colours ─────────────────────────────────────────────────────────────
TSS_DARK = "#1A1A2E"
TSS_RED  = "#C0392B"
NAVY     = "#1B3A5C"
GREEN    = "#065F46"
BORDER   = "#E5E7EB"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
[data-testid="stSidebar"] {{ background-color: {TSS_DARK}; }}
[data-testid="stSidebar"] * {{ color: white !important; }}
.main .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}
.kpi-card {{
    background: white; border-radius: 10px; padding: 1rem 1.2rem;
    border-left: 5px solid {TSS_RED}; box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}}
.kpi-label {{ font-size: 0.75rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.04em; }}
.kpi-value {{ font-size: 1.8rem; font-weight: 700; color: {TSS_DARK}; line-height: 1.15; }}
.kpi-delta {{ font-size: 0.8rem; margin-top: 0.2rem; }}
.delta-up   {{ color: {GREEN}; }}
.delta-down {{ color: {TSS_RED}; }}
.section-banner {{
    background: linear-gradient(135deg, {TSS_DARK} 0%, {NAVY} 100%);
    color: white; padding: 1rem 1.5rem; border-radius: 10px; margin-bottom: 1.2rem;
}}
.section-banner h2 {{ color: white !important; margin: 0 0 0.15rem 0; font-size: 1.35rem; }}
.section-banner p  {{ color: #CBD5E1; margin: 0; font-size: 0.85rem; }}
.insight {{
    background: #EBF2FF; border-left: 4px solid {NAVY};
    border-radius: 6px; padding: 0.75rem 1rem;
    font-size: 0.88rem; color: {NAVY}; margin: 0.6rem 0;
}}
.impact-bar {{
    background: #F8F9FA; border-radius: 10px; padding: 1rem 1.5rem;
    border: 1px solid {BORDER}; margin-top: 0.8rem;
}}
</style>
""", unsafe_allow_html=True)

# ── Reproducible seed ─────────────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

# ═════════════════════════════════════════════════════════════════════════════
#  DATA GENERATION  (all simulated)
# ═════════════════════════════════════════════════════════════════════════════
FANDOMS = ["Marvel", "DC", "Friends", "Naruto", "Cricket",
           "Brooklyn Nine-Nine", "Harry Potter", "Attack on Titan",
           "The Office", "Game of Thrones"]


@st.cache_data
def make_customers():
    n = 2000
    df = pd.DataFrame({
        "customer_id":    range(1, n + 1),
        "recency_days":   np.random.exponential(45, n).clip(1, 365).astype(int),
        "frequency":      np.random.choice([1, 2, 3, 4, 5, 6, 7, 8], n,
                                            p=[0.35, 0.25, 0.15, 0.10, 0.07, 0.04, 0.03, 0.01]),
        "monetary":       np.random.lognormal(6.5, 0.7, n).clip(200, 15000).round(-1),
        "primary_fandom": np.random.choice(FANDOMS, n,
                                            p=[0.22, 0.15, 0.14, 0.12, 0.10, 0.08, 0.07, 0.05, 0.04, 0.03]),
        "fandom_breadth": np.random.choice([1, 2, 3, 4, 5], n, p=[0.45, 0.28, 0.15, 0.08, 0.04]),
        "is_member":      np.random.choice([True, False], n, p=[0.22, 0.78]),
        "age_group":      np.random.choice(["16-20", "21-25", "26-30", "31-35", "36+"], n,
                                            p=[0.18, 0.32, 0.28, 0.14, 0.08]),
    })
    df["r_score"] = pd.qcut(df["recency_days"], 4, labels=[4, 3, 2, 1]).astype(int)
    df["f_score"] = pd.qcut(df["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    df["m_score"] = pd.qcut(df["monetary"].rank(method="first"),  4, labels=[1, 2, 3, 4]).astype(int)
    df["rfm_total"] = df["r_score"] + df["f_score"] + df["m_score"]
    df["rfm_segment"] = pd.cut(df["rfm_total"], bins=[2, 5, 8, 12],
                                labels=["Low Value", "Mid Value", "High Value"])
    churn_base = (df["recency_days"] / 365) * 0.6 + (1 / df["frequency"]) * 0.3
    df["churn_score"] = (churn_base + np.random.normal(0, 0.05, n)).clip(0, 1).round(2)
    df["churn_risk"] = pd.cut(df["churn_score"], bins=[0, 0.35, 0.65, 1.0],
                               labels=["Low Risk", "Medium Risk", "High Risk"])
    df["predicted_ltv"] = (df["monetary"] * df["frequency"] *
                            (1 + df["fandom_breadth"] * 0.18) *
                            np.random.uniform(0.8, 1.2, n)).round(-2)
    df["persona"]       = np.where(df["frequency"] >= 2, "Fandom Loyalist", "Event Buyer")
    df["uplift_score"]  = np.random.normal(0.12, 0.18, n).clip(-0.4, 0.6).round(3)
    return df


@st.cache_data
def make_revenue():
    months = pd.date_range("2023-01-01", periods=24, freq="MS")
    base   = 25 + np.arange(24) * 0.9
    spikes = np.zeros(24)
    for i in [2, 7, 11, 15, 20, 23]:
        spikes[i] = random.uniform(12, 28)
    actual = (base + spikes + np.random.normal(0, 1.5, 24)).clip(10)
    bau    = base + np.random.normal(0, 0.8, 24)
    df = pd.DataFrame({
        "month":     months,
        "actual":    actual.round(1),
        "bau":       bau.round(1),
        "is_launch": spikes > 0,
    })
    future = pd.date_range("2025-01-01", periods=6, freq="MS")
    fcast  = bau[-6:] * np.linspace(1.02, 1.10, 6)
    df_fc  = pd.DataFrame({"month": future, "forecast": fcast.round(1)})
    offers = pd.DataFrame({
        "offer_type":  ["Mystery Box", "IP Early Access", "Collector Edition", "Free Shipping", "20% Discount"],
        "conv_uplift": [18.4, 16.2, 12.8,  9.3, 21.1],
        "margin_cost": [ 4.2,  1.8,  2.1,  5.6, 18.9],
        "net_uplift":  [14.2, 14.4, 10.7,  3.7,  2.2],
    })
    return df, df_fc, offers


@st.cache_data
def make_transitions():
    rows = []
    for _ in range(600):
        f1     = random.choice(FANDOMS)
        others = [f for f in FANDOMS if f != f1]
        f2     = random.choice(others)
        rows.append({"from": f1, "to": f2, "count": random.randint(15, 180)})
    df = pd.DataFrame(rows).groupby(["from", "to"], as_index=False)["count"].sum()
    return df.sort_values("count", ascending=False).head(12)


customers   = make_customers()
rev_df, rev_fc, offers_df = make_revenue()
transitions = make_transitions()

# ═════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═════════════════════════════════════════════════════════════════════════════
def kpi(label, value, delta="", good=True, color=TSS_RED):
    d_cls  = "delta-up" if good else "delta-down"
    arrow  = "▲" if good else "▼"
    d_html = f'<div class="kpi-delta {d_cls}">{arrow} {delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color:{color};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {d_html}
    </div>""", unsafe_allow_html=True)


def insight(txt):
    st.markdown(f'<div class="insight">💡 {txt}</div>', unsafe_allow_html=True)


def banner(title, subtitle, icon=""):
    st.markdown(f"""
    <div class="section-banner">
        <h2>{icon} {title}</h2>
        <p>{subtitle}</p>
    </div>""", unsafe_allow_html=True)


def impact(items):
    parts = "  ·  ".join(
        [f"<b style='color:{TSS_RED};'>{k}:</b> {v}" for k, v in items.items()]
    )
    st.markdown(
        f'<div class="impact-bar">🎯 <b>Expected Impact</b> &nbsp;|&nbsp; {parts}</div>',
        unsafe_allow_html=True,
    )


def chart_style(fig, h=300):
    fig.update_layout(
        height=h,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=5, r=5, t=15, b=5),
        legend=dict(orientation="h", y=-0.28, font_size=11),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#F3F4F6")
    return fig


# ═════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.2rem 0 1rem 0;'>
        <div style='font-size:2rem;'>🎭</div>
        <div style='font-size:1.05rem;font-weight:700;color:white;'>The Souled Store</div>
        <div style='font-size:0.75rem;color:#F87171;margin-top:0.2rem;'>Data-Driven Growth Dashboard</div>
    </div>
    <hr style='border-color:#374151;margin:0.5rem 0 1rem 0;'>
    """, unsafe_allow_html=True)

    page = st.radio("Go to", [
        "🏠  Company Overview",
        "🎯  Solution 1: Cross-Fandom Discovery",
        "📉  Solution 2: Churn Prevention",
        "📈  Solution 3: Revenue Diversification",
    ], label_visibility="collapsed")

    st.markdown("""
    <hr style='border-color:#374151;margin:1rem 0 0.8rem 0;'>
    <div style='font-size:0.73rem;color:#9CA3AF;'>
        <b style='color:#CBD5E1;'>Course:</b> Data-Driven Growth with Python<br>
        <b style='color:#CBD5E1;'>Framework:</b> Karaman 9-Article Series<br>
        <b style='color:#CBD5E1;'>Data:</b> Simulated (Demo)<br><br>
        <b style='color:#CBD5E1;'>Team:</b> Avantika · Vivek<br>
        Nivedhitha · Atharva · Naman
    </div>
    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — COMPANY OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if "Company Overview" in page:
    banner("Company Overview",
           "North Star Metric: Monthly Repeat Purchase Revenue  ·  FY25 Revenue ~₹500 Cr", "🏠")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("FY25 Revenue (est.)", "₹500 Cr",    "+38.9% vs FY24",        True,  TSS_RED)
    with c2: kpi("Monthly Online Orders","~2.5 Lakh",  "Growing MoM",           True,  NAVY)
    with c3: kpi("Active IP Licenses",  "150+",        "Marvel, DC, Anime…",    True,  GREEN)
    with c4: kpi("Retail Stores",       "18+",         "Target 40 stores FY26", True,  "#92400E")

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.1, 0.9])

    with left:
        st.subheader("📊 North Star Metric — Monthly Repeat Purchase Revenue")
        months = pd.date_range("2023-01-01", periods=24, freq="MS")
        rng    = np.random.default_rng(1)
        repeat = (15 + np.arange(24) * 0.6 + rng.normal(0, 1.2, 24)).clip(10)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=months, y=rev_df["actual"],
                              name="Total Revenue", marker_color="#CBD5E1", opacity=0.55))
        fig.add_trace(go.Scatter(x=months, y=repeat,
                                  name="Repeat Purchase Revenue (NSM)",
                                  line=dict(color=TSS_RED, width=3),
                                  mode="lines+markers", marker=dict(size=5)))
        chart_style(fig, 320)
        fig.update_layout(xaxis_title="Month", yaxis_title="₹ Crore")
        st.plotly_chart(fig, use_container_width=True)
        insight("Repeat Purchase Revenue is the North Star — it captures whether customers are coming back, not just whether a new IP drop spiked total sales.")

    with right:
        st.subheader("👥 Customer Age Groups")
        age = customers["age_group"].value_counts().reset_index()
        age.columns = ["age_group", "count"]
        fig2 = px.pie(age, names="age_group", values="count", hole=0.45,
                      color_discrete_sequence=[TSS_DARK, TSS_RED, NAVY, GREEN, "#9F7AEA"])
        fig2.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0),
                            legend=dict(orientation="h", y=-0.2, font_size=11))
        fig2.update_traces(textinfo="percent", textfont_size=11)
        st.plotly_chart(fig2, use_container_width=True)

        st.caption("Top fandoms by customer count")
        top_f = customers["primary_fandom"].value_counts().head(6).reset_index()
        top_f.columns = ["fandom", "count"]
        fig3 = px.bar(top_f, x="count", y="fandom", orientation="h",
                      color="count", color_continuous_scale=["#FDEDEC", TSS_RED],
                      labels={"count": "Customers", "fandom": ""})
        fig3.update_layout(height=195, plot_bgcolor="white", paper_bgcolor="white",
                            coloraxis_showscale=False, margin=dict(l=0, r=0, t=0, b=0))
        fig3.update_xaxes(showgrid=False)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔍 Three Core Problems This Project Addresses")
    p1, p2, p3 = st.columns(3)
    cards = [
        (TSS_RED, "#FDEDEC", "Problem 1", "Single-Fandom Purchase Trap",
         "45% of customers have only ever bought from one IP. They're loyal but unexplored.", "Articles 2, 3, 5"),
        (GREEN,   "#ECFDF5", "Problem 2", "Post-First-Purchase Churn",
         "D2C brands average ~28% retention. Many customers buy once and never return.",      "Articles 2, 3, 4, 5, 8"),
        (NAVY,    "#EBF2FF", "Problem 3", "IP Launch Revenue Spikes",
         "~60% of GMV comes from IP launch windows. Revenue collapses in between.",           "Articles 6, 7, 8, 9"),
    ]
    for col, (accent, bg, num, title, desc, arts) in zip([p1, p2, p3], cards):
        with col:
            st.markdown(f"""
            <div style='background:{bg};border-radius:10px;padding:1rem;border-top:4px solid {accent};'>
                <div style='font-weight:700;color:{TSS_DARK};font-size:0.95rem;'>{num}</div>
                <div style='font-weight:600;color:{accent};margin:0.35rem 0 0.5rem 0;'>{title}</div>
                <div style='font-size:0.83rem;color:#374151;'>{desc}</div>
                <div style='margin-top:0.7rem;font-size:0.8rem;'><b>Articles:</b> {arts}</div>
            </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — SOLUTION 1
# ═════════════════════════════════════════════════════════════════════════════
elif "Solution 1" in page:
    banner("Solution 1: Cross-Fandom Discovery Engine",
           "RFM Segmentation (Article 2)  ·  LTV Prediction (Article 3)  ·  Next Purchase Category Predictor (Article 5)",
           "🎯")

    single_pct  = round((customers["fandom_breadth"] == 1).mean() * 100, 1)
    hv_single   = customers[(customers["rfm_segment"] == "High Value") & (customers["fandom_breadth"] == 1)]
    avg_breadth = round(customers["fandom_breadth"].mean(), 2)
    multi_ltv   = customers[customers["fandom_breadth"] >= 2]["predicted_ltv"].mean()
    single_ltv  = customers[customers["fandom_breadth"] == 1]["predicted_ltv"].mean()
    ltv_uplift  = round((multi_ltv / single_ltv - 1) * 100, 1)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Single-Fandom Customers",   f"{single_pct}%",       "Primary target group",       False, TSS_RED)
    with c2: kpi("High-Value, Single-Fandom", f"{len(hv_single):,}",  "Highest-upside cohort",      True,  NAVY)
    with c3: kpi("Avg. Fandom Breadth Score", f"{avg_breadth}",       "Target: 1.8 in 12 months",   True,  GREEN)
    with c4: kpi("LTV Uplift (Multi vs Single)", f"+{ltv_uplift}%",   "Validates business case",    True,  "#9F7AEA")

    st.markdown("<br>", unsafe_allow_html=True)
    l, r = st.columns(2)

    with l:
        st.subheader("👥 RFM Segments × Fandom Breadth")
        rfm_b = customers.groupby(["rfm_segment", "fandom_breadth"]).size().reset_index(name="count")
        fig = px.bar(rfm_b, x="rfm_segment", y="count", color="fandom_breadth",
                     barmode="group",
                     color_continuous_scale=["#FDEDEC", "#C0392B", "#7B241C"],
                     labels={"rfm_segment": "RFM Segment", "count": "Customers", "fandom_breadth": "Fandom Breadth"},
                     category_orders={"rfm_segment": ["Low Value", "Mid Value", "High Value"]})
        chart_style(fig)
        fig.update_layout(yaxis_title="No. of Customers")
        st.plotly_chart(fig, use_container_width=True)
        insight("High Value customers with Fandom Breadth = 1 are the primary target — loyal buyers who haven't been shown other IPs yet.")

    with r:
        st.subheader("💰 LTV: Single vs Multi-Fandom Buyers")
        ltv_df = customers.copy()
        ltv_df["type"] = ltv_df["fandom_breadth"].apply(
            lambda x: "Single-Fandom" if x == 1 else "Multi-Fandom (2+ IPs)"
        )
        fig2 = px.box(ltv_df, x="type", y="predicted_ltv", color="type",
                      color_discrete_map={"Single-Fandom": "#CBD5E1", "Multi-Fandom (2+ IPs)": TSS_RED},
                      labels={"predicted_ltv": "Predicted LTV (₹)", "type": ""})
        chart_style(fig2)
        fig2.update_layout(showlegend=False, yaxis_title="Predicted LTV (₹)")
        st.plotly_chart(fig2, use_container_width=True)
        insight(f"Multi-fandom customers show ~{ltv_uplift}% higher predicted LTV — confirming the case for cross-fandom recommendations.")

    l2, r2 = st.columns(2)

    with l2:
        st.subheader("🔄 Top Fandom-to-Fandom Transitions")
        trans       = transitions.copy()
        trans["pair"] = trans["from"] + " → " + trans["to"]
        fig3 = px.bar(trans, x="count", y="pair", orientation="h",
                      color="count", color_continuous_scale=["#FDEDEC", TSS_RED],
                      labels={"count": "Customers", "pair": ""})
        chart_style(fig3, 320)
        fig3.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

    with r2:
        st.subheader("📊 Fandom Breadth Distribution")
        bd = customers["fandom_breadth"].value_counts().sort_index().reset_index()
        bd.columns = ["breadth", "count"]
        bd["label"] = bd["breadth"].map(
            {1: "1 IP (Target)", 2: "2 IPs", 3: "3 IPs", 4: "4 IPs", 5: "5 IPs"}
        )
        fig4 = px.bar(bd, x="label", y="count",
                      color="breadth",
                      color_continuous_scale=["#C0392B", "#1B3A5C", "#065F46", "#9F7AEA", "#92400E"],
                      labels={"label": "", "count": "Customers"})
        chart_style(fig4, 320)
        fig4.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

    impact({
        "Fandom Breadth":         "1.2 → 1.8 (12 months)",
        "Repeat Revenue Uplift":  "+20–25% in High Value cohort",
        "Cross-Fandom CTR Target": ">8%",
    })


# ═════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — SOLUTION 2
# ═════════════════════════════════════════════════════════════════════════════
elif "Solution 2" in page:
    banner("Solution 2: Multi-Layer Churn Prevention Pipeline",
           "Churn Prediction (Articles 4,5)  ·  Persona Segmentation (Article 2)  ·  LTV Budget (Article 3)  ·  Uplift Modelling (Article 8)",
           "📉")

    high_risk   = int((customers["churn_risk"] == "High Risk").sum())
    rev_at_risk = round(customers[customers["churn_risk"] == "High Risk"]["predicted_ltv"].sum() / 1e5, 1)
    persuadable = int((customers["uplift_score"] > 0).sum())
    sure_thing  = int((customers["uplift_score"] <= 0).sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("High Churn Risk",        f"{high_risk:,}",    f"{round(high_risk/len(customers)*100,1)}% of base", False, TSS_RED)
    with c2: kpi("Revenue at Risk",        f"₹{rev_at_risk}L",  "Total LTV of high-risk segment",                   False, "#92400E")
    with c3: kpi("Persuadable Customers",  f"{persuadable:,}",  "Worth sending an offer to",                        True,  GREEN)
    with c4: kpi("Sure-Things (skip)",     f"{sure_thing:,}",   "Would buy anyway — save margin",                   True,  NAVY)

    st.markdown("<br>", unsafe_allow_html=True)
    l, r = st.columns(2)

    with l:
        st.subheader("⚠️ Churn Risk by Buyer Persona")
        pr = customers.groupby(["persona", "churn_risk"]).size().reset_index(name="count")
        fig = px.bar(pr, x="persona", y="count", color="churn_risk", barmode="stack",
                     color_discrete_map={
                         "Low Risk":    "#DCFCE7",
                         "Medium Risk": "#FEF9C3",
                         "High Risk":   TSS_RED,
                     },
                     labels={"persona": "", "count": "Customers", "churn_risk": "Risk Level"})
        chart_style(fig)
        fig.update_layout(yaxis_title="Customers")
        st.plotly_chart(fig, use_container_width=True)
        insight("Event Buyers (one purchase during a launch) have far higher churn rates — they need a separate retention playbook from day one.")

    with r:
        st.subheader("🎯 Uplift Score Distribution  (Article 8)")
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=customers[customers["uplift_score"] > 0]["uplift_score"],
            name="Persuadable — send offer",
            marker_color=TSS_RED, opacity=0.8, nbinsx=25,
        ))
        fig2.add_trace(go.Histogram(
            x=customers[customers["uplift_score"] <= 0]["uplift_score"],
            name="Skip — Sure Thing / Lost Cause",
            marker_color="#CBD5E1", opacity=0.8, nbinsx=25,
        ))
        fig2.add_vline(x=0, line_dash="dash", line_color=NAVY, line_width=2,
                       annotation_text="Uplift Threshold = 0",
                       annotation_position="top right")
        fig2.update_layout(barmode="overlay",
                            xaxis_title="Uplift Score", yaxis_title="Customers")
        chart_style(fig2)
        st.plotly_chart(fig2, use_container_width=True)
        insight("Only customers to the right of the line receive discount offers — everyone else gets content-only communication.")

    l2, r2 = st.columns(2)

    with l2:
        st.subheader("💸 LTV-Weighted Retention Budget")
        budget = pd.DataFrame({
            "Segment":       ["High LTV + High Risk", "Mid LTV + High Risk", "Low LTV + High Risk",
                               "High LTV + Medium Risk", "Mid/Low + Medium Risk"],
            "Max Spend (₹)": [150, 80, 0, 60, 0],
            "Channel":       ["Push + Email + WhatsApp", "Email + App", "Email (content only)",
                               "Push notification", "Email (content only)"],
        })
        fig3 = px.bar(budget, x="Max Spend (₹)", y="Segment", orientation="h",
                      color="Max Spend (₹)",
                      color_continuous_scale=["#F3F4F6", "#C0392B"],
                      text="Channel")
        fig3.update_traces(textposition="inside", textfont_size=10)
        chart_style(fig3, 300)
        fig3.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

    with r2:
        st.subheader("🔄 Churn Risk Distribution")
        rc = customers["churn_risk"].value_counts().reset_index()
        rc.columns = ["risk", "count"]
        fig4 = px.pie(rc, names="risk", values="count", hole=0.5,
                      color="risk",
                      color_discrete_map={
                          "Low Risk":    GREEN,
                          "Medium Risk": "#F59E0B",
                          "High Risk":   TSS_RED,
                      })
        fig4.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                            legend=dict(orientation="h", y=-0.15))
        fig4.update_traces(textinfo="percent+label", textfont_size=12)
        st.plotly_chart(fig4, use_container_width=True)

    impact({
        "Retention Rate":          "~28% → 40%+",
        "2nd-Purchase Conversion": "+15–20 pp (90-day window)",
        "Campaign ROI":            "+30–40% via Uplift targeting",
    })


# ═════════════════════════════════════════════════════════════════════════════
#  PAGE 4 — SOLUTION 3
# ═════════════════════════════════════════════════════════════════════════════
elif "Solution 3" in page:
    banner("Solution 3: Revenue Diversification",
           "LSTM Forecasting (Article 6)  ·  Market Response Models (Article 7)  ·  A/B Testing (Article 9)",
           "📈")

    launch_rev_pct = round(rev_df[rev_df["is_launch"]]["actual"].sum() / rev_df["actual"].sum() * 100, 1)
    avg_inter      = round(rev_df[~rev_df["is_launch"]]["actual"].mean(), 1)
    best_offer     = offers_df.loc[offers_df["net_uplift"].idxmax(), "offer_type"]
    launch_count   = int(rev_df["is_launch"].sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("IP Launch Months (24M)",   f"{launch_count}",       f"{launch_rev_pct}% of total GMV",    False, TSS_RED)
    with c2: kpi("Avg. Inter-Launch Revenue", f"₹{avg_inter} Cr/mo",  "Target: +25–30%",                    False, "#92400E")
    with c3: kpi("Best Non-Discount Lever",   best_offer,              "Highest net revenue uplift",         True,  GREEN)
    with c4: kpi("Discount vs Alternatives",  "8× worse ROI",         "20% discount vs Early Access",       False, NAVY)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Revenue: Actual vs BAU Baseline  (LSTM Forecast — Article 6)")

    fig = go.Figure()
    for _, row in rev_df[rev_df["is_launch"]].iterrows():
        fig.add_vrect(
            x0=row["month"] - timedelta(days=15),
            x1=row["month"] + timedelta(days=15),
            fillcolor="rgba(192,57,43,0.07)", line_width=0,
        )
    fig.add_trace(go.Scatter(
        x=rev_df["month"], y=rev_df["bau"],
        name="BAU Baseline (LSTM)", mode="lines",
        line=dict(color=NAVY, width=2, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=rev_df["month"], y=rev_df["actual"],
        name="Actual Revenue", mode="lines+markers",
        line=dict(color=TSS_RED, width=2.5), marker=dict(size=5),
    ))
    fig.add_trace(go.Scatter(
        x=rev_fc["month"], y=rev_fc["forecast"],
        name="6-Month Forecast", mode="lines+markers",
        line=dict(color=GREEN, width=2, dash="dash"),
        marker=dict(symbol="diamond", size=7),
    ))
    for _, row in rev_df[rev_df["is_launch"]].iterrows():
        fig.add_annotation(x=row["month"], y=row["actual"] + 1.5,
                            text="🚀", showarrow=False, font=dict(size=13))
    chart_style(fig, 360)
    fig.update_layout(xaxis_title="Month", yaxis_title="Revenue (₹ Crore)",
                       legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)
    insight("🚀 marks IP launch months. The gap between BAU baseline and actuals in non-launch months is the revenue shortfall our inter-launch campaigns are designed to fill.")

    l, r = st.columns(2)

    with l:
        st.subheader("🎁 Offer Type ROI Comparison  (Article 7)")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name="Conversion Uplift (%)", x=offers_df["offer_type"],
            y=offers_df["conv_uplift"], marker_color="#CBD5E1",
        ))
        fig2.add_trace(go.Bar(
            name="Margin Cost (%)", x=offers_df["offer_type"],
            y=offers_df["margin_cost"], marker_color=TSS_RED, opacity=0.75,
        ))
        fig2.add_trace(go.Scatter(
            name="Net Uplift", x=offers_df["offer_type"],
            y=offers_df["net_uplift"], mode="lines+markers+text",
            text=[str(v) for v in offers_df["net_uplift"]],
            textposition="top center",
            line=dict(color=NAVY, width=2.5), marker=dict(size=8),
        ))
        fig2.update_layout(barmode="group", yaxis_title="% Uplift / Cost")
        chart_style(fig2, 320)
        fig2.update_layout(xaxis_tickangle=-15)
        st.plotly_chart(fig2, use_container_width=True)
        insight("Mystery Box and IP Early Access match a 20% discount on conversion — at a fraction of the margin cost. These are the levers to scale.")

    with r:
        st.subheader("🧪 A/B Test Tracker  (Article 9)")
        ab = pd.DataFrame({
            "Campaign":         ["Mystery Box vs Discount", "Early Access vs No Offer",
                                  "Perennial Friends Campaign", "Membership Invite Email"],
            "Status":           ["✅ Passed (p=0.031)", "✅ Passed (p=0.018)",
                                  "⏳ Running", "📋 Planned"],
            "Net Rev/Customer": ["₹142 vs ₹119", "₹138 vs ₹101", "—", "—"],
            "Decision":         ["Scale Mystery Box", "Scale Early Access", "Awaiting", "Awaiting"],
        })
        st.dataframe(ab, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("💳 Membership Programme Funnel")
        funnel = pd.DataFrame({
            "Stage": ["Active Customers", "Targeted", "Clicked", "Converted to Member"],
            "Count": [2000, 900, 420, 180],
        })
        fig3 = px.funnel(funnel, x="Count", y="Stage",
                          color_discrete_sequence=[TSS_DARK, NAVY, TSS_RED, GREEN])
        fig3.update_layout(height=230, paper_bgcolor="white",
                            margin=dict(l=5, r=5, t=10, b=5))
        st.plotly_chart(fig3, use_container_width=True)

    impact({
        "IP-Launch Dependency":      "~60% → <40% of GMV",
        "Inter-Launch Revenue":      "+25–30% vs baseline",
        "Membership Revenue Target": "₹15–20 Cr by Year 2",
    })
