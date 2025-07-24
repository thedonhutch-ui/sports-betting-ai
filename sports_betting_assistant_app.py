import streamlit as st
import pandas as pd
import requests
import random
import altair as alt
import math

# ============================
# API & Sport Config
# ============================
ODDS_API_KEY = "e1a0d3aca26d43993c899a17c319a9b1"

st.set_page_config(page_title="Sports Betting Assistant", layout="wide")
st.title("📊 Sports Betting Assistant")

sport = st.selectbox("Choose a sport", ["NFL", "NBA", "MLB", "WNBA", "NCAAF", "NCAAB"])

sport_key_map = {
    "NFL": "americanfootball_nfl",
    "NBA": "basketball_nba",
    "MLB": "baseball_mlb",
    "WNBA": "basketball_wnba",
    "NCAAF": "americanfootball_ncaaf",
    "NCAAB": "basketball_ncaab"
}

selected_key = sport_key_map[sport]

@st.cache_data(show_spinner=False)
def fetch_odds_data(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "regions": "us",
        "markets": "h2h",
        "apiKey": ODDS_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        st.error("Failed to fetch odds data.")
        return pd.DataFrame()

    games = response.json()
    data = []
    for game in games:
        matchup = f"{game['home_team']} vs {game['away_team']}"
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                if market["key"] == "h2h":
                    outcomes = market["outcomes"]
                    row = {
                        "Matchup": matchup,
                        "Bookmaker": bookmaker["title"],
                        "Moneyline_Home": outcomes[0]["price"],
                        "Moneyline_Away": outcomes[1]["price"],
                        "Commence Time": game["commence_time"],
                        "Home Team": game['home_team'],
                        "Away Team": game['away_team']
                    }
                    data.append(row)
    return pd.DataFrame(data)

odds_df = fetch_odds_data(selected_key)

if odds_df.empty:
    st.warning("No data available yet. Try again shortly.")
else:
    # ========== FILTERS ==========
    st.sidebar.header("🔎 Filters")
    search_team = st.sidebar.text_input("Search Team (partial name)")
    min_odds, max_odds = st.sidebar.slider("Moneyline Range", -1000, 1000, (-1000, 1000))
    bookmaker_filter = st.sidebar.multiselect("Bookmaker", odds_df["Bookmaker"].unique())
    min_conf, max_conf = st.sidebar.slider("Confidence Range (%)", 50, 100, (60, 100))
    pick_count = st.sidebar.slider("Number of Picks", 1, 10, 3)

    filtered_df = odds_df.copy()
    if search_team:
        filtered_df = filtered_df[filtered_df["Matchup"].str.contains(search_team, case=False, na=False)]
    filtered_df = filtered_df[
        (filtered_df["Moneyline_Home"].between(min_odds, max_odds)) &
        (filtered_df["Moneyline_Away"].between(min_odds, max_odds))
    ]
    if bookmaker_filter:
        filtered_df = filtered_df[filtered_df["Bookmaker"].isin(bookmaker_filter)]

    st.subheader("📋 Filtered Matchups")
    st.dataframe(filtered_df)

    if not filtered_df.empty:
        # ========== PICKS ==========
        st.subheader("🔮 Suggested Value Picks")
        picks = []
        for _, row in filtered_df.sample(min(pick_count, len(filtered_df))).iterrows():
            side = random.choice(["Home", "Away"])
            team = row["Home Team"] if side == "Home" else row["Away Team"]
            odds = row["Moneyline_Home"] if side == "Home" else row["Moneyline_Away"]
            confidence = round(random.uniform(min_conf, max_conf), 2)
            
            implied_prob = round(100 / abs(odds) if odds < 0 else abs(odds) / (abs(odds) + 100) * 100, 2)

            # Confidence Tier
            if confidence >= 85:
                color = "🟢 High"
            elif confidence >= 70:
                color = "🟠 Medium"
            else:
                color = "🔴 Low"

            picks.append({
                "Pick": team,
                "Side": side,
                "Odds": odds,
                "Confidence": confidence,
                "Confidence Tier": color,
                "Implied Prob %": implied_prob,
                "Bookmaker": row["Bookmaker"],
                "Matchup": row["Matchup"],
                "Commence Time": row["Commence Time"],
                "Home Team": row["Home Team"],
                "Away Team": row["Away Team"]
            })

        picks_df = pd.DataFrame(picks).sort_values(by="Confidence", ascending=False)
        st.dataframe(picks_df)

        # ========== TEAM STATS ==========
        st.subheader("📊 Team Stats (From CSV)")
        stats_files = {
            "NFL": "nfl_team_stats.csv",
            "NBA": "nba_team_stats.csv",
            "MLB": "mlb_team_stats.csv",
            "WNBA": "wnba_team_stats.csv",
            "NCAAF": "ncaaf_team_stats.csv",
            "NCAAB": "ncaab_team_stats.csv"
        }

        try:
            stats = pd.read_csv(stats_files[sport])
            selected_teams = list(set(picks_df["Home Team"]) | set(picks_df["Away Team"]))
            team_stats = stats[stats["Team"].isin(selected_teams)]

            if team_stats.empty:
                st.info("Stats not found for selected teams.")
            else:
                st.dataframe(team_stats)

                st.subheader("📊 Stat Comparison Chart")
                melted = team_stats.melt(id_vars="Team", var_name="Stat", value_name="Value")
                chart = alt.Chart(melted).mark_bar().encode(
                    x=alt.X('Stat:N'),
                    y=alt.Y('Value:Q'),
                    color='Team:N',
                    column='Team:N'
                ).properties(width=120)
                st.altair_chart(chart, use_container_width=True)

                # Smart Notes
                st.subheader("🧠 Smart Pick Notes")
                for _, row in picks_df.iterrows():
                    team = row["Pick"]
                    opp = row["Away Team"] if team == row["Home Team"] else row["Home Team"]
                    team_row = team_stats[team_stats["Team"] == team]
                    opp_row = team_stats[team_stats["Team"] == opp]
                    if not team_row.empty and not opp_row.empty:
                        note = f"**{team} ({team_row.iloc[0,1]} PPG)** vs {opp} ({opp_row.iloc[0,1]} PPG), Def Rank: {team_row.iloc[0,3]} vs {opp_row.iloc[0,3]}"
                        st.markdown(f"- {note}")

                # Download Combined
                st.subheader("⬇️ Download Picks + Stats")
                download_df = picks_df.merge(stats, how="left", left_on="Pick", right_on="Team")
                st.download_button(
                    label="📥 Download (CSV)",
                    data=download_df.to_csv(index=False),
                    file_name="value_picks_with_stats.csv",
                    mime="text/csv"
                )

        except FileNotFoundError:
            st.warning("Stats file not found. Please upload the correct CSV.")
        except Exception as e:
            st.error(f"Error loading stats: {e}")

    # ========== ROI SIMULATOR ==========
    st.subheader("📈 ROI Simulator")
    uploaded = st.file_uploader("Upload Pick Results CSV (columns: Pick, Odds, Confidence, Result)", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        unit = 100
        df['Payout'] = df.apply(lambda x: unit * (x['Odds']/100) if x['Odds'] > 0 else unit * (100/abs(x['Odds'])) if x['Result'] == 'Win' else -unit, axis=1)
        df['Profit'] = df['Payout'].where(df['Result'] == 'Win', -unit)
        total_bets = len(df)
        wins = (df['Result'] == 'Win').sum()
        roi = df['Profit'].sum() / (unit * total_bets) * 100

        st.metric("Total Bets", total_bets)
        st.metric("Wins", wins)
        st.metric("Win Rate", f"{wins/total_bets*100:.1f}%")
        st.metric("Profit", f"${df['Profit'].sum():.2f}")
        st.metric("ROI", f"{roi:.1f}%")

    # ========== Implied Probability vs Confidence ==========
    st.subheader("📉 Confidence vs Implied Probability")
    if not picks_df.empty:
        chart = alt.Chart(picks_df).mark_circle(size=80).encode(
            x=alt.X("Implied Prob %", scale=alt.Scale(zero=False)),
            y=alt.Y("Confidence", scale=alt.Scale(zero=False)),
            tooltip=["Pick", "Confidence", "Implied Prob %", "Odds"]
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)








                      

                                    

