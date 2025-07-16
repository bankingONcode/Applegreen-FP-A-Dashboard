import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

st.set_page_config(page_title="Executive FP&A Dashboard", layout="wide")

# === Load Data ===
df = pd.read_excel("fpa_engine_full_output.xlsx", sheet_name="Base_Results")
product_analysis = pd.read_excel("fpa_engine_full_output.xlsx", sheet_name="Product_Analysis")
scenario_df = pd.read_excel("fpa_engine_full_output.xlsx", sheet_name="Scenario_Results")
variance_df = pd.read_excel("fpa_engine_full_output.xlsx", sheet_name="Variance_vs_Base")
monte_df = pd.read_excel("fpa_engine_full_output.xlsx", sheet_name="Monte_Carlo")

# === Clean ROCE ===
df["ROCE_cleaned"] = np.where(
    df["Allocated Capex/ product"] > 10,
    df["EBITDA"] / df["Allocated Capex/ product"],
    np.nan
)

# === Select Brand ===
st.title("📊 Executive FP&A Dashboard")
brand_selected = st.selectbox("Select Brand", df["Brand"].unique())
brand_df = df[df["Brand"] == brand_selected]

# === Brand-Level KPIs ===
st.subheader(f"📌 KPIs for {brand_selected}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${brand_df['Revenue'].sum():,.0f}")
col2.metric("Total EBITDA", f"${brand_df['EBITDA'].sum():,.0f}")
col3.metric("Avg ROCE", f"{brand_df['ROCE_cleaned'].mean():.2f}%")
col4.metric("Flagged SKUs", f"{brand_df[(brand_df['ROCE_cleaned'] < 10) | (brand_df['Payback'] > 24)].shape[0]}")

# === Top & Bottom Products ===
st.markdown("### 🏆 Top Performing Products by ROCE")
top_5 = brand_df.sort_values("ROCE_cleaned", ascending=False).head(5)
st.dataframe(top_5[["Product", "Revenue", "EBITDA", "ROCE_cleaned", "Payback"]])

st.markdown("### ⚠️ Underperforming Products")
underperf = brand_df[(brand_df["ROCE_cleaned"] < 10) | (brand_df["Payback"] > 24)]
st.dataframe(underperf[["Product", "Revenue", "ROCE_cleaned", "Payback"]])

# === Visual: EBITDA by Product ===
st.subheader("📊 EBITDA by Product")
bar_chart = alt.Chart(brand_df).mark_bar().encode(
    x=alt.X("EBITDA:Q", title="EBITDA ($)"),
    y=alt.Y("Product:N", sort="-x"),
    color="Product:N",
    tooltip=["Revenue", "ROCE_cleaned", "Payback"]
).properties(height=400)
st.altair_chart(bar_chart, use_container_width=True)

# === Visual: ROCE vs Revenue ===
st.subheader("📈 ROCE vs Revenue (Bubble Plot)")
scatter = alt.Chart(brand_df).mark_circle(size=100).encode(
    x="Revenue",
    y="ROCE_cleaned",
    size="EBITDA",
    color="Product",
    tooltip=["Product", "Revenue", "EBITDA", "ROCE_cleaned"]
).interactive()
st.altair_chart(scatter, use_container_width=True)

# === Scenario Planning Section ===
st.header("📉 Scenario Planning")
scenario_filtered = scenario_df[scenario_df["Brand"] == brand_selected]
selected_product = st.selectbox("Select Product for Scenario Comparison", scenario_filtered["Product"].unique())
scenario_view = scenario_filtered[scenario_filtered["Product"] == selected_product]

st.markdown("#### Scenario EBITDA Comparison")
scenario_bar = alt.Chart(scenario_view).mark_bar().encode(
    x="Scenario:N",
    y="Scenario EBITDA:Q",
    color="Scenario:N",
    tooltip=["Scenario EBITDA", alt.Tooltip("Scenario ROCE", format=".2f"), "Scenario Payback"]
)
st.altair_chart(scenario_bar, use_container_width=True)

# === Monte Carlo Simulation ===
st.header("🎲 Monte Carlo Risk Simulation")
selected_mc_product = st.selectbox("Select Product for Monte Carlo", monte_df["Product"].unique())
mc_data = monte_df[monte_df["Product"] == selected_mc_product]

fig, ax = plt.subplots()
sns.histplot(mc_data["EBITDA"], bins=50, kde=True, ax=ax)
ax.set_title(f"{selected_mc_product} – Simulated EBITDA Distribution")
st.pyplot(fig)

st.markdown(
    f"- **Mean EBITDA**: ${mc_data['EBITDA'].mean():,.0f}  \n"
    f"- **Std Dev (Volatility)**: ${mc_data['EBITDA'].std():,.0f}  \n"
    f"- **ROCE Range**: {mc_data['ROCE'].min():.2f} to {mc_data['ROCE'].max():.2f}  \n"
    f"- **Payback Range**: {mc_data['Payback'].min():.1f} to {mc_data['Payback'].max():.1f} months"
)

# === Ops Risk Flags ===
st.header("🚨 Operational Risk Flags")
flagged = brand_df[(brand_df["ROCE_cleaned"] < 10) | (brand_df["Payback"] > 24)]
st.metric("Flagged Products", flagged.shape[0])
st.dataframe(flagged[["Product", "Revenue", "ROCE_cleaned", "Payback"]])

# === Summary Recommendations ===
st.header("✅ Summary & Recommendations")
if not flagged.empty:
    worst = flagged.sort_values("Payback", ascending=False).iloc[0]
    st.markdown(f"- 🚫 Cut or fix **{worst['Product']}** — payback too long or return too low.")
if not top_5.empty:
    best = top_5.iloc[0]
    st.markdown(f"- 🚀 Invest more in **{best['Product']}** — best ROCE at {best['ROCE_cleaned']:.2f}%.")

st.markdown("📌 Use this dashboard to guide monthly reviews and reallocate based on ROI.")
