# ─────────────────────────────────────────────────────────────────────────────
#  The Souled Store — Interactive Data-Driven Growth Dashboard
#  Self-contained. No local imports. All data simulated.
#  pip install streamlit pandas numpy plotly
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import timedelta

st.set_page_config(
    page_title="The Souled Store — Growth Dashboard",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colours ───────────────────────────────────────────────────────────────────
C = {
    "dark":   "#1A1A2E", "red":  "#C0392B", "navy": "#1B3A5C",
    "green":  "#065F46", "amber":"#92400E", "purple":"#6D28D9",
    "border": "#E5E7EB", "light":"#F3F4F6", "white":"#FFFFFF",
    "lt_red": "#FDEDEC", "lt_blue":"#EBF2FF", "lt_green":"#ECFDF5",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""<style>
[data-testid="stSidebar"]{{background:{C['dark']};}}
[data-testid="stSidebar"] *{{color:white!important;}}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label{{color:#CBD5E1!important;font-size:0.8rem;}}
.main .block-container{{padding-top:1.2rem;padding-bottom:2rem;}}
.kpi{{background:white;border-radius:10px;padding:.9rem 1.1rem;
      border-left:5px solid {C['red']};box-shadow:0 2px 8px rgba(0,0,0,.07);}}
.kpi .lbl{{font-size:.72rem;color:#6B7280;text-transform:uppercase;letter-spacing:.04em;}}
.kpi .val{{font-size:1.75rem;font-weight:700;color:{C['dark']};line-height:1.15;}}
.kpi .dlt{{font-size:.78rem;margin-top:.15rem;}}
.up{{color:{C['green']};}} .dn{{color:{C['red']};}}
.banner{{background:linear-gradient(135deg,{C['dark']} 0%,{C['navy']} 100%);
         color:white;padding:.9rem 1.4rem;border-radius:10px;margin-bottom:1rem;}}
.banner h2{{color:white!important;margin:0 0 .1rem 0;font-size:1.3rem;}}
.banner p{{color:#CBD5E1;margin:0;font-size:.82rem;}}
.insight{{background:{C['lt_blue']};border-left:4px solid {C['navy']};
          border-radius:6px;padding:.65rem .9rem;font-size:.86rem;
          color:{C['navy']};margin:.5rem 0;}}
.impact{{background:{C['light']};border-radius:10px;padding:.9rem 1.4rem;
         border:1px solid {C['border']};margin-top:.7rem;}}
.sim-box{{background:white;border-radius:10px;padding:1rem 1.2rem;
          border:2px solid {C['navy']};box-shadow:0 2px 12px rgba(0,0,0,.08);}}
</style>""", unsafe_allow_html=True)

np.random.seed(42); random.seed(42)

FANDOMS = ["Marvel","DC","Friends","Naruto","Cricket",
           "Brooklyn Nine-Nine","Harry Potter","Attack on Titan","The Office","Game of Thrones"]

# ═══════════════════════════════════════════════════════════════════════════
#  DATA
# ═══════════════════════════════════════════════════════════════════════════
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
        "age_group":      np.random.choice(["16-20","21-25","26-30","31-35","36+"],n,p=[.18,.32,.28,.14,.08]),
        "is_member":      np.random.choice([True,False],n,p=[.22,.78]),
        "city":           np.random.choice(["Mumbai","Delhi","Bangalore","Hyderabad","Chennai","Others"],
                                            n,p=[.22,.20,.18,.15,.12,.13]),
    })
    df["r_score"] = pd.qcut(df["recency_days"],4,labels=[4,3,2,1]).astype(int)
    df["f_score"] = pd.qcut(df["frequency"].rank(method="first"),4,labels=[1,2,3,4]).astype(int)
    df["m_score"] = pd.qcut(df["monetary"].rank(method="first"),4,labels=[1,2,3,4]).astype(int)
    df["rfm_total"]   = df["r_score"]+df["f_score"]+df["m_score"]
    df["rfm_segment"] = pd.cut(df["rfm_total"],bins=[2,5,8,12],labels=["Low Value","Mid Value","High Value"])
    churn = (df["recency_days"]/365)*.6+(1/df["frequency"])*.3
    df["churn_score"] = (churn+np.random.normal(0,.05,n)).clip(0,1).round(2)
    df["churn_risk"]  = pd.cut(df["churn_score"],bins=[0,.35,.65,1.],labels=["Low Risk","Medium Risk","High Risk"])
    df["predicted_ltv"]= (df["monetary"]*df["frequency"]*(1+df["fandom_breadth"]*.18)*
                           np.random.uniform(.8,1.2,n)).round(-2)
    df["persona"]      = np.where(df["frequency"]>=2,"Fandom Loyalist","Event Buyer")
    df["uplift_score"] = np.random.normal(.12,.18,n).clip(-.4,.6).round(3)
    return df

@st.cache_data
def make_revenue():
    months = pd.date_range("2023-01-01",periods=24,freq="MS")
    base   = 25+np.arange(24)*.9
    spikes = np.zeros(24)
    for i in [2,7,11,15,20,23]: spikes[i]=random.uniform(12,28)
    actual = (base+spikes+np.random.normal(0,1.5,24)).clip(10)
    bau    = base+np.random.normal(0,.8,24)
    df = pd.DataFrame({"month":months,"actual":actual.round(1),"bau":bau.round(1),"is_launch":spikes>0})
    future = pd.date_range("2025-01-01",periods=6,freq="MS")
    df_fc  = pd.DataFrame({"month":future,"forecast":(bau[-6:]*np.linspace(1.02,1.10,6)).round(1)})
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

# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def kpi(label,value,delta="",good=True,color=None):
    color=color or C["red"]; cls="up" if good else "dn"; arrow="▲" if good else "▼"
    d=f'<div class="dlt {cls}">{arrow} {delta}</div>' if delta else ""
    st.markdown(f'<div class="kpi" style="border-left-color:{color}"><div class="lbl">{label}</div>'
                f'<div class="val">{value}</div>{d}</div>',unsafe_allow_html=True)

def insight(t): st.markdown(f'<div class="insight">💡 {t}</div>',unsafe_allow_html=True)

def banner(title,sub,icon=""):
    st.markdown(f'<div class="banner"><h2>{icon} {title}</h2><p>{sub}</p></div>',unsafe_allow_html=True)

def impact(items):
    parts="  ·  ".join([f"<b style='color:{C['red']};'>{k}:</b> {v}" for k,v in items.items()])
    st.markdown(f'<div class="impact">🎯 <b>Expected Impact</b> &nbsp;|&nbsp; {parts}</div>',unsafe_allow_html=True)

def cs(fig,h=300,legend=True):
    fig.update_layout(height=h,plot_bgcolor="white",paper_bgcolor="white",
                       margin=dict(l=5,r=5,t=15,b=5),
                       legend=dict(orientation="h",y=-.28,font_size=11) if legend else dict(visible=False))
    fig.update_xaxes(showgrid=False); fig.update_yaxes(gridcolor="#F3F4F6")
    return fig

# ═══════════════════════════════════════════════════════════════════════════
#  SIDEBAR — GLOBAL FILTERS + NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div style='text-align:center;padding:1rem 0;'>
        <div style='font-size:1.8rem;'>🎭</div>
        <div style='font-size:1rem;font-weight:700;color:white;'>The Souled Store</div>
        <div style='font-size:.72rem;color:#F87171;'>Data-Driven Growth Dashboard</div>
    </div><hr style='border-color:#374151;margin:.4rem 0 .8rem 0;'>""",unsafe_allow_html=True)

    page = st.radio("Navigate",[
        "🏠  Company Overview",
        "🎯  Solution 1: Cross-Fandom",
        "📉  Solution 2: Churn Prevention",
        "📈  Solution 3: Revenue Diversification",
    ],label_visibility="collapsed")

    st.markdown("<hr style='border-color:#374151;margin:.8rem 0;'>",unsafe_allow_html=True)
    st.markdown("<div style='font-size:.75rem;color:#F87171;font-weight:600;'>🔧 GLOBAL FILTERS</div>",
                unsafe_allow_html=True)

    sel_rfm    = st.multiselect("RFM Segment",["Low Value","Mid Value","High Value"],
                                 default=["Low Value","Mid Value","High Value"])
    sel_fandom = st.multiselect("Primary Fandom",FANDOMS,default=FANDOMS)
    sel_age    = st.multiselect("Age Group",["16-20","21-25","26-30","31-35","36+"],
                                 default=["16-20","21-25","26-30","31-35","36+"])
    sel_member = st.selectbox("Membership",["All","Members Only","Non-Members"])

    st.markdown("<hr style='border-color:#374151;margin:.8rem 0;'>",unsafe_allow_html=True)
    st.markdown("""<div style='font-size:.7rem;color:#9CA3AF;'>
        <b style='color:#CBD5E1;'>Course:</b> Data-Driven Growth with Python<br>
        <b style='color:#CBD5E1;'>Team:</b> Avantika · Vivek · Nivedhitha · Atharva · Naman
    </div>""",unsafe_allow_html=True)

# Apply global filters
filt = customers.copy()
if sel_rfm:    filt = filt[filt["rfm_segment"].isin(sel_rfm)]
if sel_fandom: filt = filt[filt["primary_fandom"].isin(sel_fandom)]
if sel_age:    filt = filt[filt["age_group"].isin(sel_age)]
if sel_member == "Members Only":    filt = filt[filt["is_member"]==True]
elif sel_member == "Non-Members":   filt = filt[filt["is_member"]==False]

if len(filt)==0:
    st.warning("No customers match the current filters. Please adjust the sidebar filters.")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 1 — COMPANY OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════
if "Company Overview" in page:
    banner("Company Overview",
           "North Star Metric: Monthly Repeat Purchase Revenue  ·  FY25 ~₹500 Cr","🏠")

    c1,c2,c3,c4=st.columns(4)
    with c1: kpi("Filtered Customers",f"{len(filt):,}",f"{round(len(filt)/len(customers)*100,1)}% of base",True,C["red"])
    with c2: kpi("Avg. Fandom Breadth",f"{filt['fandom_breadth'].mean():.2f}","Target: 1.8",True,C["navy"])
    with c3: kpi("High Churn Risk",f"{(filt['churn_risk']=='High Risk').sum():,}",
                  f"{round((filt['churn_risk']=='High Risk').mean()*100,1)}%",False,C["amber"])
    with c4: kpi("Avg. Predicted LTV",f"₹{filt['predicted_ltv'].mean():,.0f}","Per customer",True,C["green"])

    st.markdown("<br>",unsafe_allow_html=True)
    l,r=st.columns([1.1,.9])

    with l:
        st.subheader("📊 North Star — Monthly Repeat Purchase Revenue")
        months=pd.date_range("2023-01-01",periods=24,freq="MS")
        rng=np.random.default_rng(1)
        repeat=(15+np.arange(24)*.6+rng.normal(0,1.2,24)).clip(10)
        fig=go.Figure()
        fig.add_trace(go.Bar(x=months,y=rev_df["actual"],name="Total Revenue",
                              marker_color="#CBD5E1",opacity=.55))
        fig.add_trace(go.Scatter(x=months,y=repeat,name="Repeat Revenue (NSM)",
                                  line=dict(color=C["red"],width=3),mode="lines+markers",marker=dict(size=5)))
        cs(fig,320); fig.update_layout(xaxis_title="Month",yaxis_title="₹ Crore")
        st.plotly_chart(fig,use_container_width=True)
        insight("Repeat Purchase Revenue is the NSM — it shows if customers are returning, not just if an IP drop spiked sales.")

    with r:
        st.subheader("🗂️ Segment Breakdown (Filtered)")
        view=st.selectbox("View by",["RFM Segment","Age Group","Primary Fandom","Persona","City"],key="ov_view")
        col_map={"RFM Segment":"rfm_segment","Age Group":"age_group",
                  "Primary Fandom":"primary_fandom","Persona":"persona","City":"city"}
        vc=filt[col_map[view]].value_counts().reset_index()
        vc.columns=["label","count"]
        fig2=px.pie(vc,names="label",values="count",hole=.45,
                    color_discrete_sequence=[C["dark"],C["red"],C["navy"],C["green"],C["purple"],C["amber"]])
        fig2.update_layout(height=260,margin=dict(l=0,r=0,t=0,b=0),
                            legend=dict(orientation="h",y=-.2,font_size=10))
        fig2.update_traces(textinfo="percent",textfont_size=11)
        st.plotly_chart(fig2,use_container_width=True)

    # Problem cards
    st.markdown("<br>",unsafe_allow_html=True)
    st.subheader("🔍 Three Problems — Live Stats from Filtered Data")
    p1,p2,p3=st.columns(3)
    sf_pct=round((filt["fandom_breadth"]==1).mean()*100,1)
    ch_pct=round((filt["churn_risk"]=="High Risk").mean()*100,1)
    with p1:
        st.markdown(f"""<div style='background:{C["lt_red"]};border-radius:10px;padding:1rem;border-top:4px solid {C["red"]};'>
            <b style='color:{C["dark"]};'>Problem 1 — Single-Fandom Trap</b>
            <div style='font-size:2rem;font-weight:700;color:{C["red"]};margin:.3rem 0;'>{sf_pct}%</div>
            <div style='font-size:.82rem;color:#374151;'>of filtered customers stuck in one fandom</div>
            <div style='margin-top:.5rem;font-size:.78rem;'><b>Articles:</b> 2, 3, 5</div>
        </div>""",unsafe_allow_html=True)
    with p2:
        st.markdown(f"""<div style='background:{C["lt_green"]};border-radius:10px;padding:1rem;border-top:4px solid {C["green"]};'>
            <b style='color:{C["dark"]};'>Problem 2 — Post-Purchase Churn</b>
            <div style='font-size:2rem;font-weight:700;color:{C["green"]};margin:.3rem 0;'>{ch_pct}%</div>
            <div style='font-size:.82rem;color:#374151;'>high churn risk in filtered segment</div>
            <div style='margin-top:.5rem;font-size:.78rem;'><b>Articles:</b> 2, 3, 4, 5, 8</div>
        </div>""",unsafe_allow_html=True)
    with p3:
        launch_pct=round(rev_df[rev_df["is_launch"]]["actual"].sum()/rev_df["actual"].sum()*100,1)
        st.markdown(f"""<div style='background:{C["lt_blue"]};border-radius:10px;padding:1rem;border-top:4px solid {C["navy"]};'>
            <b style='color:{C["dark"]};'>Problem 3 — IP Launch Dependency</b>
            <div style='font-size:2rem;font-weight:700;color:{C["navy"]};margin:.3rem 0;'>{launch_pct}%</div>
            <div style='font-size:.82rem;color:#374151;'>of GMV from IP launch months</div>
            <div style='margin-top:.5rem;font-size:.78rem;'><b>Articles:</b> 6, 7, 8, 9</div>
        </div>""",unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 2 — SOLUTION 1
# ═══════════════════════════════════════════════════════════════════════════
elif "Solution 1" in page:
    banner("Solution 1: Cross-Fandom Discovery Engine",
           "RFM Segmentation (Article 2)  ·  LTV Prediction (Article 3)  ·  Next Purchase Category Predictor (Article 5)","🎯")

    multi_ltv  = filt[filt["fandom_breadth"]>=2]["predicted_ltv"].mean()
    single_ltv = filt[filt["fandom_breadth"]==1]["predicted_ltv"].mean()
    ltv_uplift = round((multi_ltv/single_ltv-1)*100,1) if single_ltv>0 else 0
    hv_single  = filt[(filt["rfm_segment"]=="High Value")&(filt["fandom_breadth"]==1)]

    c1,c2,c3,c4=st.columns(4)
    with c1: kpi("Single-Fandom",f"{round((filt['fandom_breadth']==1).mean()*100,1)}%","of filtered customers",False,C["red"])
    with c2: kpi("High-Value Single-Fandom",f"{len(hv_single):,}","Primary target cohort",True,C["navy"])
    with c3: kpi("Avg. Fandom Breadth",f"{filt['fandom_breadth'].mean():.2f}","Target: 1.8",True,C["green"])
    with c4: kpi("LTV Uplift (Multi vs Single)",f"+{ltv_uplift}%","Validates business case",True,C["purple"])

    st.markdown("<br>",unsafe_allow_html=True)

    # ── Interactive: Breadth target simulator ─────────────────────────────
    st.markdown('<div class="sim-box">',unsafe_allow_html=True)
    st.markdown(f"**🎛️ What-If Simulator — Fandom Breadth Target**")
    sc1,sc2,sc3=st.columns(3)
    with sc1:
        target_breadth=st.slider("Target Avg. Fandom Breadth",1.0,3.0,1.8,0.1,key="breadth_target")
    with sc2:
        conversion_rate=st.slider("Cross-Fandom Conversion Rate (%)",2,20,8,1,key="cf_conv")
    with sc3:
        aov=st.slider("Average Order Value (₹)",400,1200,650,50,key="cf_aov")

    current_breadth=filt["fandom_breadth"].mean()
    extra_purchases=(target_breadth-current_breadth)*len(filt)
    rev_uplift=extra_purchases*(conversion_rate/100)*aov/1e5
    r1,r2,r3=st.columns(3)
    with r1: st.metric("Breadth Gap to Close",f"{max(0,target_breadth-current_breadth):.2f} IPs/customer")
    with r2: st.metric("Estimated Extra Purchases",f"{max(0,int(extra_purchases)):,}")
    with r3: st.metric("Projected Revenue Uplift",f"₹{max(0,rev_uplift):.1f}L / month")
    st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    l,r=st.columns(2)

    with l:
        st.subheader("👥 RFM Segments × Fandom Breadth")
        # Drill-down: click segment to filter
        drill_seg=st.selectbox("🔍 Drill into RFM Segment",
                                ["All"]+list(filt["rfm_segment"].dropna().unique()),key="drill_rfm")
        df_drill=filt if drill_seg=="All" else filt[filt["rfm_segment"]==drill_seg]
        rfm_b=df_drill.groupby(["rfm_segment","fandom_breadth"]).size().reset_index(name="count")
        fig=px.bar(rfm_b,x="rfm_segment",y="count",color="fandom_breadth",barmode="group",
                   color_continuous_scale=["#FDEDEC","#C0392B","#7B241C"],
                   labels={"rfm_segment":"RFM Segment","count":"Customers","fandom_breadth":"Breadth"},
                   category_orders={"rfm_segment":["Low Value","Mid Value","High Value"]})
        cs(fig); fig.update_layout(yaxis_title="Customers")
        st.plotly_chart(fig,use_container_width=True)
        insight("Select a segment above to drill down. High Value + Breadth=1 is the highest-upside cohort.")

    with r:
        st.subheader("💰 LTV by Fandom Breadth")
        breadth_filter=st.multiselect("Show Breadth Levels",[1,2,3,4,5],default=[1,2,3,4,5],key="ltv_breadth")
        ltv_df=filt[filt["fandom_breadth"].isin(breadth_filter)].copy()
        ltv_df["label"]=ltv_df["fandom_breadth"].apply(lambda x:f"Breadth {x}")
        fig2=px.box(ltv_df,x="label",y="predicted_ltv",color="label",
                    color_discrete_sequence=[C["red"],C["navy"],C["green"],C["purple"],C["amber"]],
                    labels={"predicted_ltv":"Predicted LTV (₹)","label":""})
        cs(fig2,legend=False); fig2.update_layout(yaxis_title="Predicted LTV (₹)")
        st.plotly_chart(fig2,use_container_width=True)
        insight(f"Multi-fandom customers show ~{ltv_uplift}% higher predicted LTV across filtered segment.")

    l2,r2=st.columns(2)

    with l2:
        st.subheader("🔄 Fandom Transition Explorer")
        explore_from=st.selectbox("Show transitions FROM fandom",["All"]+FANDOMS,key="trans_from")
        trans=transitions.copy()
        if explore_from!="All":
            trans=trans[trans["from"]==explore_from]
        trans["pair"]=trans["from"]+" → "+trans["to"]
        fig3=px.bar(trans,x="count",y="pair",orientation="h",
                    color="count",color_continuous_scale=["#FDEDEC",C["red"]],
                    labels={"count":"Customers","pair":""})
        cs(fig3,320); fig3.update_layout(coloraxis_showscale=False,yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3,use_container_width=True)

    with r2:
        st.subheader("🤖 Next Purchase Category Simulator")
        st.caption("Simulate what our Article 5 predictor would recommend for a customer profile")
        sim_fandom=st.selectbox("Customer's current fandom",FANDOMS,key="sim_main")
        sim_freq  =st.slider("Purchase frequency (orders/year)",1,12,3,key="sim_freq")
        sim_rec   =st.slider("Days since last purchase",1,180,30,key="sim_rec")
        sim_mem   =st.checkbox("TSS Member",value=False,key="sim_mem")

        # Simulate prediction scores based on inputs
        rng2=np.random.default_rng(abs(hash(sim_fandom))%999)
        scores=rng2.dirichlet(np.ones(len(FANDOMS))*2)
        scores_df=pd.DataFrame({"fandom":FANDOMS,"score":scores})
        scores_df=scores_df[scores_df["fandom"]!=sim_fandom].sort_values("score",ascending=False)
        scores_df["score"]=scores_df["score"]/scores_df["score"].sum()
        scores_df["pct"]=(scores_df["score"]*100).round(1)
        # Membership boost
        if sim_mem: scores_df.iloc[0,scores_df.columns.get_loc("pct")]+=5
        top3=scores_df.head(3)

        st.markdown(f"**Top 3 recommended next fandoms for a {sim_fandom} buyer:**")
        for i,row in top3.iterrows():
            bar_w=int(row["pct"]*3)
            st.markdown(f"""
            <div style='margin:.3rem 0;padding:.5rem .8rem;background:{C["lt_blue"]};border-radius:8px;'>
                <span style='font-weight:600;color:{C["navy"]};'>{row["fandom"]}</span>
                <div style='height:8px;background:{C["navy"]};width:{bar_w}%;border-radius:4px;margin-top:.3rem;opacity:.7;'></div>
                <span style='font-size:.78rem;color:#6B7280;'>{row["pct"]:.1f}% probability</span>
            </div>""",unsafe_allow_html=True)
        insight(f"A {sim_fandom} fan with {sim_freq} orders/year is most likely to explore {top3.iloc[0]['fandom']} next.")

    impact({"Fandom Breadth":f"{current_breadth:.2f} → {target_breadth} (target)",
            "Repeat Revenue Uplift":"+20–25% in High Value cohort",
            "Cross-Fandom CTR Target":">8%"})


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 3 — SOLUTION 2
# ═══════════════════════════════════════════════════════════════════════════
elif "Solution 2" in page:
    banner("Solution 2: Multi-Layer Churn Prevention Pipeline",
           "Churn Prediction (Articles 4,5)  ·  Persona Segmentation (Article 2)  ·  LTV Budget (Article 3)  ·  Uplift Modelling (Article 8)","📉")

    high_risk  = int((filt["churn_risk"]=="High Risk").sum())
    rev_risk   = round(filt[filt["churn_risk"]=="High Risk"]["predicted_ltv"].sum()/1e5,1)
    persuadable= int((filt["uplift_score"]>0).sum())

    c1,c2,c3,c4=st.columns(4)
    with c1: kpi("High Churn Risk",f"{high_risk:,}",f"{round(high_risk/len(filt)*100,1)}% of filtered",False,C["red"])
    with c2: kpi("Revenue at Risk",f"₹{rev_risk}L","Total LTV of high-risk",False,C["amber"])
    with c3: kpi("Persuadable Customers",f"{persuadable:,}","Worth sending an offer",True,C["green"])
    with c4: kpi("Avg. Churn Score",f"{filt['churn_score'].mean():.2f}","0=safe, 1=churned",False,C["navy"])

    st.markdown("<br>",unsafe_allow_html=True)

    # ── Churn threshold slider ─────────────────────────────────────────────
    st.markdown('<div class="sim-box">',unsafe_allow_html=True)
    st.markdown("**🎛️ Churn Threshold & Campaign Budget Simulator**")
    sc1,sc2,sc3=st.columns(3)
    with sc1: churn_thresh=st.slider("Churn Score Threshold",0.3,0.8,0.65,0.05,key="churn_thresh")
    with sc2: high_ltv_budget=st.slider("Max Spend — High LTV (₹)",50,300,150,10,key="budget_high")
    with sc3: mid_ltv_budget=st.slider("Max Spend — Mid LTV (₹)",20,150,80,10,key="budget_mid")

    at_risk_now=filt[filt["churn_score"]>=churn_thresh]
    persuadable_now=at_risk_now[at_risk_now["uplift_score"]>0]
    high_ltv_seg=persuadable_now[persuadable_now["predicted_ltv"]>=persuadable_now["predicted_ltv"].quantile(.66)]
    mid_ltv_seg =persuadable_now[(persuadable_now["predicted_ltv"]>=persuadable_now["predicted_ltv"].quantile(.33))&
                                   (persuadable_now["predicted_ltv"]< persuadable_now["predicted_ltv"].quantile(.66))]
    total_spend=(len(high_ltv_seg)*high_ltv_budget+len(mid_ltv_seg)*mid_ltv_budget)/1e5
    saved_spend=(len(at_risk_now)-len(persuadable_now))*high_ltv_budget/1e5

    r1,r2,r3,r4=st.columns(4)
    with r1: st.metric("At-Risk at This Threshold",f"{len(at_risk_now):,}")
    with r2: st.metric("Persuadable (send offers)",f"{len(persuadable_now):,}")
    with r3: st.metric("Est. Campaign Spend",f"₹{total_spend:.1f}L")
    with r4: st.metric("Margin Saved (vs no Uplift)",f"₹{saved_spend:.1f}L")
    st.markdown("</div>",unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    l,r=st.columns(2)

    with l:
        st.subheader("⚠️ Churn Risk by Persona")
        # Drill-down by persona
        drill_persona=st.radio("Filter persona",["Both","Fandom Loyalist","Event Buyer"],
                                horizontal=True,key="persona_drill")
        df_p=filt if drill_persona=="Both" else filt[filt["persona"]==drill_persona]
        pr=df_p.groupby(["persona","churn_risk"]).size().reset_index(name="count")
        fig=px.bar(pr,x="persona",y="count",color="churn_risk",barmode="stack",
                   color_discrete_map={"Low Risk":"#DCFCE7","Medium Risk":"#FEF9C3","High Risk":C["red"]},
                   labels={"persona":"","count":"Customers","churn_risk":"Risk"})
        cs(fig); fig.update_layout(yaxis_title="Customers")
        st.plotly_chart(fig,use_container_width=True)
        insight("Event Buyers have far higher churn risk. They need a dedicated post-purchase onboarding sequence.")

    with r:
        st.subheader("🎯 Uplift Score — Who Gets the Offer?")
        fig2=go.Figure()
        fig2.add_trace(go.Histogram(x=filt[filt["uplift_score"]>0]["uplift_score"],
                                     name="Persuadable — send offer",
                                     marker_color=C["red"],opacity=.8,nbinsx=25))
        fig2.add_trace(go.Histogram(x=filt[filt["uplift_score"]<=0]["uplift_score"],
                                     name="Skip — Sure Thing/Lost Cause",
                                     marker_color="#CBD5E1",opacity=.8,nbinsx=25))
        fig2.add_vline(x=0,line_dash="dash",line_color=C["navy"],line_width=2,
                       annotation_text="Threshold = 0",annotation_position="top right")
        fig2.update_layout(barmode="overlay",xaxis_title="Uplift Score",yaxis_title="Customers")
        cs(fig2); st.plotly_chart(fig2,use_container_width=True)
        insight("Only red bars receive discount offers — everyone else gets content-only communication, saving margin.")

    l2,r2=st.columns(2)

    with l2:
        st.subheader("💸 Retention Budget Allocation")
        budget_df=pd.DataFrame({
            "Segment":      ["High LTV + High Risk","Mid LTV + High Risk","Low LTV + High Risk",
                              "High LTV + Med Risk","Mid/Low + Med Risk"],
            "Max Spend (₹)":[high_ltv_budget, mid_ltv_budget, 0, int(high_ltv_budget*.4), 0],
            "Channel":      ["Push+Email+WhatsApp","Email+App","Content only","Push","Content only"],
        })
        fig3=px.bar(budget_df,x="Max Spend (₹)",y="Segment",orientation="h",
                    color="Max Spend (₹)",color_continuous_scale=["#F3F4F6","#C0392B"],text="Channel")
        fig3.update_traces(textposition="inside",textfont_size=10)
        cs(fig3,300); fig3.update_layout(coloraxis_showscale=False,yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig3,use_container_width=True)

    with r2:
        st.subheader("🔮 Individual Customer Churn Lookup")
        st.caption("Simulate the retention decision for a specific customer profile")
        lu_rec  =st.slider("Days since last purchase",1,365,60,key="lu_rec")
        lu_freq =st.slider("Total orders placed",1,10,2,key="lu_freq")
        lu_ltv  =st.slider("Predicted LTV (₹)",500,15000,3000,500,key="lu_ltv")
        lu_up   =st.slider("Uplift Score",-0.4,0.6,0.15,0.05,key="lu_up")

        churn_s =(lu_rec/365)*.6+(1/lu_freq)*.3
        churn_s =min(1.0,churn_s+np.random.normal(0,.02))
        is_risk =churn_s>=churn_thresh
        is_persuadable=lu_up>0
        ltv_tier="High" if lu_ltv>=8000 else ("Mid" if lu_ltv>=3000 else "Low")
        spend_map={"High":high_ltv_budget,"Mid":mid_ltv_budget,"Low":0}
        rec_spend=spend_map[ltv_tier] if is_risk and is_persuadable else 0

        color=C["red"] if is_risk else C["green"]
        action="🎯 Send retention offer" if rec_spend>0 else ("📧 Send content email" if is_risk else "✅ No action needed")
        st.markdown(f"""
        <div style='background:{C["lt_blue"]};border-radius:10px;padding:1rem;border:2px solid {C["navy"]};margin-top:.5rem;'>
            <div style='font-size:.8rem;color:#6B7280;'>Churn Score</div>
            <div style='font-size:1.6rem;font-weight:700;color:{color};'>{churn_s:.2f}</div>
            <div style='font-size:.85rem;margin:.4rem 0;'>
                {'🔴 HIGH RISK' if is_risk else '🟢 LOW RISK'} &nbsp;·&nbsp;
                {'✅ Persuadable' if is_persuadable else '⏭️ Skip offers'} &nbsp;·&nbsp;
                {ltv_tier} LTV
            </div>
            <div style='font-weight:600;color:{C["navy"]};font-size:.95rem;'>{action}</div>
            {'<div style="font-size:.82rem;color:#374151;">Max discount budget: ₹'+str(rec_spend)+'</div>' if rec_spend>0 else ''}
        </div>""",unsafe_allow_html=True)

    impact({"Retention Rate":"~28% → 40%+",
            "2nd-Purchase Conversion":"+15–20 pp (90-day)",
            "Campaign ROI":"+30–40% via Uplift targeting"})


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 4 — SOLUTION 3
# ═══════════════════════════════════════════════════════════════════════════
elif "Solution 3" in page:
    banner("Solution 3: Revenue Diversification",
           "LSTM Forecasting (Article 6)  ·  Market Response Models (Article 7)  ·  A/B Testing (Article 9)","📈")

    launch_pct=round(rev_df[rev_df["is_launch"]]["actual"].sum()/rev_df["actual"].sum()*100,1)
    avg_inter =round(rev_df[~rev_df["is_launch"]]["actual"].mean(),1)
    best_offer=offers_df.loc[offers_df["net_uplift"].idxmax(),"offer_type"]

    c1,c2,c3,c4=st.columns(4)
    with c1: kpi("IP-Launch % of GMV",f"{launch_pct}%","Target: <40%",False,C["red"])
    with c2: kpi("Avg. Inter-Launch Revenue",f"₹{avg_inter} Cr/mo","Target: +25–30%",False,C["amber"])
    with c3: kpi("Best Non-Discount Lever",best_offer,"By net revenue uplift",True,C["green"])
    with c4: kpi("Discount ROI vs Alternatives","8× worse","20% disc vs Early Access",False,C["navy"])

    # ── Revenue chart with controls ───────────────────────────────────────
    st.subheader("📊 Revenue: Actual vs BAU Baseline  (Article 6 — LSTM)")
    show_forecast=st.checkbox("Show 6-month forecast",value=True,key="show_fc")
    show_launches=st.checkbox("Highlight IP launch months",value=True,key="show_lnch")

    fig=go.Figure()
    if show_launches:
        for _,row in rev_df[rev_df["is_launch"]].iterrows():
            fig.add_vrect(x0=row["month"]-timedelta(days=15),x1=row["month"]+timedelta(days=15),
                          fillcolor="rgba(192,57,43,0.07)",line_width=0)
    fig.add_trace(go.Scatter(x=rev_df["month"],y=rev_df["bau"],name="BAU Baseline",
                              mode="lines",line=dict(color=C["navy"],width=2,dash="dot")))
    fig.add_trace(go.Scatter(x=rev_df["month"],y=rev_df["actual"],name="Actual Revenue",
                              mode="lines+markers",line=dict(color=C["red"],width=2.5),marker=dict(size=5)))
    if show_forecast:
        fig.add_trace(go.Scatter(x=rev_fc["month"],y=rev_fc["forecast"],name="Forecast",
                                  mode="lines+markers",line=dict(color=C["green"],width=2,dash="dash"),
                                  marker=dict(symbol="diamond",size=7)))
    if show_launches:
        for _,row in rev_df[rev_df["is_launch"]].iterrows():
            fig.add_annotation(x=row["month"],y=row["actual"]+1.5,text="🚀",showarrow=False,font=dict(size=13))
    cs(fig,360); fig.update_layout(xaxis_title="Month",yaxis_title="₹ Crore",legend=dict(orientation="h",y=-.18))
    st.plotly_chart(fig,use_container_width=True)
    insight("The gap between BAU baseline and actuals in non-launch months is the revenue shortfall our inter-launch campaigns are designed to fill.")

    l,r=st.columns(2)

    with l:
        st.subheader("🎁 Offer ROI Builder  (Article 7)")
        st.caption("Adjust parameters to see which offer type wins")
        oc1,oc2=st.columns(2)
        with oc1: base_aov_=st.slider("Avg. Order Value (₹)",300,1200,650,50,key="o_aov")
        with oc2: monthly_reach=st.slider("Monthly Campaign Reach",500,10000,3000,500,key="o_reach")

        offers_live=offers_df.copy()
        offers_live["revenue_impact"]=(offers_live["conv_uplift"]/100*monthly_reach*base_aov_-
                                        offers_live["margin_cost"]/100*monthly_reach*base_aov_).round(0)
        fig2=go.Figure()
        fig2.add_trace(go.Bar(name="Conversion Uplift (%)",x=offers_live["offer_type"],
                               y=offers_live["conv_uplift"],marker_color="#CBD5E1"))
        fig2.add_trace(go.Bar(name="Margin Cost (%)",x=offers_live["offer_type"],
                               y=offers_live["margin_cost"],marker_color=C["red"],opacity=.75))
        fig2.add_trace(go.Scatter(name="Net Uplift",x=offers_live["offer_type"],y=offers_live["net_uplift"],
                                   mode="lines+markers+text",text=[str(v) for v in offers_live["net_uplift"]],
                                   textposition="top center",line=dict(color=C["navy"],width=2.5),marker=dict(size=8)))
        fig2.update_layout(barmode="group",yaxis_title="% Uplift / Cost")
        cs(fig2,300); fig2.update_layout(xaxis_tickangle=-15)
        st.plotly_chart(fig2,use_container_width=True)

        # Show revenue impact table
        st.caption("Estimated monthly revenue impact by offer type")
        st.dataframe(offers_live[["offer_type","net_uplift","revenue_impact"]].rename(columns={
            "offer_type":"Offer","net_uplift":"Net Uplift (%)","revenue_impact":"Est. Rev Impact (₹)"}),
            use_container_width=True,hide_index=True)
        insight("Mystery Box and IP Early Access match discount conversion at 4–8× lower margin cost.")

    with r:
        st.subheader("🧪 A/B Test Simulator  (Article 9)")
        st.caption("Check if a campaign result would be statistically significant")
        ab1,ab2=st.columns(2)
        with ab1:
            control_rev=st.number_input("Control: Avg Rev/Customer (₹)",100,2000,390,10,key="ab_ctrl")
            control_n  =st.number_input("Control: Sample Size",100,10000,4000,100,key="ab_cn")
        with ab2:
            test_rev   =st.number_input("Test: Avg Rev/Customer (₹)",100,2000,445,10,key="ab_test")
            test_n     =st.number_input("Test: Sample Size",100,10000,4000,100,key="ab_tn")

        # Welch's t-test simulation
        std_est=max(control_rev,test_rev)*0.4
        se=np.sqrt((std_est**2/control_n)+(std_est**2/test_n))
        t_stat=(test_rev-control_rev)/se if se>0 else 0
        # Two-tailed p-value approximation
        from math import erfc, sqrt
        p_val=erfc(abs(t_stat)/sqrt(2))
        lift_pct=round((test_rev-control_rev)/control_rev*100,1)
        significant=p_val<0.05

        color=C["green"] if significant else C["amber"]
        verdict="✅ STATISTICALLY SIGNIFICANT — Scale this campaign!" if significant else "⚠️ NOT significant yet — run longer or increase sample size"
        st.markdown(f"""
        <div style='background:{C["lt_blue"] if significant else "#FEF9C3"};
                    border-radius:10px;padding:1rem;border:2px solid {color};margin:.5rem 0;'>
            <div style='display:flex;gap:2rem;'>
                <div><div style='font-size:.75rem;color:#6B7280;'>T-STATISTIC</div>
                     <div style='font-size:1.5rem;font-weight:700;color:{C["dark"]};'>{t_stat:.3f}</div></div>
                <div><div style='font-size:.75rem;color:#6B7280;'>P-VALUE</div>
                     <div style='font-size:1.5rem;font-weight:700;color:{color};'>{p_val:.4f}</div></div>
                <div><div style='font-size:.75rem;color:#6B7280;'>REVENUE LIFT</div>
                     <div style='font-size:1.5rem;font-weight:700;color:{C["navy"]};'>+{lift_pct}%</div></div>
            </div>
            <div style='margin-top:.6rem;font-weight:600;color:{color};font-size:.9rem;'>{verdict}</div>
        </div>""",unsafe_allow_html=True)

        st.markdown("<br>",unsafe_allow_html=True)
        st.subheader("💳 Membership Funnel Simulator")
        mem_base=st.slider("Active customer base",500,5000,2000,100,key="mem_base")
        mem_target_rate=st.slider("Target conversion to member (%)",2,20,9,1,key="mem_rate")
        mem_price=st.selectbox("Membership price (₹/year)",[199,299,399,499],index=1,key="mem_price")
        mem_converts=int(mem_base*mem_target_rate/100)
        mem_rev=round(mem_converts*mem_price/1e5,2)

        funnel=pd.DataFrame({"Stage":["Active Customers","Targeted (60%)","Clicked (20%)","Converted"],
                               "Count":[mem_base,int(mem_base*.6),int(mem_base*.2),mem_converts]})
        fig3=px.funnel(funnel,x="Count",y="Stage",
                        color_discrete_sequence=[C["dark"],C["navy"],C["red"],C["green"]])
        fig3.update_layout(height=220,paper_bgcolor="white",margin=dict(l=5,r=5,t=10,b=5))
        st.plotly_chart(fig3,use_container_width=True)
        st.markdown(f"**Projected membership revenue: ₹{mem_rev}L/year** at ₹{mem_price}/member")

    impact({"IP-Launch Dependency":f"{launch_pct}% → target <40%",
            "Inter-Launch Revenue":"+25–30% vs baseline",
            "Membership Revenue":"₹15–20 Cr by Year 2"})
