# Search Console Analytics Dashboard

Advanced Streamlit application for visualizing Google Search Console data with comparative period analysis.

## Features

- OAuth authentication with Google Search Console API
- Flexible date range options (7/14/30/90 days, monthly, custom)
- Interactive data visualization
  - Time-series charts (clicks, impressions, CTR, position)
  - Dimension-based bar charts with color gradients
  - Dual-axis charts for metric correlation analysis
- Performance metrics with period-over-period comparison
- Exportable data tables with metric sorting
- Mobile-responsive UI design

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

# Set up Google API credentials
# 1. Visit https://console.cloud.google.com/
# 2. Create project and enable Search Console API
# 3. Create OAuth credentials (Desktop application)
# 4. Download as credentials.json to project root

# Launch application
streamlit run app.py
```

## Usage Guide

1. Click "Authenticate with Google" on first run
2. Select property from dropdown menu
3. Choose date range (preset or custom)
4. Select primary dimension (Date/Query/Page/Country/Device)
5. Click "Get Data" to generate dashboard

## Dashboard Components

- **Summary Cards**: Total metrics with period comparison
- **Time Series Charts**: Daily/weekly performance trends
- **Dimension Analysis**: Top performing pages/queries/countries
- **Data Table**: Sortable metrics with CSV export

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
