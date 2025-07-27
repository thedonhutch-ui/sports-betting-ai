import streamlit as st
import pandas as pd
import requests

# Example suggested picks for demonstration (replace with real logic/API)
suggested_picks = [
    {"Pick": "Las Vegas Aces vs Phoenix Mercury", "Confidence": 0.88},
    {"Pick": "New York Liberty vs Chicago Sky", "Confidence": 0.81},
]

# URLs for each sport's stats CSV from Google Sheets
GOOGLE_SHEETS_URLS = {
    "WNBA": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=1354086104",
    "NFL": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=0",
    "NBA": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=1494548643",
    "NCAAF": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=1807990318",
    "NCAAB": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=783040797",
    "MLB": "https://docs.google.com/spreadsheets/d/10qHJPF7tD7eSl8sRcTDrnzpL60a1Sk8rBuv5J19z1JI/export?format=csv&gid=1111623914"
}

# Allow user to choose a sport
selected_sport = st.sidebar.selectbox("Select a sport", list(GOOGLE_SHEETS_URLS.keys()))

# Load the corresponding Google Sheet
@st.cache_data
def load_stats(url):
    return pd.read_csv(url)

stats_url = GOOGLE_SHEETS_URLS[selected_sport]
stats_df = load_stats(stats_url)

# ✅ DEBUG: Show raw column names before accessing any
st.subheader("🧪 Debug: Google Sheet Column Names")
st.write("Raw columns from Google Sheet:", stats_df.columns.tolist())

# Clean up the column names to be safe
stats_df.columns = stats_df.columns.str.strip()

# Check if 'Team' column exists before proceeding
if "Team" not in stats_df.columns:
    st.error("❌ 'Team' column not found in the Google Sheet. Please check the sheet formatting.")
else:
    # Clean team names in both sources
    stats_df["Team_clean"] = stats_df["Team"].str.lower().str.replace(r'\W+', '', regex=True)

    picks_df = pd.DataFrame(suggested_picks)
    picks_df["Pick_clean"] = picks_df["Pick"].str.lower().str.replace(r'\W+', '', regex=True)

    # Extract team names from picks for comparison (simple example)
    selected_teams = []
    for pick in picks_df["Pick_clean"]:
        for team in stats_df["Team_clean"]:
            if team in pick:
                selected_teams.append(team)

    selected_teams = list(set(selected_teams))

    team_stats = stats_df[stats_df["Team_clean"].isin(selected_teams)]

    st.subheader("🎯 Filtered Matchups")
    st.dataframe(picks_df)

    st.subheader("✅ Suggested Picks")
    for pick in suggested_picks:
        st.markdown(f"- **{pick['Pick']}** (Confidence: {pick['Confidence']*100:.1f}%)")

    st.subheader("📈 Team Stat Comparison")
    if not team_stats.empty:
        st.dataframe(team_stats)
    else:
        st.warning("⚠️ No matching stats found for suggested picks. Make sure team names in Google Sheets and picks match.")
