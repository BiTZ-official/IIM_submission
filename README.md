# Flood Monitoring Control Panel

### BiTZ Team - IIM Submission

A comprehensive flood monitoring and early warning system prototype that integrates multiple data sources to predict flood risks and send multilingual alerts.

## Features

- **Real-time Monitoring**: Continuous monitoring of environmental parameters across districts
- **Flood Risk Prediction**: Machine learning-based prediction using historical data
- **Multilingual Alerts**: Automatic translation and dissemination of alerts in multiple Indian languages
- **GUI Control Panel**: User-friendly interface for district-wise monitoring and manual interventions
- **Simulation Environment**: Built-in simulated APIs for testing and demonstration
- **Automated Scanning**: Background scanning with configurable intervals

## Project Structure

```
IIM_submission/
├── code-files/
│   ├── API_links.json          # API endpoint configurations
│   ├── districts.json          # List of monitored districts
│   ├── main.processor.py       # Main GUI application
│   ├── process.py              # Flood prediction API server
│   ├── requirements.txt        # Python dependencies
│   ├── settings.json           # Application settings
│   ├── simulated_data.py       # Simulated API server for testing
│   └── training_data.json      # Historical training dataset
├── demo-vid/                   # Demonstration videos
├── Verification-document/      # Project documentation
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for version control)

### Setup Steps

1. **Clone or navigate to the project directory:**

   ```bash
   cd IIM_submission
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r code-files/requirements.txt
   ```

4. **Navigate to the code directory:**
   ```bash
   cd code-files
   ```

## Usage

### Running the System

The system consists of three main components that need to run simultaneously:

1. **Start the Simulated Data Server (Port 8080):**

   ```
   python simulated_data.py
   ```

   This provides mock APIs for testing. Access the control panel at `http://127.0.0.1:8080/CP`

2. **Start the Processing API Server (Port 8090):**

   ```
   python process.py
   ```

   This handles flood risk predictions.

3. **Start the Main GUI Application:**
   ```bash
   python main.processor.py
   ```
   This launches the monitoring control panel.

### Testing the System

1. Open the control panel in your browser: `http://127.0.0.1:8080/CP`
2. Select different districts and change simulation modes (Neutral, Flood, Heavy Rain, Drought, Custom)
3. Observe the GUI application update district colors based on risk levels
4. Click on districts to view detailed information and send test alerts

## API Endpoints

### Simulated APIs (Port 8080)

- `GET /demo_mosdac_api` - Satellite rainfall data
- `GET /demo_imd_api` - Weather station data
- `GET /demo_cwc_api` - River water level data
- `GET /demo_nwic_api` - Groundwater data
- `GET /demo_bhuvan_api` - Geospatial data
- `GET /demo_bhashini_api?text=<message>` - Translation service
- `GET /demo_district_api?district=<name>` - District environmental data
- `POST /MESSAGE_APi` - Message sending service
- `GET /CP` - Web control panel

### Processing API (Port 8090)

- `GET /process_api?location=<district>&rainfall=<mm>&river_level=<m>&dam_release=<cumecs>` - Flood risk prediction

## Configuration

### API Links

Edit `API_links.json` to configure API endpoints:

```json
[
  {
    "name": "District",
    "Link": "127.0.0.1:8080/demo_district_api",
    "API_key": ""
  }
]
```

### Districts

Modify `districts.json` to add or remove monitored districts:

```json
["District1", "District2", "District3"]
```

### Training Data

Update `training_data.json` with historical flood data for better predictions.

## Dependencies

Key packages (see `requirements.txt` for complete list):

- `fastapi` - Web framework for APIs
- `uvicorn` - ASGI server
- `requests` - HTTP client
- `pandas` - Data manipulation
- `tkinter` - GUI framework (built-in with Python)

## Development

### Adding New Features

1. Modify the respective Python files in `code-files/`
2. Update API endpoints in `simulated_data.py` if needed
3. Test with the control panel
4. Update this README with new instructions

### Data Sources

The system integrates data from:

- MOSDAC (Satellite data)
- IMD (Weather data)
- CWC (River levels)
- NWIC (Groundwater)
- Bhuvan (Geospatial)
- Bhashini (Translation)

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8080 and 8090 are available
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **API authorization**: Use correct API keys in requests
4. **Data files**: Ensure JSON files are present and valid

### Logs

Check console output for error messages and API responses.

## License

This project is developed as part of IIM submission by BiTZ Team.

## Contact

For questions or support, please contact the BiTZ development team.
