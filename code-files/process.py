"""
Flood Prediction Processing API

This module provides a FastAPI-based service for flood risk prediction.
It uses historical training data to assess flood likelihood based on
environmental parameters like rainfall, river levels, and dam releases.

Features:
- Location-based flood risk assessment
- Time estimation for flood occurrence
- Color-coded risk levels
- RESTful API endpoint for predictions

Dependencies:
- fastapi: Web framework
- pandas: Data manipulation
- uvicorn: ASGI server

Author: BiTZ Team
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import uvicorn
import os
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "training_data.json"
if os.path.exists(DATA_FILE):
    historical_df = pd.read_json(DATA_FILE)
else:
    historical_df = pd.DataFrame(columns=["hour", "location", "rainfall", "river_level", "dam_release", "flood_occurred"])


def predict_flood_and_time(location: str, rainfall: float, river_level: float, dam_release: float):
    """
    Predict flood risk and time to occurrence based on historical data.

    Uses a simple scoring system comparing current parameters against
    historical flood cases for the given location.

    Args:
        location (str): District or location name.
        rainfall (float): Current rainfall in mm.
        river_level (float): Current river level in meters.
        dam_release (float): Current dam release in cumecs.

    Returns:
        tuple: (flood_risk, time_left_hours, color_code)
            - flood_risk: "Yes", "Likely", "Unlikely", "No", or "Unknown"
            - time_left_hours: Estimated hours until flood or "N/A"
            - color_code: Color indicator ("red", "orange", "yellow", "green", "gray")
    """
    # Normalize location string for comparison
    try:
        if "location" in historical_df.columns:
            df_loc = historical_df[historical_df["location"].str.strip().str.lower() == location.strip().lower()]
        else:
            df_loc = pd.DataFrame()
    except Exception:
        df_loc = pd.DataFrame()

    # Filter for historical flood cases (prefer location-specific, else global)
    try:
        if not df_loc.empty and "flood_occurred" in df_loc.columns:
            flood_cases = df_loc[df_loc["flood_occurred"] == 1]
        elif "flood_occurred" in historical_df.columns:
            flood_cases = historical_df[historical_df["flood_occurred"] == 1]
        else:
            flood_cases = pd.DataFrame()
    except Exception:
        flood_cases = pd.DataFrame()

    if flood_cases.empty:
        return "No", "N/A", "green"

    # Calculate average values from flood cases
    avg_rain = flood_cases["rainfall"].mean()
    avg_river = flood_cases["river_level"].mean()
    avg_dam = flood_cases["dam_release"].mean()

    # Score based on how many parameters exceed historical flood averages
    score = 0
    try:
        if float(rainfall) >= float(avg_rain):
            score += 1
    except Exception:
        pass
    try:
        if float(river_level) >= float(avg_river):
            score += 1
    except Exception:
        pass
    try:
        if float(dam_release) >= float(avg_dam):
            score += 1
    except Exception:
        pass

    # Determine risk level and time based on score
    if score == 3:
        return "Yes", 18, "red"
    elif score == 2:
        return "Likely", 30, "orange"
    elif score == 1:
        return "Unlikely", 50, "yellow"
    else:
        return "No", "N/A", "green"


@app.get("/process_api")
async def process_api(location: str, rainfall: float, river_level: float, dam_release: float):
    """
    API endpoint for flood prediction.

    Accepts environmental parameters and returns flood risk assessment.

    Query Parameters:
        location (str): District name
        rainfall (float): Rainfall in mm
        river_level (float): River level in meters
        dam_release (float): Dam release in cumecs

    Returns:
        JSONResponse: Prediction results in district-specific format
    """
    flood_risk, time_left, color = predict_flood_and_time(location, rainfall, river_level, dam_release)
    
    # Get max river level for the location (safe handling)
    try:
        if "location" in historical_df.columns:
            df_loc = historical_df[historical_df["location"].str.strip().str.lower() == location.strip().lower()]
        else:
            df_loc = pd.DataFrame()
    except Exception:
        df_loc = pd.DataFrame()

    max_river_level = None
    try:
        if not df_loc.empty and "river_level" in df_loc.columns:
            max_river_level = df_loc["river_level"].max()
        elif "river_level" in historical_df.columns and not historical_df.empty:
            max_river_level = historical_df["river_level"].max()
    except Exception:
        max_river_level = None

    # Determine flood_occurred based on risk
    flood_occurred = 1 if flood_risk in ["Yes", "Likely"] else 0

    # Set hour to time_left if numeric, else 0
    hour = time_left if isinstance(time_left, int) else 0
    
    return JSONResponse(content={
        "location": location.title(),
        "rainfall": rainfall,
        "river_level": river_level,
        "M_river_level": max_river_level,
        "dam_release": dam_release,
        "hour": hour,
        "flood_occurred": flood_occurred
    })


if __name__ == "__main__":
    # Run the FastAPI server on localhost port 8090
    uvicorn.run(app, host="127.0.0.1", port=8090)