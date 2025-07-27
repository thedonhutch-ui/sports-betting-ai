import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="📊 Sports Betting Assistant", layout="wide")

st.title("🏈📈 Sports Betting Assistant with Team Stats")

# ---------------------- #
# 1. Load Google Sheets URLs
# ---------------------- #
SHEET_URLS = {
    "NFL":   "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=0",
    "NBA":   "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=1494548643",
    "WNBA":  "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=1354086104",
    "MLB":   "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=1111623914",
    "NCAAF": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=1807990318",
    "NCAAB": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=783040797",
}

# ---------------------- #
# 2. Clean Function
# ---------------------- #
def clean_name(name):
    return ''.join(e.lower() for e in str(name) if e.isalnum())

# ---------------------- #
# 3. Select Sport
# ---------------------- #
sport = st.selectbox("Select a sport:", list(SHEET_URLS.keys()))
sheet_url = SHEET_URLS[sport]

# ---------------------- #
# 4. Load Team Stats from Google Sheets
# ---------------------- #
try:
    stats_df = pd.read_csv(sheet_url)

    # Clean column names
    stats_df.columns = stats_df.columns.str.strip().str.lower()

    # Debug: show raw column names
    st.subheader("🧪 Debug: Columns in loaded Google Sheet")
    st.write(stats_df.columns.tolist())

    if 'team' not in stats_df.columns:
        st.error("❌ The 'team' column is missing in this sheet after cleaning.")
        stats_df = None
    else:
        # Create cleaned team column
        stats_df["team_clean"] = stats_df["team"].apply(clean_name)
except Exception as e:
    st.error(f"Failed to load stats: {e}")
    stats_df = None

# ---------------------- #
# 5. Simulate Suggested Picks
# ---------------------- #
st.subheader("✅ Suggested Picks (Simulated)")
picks_data = [
    {"Matchup": "Aces vs Liberty", "Pick": "Aces"},
    {"Matchup": "Storm vs Mercury", "Pick": "Storm"},
    {"Matchup": "Lynx vs Wings", "Pick": "Lynx"},
]
picks_df = pd.DataFrame(picks_data)
picks_df["pick_clean"] = picks_df["Pick"].apply(clean_name)
st.dataframe(picks_df)

# ---------------------- #
# 6. Compare Team Stats to Picks
# ---------------------- #
if stats_df is not None:
    st.subheader("📊 Team Stat Comparison for Suggested Picks")

    # Match cleaned picks to stats
    merged_df = picks_df.merge(
        stats_df,
        left_on="pick_clean",
        right_on="team_clean",
        how="left",
        suffixes=("", "_stat")
    )

    # Debug output
    st.write("🔎 Picks (from API):", picks_df["pick_clean"].unique().tolist())
    st.write("📋 Teams (from Sheet):", stats_df["team_clean"].unique().tolist())

    if merged_df.isnull().any().any():
        st.warning("⚠️ Some teams from picks didn't match team stats.")

    st.dataframe(merged_df)

else:
    st.warning("📉 Stats not loaded, cannot compare with picks.")
