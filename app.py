import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import json
import base64
import webbrowser
from streamlit.components.v1 import html

# Set page config
st.set_page_config(
    page_title="Search Console Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define the required scopes
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

def get_credentials():
    """Get or refresh credentials for Google API."""
    creds = None
    
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    # If there are no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # We'll handle this with a popup window in the main function
            return None
            
    return creds

def is_streamlit_cloud():
    """Check if the app is running on Streamlit Cloud."""
    # Streamlit Cloud sets this environment variable
    return os.environ.get('STREAMLIT_SHARING_MODE') == 'streamlit_cloud'

def get_redirect_uri():
    """Get the appropriate redirect URI based on the environment."""
    if is_streamlit_cloud():
        # For Streamlit Cloud deployment
        return 'https://search-console-dashboard-ad.streamlit.app/callback'
    else:
        # For local development
        return 'http://localhost:8501/callback'

def create_oauth_popup():
    """Create a popup window for OAuth authentication."""
    auth_url = None
    error_message = None
    
    try:
        # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        
        # Set up the flow to use the appropriate redirect URI
        redirect_uri = get_redirect_uri()
        flow.redirect_uri = redirect_uri
        
        # Generate the authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
    except FileNotFoundError:
        error_message = """
        <div style="
            background-color: #f8d7da;
            color: #721c24;
            padding: 20px;
            border-radius: 5px;
            text-align: center;
            margin: 20px auto;
            max-width: 600px;
        ">
            <h3>Missing credentials.json file</h3>
            <p>Please create a project in Google Cloud Console, enable the Search Console API, and download the OAuth credentials as 'credentials.json' to the project directory.</p>
            <p>Follow the instructions in the README.md file for detailed setup steps.</p>
        </div>
        """
    
    # JavaScript to open a popup window
    js_code = """
    <script>
    function openPopup() {
    """
    
    if auth_url:
        js_code += f"""
        var popup = window.open(
            "{auth_url}", 
            "Google Authentication",
            "width=800,height=600,status=yes,scrollbars=yes,resizable=yes"
        );
        
        // Check if popup was blocked
        if (!popup || popup.closed || typeof popup.closed=='undefined') {{
            alert("Popup blocked! Please allow popups for this site.");
        }}
        
        // Poll for changes in the URL of the popup
        var pollTimer = window.setInterval(function() {{
            try {{
                // If the popup is closed, stop polling
                if (popup.closed) {{
                    window.clearInterval(pollTimer);
                    window.location.reload();
                }}
                
                // If we can access the URL and it contains 'code=', the auth is complete
                if (popup.location.href.includes('code=')) {{
                    window.clearInterval(pollTimer);
                    popup.close();
                    window.location.reload();
                }}
            }} catch(e) {{
                // Permission denied, keep polling
            }}
        }}, 500);
        """
    else:
        js_code += """
        alert("Missing credentials.json file. Please follow the setup instructions in the README.");
        """
    
    js_code += """
    }
    </script>
    """
    
    # Add error message if there is one
    if error_message:
        js_code += error_message
    
    # Always add the button
    js_code += """
    <button onclick="openPopup()" style="
        background-color: #4285F4;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    ">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 48 48" style="margin-right: 10px;">
            <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"/>
            <path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"/>
            <path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"/>
            <path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"/>
        </svg>
        Authenticate with Google
    </button>
    """
    
    return js_code

def handle_oauth_callback():
    """Handle the OAuth callback and save credentials."""
    try:
        # Get the authorization code from the URL
        if 'code' in st.query_params:
            auth_code = st.query_params['code']
            
            # Create a flow instance
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            
            # Set up the flow to use the appropriate redirect URI
            redirect_uri = get_redirect_uri()
            flow.redirect_uri = redirect_uri
            
            # Exchange the authorization code for credentials
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
            
            # Clear the URL parameters
            st.query_params.clear()
            
            return creds
    except FileNotFoundError:
        st.error("Missing credentials.json file. Please follow the setup instructions in the README.")
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
    
    return None

def get_search_console_service():
    """Build the Search Console service."""
    creds = get_credentials()
    service = build('searchconsole', 'v1', credentials=creds)
    return service

def get_site_list(service):
    """Get the list of sites in Search Console."""
    sites = service.sites().list().execute()
    return [site['siteUrl'] for site in sites.get('siteEntry', [])]

def get_search_analytics_data(service, site_url, start_date, end_date, dimensions, row_limit=1000):
    """Get search analytics data from Search Console."""
    request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': dimensions,
        'rowLimit': row_limit
    }
    
    response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
    return response

