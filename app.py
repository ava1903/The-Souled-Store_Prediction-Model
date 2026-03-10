# ─────────────────────────────────────────────────────────────────────────────
#  The Souled Store — Data-Driven Growth Dashboard
#  Light theme  ·  TSS brand colours  ·  Fully interactive
#  No local imports. pip install streamlit pandas numpy plotly
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import timedelta
from math import erfc, sqrt

st.set_page_config(
    page_title="The Souled Store — Growth Dashboard",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── TSS Brand Palette ─────────────────────────────────────────────────────────
# Primary: TSS Red  |  Black  |  White  |  Light grey backgrounds
TSS_RED    = "#E8192C"   # exact TSS brand red
TSS_BLACK  = "#1A1A1A"
TSS_WHITE  = "#FFFFFF"
TSS_GREY   = "#F5F5F5"
TSS_MGREY  = "#E0E0E0"
TSS_DGREY  = "#6B6B6B"
TSS_RED_LT = "#FFF0F1"   # very light red tint for backgrounds
TSS_RED_MD = "#FCDCDF"   # medium red tint

# Chart accent colours (kept minimal — red leads)
CHART_2    = "#FF6B6B"   # lighter red for second series
CHART_3    = "#2D2D2D"   # near-black for third series
CHART_4    = "#9E9E9E"   # grey for neutral series
CHART_5    = "#FFB3B8"   # pale red

# ── CSS — light, clean, TSS-branded ──────────────────────────────────────────
st.markdown(f"""
<style>
/* ── Base ── */
.main .block-container {{
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: {TSS_BLACK};
    border-right: 3px solid {TSS_RED};
}}
[data-testid="stSidebar"] * {{ color: {TSS_WHITE} !important; }}
[data-testid="stSidebar"] .stRadio > label {{ color: #BBBBBB !important; font-size: 0.82rem; }}
[data-testid="stSidebar"] .stMultiSelect span,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label {{ color: #AAAAAA !important; font-size: 0.78rem; }}
[data-testid="stSidebar"] hr {{ border-color: #333333 !important; }}

/* ── KPI cards ── */
.kpi {{
    background: {TSS_WHITE};
    border-radius: 8px;
    padding: 1rem 1.1rem;
    border-top: 4px solid {TSS_RED};
    border: 1px solid {TSS_MGREY};
    border-top: 4px solid {TSS_RED};
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}}
.kpi .lbl {{
    font-size: 0.7rem;
    color: {TSS_DGREY};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
}}
.kpi .val {{
    font-size: 1.75rem;
    font-weight: 700;
    color: {TSS_BLACK};
    line-height: 1.15;
    margin: 0.2rem 0;
}}
.kpi .dlt {{ font-size: 0.76rem; font-weight: 500; }}
.up {{ color: #1E7E34; }}
.dn {{ color: {TSS_RED}; }}

/* ── Section banner ── */
.banner {{
    background: {TSS_BLACK};
    border-left: 6px solid {TSS_RED};
    padding: 0.85rem 1.3rem;
    border-radius: 8px;
    margin-bottom: 1.1rem;
}}
.banner h2 {{
    color: {TSS_WHITE} !important;
    margin: 0 0 0.1rem 0;
    font-size: 1.25rem;
    font-weight: 700;
}}
.banner p {{ color: #AAAAAA; margin: 0; font-size: 0.8rem; }}

/* ── Insight box ── */
.insight {{
    background: {TSS_RED_LT};
    border-left: 4px solid {TSS_RED};
    border-radius: 6px;
    padding: 0.6rem 0.9rem;
    font-size: 0.84rem;
    color: {TSS_BLACK};
    margin: 0.5rem 0;
}}

/* ── Impact bar ── */
.impact {{
    background: {TSS_GREY};
    border-radius: 8px;
    padding: 0.85rem 1.3rem;
    border: 1px solid {TSS_MGREY};
    margin-top: 0.8rem;
    font-size: 0.87rem;
}}

/* ── Simulator box ── */
.sim-box {{
    background: {TSS_WHITE};
    border-radius: 8px;
    padding: 1rem 1.2rem;
    border: 2px solid {TSS_RED};
    box-shadow: 0 2px 10px rgba(232,25,44,0.08);
    margin-bottom: 0.5rem;
}}

/* ── Tags / pills ── */
.pill {{
    display: inline-block;
    background: {TSS_RED};
    color: white;
    border-radius: 20px;
    padding: 0.15rem 0.65rem;
    font-size: 0.72rem;
    font-weight: 600;
    margin-right: 0.3rem;
}}
.pill-grey {{
    background: {TSS_MGREY};
    color: {TSS_BLACK};
}}

/* ── Problem cards ── */
.prob-card {{
    background: {TSS_WHITE};
    border-radius: 10px;
    padding: 1rem 1.1rem;
    border: 1px solid {TSS_MGREY};
    border-top: 5px solid {TSS_RED};
    height: 100%;
}}

/* ── Customer lookup result ── */
.lookup-result {{
    background: {TSS_WHITE};
    border-radius: 8px;
    padding: 1rem;
    border: 2px solid {TSS_MGREY};
    margin-top: 0.5rem;
}}
</style>
""", unsafe_allow_html=True)

# ── Seed ─────────────────────────────────────────────────────────────────────
np.random.seed(42); random.seed(42)

FANDOMS = ["Marvel","DC","Friends","Naruto","Cricket",
           "Brooklyn Nine-Nine","Harry Potter","Attack on Titan","The Office","Game of Thrones"]

# ═════════════════════════════════════════════════════════════════════════════
#  DATA
# ═════════════════════════════════════════════════════════════════════════════
@st.cache_data
def make_customers():
    n = 2000
    df = pd.DataFrame({
        "customer_id":    range(1, n+1),
        "recency_days":   np.random.exponential(45,n).clip(1,365).astype(int),
        "frequency":      np.random.choice([1,2,3,4,5,6,7,8],n,p=[.35,.25,.15,.10,.07,.04,.03,.01]),
        "monetary":       np.random.lognormal(6.5,.7,n).clip(200,15000).round(-1),
        "primary_fandom": np.random.choice(FANDOMS,n,p=[.22,.15,.14,.12,.10,.08,.07,.05,.04,.03]),
        "fandom_breadth": np.random.choice([1,2,3,4,5],n,p=[.45,.28,.15,.08,.04]),
        "age_group":      np.random.choice(["16-20","21-25","26-30","31-35","36+"],n,
                                            p=[.18,.32,.28,.14,.08]),
        "is_member":      np.random.choice([True,False],n,p=[.22,.78]),
        "city":           np.random.choice(["Mumbai","Delhi","Bangalore","Hyderabad","Chennai","Others"],
                                            n,p=[.22,.20,.18,.15,.12,.13]),
    })
    df["r_score"] = pd.qcut(df["recency_days"],4,labels=[4,3,2,1]).astype(int)
    df["f_score"] = pd.qcut(df["frequency"].rank(method="first"),4,labels=[1,2,3,4]).astype(int)
    df["m_score"] = pd.qcut(df["monetary"].rank(method="first"),4,labels=[1,2,3,4]).astype(int)
    df["rfm_total"]   = df["r_score"]+df["f_score"]+df["m_score"]
    df["rfm_segment"] = pd.cut(df["rfm_total"],bins=[2,5,8,12],
                                labels=["Low Value","Mid Value","High Value"])
    churn = (df["recency_days"]/365)*.6+(1/df["frequency"])*.3
    df["churn_score"] = (churn+np.random.normal(0,.05,n)).clip(0,1).round(2)
    df["churn_risk"]  = pd.cut(df["churn_score"],bins=[0,.35,.65,1.],
                                labels=["Low Risk","Medium Risk","High Risk"])
    df["predicted_ltv"] = (df["monetary"]*df["frequency"]*(1+df["fandom_breadth"]*.18)*
                            np.random.uniform(.8,1.2,n)).round(-2)
    df["persona"]       = np.where(df["frequency"]>=2,"Fandom Loyalist","Event Buyer")
    df["uplift_score"]  = np.random.normal(.12,.18,n).clip(-.4,.6).round(3)
    return df

@st.cache_data
def make_revenue():
    months = pd.date_range("2023-01-01",periods=24,freq="MS")
    base   = 25+np.arange(24)*.9
    spikes = np.zeros(24)
    for i in [2,7,11,15,20,23]: spikes[i]=random.uniform(12,28)
    actual = (base+spikes+np.random.normal(0,1.5,24)).clip(10)
    bau    = base+np.random.normal(0,.8,24)
    df = pd.DataFrame({"month":months,"actual":actual.round(1),
                        "bau":bau.round(1),"is_launch":spikes>0})
    future = pd.date_range("2025-01-01",periods=6,freq="MS")
    df_fc  = pd.DataFrame({"month":future,
                            "forecast":(bau[-6:]*np.linspace(1.02,1.10,6)).round(1)})
    offers = pd.DataFrame({
        "offer_type":  ["Mystery Box","IP Early Access","Collector Edition","Free Shipping","20% Discount"],
        "conv_uplift": [18.4,16.2,12.8,9.3,21.1],
        "margin_cost": [4.2,1.8,2.1,5.6,18.9],
        "net_uplift":  [14.2,14.4,10.7,3.7,2.2],
    })
    return df, df_fc, offers

@st.cache_data
def make_transitions():
    rows=[]
    for _ in range(600):
        f1=random.choice(FANDOMS); f2=random.choice([f for f in FANDOMS if f!=f1])
        rows.append({"from":f1,"to":f2,"count":random.randint(15,180)})
    df=pd.DataFrame(rows).groupby(["from","to"],as_index=False)["count"].sum()
    return df.sort_values("count",ascending=False).head(15)

customers=make_customers(); rev_df,rev_fc,offers_df=make_revenue(); transitions=make_transitions()

# ═════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═════════════════════════════════════════════════════════════════════════════
def kpi(label, value, delta="", good=True, accent=TSS_RED):
    cls = "up" if good else "dn"
    arrow = "▲" if good else "▼"
    d = f'<div class="dlt {cls}">{arrow} {delta}</div>' if delta else ""
    st.markdown(
        f'<div class="kpi" style="border-top-color:{accent};">'
        f'<div class="lbl">{label}</div><div class="val">{value}</div>{d}</div>',
        unsafe_allow_html=True
    )

def insight(t):
    st.markdown(f'<div class="insight">💡 {t}</div>', unsafe_allow_html=True)

def banner(title, sub, icon=""):
    st.markdown(
        f'<div class="banner"><h2>{icon} {title}</h2><p>{sub}</p></div>',
        unsafe_allow_html=True
    )

def impact(items):
    parts = "  ·  ".join(
        [f"<b style='color:{TSS_RED};'>{k}:</b> {v}" for k,v in items.items()]
    )
    st.markdown(f'<div class="impact">🎯 <b>Expected Impact</b> &nbsp;|&nbsp; {parts}</div>',
                unsafe_allow_html=True)

def cs(fig, h=300):
    fig.update_layout(
        height=h,
        plot_bgcolor=TSS_WHITE,
        paper_bgcolor=TSS_WHITE,
        margin=dict(l=5,r=5,t=20,b=5),
        font=dict(color=TSS_BLACK, family="sans-serif"),
        legend=dict(orientation="h", y=-0.28, font_size=11,
                    bgcolor="rgba(0,0,0,0)", borderwidth=0),
    )
    fig.update_xaxes(showgrid=False, linecolor=TSS_MGREY, tickcolor=TSS_MGREY)
    fig.update_yaxes(gridcolor="#F0F0F0", linecolor=TSS_MGREY)
    return fig

# TSS red gradient for charts (light → dark red)
RED_SCALE = [[0,"#FFE0E3"],[0.5,TSS_RED],[1,"#8B0000"]]

# ═════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:1.2rem 0 0.8rem 0;'>
        <div style='font-size:2rem;'>👻</div>
        <div style='font-size:1.05rem;font-weight:800;color:{TSS_WHITE};
                    letter-spacing:0.02em;'>THE SOULED STORE</div>
        <div style='font-size:0.7rem;color:{TSS_RED};margin-top:0.15rem;
                    text-transform:uppercase;letter-spacing:0.1em;'>
            Data-Driven Growth Dashboard
        </div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    page = st.radio("Navigate", [
        "🏠  Company Overview",
        "🎯  Solution 1: Cross-Fandom",
        "📉  Solution 2: Churn Prevention",
        "📈  Solution 3: Revenue Diversification",
    ], label_visibility="collapsed")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:.72rem;color:{TSS_RED};font-weight:700;"
                f"text-transform:uppercase;letter-spacing:.08em;'>🔧 Filters</div>",
                unsafe_allow_html=True)

    sel_rfm    = st.multiselect("RFM Segment",
                                 ["Low Value","Mid Value","High Value"],
                                 default=["Low Value","Mid Value","High Value"])
    sel_fandom = st.multiselect("Primary Fandom", FANDOMS, default=FANDOMS)
    sel_age    = st.multiselect("Age Group",
                                 ["16-20","21-25","26-30","31-35","36+"],
                                 default=["16-20","21-25","26-30","31-35","36+"])
    sel_member = st.selectbox("Membership", ["All","Members Only","Non-Members"])

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-size:.68rem;color:#888;line-height:1.7;'>
        <b style='color:#CCC;'>Course:</b> Data-Driven Growth with Python<br>
        <b style='color:#CCC;'>Framework:</b> Karaman 9-Article Series<br>
        <b style='color:#CCC;'>Data:</b> Simulated · Demo only<br><br>
        <b style='color:#CCC;'>Team:</b><br>
        Avantika · Vivek · Nivedhitha<br>Atharva · Naman
    </div>
    """, unsafe_allow_html=True)

# Apply filters
filt = customers.copy()
if sel_rfm:    filt = filt[filt["rfm_segment"].isin(sel_rfm)]
if sel_fandom: filt = filt[filt["primary_fandom"].isin(sel_fandom)]
if sel_age:    filt = filt[filt["age_group"].isin(sel_age)]
if sel_member == "Members Only":  filt = filt[filt["is_member"]==True]
elif sel_member == "Non-Members": filt = filt[filt["is_member"]==False]

if len(filt)==0:
    st.warning("⚠️ No customers match the current filters. Please adjust the sidebar.")
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — COMPANY OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
if "Company Overview" in page:
    banner("Company Overview",
           "North Star Metric: Monthly Repeat Purchase Revenue  ·  FY25 Revenue ~₹500 Cr", "🏠")

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("Filtered Customers",    f"{len(filt):,}",
                  f"{round(len(filt)/len(customers)*100,1)}% of base", True)
    with c2: kpi("Avg. Fandom Breadth",   f"{filt['fandom_breadth'].mean():.2f}",
                  "Target: 1.8", True, CHART_3)
    with c3: kpi("High Churn Risk",
                  f"{(filt['churn_risk']=='High Risk').sum():,}",
                  f"{round((filt['churn_risk']=='High Risk').mean()*100,1)}% of filtered",
                  False, TSS_RED)
    with c4: kpi("Avg. Predicted LTV",    f"₹{filt['predicted_ltv'].mean():,.0f}",
                  "Per customer", True, CHART_3)

    st.markdown("<br>", unsafe_allow_html=True)
    l, r = st.columns([1.15, 0.85])

    with l:
        st.subheader("📊 North Star — Monthly Repeat Purchase Revenue")
        months = pd.date_range("2023-01-01",periods=24,freq="MS")
        repeat = (15+np.arange(24)*.6+np.random.default_rng(1).normal(0,1.2,24)).clip(10)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=months, y=rev_df["actual"], name="Total Revenue",
                              marker_color=TSS_MGREY, opacity=0.7))
        fig.add_trace(go.Scatter(x=months, y=repeat, name="Repeat Revenue (NSM)",
                                  line=dict(color=TSS_RED, width=3),
                                  mode="lines+markers", marker=dict(size=5, color=TSS_RED)))
        cs(fig, 320)
        fig.update_layout(xaxis_title="Month", yaxis_title="₹ Crore")
        st.plotly_chart(fig, use_container_width=True)
        insight("Repeat Purchase Revenue is our North Star — it shows whether customers are actually coming back, not just whether a new IP launch spiked total sales.")

    with r:
        st.subheader("🗂️ Segment Breakdown")
        view = st.selectbox("Break down by",
                             ["RFM Segment","Age Group","Primary Fandom","Persona","City"],
                             key="ov_view")
        col_map = {"RFM Segment":"rfm_segment","Age Group":"age_group",
                    "Primary Fandom":"primary_fandom","Persona":"persona","City":"city"}
        vc = filt[col_map[view]].value_counts().reset_index()
        vc.columns = ["label","count"]
        fig2 = px.pie(vc, names="label", values="count", hole=0.48,
                       color_discrete_sequence=[TSS_RED,TSS_BLACK,CHART_2,CHART_4,
                                                 "#FF8C94","#C0C0C0"])
        fig2.update_layout(height=265, paper_bgcolor=TSS_WHITE, plot_bgcolor=TSS_WHITE,
                            margin=dict(l=0,r=0,t=0,b=0),
                            font=dict(color=TSS_BLACK),
                            legend=dict(orientation="h", y=-0.18, font_size=10))
        fig2.update_traces(textinfo="percent", textfont_size=11)
        st.plotly_chart(fig2, use_container_width=True)

    # Problem cards
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🔍 Three Core Problems — Live from Filtered Data")
    p1, p2, p3 = st.columns(3)
    sf_pct  = round((filt["fandom_breadth"]==1).mean()*100,1)
    ch_pct  = round((filt["churn_risk"]=="High Risk").mean()*100,1)
    lnch_pct= round(rev_df[rev_df["is_launch"]]["actual"].sum()/rev_df["actual"].sum()*100,1)

    for col, num, title, stat, stat_label, arts, accent in [
        (p1,"01","Single-Fandom Trap",      f"{sf_pct}%",   "single-fandom buyers",       "2,3,5",  TSS_RED),
        (p2,"02","Post-Purchase Churn",      f"{ch_pct}%",   "high churn risk (filtered)", "2,3,4,5,8",CHART_3),
        (p3,"03","IP Launch Dependency",     f"{lnch_pct}%", "of GMV from launch months",  "6,7,8,9",TSS_RED),
    ]:
        with col:
            st.markdown(f"""
            <div class="prob-card" style="border-top-color:{accent};">
                <div style='font-size:.7rem;color:{TSS_DGREY};font-weight:700;
                            text-transform:uppercase;letter-spacing:.06em;'>Problem {num}</div>
                <div style='font-weight:700;color:{TSS_BLACK};font-size:.95rem;
                            margin:.35rem 0 .5rem 0;'>{title}</div>
                <div style='font-size:2rem;font-weight:800;color:{accent};
                            line-height:1;margin-bottom:.3rem;'>{stat}</div>
                <div style='font-size:.8rem;color:{TSS_DGREY};'>{stat_label}</div>
                <div style='margin-top:.6rem;'>
                    <span class="pill">Articles {arts}</span>
                </div>
            </div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — SOLUTION 1
