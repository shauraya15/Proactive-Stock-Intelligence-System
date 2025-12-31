import streamlit as st
from snowflake.snowpark.context import get_active_session

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Proactive Stock Intelligence System",
    page_icon="🚨",
    layout="wide"
)

session = get_active_session()

# ============================================================
# GLOBAL STYLES (WOW UI – Snowflake Safe)
# ============================================================
st.markdown("""
<style>
@keyframes fadeInUp {
  from {opacity: 0; transform: translateY(25px);}
  to {opacity: 1; transform: translateY(0);}
}

.fade-in {
  animation: fadeInUp 1s ease forwards;
}

.header-box {
  padding: 40px;
  border-radius: 26px;
  background: linear-gradient(135deg, #020617, #111827);
  color: white;
  box-shadow: 0 25px 60px rgba(0,0,0,0.6);
}

.kpi-card {
  padding: 26px;
  border-radius: 22px;
  color: white;
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-6px);
}

.kpi-red { background: linear-gradient(135deg, #dc2626, #fb7185); }
.kpi-blue { background: linear-gradient(135deg, #2563eb, #38bdf8); }
.kpi-green { background: linear-gradient(135deg, #16a34a, #4ade80); }

.section-box {
  padding: 30px;
  border-radius: 24px;
  background: rgba(255,255,255,0.9);
  box-shadow: 0 15px 45px rgba(0,0,0,0.1);
}

.action-box {
  padding: 32px;
  border-radius: 26px;
  background: linear-gradient(135deg, #fff7ed, #ffedd5);
  border: 2px solid #fb923c;
}

.badge-live {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 999px;
  background: #22c55e;
  color: white;
  font-weight: 700;
}

.stButton>button {
  font-size: 18px;
  font-weight: 700;
  padding: 14px;
  border-radius: 14px;
  background: linear-gradient(90deg, #f97316, #fb923c);
  color: white;
  border: none;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="header-box fade-in">
  <h1>🚨 Proactive Stock Intelligence System</h1>
  <h4>Explainable AI • Human-in-the-Loop • Action-Oriented</h4>
  <p>Mission-critical supply chain intelligence for public health & NGOs</p>
  <span class="badge-live">🟢 LIVE — Snowflake Native Intelligence</span>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============================================================
# LOAD HIGH-RISK ALERTS
# ============================================================
alerts_df = session.sql("""
    SELECT
        location,
        item,
        date,
        days_of_stock_left,
        recommended_reorder_qty,
        reason_supply_gap,
        reason_high_consumption,
        reason_long_lead_time
    FROM STOCK_INTELLIGENCE_DB.PUBLIC.STOCK_RISK_EXPLANATIONS
    WHERE stock_risk_level = 'HIGH'
    ORDER BY days_of_stock_left ASC
""").to_pandas()

if alerts_df.empty:
    st.success("✅ All items are currently within safe operational limits.")
    st.stop()

# ============================================================
# KPI STRIP
# ============================================================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="kpi-card kpi-red fade-in">
      <h3>🔴 Critical Alerts</h3>
      <h1>{len(alerts_df)}</h1>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card kpi-blue fade-in">
      <h3>⏳ Min Days Left</h3>
      <h1>{round(alerts_df["DAYS_OF_STOCK_LEFT"].min(),1)}</h1>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card kpi-green fade-in">
      <h3>📦 Max Reorder Qty</h3>
      <h1>{int(alerts_df["RECOMMENDED_REORDER_QTY"].max())}</h1>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================
# INVENTORY HEATMAP (NO PLOTLY – SAFE)
# ============================================================
st.markdown("""
<div class="section-box fade-in">
<h2>📍 Inventory Risk Heatmap</h2>
<p><b>Days of stock remaining by location and item</b><br>
🔴 Critical • 🟡 Warning • 🟢 Safe</p>
</div>
""", unsafe_allow_html=True)

heatmap_df = alerts_df.pivot_table(
    index="LOCATION",
    columns="ITEM",
    values="DAYS_OF_STOCK_LEFT",
    aggfunc="min"
)

def color_scale(val):
    if val <= 2:
        return "background-color:#dc2626;color:white;"
    elif val <= 5:
        return "background-color:#facc15;color:black;"
    else:
        return "background-color:#16a34a;color:white;"

styled_heatmap = heatmap_df.style.applymap(color_scale).format("{:.1f}")

st.dataframe(styled_heatmap, use_container_width=True)

st.divider()

# ============================================================
# ALERT TABLE
# ============================================================
st.markdown("""
<div class="section-box fade-in">
<h2>⚠️ Items Requiring Immediate Attention</h2>
<p>Only actionable, explainable risks are surfaced.</p>
</div>
""", unsafe_allow_html=True)

st.dataframe(alerts_df, use_container_width=True, hide_index=True)

st.divider()

# ============================================================
# DECISION INTELLIGENCE
# ============================================================
st.markdown("""
<div class="section-box fade-in">
<h3>🧠 Why these alerts were generated</h3>
<ul>
  <li>📉 Stock projected to deplete before replenishment</li>
  <li>📈 Sustained consumption trend detected</li>
  <li>⏱️ Long supplier lead-time increases risk</li>
</ul>
<p><b>This system prioritizes operational action — not reporting.</b></p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ============================================================
# OPERATIONAL ACTION (WRITE-BACK)
# ============================================================
st.markdown("""
<div class="action-box fade-in">
<h2>🛠️ Log Operational Decision</h2>
<p>Close the loop by persisting human decisions directly into Snowflake.</p>
</div>
""", unsafe_allow_html=True)

selected_item = st.selectbox(
    "Select item to acknowledge",
    sorted(alerts_df["ITEM"].unique())
)

if st.button("🚨 ACKNOWLEDGE & LOG DECISION", use_container_width=True):
    session.sql(f"""
        UPDATE STOCK_INTELLIGENCE_DB.PUBLIC.STOCK_ALERT_LOG
        SET alert_status = 'ACKNOWLEDGED'
        WHERE item = '{selected_item}'
          AND alert_status = 'NEW'
    """).collect()

    st.success(f"✅ All active alerts for **{selected_item}** acknowledged.")
    st.rerun()

st.divider()

# ============================================================
# FOOTER
# ============================================================
st.info("""
**Impact at scale**
• Prevents life-critical medicine stock-outs  
• Enables proactive procurement  
• Creates audit-ready operational logs  
• Designed for governments, NGOs & disaster response
""")

st.caption(
    "Built on Snowflake Dynamic Tables • Tasks • Streamlit | "
    "Explainable • Human-in-the-Loop • Production-Ready"
)
