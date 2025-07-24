import streamlit as st
import pandas as pd
import requests
import random
import altair as alt

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
    params = {"regions": "us", "markets": "h2h", "apiKey": ODDS_API_KEY}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        st.error("Failed to fetch odds data.")
        return pd.DataFrame()
    data = []
    for game in response.json():
        matchup = f"{game['home_team']} vs {game['away_team']}"
        for b in game.get("bookmakers", []):
            for m in b.get("markets", []):
                if m["key"] == "h2h":
                    outcomes = m["outcomes"]
                    data.append({
                        "Matchup": matchup,
                        "Bookmaker": b["title"],
                        "Moneyline_Home": outcomes[0]["price"],
                        "Moneyline_Away": outcomes[1]["price"],
                        "Commence Time": game["commence_time"],
                        "Home Team": game["home_team"],
                        "Away Team": game["away_team"]
                    })
    return pd.DataFrame(data)

odds_df = fetch_odds_data(selected_key)

if odds_df.empty:
    st.warning("No odds data available. Please refresh.")
else:
    st.sidebar.header("🔎 Filters")
    search_team = st.sidebar.text_input("Search Team")
    min_odds, max_odds = st.sidebar.slider("Moneyline Range", -1000, 1000, (-1000, 1000))
    bookmakers = st.sidebar.multiselect("Bookmaker", odds_df["Bookmaker"].unique())
    min_conf, max_conf = st.sidebar.slider("Confidence Range (%)", 50, 100, (60, 100))
    pick_count = st.sidebar.slider("Number of Picks", 1, 10, 3)

    df = odds_df.copy()
    if search_team:
        df = df[df["Matchup"].str.contains(search_team, case=False)]
    df = df[df["Moneyline_Home"].between(min_odds, max_odds) & df["Moneyline_Away"].between(min_odds, max_odds)]
    if bookmakers:
        df = df[df["Bookmaker"].isin(bookmakers)]

    st.subheader("📋 Filtered Matchups")
    st.dataframe(df)

    if not df.empty:
        st.subheader("🔮 Suggested Value Picks")
        picks = []
        sample_df = df.sample(n=min(pick_count, len(df)))
        for _, r in sample_df.iterrows():
            side = random.choice(["Home", "Away"])
            team = r["Home Team"] if side == "Home" else r["Away Team"]
            odds = r["Moneyline_Home"] if side == "Home" else r["Moneyline_Away"]
            confidence = round(random.uniform(min_conf, max_conf), 2)
            picks.append({**r.to_dict(), "Pick": team, "Side": side, "Odds": odds, "Confidence": confidence})

        picks_df = pd.DataFrame(picks).sort_values("Confidence", ascending=False)
        st.dataframe(picks_df)

        st.subheader("📊 Team Stats (From CSV)")
        stat_files = {
            "NFL": "nfl_team_stats.csv",
            "NBA": "nba_team_stats.csv",
            "MLB": "mlb_team_stats.csv",
            "WNBA": "wnba_team_stats.csv",
            "NCAAF": "ncaaf_team_stats.csv",
            "NCAAB": "ncaab_team_stats.csv"
        }

        try:
            stats = pd.read_csv(stat_files[sport])
            teams = set(picks_df["Home Team"]) | set(picks_df["Away Team"])
            team_stats = stats[stats["Team"].isin(teams)]
            if team_stats.empty:
                st.info("No stats found for selected teams.")
            else:
                st.dataframe(team_stats)

                st.subheader("📊 Stat Comparison Chart")
                melted = team_stats.melt(id_vars="Team", var_name="Stat", value_name="Value")
                chart = alt.Chart(melted).mark_bar().encode(
                    x="Stat:N", y="Value:Q", color="Team:N", column="Team:N"
                ).properties(width=120)
                st.altair_chart(chart, use_container_width=True)

                st.subheader("⬇️ Download Picks + Stats")
                dl_df = picks_df.merge(stats, how="left", left_on="Pick", right_on="Team")
                st.download_button(
                    "📥 Download (CSV)",
                    data=dl_df.to_csv(index=False),
                    file_name="value_picks_with_stats.csv",
                    mime="text/csv"
                )
# ========== TEAM STATS SECTION ==========
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

            # ========== STATS VISUALIZATION ==========
            st.subheader("📊 Stat Comparison Chart")
            melted = team_stats.melt(id_vars="Team", var_name="Stat", value_name="Value")
            chart = alt.Chart(melted).mark_bar().encode(
                x=alt.X('Stat:N', title="Stat Category"),
                y=alt.Y('Value:Q', title="Stat Value"),
                color='Team:N',
                column='Team:N'
            ).properties(width=120)
            st.altair_chart(chart, use_container_width=True)

            # ========== COMBINED DOWNLOAD ==========
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
        except FileNotFoundError:
            st.warning("Stats file not found. Please upload the correct CSV.")
        except Exception as e:
            st.error(f"Error loading stats: {e}")

                                    