# ═════════════════════════════════════════════════════════════════════════════
elif "Solution 1" in page:
    banner("Solution 1: Cross-Fandom Discovery Engine",
           "RFM Segmentation (Article 2)  ·  LTV Prediction (Article 3)  ·  Next Purchase Category Predictor (Article 5)",
           "🎯")

    multi_ltv  = filt[filt["fandom_breadth"]>=2]["predicted_ltv"].mean()
    single_ltv = filt[filt["fandom_breadth"]==1]["predicted_ltv"].mean()
    ltv_uplift = round((multi_ltv/single_ltv-1)*100,1) if single_ltv>0 else 0
    hv_single  = filt[(filt["rfm_segment"]=="High Value")&(filt["fandom_breadth"]==1)]
    cur_breadth= round(filt["fandom_breadth"].mean(),2)

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("Single-Fandom Customers",   f"{round((filt['fandom_breadth']==1).mean()*100,1)}%",
                  "Primary target group", False)
    with c2: kpi("High-Value, Single-Fandom", f"{len(hv_single):,}",
                  "Highest-upside cohort", True, CHART_3)
    with c3: kpi("Avg. Fandom Breadth",        f"{cur_breadth}",
                  "Target: 1.8 in 12 months", True, CHART_3)
    with c4: kpi("LTV Uplift (Multi vs Single)",f"+{ltv_uplift}%",
                  "Validates the business case", True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── What-If Simulator ─────────────────────────────────────────────────
    st.markdown('<div class="sim-box">', unsafe_allow_html=True)
    st.markdown(f"**🎛️ What-If: Fandom Breadth Target Simulator**")
    st.caption(f"Current avg. fandom breadth in filtered segment: **{cur_breadth}** — set target above this to see uplift")
    sc1,sc2,sc3 = st.columns(3)
    # Default slider to cur_breadth + 0.3, min to cur_breadth so gap is always positive
    slider_min  = round(cur_breadth, 1)
    slider_def  = min(round(cur_breadth + 0.3, 1), 3.0)
    with sc1: target_b  = st.slider("Target Avg. Fandom Breadth", slider_min, 3.0, slider_def, 0.1)
    with sc2: conv_rate = st.slider("Cross-Fandom Conversion Rate (%)", 2, 20, 10, 1)
    with sc3: sim_aov   = st.slider("Average Order Value (₹)", 400, 1200, 700, 50)
    # Extra purchases = customers who need to be moved up × avg orders needed × conversion
    gap        = round(target_b - cur_breadth, 2)
    single_fans= int((filt["fandom_breadth"]==1).sum())
    # Each % point of conversion on single-fandom customers = extra purchases
    extra      = int(single_fans * (conv_rate / 100) * gap * 10)
    uplift_rev = extra * sim_aov / 1e5
    r1,r2,r3 = st.columns(3)
    with r1: st.metric("Breadth Gap to Close",      f"+{gap:.1f} IPs/customer")
    with r2: st.metric("Estimated Extra Purchases",  f"{extra:,}")
    with r3: st.metric("Projected Revenue Uplift",   f"₹{uplift_rev:.1f}L / month")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    l, r = st.columns(2)

    with l:
        st.subheader("👥 RFM Segments × Fandom Breadth")
        drill = st.selectbox("🔍 Drill into segment",
                              ["All"]+list(filt["rfm_segment"].dropna().unique()), key="d1")
        df_d  = filt if drill=="All" else filt[filt["rfm_segment"]==drill]
        rfm_b = df_d.groupby(["rfm_segment","fandom_breadth"]).size().reset_index(name="count")
        fig   = px.bar(rfm_b, x="rfm_segment", y="count", color="fandom_breadth",
                        barmode="group",
                        color_continuous_scale=RED_SCALE,
                        labels={"rfm_segment":"RFM Segment","count":"Customers",
                                 "fandom_breadth":"Fandom Breadth"},
                        category_orders={"rfm_segment":["Low Value","Mid Value","High Value"]})
        cs(fig); fig.update_layout(yaxis_title="Customers", coloraxis_colorbar_title="Breadth")
        st.plotly_chart(fig, use_container_width=True)
        insight("High Value + Breadth = 1 is the primary target — loyal buyers who haven't been introduced to other IPs yet.")

    with r:
        st.subheader("💰 LTV by Fandom Breadth")
        bsel = st.multiselect("Show Breadth Levels",[1,2,3,4,5],default=[1,2,3,4,5],key="bsel")
        ltv_d= filt[filt["fandom_breadth"].isin(bsel)].copy()
        ltv_d["label"] = ltv_d["fandom_breadth"].apply(lambda x:f"Breadth {x}")
        fig2 = px.box(ltv_d, x="label", y="predicted_ltv", color="label",
                       color_discrete_sequence=[TSS_RED,CHART_3,CHART_2,CHART_4,"#FF8C94"],
                       labels={"predicted_ltv":"Predicted LTV (₹)","label":""})
        cs(fig2); fig2.update_layout(showlegend=False, yaxis_title="Predicted LTV (₹)")
        st.plotly_chart(fig2, use_container_width=True)
        insight(f"Multi-fandom customers show ~{ltv_uplift}% higher predicted LTV — confirming the case for cross-fandom investment.")

    l2, r2 = st.columns(2)

    with l2:
        st.subheader("🔄 Fandom Transition Explorer")
        from_f = st.selectbox("Transitions FROM fandom",["All"]+FANDOMS,key="tf")
        trans  = transitions.copy()
        if from_f!="All": trans=trans[trans["from"]==from_f]
        trans["pair"] = trans["from"]+" → "+trans["to"]
        fig3 = px.bar(trans, x="count", y="pair", orientation="h",
                       color="count", color_continuous_scale=RED_SCALE,
                       labels={"count":"Customers","pair":""})
        cs(fig3,320)
        fig3.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

    with r2:
        st.subheader("🤖 Next Purchase Category Simulator")
        st.caption("Simulates Article 5's category predictor for a given customer profile")
        sf   = st.selectbox("Customer's current fandom", FANDOMS, key="sf")
        sfr  = st.slider("Purchase frequency (orders/year)",1,12,3,key="sfr")
        sre  = st.slider("Days since last purchase",1,180,30,key="sre")
        smem = st.checkbox("TSS Member",value=False,key="smem")

        rng2   = np.random.default_rng(abs(hash(sf))%999)
        # Drive scores from actual transition data so predictor matches transition explorer
        all_trans = transitions.copy()
        # Get transition counts FROM selected fandom; fall back to uniform if none
        from_rows = all_trans[all_trans["from"]==sf]
        if len(from_rows) > 0:
            score_map = dict(zip(from_rows["to"], from_rows["count"]))
        else:
            # Build full transition table for fandoms not in top-15
            rows_full=[]
            _r=np.random.default_rng(abs(hash(sf))%999)
            for _f in FANDOMS:
                if _f!=sf:
                    rows_full.append({"to":_f,"count":int(_r.integers(15,180))})
            score_map = {r["to"]:r["count"] for r in rows_full}

        sdf = pd.DataFrame([
            {"fandom": f, "score": score_map.get(f, 1)}
            for f in FANDOMS if f != sf
        ])
        # Add small noise so identical counts get varied ordering
        sdf["score"] = sdf["score"] + rng2.uniform(0, 20, len(sdf))
        sdf = sdf.sort_values("score", ascending=False)
        sdf["pct"] = (sdf["score"] / sdf["score"].sum() * 100).round(1)
        if smem: sdf.iloc[0, sdf.columns.get_loc("pct")] += 5
        top3 = sdf.head(3)

        st.markdown(f"**Top 3 recommendations for a {sf} buyer:**")
        for _,row in top3.iterrows():
            bw = int(row["pct"]*2.8)
            st.markdown(f"""
            <div style='margin:.3rem 0;padding:.55rem .9rem;background:{TSS_RED_LT};
                        border-radius:7px;border-left:4px solid {TSS_RED};'>
                <span style='font-weight:700;color:{TSS_BLACK};'>{row["fandom"]}</span>
                <div style='height:7px;background:{TSS_RED};width:{bw}%;
                            border-radius:4px;margin-top:.3rem;opacity:.75;'></div>
                <span style='font-size:.75rem;color:{TSS_DGREY};'>{row["pct"]:.1f}% match score</span>
            </div>""", unsafe_allow_html=True)
        insight(f"A {sf} fan buying {sfr}x/year is most likely to explore {top3.iloc[0]['fandom']} next.")

    impact({"Fandom Breadth":f"{cur_breadth} → {target_b} (target)",
            "Repeat Revenue Uplift":"+20–25% in High Value cohort",
            "CTR Target":">8%"})


# ═════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — SOLUTION 2
# ═════════════════════════════════════════════════════════════════════════════
elif "Solution 2" in page:
    banner("Solution 2: Multi-Layer Churn Prevention Pipeline",
           "Churn Prediction (Articles 4,5)  ·  Persona Segmentation (Article 2)  ·  LTV Budget (Article 3)  ·  Uplift Modelling (Article 8)",
           "📉")

    high_risk   = int((filt["churn_risk"]=="High Risk").sum())
    rev_risk    = round(filt[filt["churn_risk"]=="High Risk"]["predicted_ltv"].sum()/1e5,1)
    persuadable = int((filt["uplift_score"]>0).sum())

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("High Churn Risk",       f"{high_risk:,}",
                  f"{round(high_risk/len(filt)*100,1)}% of filtered", False)
    with c2: kpi("Revenue at Risk",       f"₹{rev_risk}L",
                  "LTV of high-risk segment", False, CHART_3)
    with c3: kpi("Persuadable Customers", f"{persuadable:,}",
                  "Worth sending an offer", True, CHART_3)
    with c4: kpi("Avg. Churn Score",      f"{filt['churn_score'].mean():.2f}",
                  "0 = safe,  1 = churned", False)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Simulator ─────────────────────────────────────────────────────────
    st.markdown('<div class="sim-box">', unsafe_allow_html=True)
    st.markdown("**🎛️ Campaign Budget Simulator — Adjust thresholds, see impact live**")
    sc1,sc2,sc3 = st.columns(3)
    with sc1: thresh    = st.slider("Churn Score Threshold",0.3,0.8,0.65,0.05)
    with sc2: hi_budget = st.slider("Max Spend — High LTV (₹)",50,300,150,10)
    with sc3: mi_budget = st.slider("Max Spend — Mid LTV (₹)",20,150,80,10)

    at_risk   = filt[filt["churn_score"]>=thresh]
    persuad   = at_risk[at_risk["uplift_score"]>0]
    hi_seg    = persuad[persuad["predicted_ltv"]>=persuad["predicted_ltv"].quantile(.66)]
    mi_seg    = persuad[(persuad["predicted_ltv"]>=persuad["predicted_ltv"].quantile(.33))&
                          (persuad["predicted_ltv"]<persuad["predicted_ltv"].quantile(.66))]
    tot_spend = (len(hi_seg)*hi_budget+len(mi_seg)*mi_budget)/1e5
    saved     = (len(at_risk)-len(persuad))*hi_budget/1e5
    r1,r2,r3,r4 = st.columns(4)
    with r1: st.metric("At-Risk (this threshold)",f"{len(at_risk):,}")
    with r2: st.metric("Persuadable — send offers",f"{len(persuad):,}")
    with r3: st.metric("Est. Campaign Spend",f"₹{tot_spend:.1f}L")
    with r4: st.metric("Margin Saved vs No-Uplift",f"₹{saved:.1f}L")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    l, r = st.columns(2)

    with l:
        st.subheader("⚠️ Churn Risk by Buyer Persona")
        dp = st.radio("Filter",["Both","Fandom Loyalist","Event Buyer"],
                       horizontal=True, key="dp")
        dfp = filt if dp=="Both" else filt[filt["persona"]==dp]
        pr  = dfp.groupby(["persona","churn_risk"]).size().reset_index(name="count")
        fig = px.bar(pr, x="persona", y="count", color="churn_risk", barmode="stack",
                      color_discrete_map={"Low Risk":"#D4EDDA",
                                           "Medium Risk":"#FFF3CD",
                                           "High Risk":TSS_RED},
                      labels={"persona":"","count":"Customers","churn_risk":"Risk"})
        cs(fig); fig.update_layout(yaxis_title="Customers")
        st.plotly_chart(fig, use_container_width=True)
        insight("Event Buyers have far higher churn rates. They need a dedicated post-purchase email sequence from day one.")

    with r:
        st.subheader("🎯 Uplift Score — Who Gets the Offer?")
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=filt[filt["uplift_score"]>0]["uplift_score"],
            name="Persuadable — send offer",
            marker_color=TSS_RED, opacity=0.85, nbinsx=25))
        fig2.add_trace(go.Histogram(
            x=filt[filt["uplift_score"]<=0]["uplift_score"],
            name="Skip — Sure Thing / Lost Cause",
            marker_color=TSS_MGREY, opacity=0.85, nbinsx=25))
        fig2.add_vline(x=0, line_dash="dash", line_color=TSS_BLACK, line_width=2,
                        annotation_text="Threshold = 0",
                        annotation_font_color=TSS_BLACK,
                        annotation_position="top right")
        fig2.update_layout(barmode="overlay",
                            xaxis_title="Uplift Score", yaxis_title="Customers")
        cs(fig2); st.plotly_chart(fig2, use_container_width=True)
        insight("Only the red bars receive discount offers — grey bars get content-only emails, saving margin without losing engagement.")

    l2, r2 = st.columns(2)

    with l2:
        st.subheader("💸 Retention Budget Allocation")
        bdg = pd.DataFrame({
            "Segment":       ["High LTV + High Risk","Mid LTV + High Risk","Low LTV + High Risk",
                               "High LTV + Med Risk","Mid/Low + Med Risk"],
            "Max Spend (₹)": [hi_budget, mi_budget, 0, int(hi_budget*.4), 0],
            "Channel":       ["Push+Email+WhatsApp","Email+App","Content only",
                               "Push","Content only"],
        })
        fig3 = px.bar(bdg, x="Max Spend (₹)", y="Segment", orientation="h",
                       color="Max Spend (₹)",
                       color_continuous_scale=[[0,TSS_MGREY],[0.01,TSS_RED_MD],[1,TSS_RED]],
                       text="Channel")
        fig3.update_traces(textposition="inside", textfont_size=10,
                            textfont_color=TSS_BLACK)
        cs(fig3,300)
        fig3.update_layout(coloraxis_showscale=False,
                            yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3, use_container_width=True)

    with r2:
        st.subheader("🔮 Customer Churn Decision Tool")
        st.caption("Enter a customer's details to get a real-time retention recommendation")
        lu_rec  = st.slider("Days since last purchase",1,365,60,key="lu_rec")
        lu_freq = st.slider("Total orders placed",1,10,2,key="lu_freq")
        lu_ltv  = st.slider("Predicted LTV (₹)",500,15000,3000,500,key="lu_ltv")
        lu_up   = st.slider("Uplift Score",-0.4,0.6,0.15,0.05,key="lu_up")

        cs_ = min(1.0,(lu_rec/365)*.6+(1/lu_freq)*.3+np.random.normal(0,.02))
        is_risk  = cs_>=thresh
        is_pers  = lu_up>0
        ltv_tier = "High" if lu_ltv>=8000 else ("Mid" if lu_ltv>=3000 else "Low")
        rec_spend= {True:{"High":hi_budget,"Mid":mi_budget,"Low":0},
                     False:{"High":int(hi_budget*.4),"Mid":0,"Low":0}}[is_risk][ltv_tier]
        action   = ("🎯 Send retention offer" if rec_spend>0
                     else "📧 Send content email" if is_risk
                     else "✅ No action needed")
        border   = TSS_RED if is_risk else "#1E7E34"

        st.markdown(f"""
        <div class="lookup-result" style="border-color:{border};border-width:2px;">
            <div style='display:flex;gap:1.5rem;align-items:flex-start;'>
                <div>
                    <div style='font-size:.68rem;color:{TSS_DGREY};text-transform:uppercase;
                                font-weight:600;'>Churn Score</div>
                    <div style='font-size:1.8rem;font-weight:800;color:{border};'>{cs_:.2f}</div>
                </div>
                <div style='flex:1;padding-top:.2rem;'>
                    <div style='margin-bottom:.3rem;'>
                        <span class="pill {'pill' if is_risk else 'pill pill-grey'}"
                              style="background:{''+TSS_RED if is_risk else TSS_MGREY};
                                     color:{'white' if is_risk else TSS_BLACK};">
                            {'🔴 HIGH RISK' if is_risk else '🟢 LOW RISK'}
                        </span>
                        <span class="pill" style="background:{''+TSS_BLACK if is_pers else TSS_MGREY};
                                                   color:{'white' if is_pers else TSS_BLACK};">
                            {'✅ Persuadable' if is_pers else '⏭ Skip offers'}
                        </span>
                        <span class="pill pill-grey">{ltv_tier} LTV</span>
                    </div>
                    <div style='font-weight:700;color:{TSS_BLACK};font-size:.95rem;'>{action}</div>
                    {'<div style="font-size:.8rem;color:'+TSS_DGREY+';margin-top:.2rem;">Max budget: ₹'+str(rec_spend)+'</div>' if rec_spend>0 else ''}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    impact({"Retention Rate":"~28% → 40%+",
            "2nd-Purchase Conversion":"+15–20 pp (90-day)",
            "Campaign ROI":"+30–40% via Uplift targeting"})


# ═════════════════════════════════════════════════════════════════════════════
#  PAGE 4 — SOLUTION 3
# ═════════════════════════════════════════════════════════════════════════════
elif "Solution 3" in page:
    banner("Solution 3: Revenue Diversification",
           "LSTM Forecasting (Article 6)  ·  Market Response Models (Article 7)  ·  A/B Testing (Article 9)",
           "📈")

    launch_pct = round(rev_df[rev_df["is_launch"]]["actual"].sum()/rev_df["actual"].sum()*100,1)
    avg_inter  = round(rev_df[~rev_df["is_launch"]]["actual"].mean(),1)
    best_offer = offers_df.loc[offers_df["net_uplift"].idxmax(),"offer_type"]

    c1,c2,c3,c4 = st.columns(4)
    with c1: kpi("IP-Launch % of GMV",    f"{launch_pct}%","Target: <40%",False)
    with c2: kpi("Avg Inter-Launch Rev",  f"₹{avg_inter} Cr/mo","Target: +25–30%",False,CHART_3)
    with c3: kpi("Best Non-Discount Lever",best_offer,"By net revenue uplift",True,CHART_3)
    with c4: kpi("Discount ROI vs Alt.",  "8× worse","20% disc vs Early Access",False)

    # ── Revenue Chart ─────────────────────────────────────────────────────
    st.subheader("📊 Actual Revenue vs BAU Baseline  (Article 6 — LSTM Forecast)")
    tc1,tc2 = st.columns(2)
    with tc1: show_fc   = st.checkbox("Show 6-month forecast",value=True)
    with tc2: show_lnch = st.checkbox("Highlight IP launch months",value=True)

    fig = go.Figure()
    if show_lnch:
        for _,row in rev_df[rev_df["is_launch"]].iterrows():
            fig.add_vrect(x0=row["month"]-timedelta(days=15),
                           x1=row["month"]+timedelta(days=15),
                           fillcolor=f"rgba(232,25,44,0.06)", line_width=0)
    fig.add_trace(go.Scatter(x=rev_df["month"],y=rev_df["bau"],name="BAU Baseline (LSTM)",
                              mode="lines",line=dict(color=TSS_DGREY,width=2,dash="dot")))
    fig.add_trace(go.Scatter(x=rev_df["month"],y=rev_df["actual"],name="Actual Revenue",
                              mode="lines+markers",line=dict(color=TSS_RED,width=2.5),
                              marker=dict(size=5,color=TSS_RED)))
    if show_fc:
        fig.add_trace(go.Scatter(x=rev_fc["month"],y=rev_fc["forecast"],name="Forecast",
                                  mode="lines+markers",
                                  line=dict(color=TSS_BLACK,width=2,dash="dash"),
                                  marker=dict(symbol="diamond",size=7,color=TSS_BLACK)))
    if show_lnch:
        for _,row in rev_df[rev_df["is_launch"]].iterrows():
            fig.add_annotation(x=row["month"],y=row["actual"]+1.5,
                                text="🚀",showarrow=False,font=dict(size=13))
    cs(fig,360)
    fig.update_layout(xaxis_title="Month",yaxis_title="Revenue (₹ Crore)",
                       legend=dict(orientation="h",y=-0.18))
    st.plotly_chart(fig, use_container_width=True)
    insight("🚀 = IP launch month. The gap between BAU baseline and actuals in non-launch months is the revenue shortfall our inter-launch campaigns are designed to fill.")

    l, r = st.columns(2)

    with l:
        st.subheader("🎁 Offer ROI Builder  (Article 7)")
        oc1,oc2 = st.columns(2)
        with oc1: o_aov   = st.slider("Avg. Order Value (₹)",300,1200,650,50)
        with oc2: o_reach = st.slider("Monthly Campaign Reach",500,10000,3000,500)
        o_live = offers_df.copy()
        o_live["rev_impact"] = ((o_live["conv_uplift"]/100 - o_live["margin_cost"]/100)
                                  * o_reach * o_aov).round(0)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(name="Conversion Uplift (%)",x=o_live["offer_type"],
                               y=o_live["conv_uplift"],marker_color=TSS_MGREY))
        fig2.add_trace(go.Bar(name="Margin Cost (%)",x=o_live["offer_type"],
                               y=o_live["margin_cost"],marker_color=TSS_RED,opacity=0.8))
        fig2.add_trace(go.Scatter(name="Net Uplift",x=o_live["offer_type"],
                                   y=o_live["net_uplift"],mode="lines+markers+text",
                                   text=[str(v) for v in o_live["net_uplift"]],
                                   textposition="top center",textfont=dict(color=TSS_BLACK),
                                   line=dict(color=TSS_BLACK,width=2.5),
                                   marker=dict(size=8,color=TSS_BLACK)))
        fig2.update_layout(barmode="group",yaxis_title="% Uplift / Cost")
        cs(fig2,300); fig2.update_layout(xaxis_tickangle=-15)
        st.plotly_chart(fig2, use_container_width=True)

        st.caption("Estimated monthly revenue impact")
        st.dataframe(
            o_live[["offer_type","net_uplift","rev_impact"]].rename(columns={
                "offer_type":"Offer","net_uplift":"Net Uplift (%)","rev_impact":"Est. Monthly Rev (₹)"}),
            use_container_width=True, hide_index=True
        )
        insight("Mystery Box and IP Early Access match discount conversion at 4–8× lower margin cost.")

    with r:
        st.subheader("🧪 A/B Test Significance Calculator  (Article 9)")
        ab1,ab2 = st.columns(2)
        with ab1:
            ctrl_rev = st.number_input("Control: Avg Rev/Customer (₹)",100,2000,390,10)
            ctrl_n   = st.number_input("Control: Sample Size",100,10000,4000,100)
        with ab2:
            test_rev = st.number_input("Test: Avg Rev/Customer (₹)",100,2000,445,10)
            test_n   = st.number_input("Test: Sample Size",100,10000,4000,100)

        std_e = max(ctrl_rev,test_rev)*0.4
        se    = sqrt((std_e**2/ctrl_n)+(std_e**2/test_n)) if ctrl_n>0 and test_n>0 else 1
        t_s   = (test_rev-ctrl_rev)/se
        p_val = erfc(abs(t_s)/sqrt(2))
        lift  = round((test_rev-ctrl_rev)/ctrl_rev*100,1) if ctrl_rev>0 else 0
        sig   = p_val<0.05

        bdr   = "#1E7E34" if sig else "#856404"
        bg    = "#D4EDDA" if sig else "#FFF3CD"
        v_txt = ("✅ SIGNIFICANT — safe to scale this campaign!"
                  if sig else "⚠️ NOT significant yet — run longer or increase sample size")

        st.markdown(f"""
        <div style='background:{bg};border-radius:8px;padding:1rem;
                    border:2px solid {bdr};margin:.5rem 0;'>
            <div style='display:flex;gap:2rem;margin-bottom:.5rem;'>
                <div><div style='font-size:.65rem;color:{TSS_DGREY};font-weight:700;
                                 text-transform:uppercase;'>T-Statistic</div>
                     <div style='font-size:1.5rem;font-weight:800;color:{TSS_BLACK};'>{t_s:.3f}</div></div>
                <div><div style='font-size:.65rem;color:{TSS_DGREY};font-weight:700;
                                 text-transform:uppercase;'>P-Value</div>
                     <div style='font-size:1.5rem;font-weight:800;color:{bdr};'>{p_val:.4f}</div></div>
                <div><div style='font-size:.65rem;color:{TSS_DGREY};font-weight:700;
                                 text-transform:uppercase;'>Revenue Lift</div>
                     <div style='font-size:1.5rem;font-weight:800;color:{TSS_RED};'>+{lift}%</div></div>
            </div>
            <div style='font-weight:700;color:{bdr};font-size:.88rem;'>{v_txt}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("💳 Membership Funnel Simulator")
        mfc1,mfc2 = st.columns(2)
        with mfc1: mem_base  = st.slider("Active customer base",500,5000,2000,100)
        with mfc2: mem_rate  = st.slider("Target conversion (%)",2,20,9,1)
        mem_price    = st.selectbox("Membership price (₹/year)",[199,299,399,499],index=1)
        mem_converts = int(mem_base*mem_rate/100)
        mem_rev      = round(mem_converts*mem_price/1e5,2)

        funnel = pd.DataFrame({
            "Stage":["Active Customers","Targeted (60%)","Clicked (20%)","Converted to Member"],
            "Count":[mem_base,int(mem_base*.6),int(mem_base*.2),mem_converts],
        })
        fig3 = px.funnel(funnel, x="Count", y="Stage",
                          color_discrete_sequence=[TSS_BLACK, CHART_3, CHART_2, TSS_RED])
        fig3.update_layout(height=220, paper_bgcolor=TSS_WHITE,
                            font=dict(color=TSS_BLACK),
                            margin=dict(l=5,r=5,t=10,b=5))
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown(f"**Projected membership revenue: ₹{mem_rev}L/year** "
                     f"({mem_converts:,} members × ₹{mem_price}/year)")

    impact({"IP-Launch Dependency":f"{launch_pct}% → target <40%",
            "Inter-Launch Revenue":"+25–30% vs baseline",
            "Membership Revenue":"₹15–20 Cr by Year 2"})
