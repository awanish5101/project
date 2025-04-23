import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set Streamlit page configuration
st.set_page_config(page_title="DevTrack – GitHub Dashboard", layout="wide")
st.title("🚀 DevTrack – GitHub Productivity Dashboard")

# Sidebar for user input
st.sidebar.header("🔍 GitHub User")
username = st.sidebar.text_input("Enter GitHub username", value="torvalds")

if username:
    st.sidebar.markdown(f"Viewing data for **{username}**")

    # Fetch public repositories
    repos_url = f"https://api.github.com/users/{username}/repos"
    repos_res = requests.get(repos_url)

    if repos_res.status_code == 200:
        repos_data = repos_res.json()
        repo_names = [repo['name'] for repo in repos_data]

        selected_repo = st.sidebar.selectbox("📁 Select Repository", repo_names)

        if selected_repo:
            commits_url = f"https://api.github.com/repos/{username}/{selected_repo}/commits"
            commits_res = requests.get(commits_url)

            if commits_res.status_code == 200:
                commits_data = commits_res.json()
                commit_dates = [
                    datetime.strptime(commit['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
                    for commit in commits_data
                ]

                df = pd.DataFrame(commit_dates, columns=["commit_date"])
                df["date"] = df["commit_date"].dt.date
                df["hour"] = df["commit_date"].dt.hour

                st.subheader(f"📈 Daily Commit Activity in {selected_repo}")
                daily_commits = df.groupby("date").size().reset_index(name='count')
                fig = px.line(daily_commits, x='date', y='count', title='Daily Commits Over Time')
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("🕒 Commits by Hour")
                hourly_commits = df.groupby("hour").size().reset_index(name='count')
                fig2 = px.bar(hourly_commits, x='hour', y='count', title='Hourly Commit Distribution')
                st.plotly_chart(fig2, use_container_width=True)

                # Language usage
                st.subheader("🧑‍💻 Language Distribution (Repo-wide)")
                lang_url = f"https://api.github.com/repos/{username}/{selected_repo}/languages"
                lang_res = requests.get(lang_url)
                if lang_res.status_code == 200:
                    lang_data = lang_res.json()
                    lang_df = pd.DataFrame(lang_data.items(), columns=["Language", "Bytes"])
                    fig3 = px.pie(lang_df, names='Language', values='Bytes', title='Language Usage')
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.warning("Couldn't fetch language data.")

            else:
                st.error("❌ Couldn't fetch commits. Try again later or check repo visibility.")
    else:
        st.error("❌ Couldn't fetch repositories. Please check the username.")
else:
    st.info("👆 Enter a GitHub username in the sidebar to begin.")