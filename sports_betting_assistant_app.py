import streamlit as st
import pandas as pd
import requests

# --- Config ---
SPORTSDATAIO_API_KEY = "7fb7250dacd54cb997b9fbfceb011044"
SPORT = "mlb"

# --- Helper: Clean team stats from SportsDataIO ---
def clean_team_stats(df):
    if df.empty:
        st.warning("No stats returned from the API.")
        return df

    if "Name" not in df.columns:
        st.error("❌ 'Name' column missing in MLB stats DataFrame.")
        return df

    df["Name_clean"] = df["Name"].astype(str).str.lower().str.replace(r'\W+', '', regex=True)
    return df

# --- Helper: Clean pick names (simulate picks for demo) ---
def clean_name(name):
    return str(name).lower().replace(" ", "").replace("-", "")

# --- Load MLB team stats from SportsDataIO ---
def load_mlb_team_stats():
    url = f"https://api.sportsdata.io/v4/mlb/stats/json/TeamSeasonStats/2024"
    headers = {"Ocp-Apim-Subscription-Key": SPORTSDATAIO_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.error(f"❌ Failed to fetch MLB stats: {response.status_code}")
        return pd.DataFrame()

    df = pd.DataFrame(response.json())
    return clean_team_stats(df)

# --- Simulated Picks (replace with your own logic/API later) ---
def get_sample_picks():
    return pd.DataFrame({
        "Team": ["Yankees", "Red Sox", "Dodgers", "Astros"],
        "Confidence": [0.72, 0.65, 0.58, 0.81],
    })

# --- App UI ---
st.title("⚾ MLB Betting Assistant (Live Stats)")

# Load data
mlb_stats = load_mlb_team_stats()
picks_df = get_sample_picks()
picks_df["Team_clean"] = picks_df["Team"].apply(clean_name)

if mlb_stats.empty:
    st.stop()

# Match stats to picks
comparison = pd.merge(
    picks_df,
    mlb_stats,
    left_on="Team_clean",
    right_on="Name_clean",
    how="left"
)

# Display filtered matchups
st.subheader("🧠 Suggested Picks")
for _, row in picks_df.iterrows():
    st.markdown(f"✅ **{row['Team']}** with confidence **{int(row['Confidence']*100)}%**")

# Show stat comparison
st.subheader("📊 Team Stat Comparison (Matched)")
if comparison.empty or comparison["Name"].isna().all():
    st.warning("No matching stats found for the suggested picks.")
else:
    stat_cols = ["Name", "Wins", "Losses", "Runs", "EarnedRunAverage", "BattingAverage"]
    existing = [col for col in stat_cols if col in comparison.columns]
    st.dataframe(comparison[existing])

# Debug output (optional)
# st.write("Raw Stats Columns:", mlb_stats.columns.tolist())
# st.write("Team Names from API:", mlb_stats['Name_clean'].unique().tolist())
# st.write("Team Names from Picks:", picks_df['Team_clean'].unique().tolist())