def parse_search_analytics(response, dimensions):
    """Parse the search analytics response into a DataFrame."""
    if 'rows' not in response:
        return pd.DataFrame()
    
    rows = []
    for row in response['rows']:
        parsed_row = {}
        for i, dimension in enumerate(dimensions):
            parsed_row[dimension] = row['keys'][i]
        
        parsed_row['clicks'] = row['clicks']
        parsed_row['impressions'] = row['impressions']
        parsed_row['ctr'] = row['ctr']
        parsed_row['position'] = row['position']
        
        rows.append(parsed_row)
    
    return pd.DataFrame(rows)

def get_previous_period_data(service, site_url, current_start, current_end, dimensions):
    """Get data for the previous period of the same length."""
    delta = datetime.datetime.strptime(current_end, '%Y-%m-%d') - datetime.datetime.strptime(current_start, '%Y-%m-%d')
    prev_end = datetime.datetime.strptime(current_start, '%Y-%m-%d') - datetime.timedelta(days=1)
    prev_start = prev_end - delta
    
    response = get_search_analytics_data(service, site_url, prev_start.strftime('%Y-%m-%d'), 
                                         prev_end.strftime('%Y-%m-%d'), dimensions)
    
    return parse_search_analytics(response, dimensions)

def main():
    st.title("Google Search Console Dashboard")
    
    # Initialize session state for storing data between reruns
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'service' not in st.session_state:
        st.session_state.service = None
    if 'selected_site' not in st.session_state:
        st.session_state.selected_site = None
    
    # Check if we're on the callback route
    if 'code' in st.query_params:
        with st.spinner("Completing authentication..."):
            creds = handle_oauth_callback()
            if creds:
                st.session_state.service = build('searchconsole', 'v1', credentials=creds)
                st.session_state.authenticated = True
                st.success("Authentication successful!")
                st.experimental_rerun()
    
    # Authentication section
    if not st.session_state.authenticated:
        st.info("Please authenticate with Google to access Search Console data.")
        
        # Try to get credentials silently first
        creds = get_credentials()
        if creds:
            try:
                st.session_state.service = build('searchconsole', 'v1', credentials=creds)
                st.session_state.authenticated = True
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Authentication failed: {e}")
        else:
            # Display the authentication button in the center
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            html(create_oauth_popup(), height=80)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.sidebar.success("Successfully authenticated!")
        
        # Get site list
        if st.session_state.service:
            sites = get_site_list(st.session_state.service)
            
            if not sites:
                st.error("No sites found in Search Console. Please add a site first.")
            else:
                # Site selection
                selected_site = st.sidebar.selectbox(
                    "Select a website",
                    sites,
                    index=0 if st.session_state.selected_site is None else sites.index(st.session_state.selected_site)
                )
                
                if selected_site != st.session_state.selected_site:
                    st.session_state.selected_site = selected_site
                    st.experimental_rerun()
                
                # Date range selection
                st.sidebar.header("Date Range")
                
                # Predefined date ranges
                today = datetime.date.today()
                date_ranges = {
                    "Last 7 days": (today - datetime.timedelta(days=7), today),
                    "Last 14 days": (today - datetime.timedelta(days=14), today),
                    "Last 30 days": (today - datetime.timedelta(days=30), today),
                    "Last 90 days": (today - datetime.timedelta(days=90), today),
                    "This month": (today.replace(day=1), today),
                    "Previous month": (
                        (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1),
                        today.replace(day=1) - datetime.timedelta(days=1)
                    ),
                    "This year": (today.replace(month=1, day=1), today),
                    "Custom range": (None, None)
                }
                
                selected_range = st.sidebar.selectbox("Select date range", list(date_ranges.keys()))
                
                if selected_range == "Custom range":
                    col1, col2 = st.sidebar.columns(2)
                    start_date = col1.date_input("Start date", value=today - datetime.timedelta(days=30), max_value=today)
                    end_date = col2.date_input("End date", value=today, min_value=start_date, max_value=today)
                else:
                    start_date, end_date = date_ranges[selected_range]
                
                # Convert dates to strings
                start_date_str = start_date.strftime('%Y-%m-%d')
                end_date_str = end_date.strftime('%Y-%m-%d')
                
                # Dimension selection
                st.sidebar.header("Dimensions")
                
                dimensions_options = {
                    "Date": "date",
                    "Query": "query",
                    "Page": "page",
                    "Country": "country",
                    "Device": "device"
                }
                
                primary_dimension = st.sidebar.selectbox(
                    "Primary dimension",
                    list(dimensions_options.keys()),
                    index=0
                )
                
                # Fetch data when Submit button is clicked
                if st.sidebar.button("Get Data"):
                    with st.spinner("Fetching data from Search Console..."):
                        # Get current period data
                        dimensions = [dimensions_options[primary_dimension]]
                        current_data = get_search_analytics_data(
                            st.session_state.service, 
                            selected_site, 
                            start_date_str, 
                            end_date_str, 
                            dimensions
                        )
                        
                        df_current = parse_search_analytics(current_data, dimensions)
                        
                        if df_current.empty:
                            st.error("No data found for the selected parameters.")
                        else:
                            # Get previous period data for comparison
                            df_previous = get_previous_period_data(
                                st.session_state.service, 
                                selected_site, 
                                start_date_str, 
                                end_date_str, 
                                dimensions
                            )
                            
                            # Format date if date dimension is selected
                            if primary_dimension == "Date":
                                df_current[dimensions_options[primary_dimension]] = pd.to_datetime(df_current[dimensions_options[primary_dimension]])
                                df_current = df_current.sort_values(dimensions_options[primary_dimension])
                            
                            # Dashboard layout
                            st.header(f"Search Console Data: {start_date_str} to {end_date_str}")
                            
                            # Summary metrics
                            col1, col2, col3, col4 = st.columns(4)
                            
                            total_clicks = df_current['clicks'].sum()
                            total_impressions = df_current['impressions'].sum()
                            avg_ctr = (df_current['clicks'].sum() / df_current['impressions'].sum()) * 100 if df_current['impressions'].sum() > 0 else 0
                            avg_position = df_current['position'].mean()
                            
                            # Calculate percentage changes
                            prev_clicks = df_previous['clicks'].sum() if not df_previous.empty else 0
                            prev_impressions = df_previous['impressions'].sum() if not df_previous.empty else 0
                            
                            clicks_change = ((total_clicks - prev_clicks) / prev_clicks * 100) if prev_clicks > 0 else 0
                            impressions_change = ((total_impressions - prev_impressions) / prev_impressions * 100) if prev_impressions > 0 else 0
                            
                            # Display metrics with percentage changes
                            col1.metric(
                                "Total Clicks", 
                                f"{int(total_clicks):,}", 
                                f"{clicks_change:.1f}%" if prev_clicks > 0 else "N/A"
                            )
                            
                            col2.metric(
                                "Total Impressions", 
                                f"{int(total_impressions):,}", 
                                f"{impressions_change:.1f}%" if prev_impressions > 0 else "N/A"
                            )
                            
                            col3.metric("Average CTR", f"{avg_ctr:.2f}%")
                            col4.metric("Average Position", f"{avg_position:.2f}")
                            
                            # Charts
                            st.subheader("Clicks and Impressions")
                            
                            # Create time series charts if date is the dimension
                            if primary_dimension == "Date":
                                # Line chart for clicks and impressions over time
                                fig = go.Figure()
                                
                                fig.add_trace(go.Scatter(
                                    x=df_current[dimensions_options[primary_dimension]],
                                    y=df_current['clicks'],
                                    mode='lines+markers',
                                    name='Clicks',
                                    line=dict(color='blue', width=2)
                                ))
                                
                                fig.add_trace(go.Scatter(
                                    x=df_current[dimensions_options[primary_dimension]],
                                    y=df_current['impressions'],
                                    mode='lines+markers',
                                    name='Impressions',
                                    line=dict(color='red', width=2),
                                    yaxis='y2'
                                ))
                                
                                fig.update_layout(
                                    title='Clicks and Impressions Over Time',
                                    xaxis=dict(title='Date'),
                                    yaxis=dict(title='Clicks', titlefont=dict(color='blue')),
                                    yaxis2=dict(
                                        title='Impressions',
                                        titlefont=dict(color='red'),
                                        overlaying='y',
                                        side='right'
                                    ),
                                    legend=dict(x=0.01, y=0.99),
                                    height=500
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Line chart for CTR and Position over time
                                fig2 = go.Figure()
                                
                                fig2.add_trace(go.Scatter(
                                    x=df_current[dimensions_options[primary_dimension]],
                                    y=df_current['ctr'] * 100,  # Convert to percentage
                                    mode='lines+markers',
                                    name='CTR (%)',
                                    line=dict(color='green', width=2)
                                ))
                                
                                fig2.add_trace(go.Scatter(
                                    x=df_current[dimensions_options[primary_dimension]],
                                    y=df_current['position'],
                                    mode='lines+markers',
                                    name='Position',
                                    line=dict(color='orange', width=2),
                                    yaxis='y2'
                                ))
                                
                                fig2.update_layout(
                                    title='CTR and Position Over Time',
                                    xaxis=dict(title='Date'),
                                    yaxis=dict(title='CTR (%)', titlefont=dict(color='green')),
                                    yaxis2=dict(
                                        title='Position',
                                        titlefont=dict(color='orange'),
                                        overlaying='y',
                                        side='right',
                                        autorange='reversed'  # Lower position is better
                                    ),
                                    legend=dict(x=0.01, y=0.99),
                                    height=500
                                )
                                
                                st.plotly_chart(fig2, use_container_width=True)
                            else:
                                # For non-date dimensions, show bar charts
                                # Limit to top 10 for better visualization
                                top_df = df_current.sort_values('clicks', ascending=False).head(10)
                                
                                # Bar chart for clicks
                                fig = px.bar(
                                    top_df,
                                    x=dimensions_options[primary_dimension],
                                    y='clicks',
                                    title=f'Top 10 {primary_dimension}s by Clicks',
                                    color='clicks',
                                    color_continuous_scale='blues'
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Bar chart for impressions
                                fig2 = px.bar(
                                    top_df,
                                    x=dimensions_options[primary_dimension],
                                    y='impressions',
                                    title=f'Top 10 {primary_dimension}s by Impressions',
                                    color='impressions',
                                    color_continuous_scale='reds'
                                )
                                
                                st.plotly_chart(fig2, use_container_width=True)
                            
                            # Data table
                            st.subheader("Detailed Data")
                            
                            # Sort and format the table data
                            if primary_dimension == "Date":
                                display_df = df_current.sort_values(dimensions_options[primary_dimension], ascending=False)
                            else:
                                display_df = df_current.sort_values('clicks', ascending=False)
                            
                            # Format columns
                            display_df['clicks'] = display_df['clicks'].astype(int)
                            display_df['impressions'] = display_df['impressions'].astype(int)
                            display_df['ctr'] = (display_df['ctr'] * 100).round(2).astype(str) + '%'
                            display_df['position'] = display_df['position'].round(2)
                            
                            # Rename columns for better display
                            display_df = display_df.rename(columns={
                                dimensions_options[primary_dimension]: primary_dimension,
                                'ctr': 'CTR',
                                'position': 'Position'
                            })
                            
                            # Show the table
                            st.dataframe(display_df, use_container_width=True)
                            
                            # Add download button
                            csv = df_current.to_csv(index=False)
                            st.download_button(
                                label="Download data as CSV",
                                data=csv,
                                file_name=f'search_console_data_{start_date_str}_to_{end_date_str}.csv',
                                mime='text/csv',
                            )

if __name__ == '__main__':
    main()
