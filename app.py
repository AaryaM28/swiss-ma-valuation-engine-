import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Swiss M&A Valuation Engine", layout="wide")

st.title("🇨🇭 Swiss M&A Valuation Engine")
st.markdown("""
This institutional-grade dashboard automatically scrapes live market data from public Swiss equities to determine 
the implied operational valuation (**Enterprise Value**) of a private target company using market multiples (**EV/EBITDA**).
""")
st.write("---")
st.sidebar.header("Target Company Financials")
target_name = st.sidebar.text_input("Company Name", value="Zurich BioTech AG")

# Input slider for EBITDA (ranging from 1M to 100M, default 25M)
target_ebitda = st.sidebar.slider(
    "Target Annual EBITDA (in CHF)", 
    min_value=1_000_000, 
    max_value=100_000_000, 
    value=25_000_000, 
    step=1_000_000
)
tickers = ["NESN.SW", "NOVN.SW", "RO.SW"]
comps_data = []
with st.spinner("Scraping live market multiples from SIX Swiss Exchange..."):
  for tick in tickers:
      stock = yf.Ticker(tick)
      info = stock.info
      name = info.get("longName", tick)
      enterprise_val = info.get("enterpriseValue", 0)
      ebitda = info.get("ebitda", 1) 
      ev_ebitda_multiple = info.get("enterpriseToEbitda", 0)
      rev_growth = info.get("revenueGrowth", 0)
      
      comps_data.append({
          "Ticker": tick,
          "Company Name": name,
          "Enterprise Value ($B)": round(enterprise_val / 1_000_000_000, 2), # convert to billions
          "EBITDA ($B)": round(ebitda / 1_000_000_000, 2),
          "EV / EBITDA": round(ev_ebitda_multiple, 2),
          "Revenue Growth (%)": rev_growth
      })

df = pd.DataFrame(comps_data)
avg_ev_ebitda = df["EV / EBITDA"].median() #to avoid outliers skewing data 

#print layout 
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Public Peer Group (Trading Comps)")
    st.dataframe(df, use_container_width=True)
with col2:
    st.subheader("Market Benchmark")
    # final valuation multiple as a large metric card
    st.metric(label="Peer Group Median EV/EBITDA", value=f"{round(avg_ev_ebitda, 2)}x")

st.write("---")
st.subheader(f"Implied Valuation Analysis: {target_name}")
implied_ev = target_ebitda * avg_ev_ebitda 
v_col1, v_col2 = st.columns(2)
with v_col1:
    st.metric(label="Input Operating EBITDA", value=f"CHF {target_ebitda:,}")
with v_col2:
    # Highlight the final enterprise valuation target
    st.metric(label="Implied Enterprise Value (Estimated Takeover Price)", value=f"CHF {round(implied_ev, 2):,}")

st.info(f"💡 **Analyst Note:** A buyer looking to acquire {target_name} would expect to pay an enterprise value of approximately **CHF {round(implied_ev, 2):,}** based on current public trading valuations of peer institutions.")
