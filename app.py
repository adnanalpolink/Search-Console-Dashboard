import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="GSC Explorer",
    page_icon="🔍",
    layout="wide"
)

# Google OAuth2 configuration
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [os.getenv("REDIRECT_URI", "https://your-streamlit-app-url.streamlit.app")],
        "scopes": SCOPES
    }
}

def init_session_state():
    if 'credentials' not in st.session_state:
        st.session_state.credentials = None
    if 'service' not in st.session_state:
        st.session_state.service = None
    if 'sites' not in st.session_state:
        st.session_state.sites = []

def authenticate():
    if not st.session_state.credentials:
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=os.getenv("REDIRECT_URI", "https://your-streamlit-app-url.streamlit.app")
        )
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        st.markdown(f'<a href="{auth_url}" target="_self">Login with Google</a>', unsafe_allow_html=True)
        return False
    return True

def fetch_gsc_data(start_date, end_date, site_url):
    try:
        request = {
            'startDate': start_date,
            'endDate': end_date,
            'dimensions': ['query', 'page', 'device', 'country'],
            'rowLimit': 25000,
            'startRow': 0,
            'type': 'web'
        }
        
        response = st.session_state.service.searchanalytics().query(
            siteUrl=site_url,
            body=request
        ).execute()
        
        if 'rows' not in response:
            return pd.DataFrame()
            
        data = []
        for row in response['rows']:
            data.append({
                'query': row['keys'][0],
                'page': row['keys'][1],
                'device': row['keys'][2],
                'country': row['keys'][3],
                'clicks': row['clicks'],
                'impressions': row['impressions'],
                'ctr': row['ctr'],
                'position': row['position']
            })
        
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()

def main():
    init_session_state()
    
    st.title("🔍 GSC Explorer")
    
    if not authenticate():
        return
    
    # Sidebar for site selection and date range
    with st.sidebar:
        st.header("Settings")
        if not st.session_state.sites:
            try:
                st.session_state.sites = st.session_state.service.sites().list().execute().get('siteEntry', [])
            except Exception as e:
                st.error(f"Error fetching sites: {str(e)}")
        
        site_url = st.selectbox(
            "Select Site",
            options=[site['siteUrl'] for site in st.session_state.sites],
            format_func=lambda x: x.replace('https://', '').replace('http://', '')
        )
        
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
    
    # Main content area
    if site_url and date_range:
        start_date = date_range[0].strftime('%Y-%m-%d')
        end_date = date_range[1].strftime('%Y-%m-%d')
        
        # Fetch data
        df = fetch_gsc_data(start_date, end_date, site_url)
        
        if not df.empty:
            # Top queries
            st.subheader("Top Queries")
            top_queries = df.nlargest(10, 'clicks')[['query', 'clicks', 'impressions', 'ctr', 'position']]
            st.dataframe(top_queries)
            
            # Performance metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Clicks", int(df['clicks'].sum()))
            with col2:
                st.metric("Total Impressions", int(df['impressions'].sum()))
            with col3:
                st.metric("Average CTR", f"{df['ctr'].mean():.2%}")
            with col4:
                st.metric("Average Position", f"{df['position'].mean():.2f}")
            
            # Visualizations
            st.subheader("Performance Trends")
            
            # Clicks by Device
            fig_device = px.pie(df, values='clicks', names='device', title='Clicks by Device')
            st.plotly_chart(fig_device, use_container_width=True)
            
            # Top Countries
            country_clicks = df.groupby('country')['clicks'].sum().reset_index()
            fig_country = px.bar(country_clicks.nlargest(10, 'clicks'), 
                               x='country', y='clicks', 
                               title='Top 10 Countries by Clicks')
            st.plotly_chart(fig_country, use_container_width=True)
            
            # Query Performance
            query_performance = df.groupby('query').agg({
                'clicks': 'sum',
                'impressions': 'sum',
                'ctr': 'mean',
                'position': 'mean'
            }).reset_index()
            
            st.subheader("Query Analysis")
            st.dataframe(query_performance.nlargest(20, 'clicks'))

if __name__ == "__main__":
    main()
