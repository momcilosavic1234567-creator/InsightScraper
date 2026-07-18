import os
import json
import asyncio
import threading
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.database import get_all_jobs, update_job_status, update_job_notes
from main import run_pipeline


SCRAPE_STATUS = []
SCRAPE_STATUS_LOCK = threading.Lock()
SCRAPE_RUNNING = False


def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config_data):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)


def add_scrape_log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with SCRAPE_STATUS_LOCK:
        SCRAPE_STATUS.append(f"{timestamp} - {message}")


def get_scrape_logs():
    with SCRAPE_STATUS_LOCK:
        return list(SCRAPE_STATUS)


def clear_scrape_logs():
    with SCRAPE_STATUS_LOCK:
        SCRAPE_STATUS.clear()


def background_scrape():
    global SCRAPE_RUNNING
    if SCRAPE_RUNNING:
        return

    SCRAPE_RUNNING = True
    clear_scrape_logs()
    add_scrape_log("Background scrape started.")
    try:
        asyncio.run(run_pipeline())
        add_scrape_log("Background scrape finished successfully.")
    except Exception as exc:
        add_scrape_log(f"Background scrape failed: {exc}")
    finally:
        SCRAPE_RUNNING = False


def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.stop()


def main():
    st.set_page_config(
        page_title="InsightScraper Dashboard",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
            .stApp {
                background-color: #0f172a;
                color: #f1f5f9;
            }
            div[data-testid="stMetricValue"] {
                font-size: 2rem;
                font-weight: 700;
                color: #38bdf8;
            }
            div[data-testid="stMetricLabel"] {
                font-size: 0.9rem;
                color: #94a3b8;
            }
            .badge-source {
                background-color: #0369a1;
                color: #e0f2fe;
                padding: 0.15rem 0.5rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
            }
            .badge-location {
                background-color: #334155;
                color: #cbd5e1;
                padding: 0.15rem 0.5rem;
                border-radius: 9999px;
                font-size: 0.75rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🔍 InsightScraper Dashboard")
    st.markdown("ETL Pipeline & Job Application Tracker")

    config = load_config()
    config.setdefault("settings", {})

    st.sidebar.header("🕹️ Scraper Controls")
    if st.sidebar.button("🚀 Run Scraper Now", use_container_width=True):
        if not SCRAPE_RUNNING:
            thread = threading.Thread(target=background_scrape, daemon=True)
            thread.start()
            st.sidebar.success("Background scraper started. Refresh the status section below.")
        else:
            st.sidebar.warning("A scraping job is already running. Please wait for it to finish.")

    if SCRAPE_RUNNING:
        with st.sidebar.spinner("Background scraping in progress..."):
            st.sidebar.write("The scraper is running in the background. Logs will update when you refresh.")

    if st.sidebar.button("🔄 Refresh Scrape Status", use_container_width=True):
        safe_rerun()

    st.sidebar.divider()
    st.sidebar.header("📡 Scrape Status")
    status_logs = get_scrape_logs()
    if status_logs:
        for line in status_logs[-10:]:
            st.sidebar.text(line)
    else:
        st.sidebar.info("No background scrape logs available yet.")

    st.sidebar.header("🎯 Filters")
    search_query = st.sidebar.text_input("Search Title or Company", "").strip().lower()
    available_sources = ["All", "Python.org", "WeWorkRemotely", "RemoteOK"]
    selected_source = st.sidebar.selectbox("Job Source", available_sources)
    available_statuses = ["All", "New", "Favorite", "Applied", "Rejected"]
    selected_status = st.sidebar.selectbox("Application Status", available_statuses)
    remote_only = st.sidebar.checkbox("Remote Roles Only", value=False)
    st.sidebar.caption("Tip: add more sources by editing config.json and restarting the app.")

    df = get_all_jobs()

    if not df.empty:
        filtered_df = df.copy()
        for column in ["title", "company", "location", "source", "status"]:
            if column in filtered_df.columns:
                filtered_df[column] = filtered_df[column].fillna("N/A" if column != "status" else "New")
        filtered_df["title"] = filtered_df["title"].astype(str)
        filtered_df["company"] = filtered_df["company"].astype(str)
        filtered_df["location"] = filtered_df["location"].astype(str)
        filtered_df["source"] = filtered_df["source"].astype(str)
        filtered_df["status"] = filtered_df["status"].astype(str)

        if search_query:
            filtered_df = filtered_df[
                filtered_df["title"].str.lower().str.contains(search_query)
                | filtered_df["company"].str.lower().str.contains(search_query)
            ]

        if selected_source != "All":
            filtered_df = filtered_df[filtered_df["source"] == selected_source]

        if selected_status != "All":
            filtered_df = filtered_df[filtered_df["status"] == selected_status]

        if remote_only:
            filtered_df = filtered_df[filtered_df["location"].str.contains("remote", case=False, na=False)]

        tab_explorer, tab_tracker, tab_analytics, tab_config = st.tabs([
            "📋 Job Explorer",
            "🎯 Application Tracker",
            "📊 Insights & Analytics",
            "⚙️ Pipeline Config",
        ])

        with tab_explorer:
            st.subheader(f"Available Listings ({len(filtered_df)} jobs matching filters)")
            if filtered_df.empty:
                st.info("No jobs found matching your filters. Try broadening the search or run a new scrape.")
            else:
                for _, row in filtered_df.iterrows():
                    with st.container():
                        col_info, col_actions = st.columns([4, 1.5])
                        with col_info:
                            source_badge = f"<span class='badge-source'>{row['source']}</span>"
                            loc_badge = f"<span class='badge-location'>{row['location']}</span>"
                            st.markdown(f"{source_badge} {loc_badge}", unsafe_allow_html=True)
                            safe_title = str(row['title']) if pd.notna(row['title']) else 'Untitled'
                            safe_company = str(row['company']) if pd.notna(row['company']) else 'Unknown'
                            safe_link = str(row['link']) if pd.notna(row['link']) else '#'
                            st.markdown(f"### [{safe_title}]({safe_link})")
                            st.markdown(f"**🏢 {safe_company}**")
                            st.caption(f"Posted: {row.get('date_posted', 'N/A')} | Scraped: {row.get('scraped_at', 'N/A')}")
                            if row.get("notes"):
                                st.info(f"📝 **Notes:** {row['notes']}")

                        with col_actions:
                            status_options = ["New", "Favorite", "Applied", "Rejected"]
                            current_status = row.get("status", "New") or "New"
                            current_status_idx = status_options.index(current_status) if current_status in status_options else 0
                            new_status = st.selectbox(
                                "Update Status",
                                status_options,
                                index=current_status_idx,
                                key=f"status_select_{row['id']}",
                            )
                            if new_status != current_status:
                                update_job_status(row["id"], new_status)
                                st.toast(f"Updated '{safe_title}' status to {new_status}!")
                                safe_rerun()

                            note_input = st.text_input(
                                "Add Note",
                                value=row.get("notes", ""),
                                key=f"note_input_{row['id']}",
                            )
                            if note_input != row.get("notes", ""):
                                update_job_notes(row["id"], note_input)
                                st.toast(f"Updated notes for '{safe_title}'!")
                                safe_rerun()

                        st.divider()

        with tab_tracker:
            st.subheader("🎯 Kanban Application Spreadsheet")
            st.markdown("Edit application status and notes directly in the table below, then click **Save Changes**.")
            tracker_df = df[["id", "title", "company", "location", "source", "status", "notes", "link"]].copy()
            tracker_df = tracker_df.fillna({
                "title": "N/A",
                "company": "N/A",
                "location": "N/A",
                "source": "Unknown",
                "status": "New",
                "notes": "",
            })
            edited_df = st.data_editor(
                tracker_df,
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "title": st.column_config.TextColumn("Job Title", disabled=True),
                    "company": st.column_config.TextColumn("Company", disabled=True),
                    "location": st.column_config.TextColumn("Location", disabled=True),
                    "source": st.column_config.TextColumn("Source", disabled=True),
                    "status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["New", "Favorite", "Applied", "Rejected"],
                        required=True,
                    ),
                    "notes": st.column_config.TextColumn("My Notes", width="medium"),
                    "link": st.column_config.LinkColumn("Listing URL", disabled=True),
                },
                hide_index=True,
                width="stretch",
                key="tracker_data_editor",
            )
            if st.button("💾 Save Tracker Changes"):
                changes_saved = 0
                for _, row in edited_df.iterrows():
                    original_row = tracker_df[tracker_df["id"] == row["id"]].iloc[0]
                    if row["status"] != original_row["status"]:
                        update_job_status(row["id"], row["status"])
                        changes_saved += 1
                    if row["notes"] != original_row["notes"]:
                        update_job_notes(row["id"], row["notes"])
                        changes_saved += 1
                if changes_saved > 0:
                    st.success(f"Successfully saved {changes_saved} updates to the database!")
                    safe_rerun()
                else:
                    st.info("No modifications detected.")

        with tab_analytics:
            st.subheader("📊 Analytics Overview")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Scraped", len(df))
            col2.metric("Applied Roles", len(df[df["status"] == "Applied"]))
            col3.metric("Favorites", len(df[df["status"] == "Favorite"]))
            today_str = datetime.now().strftime("%Y-%m-%d")
            new_today = len(df[df["scraped_at"].str.startswith(today_str)])
            col4.metric("Scraped Today", new_today)
            st.divider()
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.markdown("#### 📍 Job Post Distribution by Source")
                source_counts = df["source"].value_counts().reset_index()
                source_counts.columns = ["source", "count"]
                fig_source = px.pie(
                    source_counts,
                    names="source",
                    values="count",
                    hole=0.4,
                    color_discrete_sequence=["#38bdf8", "#0369a1", "#14b8a6"],
                )
                fig_source.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#f1f5f9",
                )
                st.plotly_chart(fig_source, use_container_width=True)
            with chart_col2:
                st.markdown("#### 🏢 Top Hiring Companies")
                top_companies = df["company"].value_counts().head(10).reset_index()
                top_companies.columns = ["company", "count"]
                fig_comp = px.bar(
                    top_companies,
                    x="company",
                    y="count",
                    labels={"count": "Number of Jobs", "company": "Company"},
                    color="count",
                    color_continuous_scale="Blues",
                )
                fig_comp.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#f1f5f9",
                )
                st.plotly_chart(fig_comp, use_container_width=True)

        with tab_config:
            st.subheader("⚙️ Scraper Engine & Notification Configuration")
            with st.form("config_form"):
                st.markdown("#### Scraper Run Settings")
                headless = st.checkbox(
                    "Run Browser Headless (Recommended)",
                    value=config.get("settings", {}).get("headless", True),
                )
                timeout = st.number_input(
                    "Network Timeout (ms)",
                    min_value=5000,
                    max_value=120000,
                    value=config.get("settings", {}).get("timeout", 30000),
                    step=5000,
                )
                st.divider()
                st.markdown("#### Discord Notification Webhook")
                st.markdown(
                    "Discord notifications are enabled by setting the environment variable `DISCORD_WEBHOOK_URL`. "
                    "This value is intentionally not stored in `config.json` for security reasons."
                )
                if os.environ.get("DISCORD_WEBHOOK_URL"):
                    st.success("Discord webhook enabled via environment variable.")
                else:
                    st.warning("No Discord webhook configured. Set DISCORD_WEBHOOK_URL to enable notifications.")
                keywords_list = config.get("settings", {}).get("notification_keywords", [])
                keywords_str = st.text_area(
                    "Keywords of Interest (comma-separated)",
                    value=", ".join(keywords_list),
                    help="Sends a Discord notification when new jobs match these keywords.",
                )
                submitted = st.form_submit_button("Save Configuration")
                if submitted:
                    config["settings"]["headless"] = headless
                    config["settings"]["timeout"] = timeout
                    config["settings"]["notification_keywords"] = [kw.strip() for kw in keywords_str.split(",") if kw.strip()]
                    save_config(config)
                    st.success("Configuration updated successfully!")
                    safe_rerun()
    else:
        st.info("👋 No listings found in the database. Click **🚀 Run Scraper Now** in the sidebar to scrape your first jobs!")


if __name__ == "__main__":
    main()
