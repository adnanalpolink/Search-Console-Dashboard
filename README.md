# Search Console Analytics Dashboard

Advanced Streamlit application for visualizing Google Search Console data with comparative period analysis. This dashboard now features a popup authentication window for a smoother user experience.

## Features

- **Popup OAuth Authentication**: Authenticate with Google in a popup window
- **Flexible Date Range Options**: 7/14/30/90 days, monthly, custom
- **Interactive Data Visualization**:
  - Time-series charts (clicks, impressions, CTR, position)
  - Dimension-based bar charts with color gradients
  - Dual-axis charts for metric correlation analysis
- **Performance Metrics**: With period-over-period comparison
- **Exportable Data Tables**: With metric sorting
- **Mobile-responsive UI Design**

## Quick Setup

### Requirements

- Python 3.7+
- Google Search Console access

### Installation

```bash
# Clone repo
git clone https://github.com/your-username/search-console-dashboard
cd search-console-dashboard

# Install dependencies
pip install -r requirements.txt
```

### Deployment Options

#### Local Development

For local development, the app will use `http://localhost:8501/callback` as the redirect URI.

#### Streamlit Cloud Deployment

When deploying to Streamlit Cloud, the app will automatically detect the environment and use your Streamlit app URL as the redirect URI (e.g., `https://search-console-dashboard-ad.streamlit.app/callback`).

**Important:** When setting up your OAuth credentials in Google Cloud Console, you need to add both the local and cloud redirect URIs to the list of authorized redirect URIs:
- `http://localhost:8501/callback` (for local development)
- `https://search-console-dashboard-ad.streamlit.app/callback` (for Streamlit Cloud)

### Setting Up Google API Credentials

1. **Create a Google Cloud Project**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable the Search Console API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Search Console API" and enable it

3. **Create OAuth Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Web application" as the application type (not Desktop application)
   - Give it a name (e.g., "Search Console Dashboard")
   - Add authorized redirect URIs:
     - `http://localhost:8501/callback` (for local development)
     - `https://search-console-dashboard-ad.streamlit.app/callback` (for Streamlit Cloud)
   - Click "Create"

4. **Download Credentials**:
   - Download the JSON file
   - Rename it to `credentials.json`
   - Place it in the root directory of this project

   > Note: You can use the provided `credentials.json.template` as a reference for the format.

5. **Launch the Application**:
   ```bash
   streamlit run app.py
   ```

### Deploying to Streamlit Cloud

1. Push your code to a GitHub repository
2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect it to your GitHub repository
4. Add your `credentials.json` file as a secret file in the Streamlit Cloud dashboard
   - Go to your app settings
   - Under "Secrets", add a new file secret
   - Name it `credentials.json` and paste the contents of your credentials file
5. Deploy the app

## Usage Guide

1. When you first run the application, click the "Authenticate with Google" button in the center of the screen
2. A popup window will open for Google authentication
3. Grant access to your Search Console data
4. The popup will automatically close and the dashboard will load
5. Select a property from the dropdown menu
6. Choose a date range (preset or custom)
7. Select a primary dimension (Date/Query/Page/Country/Device)
8. Click "Get Data" to generate the dashboard

## Dashboard Components

- **Summary Cards**: Total metrics with period comparison
- **Time Series Charts**: Daily/weekly performance trends
- **Dimension Analysis**: Top performing pages/queries/countries
- **Data Table**: Sortable metrics with CSV export

## Troubleshooting

- **Missing credentials.json file**: If you see an error about a missing credentials file, follow the "Setting Up Google API Credentials" section above.
- **Popup Blocked**: If the authentication popup is blocked, allow popups for the application in your browser settings.
- **Authentication Failed**: Ensure you have access to Google Search Console and that the API is enabled in your Google Cloud project.

## API Reference

The application uses the following Search Console API endpoints:

- `sites().list()`: Retrieve available properties
- `searchanalytics().query()`: Get performance metrics

## Docker Deployment

```bash
# Build container
docker build -t search-console-dashboard .

# Run container
docker run -p 8501:8501 search-console-dashboard
```

## Contributing

Pull requests welcome. For major changes, please open an issue first.
