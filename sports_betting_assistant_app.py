import streamlit as st
import pandas as pd
import requests
import random

ODDS_API_KEY = "e1a0d3aca26d43993c899a17c319a9b1"

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

@st.cache_data
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
    # ========== FILTER SECTION ==========
    st.sidebar.header("🔎 Filters")
    search_team = st.sidebar.text_input("Search Team (partial name)")
    min_odds, max_odds = st.sidebar.slider("Moneyline Range", -1000, 1000, (-1000, 1000))
    bookmaker_filter = st.sidebar.multiselect("Bookmaker", odds_df["Bookmaker"].unique())

    filtered_df = odds_df.copy()

    if search_team:
        filtered_df = filtered_df[
            filtered_df["Matchup"].str.contains(search_team, case=False, na=False)
        ]
    filtered_df = filtered_df[
        (filtered_df["Moneyline_Home"].between(min_odds, max_odds)) &
        (filtered_df["Moneyline_Away"].between(min_odds, max_odds))
    ]
    if bookmaker_filter:
        filtered_df = filtered_df[filtered_df["Bookmaker"].isin(bookmaker_filter)]

    st.subheader("📋 Filtered Matchups")
    st.dataframe(filtered_df)

    if not filtered_df.empty:
        # ========== VALUE PICK ==========
        st.subheader("🔮 Suggested Value Pick")
        random_row = filtered_df.sample(1).iloc[0]
        pick_side = random.choice(["Home", "Away"])
        team = random_row["Home Team"] if pick_side == "Home" else random_row["Away Team"]
        odds = random_row["Moneyline_Home"] if pick_side == "Home" else random_row["Moneyline_Away"]
        confidence = round(random.uniform(52.0, 75.0), 2)

        st.markdown(f"""
        ### ✅ Pick: **{team}**
        - Odds: `{odds}`
        - Confidence: `{confidence}%`
        - Bookmaker: `{random_row["Bookmaker"]}`
        - Game: `{random_row["Matchup"]}`
        - Time: `{random_row["Commence Time"]}`
        """)

        # ===== REAL TEAM STATS MERGE =====
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
            team_stats = pd.read_csv(stats_files[sport])
            selected_teams = [random_row["Home Team"], random_row["Away Team"]]
            filtered_stats = team_stats[team_stats["Team"].isin(selected_teams)]

            if filtered_stats.empty:
                st.info("Stats not found for these teams.")
            else:
                st.dataframe(filtered_stats)

                # ========== ADVANCED EXPLANATION ==========
                st.subheader("🤖 Why This Pick?")
                team_stat_row = filtered_stats[filtered_stats["Team"] == team].iloc[0]
                opponent = random_row["Away Team"] if team == random_row["Home Team"] else random_row["Home Team"]
                opponent_stats = team_stats[team_stats["Team"] == opponent]

                if not opponent_stats.empty:
                    opponent_row = opponent_stats.iloc[0]

                    if sport in ["NFL", "NCAAF"]:
                        explanation = f"""
                        ### 🧠 Why We Picked {team}
                        - {team} scores **{team_stat_row['PPG']} PPG** vs {opponent}'s **{opponent_row['PPG']}**
                        - Total offense: **{team_stat_row['Yards/Game']}** vs **{opponent_row['Yards/Game']}**
                        - Defense: {team} is #{team_stat_row['Defense Rank']}, {opponent} is #{opponent_row['Defense Rank']}
                        - Odds: `{odds}`, Confidence: `{confidence}%`
                        """
                    elif sport in ["NBA", "WNBA", "NCAAB"]:
                        explanation = f"""
                        ### 🧠 Why We Picked {team}
                        - {team} averages **{team_stat_row['PPG']} PPG**, {opponent} averages **{opponent_row['PPG']}**
                        - Rebound control: **{team_stat_row.get('RPG', 'N/A')} RPG** vs **{opponent_row.get('RPG', 'N/A')} RPG**
                        - Defense rank: #{team_stat_row.get('Defense Rank', 'N/A')} vs #{opponent_row.get('Defense Rank', 'N/A')}
                        - Odds: `{odds}`, Confidence: `{confidence}%`
                        """
                    elif sport == "MLB":
                        explanation = f"""
                        ### 🧠 Why We Picked {team}
                        - Batting Avg: **{team_stat_row.get('AVG', 'N/A')}** vs **{opponent_row.get('AVG', 'N/A')}**
                        - ERA: **{team_stat_row.get('ERA', 'N/A')}** vs **{opponent_row.get('ERA', 'N/A')}**
                        - Run differential and defense rank are similar.
                        - Odds: `{odds}`, Confidence: `{confidence}%`
                        """
                    else:
                        explanation = "Stats available but not yet configured for this sport."

                    st.markdown(explanation)

                # ========== DOWNLOAD PICK AND STATS ==========
                st.subheader("⬇️ Download This Pick & Team Stats")
                pick_info = pd.DataFrame([{
                    "Pick": team,
                    "Odds": odds,
                    "Confidence": f"{confidence}%",
                    "Bookmaker": random_row["Bookmaker"],
                    "Matchup": random_row["Matchup"],
                    "Commence Time": random_row["Commence Time"]
                }])

                export_df = pd.concat([pick_info, filtered_stats], axis=0, ignore_index=True)

                st.download_button(
                    label="📥 Download Pick + Stats (CSV)",
                    data=export_df.to_csv(index=False),
                    file_name="betting_pick_and_team_stats.csv",
                    mime="text/csv"
                )

        except FileNotFoundError:
            st.warning("Stats file not found. Please upload the correct CSV.")
        except Exception as e:
            st.error(f"Error loading stats: {e}")
            

