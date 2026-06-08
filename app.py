import streamlit as st
import pandas as pd
import os
import json
import asyncio
import plotly.express as px
from datetime import datetime
from utils.database import get_all_jobs, update_job_status, update_job_notes
from main import run_pipeline

# Page Configuration
st.set_page_config(
    page_title="InsightScraper Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    /* Main Layout Styling */
    .stApp {
        background-color: #0f172a;
        color: #f1f5f9;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #38bdf8;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #94a3b8;
    }
    
    /* Custom Card Styling for Job Listings */
    .job-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .job-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    }
    .job-title {
        color: #f8fafc;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        text-decoration: none;
    }
    .job-company {
        color: #38bdf8;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .job-meta {
        font-size: 0.85rem;
        color: #94a3b8;
        display: flex;
        gap: 1rem;
        margin-bottom: 0.75rem;
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
""", unsafe_allow_html=True)

# Helper function to load config
def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    return {}

# Helper function to save config
def save_config(config_data):
    with open("config.json", "w") as f:
        json.dump(config_data, f, indent=4)

# 1. Page Header & Sidebar
st.title("🔍 InsightScraper Dashboard")
st.markdown("ETL Pipeline & Job Application Tracker")

config = load_config()

# Sidebar: Pipeline Control
st.sidebar.header("🕹️ Scraper Controls")
if st.sidebar.button("🚀 Run Scraper Now", use_container_width=True):
    with st.spinner("Scraping job listings... This may take a few seconds."):
        # Run async scraper pipeline
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_pipeline())
        loop.close()
    st.sidebar.success("Scraper executed successfully!")
    st.rerun()

st.sidebar.divider()

# Sidebar: Filters
st.sidebar.header("🎯 Filters")

# Search Title/Company
search_query = st.sidebar.text_input("Search Title or Company", "").strip().lower()

# Filter: Sources
available_sources = ["All", "Python.org", "WeWorkRemotely"]
selected_source = st.sidebar.selectbox("Job Source", available_sources)

# Filter: Status
available_statuses = ["All", "New", "Favorite", "Applied", "Rejected"]
selected_status = st.sidebar.selectbox("Application Status", available_statuses)

# Filter: Remote Only
remote_only = st.sidebar.checkbox("Remote Roles Only", value=False)

# 2. Fetch Data from SQLite
df = get_all_jobs()

if not df.empty:
    # Apply Filters to DataFrame
    filtered_df = df.copy()
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df['title'].str.lower().str.contains(search_query) |
            filtered_df['company'].str.lower().str.contains(search_query)
        ]
        
    if selected_source != "All":
        filtered_df = filtered_df[filtered_df['source'] == selected_source]
        
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
        
    if remote_only:
        filtered_df = filtered_df[filtered_df['location'].str.contains('remote', case=False, na=False)]
        
    # Tabs Layout
    tab_explorer, tab_tracker, tab_analytics, tab_config = st.tabs([
        "📋 Job Explorer", 
        "🎯 Application Tracker", 
        "📊 Insights & Analytics", 
        "⚙️ Pipeline Config"
    ])
    
    # ------------------
    # TAB 1: JOB EXPLORER
    # ------------------
    with tab_explorer:
        st.subheader(f"Available Listings ({len(filtered_df)} jobs matching filters)")
        
        if filtered_df.empty:
            st.info("No jobs found matching your filters.")
        else:
            # Display jobs in card formats
            for index, row in filtered_df.iterrows():
                with st.container():
                    # Create columns inside container for layout
                    col_info, col_actions = st.columns([4, 1.5])
                    
                    with col_info:
                        # Badges line
                        source_badge = f"<span class='badge-source'>{row['source']}</span>"
                        loc_badge = f"<span class='badge-location'>{row['location']}</span>"
                        st.markdown(f"{source_badge} {loc_badge}", unsafe_allow_html=True)
                        
                        # Job link and title
                        st.markdown(f"### [{row['title']}]({row['link']})")
                        st.markdown(f"**🏢 {row['company']}**")
                        st.caption(f"Posted: {row['date_posted']} | Scraped: {row['scraped_at']}")
                        
                        if row['notes']:
                            st.info(f"📝 **Notes:** {row['notes']}")
                            
                    with col_actions:
                        # Status Changer Dropdown
                        status_options = ["New", "Favorite", "Applied", "Rejected"]
                        current_status_idx = status_options.index(row['status']) if row['status'] in status_options else 0
                        
                        # Use a unique key per job
                        new_status = st.selectbox(
                            "Update Status", 
                            status_options, 
                            index=current_status_idx, 
                            key=f"status_select_{row['id']}"
                        )
                        
                        if new_status != row['status']:
                            update_job_status(row['id'], new_status)
                            st.toast(f"Updated '{row['title']}' status to {new_status}!")
                            st.rerun()
                            
                        # Quick Notes Input
                        note_input = st.text_input(
                            "Add Note", 
                            value=row['notes'], 
                            key=f"note_input_{row['id']}"
                        )
                        if note_input != row['notes']:
                            update_job_notes(row['id'], note_input)
                            st.toast(f"Updated notes for '{row['title']}'!")
                            st.rerun()
                            
                    st.divider()

    # ------------------
    # TAB 2: APPLICATION TRACKER
    # ------------------
    with tab_tracker:
        st.subheader("🎯 Kanban Application Spreadsheet")
        st.markdown("Edit application status and notes directly in the table below, then click **Save Changes**.")
        
        # Display editable table
        tracker_df = df[['id', 'title', 'company', 'location', 'source', 'status', 'notes', 'link']].copy()
        
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
                    required=True
                ),
                "notes": st.column_config.TextColumn("My Notes", width="medium"),
                "link": st.column_config.LinkColumn("Listing URL", disabled=True)
            },
            hide_index=True,
            use_container_width=True,
            key="tracker_data_editor"
        )
        
        if st.button("💾 Save Tracker Changes"):
            changes_saved = 0
            for index, row in edited_df.iterrows():
                original_row = tracker_df[tracker_df['id'] == row['id']].iloc[0]
                
                # If status changed
                if row['status'] != original_row['status']:
                    update_job_status(row['id'], row['status'])
                    changes_saved += 1
                    
                # If notes changed
                if row['notes'] != original_row['notes']:
                    update_job_notes(row['id'], row['notes'])
                    changes_saved += 1
                    
            if changes_saved > 0:
                st.success(f"Successfully saved {changes_saved} updates to the database!")
                st.rerun()
            else:
                st.info("No modifications detected.")

    # ------------------
    # TAB 3: INSIGHTS & ANALYTICS
    # ------------------
    with tab_analytics:
        st.subheader("📊 Analytics Overview")
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Scraped", len(df))
        col2.metric("Applied Roles", len(df[df['status'] == 'Applied']))
        col3.metric("Favorites", len(df[df['status'] == 'Favorite']))
        
        # Calculate new today
        today_str = datetime.now().strftime("%Y-%m-%d")
        new_today = len(df[df['scraped_at'].str.startswith(today_str)])
        col4.metric("Scraped Today", new_today)
        
        st.divider()
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### 📍 Job Post Distribution by Source")
            source_counts = df['source'].value_counts().reset_index()
            fig_source = px.pie(
                source_counts, 
                names='source', 
                values='count', 
                hole=0.4,
                color_discrete_sequence=['#38bdf8', '#0369a1']
            )
            fig_source.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f1f5f9')
            st.plotly_chart(fig_source, use_container_width=True)
            
        with chart_col2:
            st.markdown("#### 🏢 Top Hiring Companies")
            top_companies = df['company'].value_counts().head(10).reset_index()
            fig_comp = px.bar(
                top_companies,
                x='company',
                y='count',
                labels={'count': 'Number of Jobs', 'company': 'Company'},
                color='count',
                color_continuous_scale='Blues'
            )
            fig_comp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f1f5f9')
            st.plotly_chart(fig_comp, use_container_width=True)

    # ------------------
    # TAB 4: CONFIGURATION EDITOR
    # ------------------
    with tab_config:
        st.subheader("⚙️ Scraper Engine & Notification Configuration")
        
        with st.form("config_form"):
            st.markdown("#### Scraper Run Settings")
            headless = st.checkbox("Run Browser Headless (Recommended)", value=config.get("settings", {}).get("headless", True))
            timeout = st.number_input("Network Timeout (ms)", min_value=5000, max_value=120000, value=config.get("settings", {}).get("timeout", 30000), step=5000)
            
            st.divider()
            
            st.markdown("#### Discord Notification Webhook")
            discord_url = st.text_input("Discord Webhook URL", value=config.get("settings", {}).get("discord_webhook_url", ""))
            
            # Keywords input
            keywords_list = config.get("settings", {}).get("notification_keywords", [])
            keywords_str = st.text_area("Keywords of Interest (comma-separated)", value=", ".join(keywords_list), help="Sends a Discord notification when new jobs match these keywords.")
            
            # Save configuration button
            submitted = st.form_submit_button("Save Configuration")
            if submitted:
                # Update config dictionary
                config["settings"]["headless"] = headless
                config["settings"]["timeout"] = timeout
                config["settings"]["discord_webhook_url"] = discord_url
                config["settings"]["notification_keywords"] = [kw.strip() for kw in keywords_str.split(",") if kw.strip()]
                
                save_config(config)
                st.success("Configuration updated successfully!")
                st.rerun()

else:
    st.info("👋 No listings found in the database. Click **🚀 Run Scraper Now** in the sidebar to scrape your first jobs!")