import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="FP&A Dashboard", layout="wide")

# Load pre-exported outputs
df = pd.read_excel("fpa_engine_full_output.xlsx", sheet_name="Base_Results")
product_analysis = pd.read_excel("fpa_engine_full_output.xlsx", sheet_name="Product_Analysis")
scenario_df = pd.read_excel("fpa_engine_full_output.xlsx", sheet_name="Scenario_Results")
variance_df = pd.read_excel("fpa_engine_full_output.xlsx", sheet_name="Variance_vs_Base")
monte_df = pd.read_excel("fpa_engine_full_output.xlsx", sheet_name="Monte_Carlo")

st.markdown("""
## 🎯 Why We Built This Engine

This tool is not about reporting — it's about making **better business decisions** without waiting on incomplete data.

We reverse-engineered:
- 📊 Where you're earning profit vs. just generating revenue
- 🔄 Which products are burning resources without ROI
- ⚠️ Where volatility puts your forecasts at risk

Every simulation, scenario, and flag here tells you:  
> **Where to cut, where to reinvest, and where to fix operations.**
""")


st.title("📊 Applegreen FP&A Engine Dashboard")
st.markdown("### Powered by Python + Monte Carlo Simulations + Scenario Planning")

st.markdown("#### 🎯 Key Takeaways")
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${df['Revenue'].sum():,.0f}")
col2.metric("Total EBITDA", f"${df['EBITDA'].sum():,.0f}")
col3.metric("Average ROCE", f"{df['ROCE'].mean():.2%}")

st.header("💰 Product-Level Profitability")

brand_selected = st.selectbox("Choose a Brand", df["Brand"].unique())
brand_products = product_analysis[product_analysis["Brand"] == brand_selected]
st.dataframe(brand_products.sort_values("EBITDA", ascending=False))

st.markdown("### 🔍 What This Means")

top_roce = df.loc[df["ROCE"].idxmax()]
worst_roce = df.loc[df["ROCE"].idxmin()]

st.markdown(f"""
- ✅ Best performer: **{top_roce['Product']}** with **ROCE {top_roce['ROCE']:.2%}**  
  → Consider allocating more CapEx or promotional budget here

- 🛑 Worst performer: **{worst_roce['Product']}** with **ROCE {worst_roce['ROCE']:.2%}**  
  → High spend, low return — reassess pricing, COGS, or operational support
""")


st.header("📉 Scenario Planning")

scenario = st.selectbox("Select a Scenario", scenario_df["Scenario"].unique())
scen_data = scenario_df[(scenario_df["Scenario"] == scenario) & (scenario_df["Brand"] == brand_selected)]

st.dataframe(scen_data.sort_values(by="Scenario EBITDA", ascending=False))


st.header("🎲 Monte Carlo Risk Simulation")

product_selected = st.selectbox("Select Product for Risk View", monte_df["Product"].unique())
mc_data = monte_df[monte_df["Product"] == product_selected]

fig, ax = plt.subplots()
sns.histplot(mc_data["EBITDA"], bins=40, kde=True, ax=ax)
ax.set_title(f"{product_selected} – Simulated EBITDA Distribution")
ax.set_xlabel("EBITDA")
st.pyplot(fig)

st.header("⚠️ What Happens If We Do Nothing")

st.markdown("""
- 🧯 **Opex waste continues** — fixed costs dilute margins on underperforming products
- ⏳ **CapEx tied up** in low-return items delays ROI elsewhere
- 🎯 **Focus drifts** — high-ROCE opportunities get buried under high-volume distractions
- 🎲 **Financial risk increases** — we commit to volatile products without safeguards

> Inaction is not neutral — it’s a hidden cost.
""")



st.header("🔥 Operational Risk Flags (Auto-detected)")

ops_flags = df[
    ((df["ROCE"] < 0.1) | (df["Payback"] > 24)) & (df["Revenue"] > 5000)
].copy()
ops_flags["Issue"] = np.where(
    df["ROCE"] < 0.1, "⚠️ Low ROCE",
    np.where(df["Payback"] > 24, "📉 Slow Payback", "✅ OK")
)

st.dataframe(ops_flags[["Brand", "Product", "Revenue", "ROCE", "Payback", "Issue"]])


st.header("🧾 Key Insights & Next Steps")

st.markdown("""
- 📌 Focus on high-EBITDA, high-ROCE products
- 🛑 Flag/remove poor performers with >24 month payback
- 🔁 Use scenario results for pricing/volume decisions
- 🎲 Use Monte Carlo to identify volatility risks
""")

# 🎲 Monte Carlo Simulation Section
...

# ✅ WHY THIS MATTERS SECTION — PASTE HERE
st.markdown("---")
st.header("📣 Why This Analysis Matters")

audience = st.radio("Select Audience", ["Management", "Operations"])

if audience == "Management":
    st.subheader("📌 Strategic Finance Recommendations")
    st.markdown("""
    - **Reinvest in high-ROCE SKUs**
    - **Cut CapEx from low-return items**
    - **Use pricing strategy to drive EBITDA**
    - **Focus on low-risk product growth paths**
    """)
elif audience == "Operations":
    st.subheader("🔍 Operational Efficiency Opportunities")
    st.markdown("""
    - **Cut Opex drag from low-volume items**
    - **Streamline SKU focus based on EBITDA**
    - **Address price/COGS misalignments**
    - **Inventory + labor can be optimized immediately**
    """)

st.markdown("---")
st.header("✅ So What Should We Do Now?")

st.markdown("""
- 🚀 **Double down on high-ROCE products** — fast return, low risk
- ✂️ **Cut back on slow-payback, volatile SKUs**
- 🔁 **Use this engine to reforecast monthly** and tie it to site-level decision making
- 🛠️ **Don’t wait on ops** — take control of capital planning using this data
""")
