import streamlit as st
import pandas as pd
import glob
import os
import plotly.express as px

# Page configuration
st.set_page_config(page_title="InsightScraper Dashboard", page_icon="🔍")

st.title("🔍 InsightScraper: Data Insights")
st.markdown("Analyzing the latest data collected by the automated pipeline.")

# 1. Load the most recent data
def load_latest_data():

    # Ensure the directory exists to avoid OS errors
    if not os.path.exists('data'):
        return None, None

    list_of_files = glob.glob('data/*.csv')
    if not list_of_files:
        return None, None
    
    latest_file = max(list_of_files, key=os.path.getctime)
    try:
        return pd.read_csv(latest_file), latest_file
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None, None
    return pd.read_csv(latest_file), latest_file

df, filename = load_latest_data()

if df is not None and filename is not None:
    st.sidebar.success(f"Loaded: {os.path.basename(filename)}")
    
    # 2. Key Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Listings", len(df))
    col2.metric("Unique Companies", df['company'].nunique())
    col3.metric("Remote Roles", len(df[df['location'].str.contains('Remote', case=False)]))

    st.divider()

    # 3. Visualizations
    st.subheader("📍 Job Locations Distribution")
    fig_loc = px.pie(df, names='location', hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_loc, use_container_width=True)

    st.subheader("🏢 Top Hiring Companies")
    top_companies = df['company'].value_counts().head(10).reset_index()
    fig_comp = px.bar(top_companies, x='company', y='count', 
                      labels={'count': 'Number of Jobs', 'company': 'Company'},
                      color='count', color_continuous_scale='Viridis')
    st.plotly_chart(fig_comp, use_container_width=True)

    # 4. Raw Data Table
    with st.expander("See Raw Data"):
        st.dataframe(df, use_container_width=True)

else:
    st.error("No data found in the /data folder. Run the scraper first!")