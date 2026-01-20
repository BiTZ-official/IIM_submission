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

app = FastAPI()

# Path to training data file
DATA_FILE = "training_data.json"

# Load historical training data or create empty DataFrame if file doesn't exist
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
    df = historical_df[historical_df["location"].str.strip().str.lower() == location.strip().lower()]
    if df.empty:
        return "Unknown", "N/A", "gray"

    # Filter for historical flood cases
    flood_cases = df[df["flood_occurred"] == 1]
    if flood_cases.empty:
        return "No", "N/A", "green"

    # Calculate average values from flood cases
    avg_rain = flood_cases["rainfall"].mean()
    avg_river = flood_cases["river_level"].mean()
    avg_dam = flood_cases["dam_release"].mean()

    # Score based on how many parameters exceed historical flood averages
    score = 0
    if rainfall >= avg_rain: score += 1
    if river_level >= avg_river: score += 1
    if dam_release >= avg_dam: score += 1

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
        JSONResponse: Prediction results including risk, time, and message
    """
    flood_risk, time_left, color = predict_flood_and_time(location, rainfall, river_level, dam_release)
    return JSONResponse(content={
        "location": location.title(),
        "rainfall": rainfall,
        "river_level": river_level,
        "dam_release": dam_release,
        "flood_risk": flood_risk,
        "time_left_hours": time_left,
        "color_code": color,
        "message": f"Flood risk: {flood_risk}. Estimated time left: {time_left} hours." if time_left != "N/A" else "No flood expected."
    })


if __name__ == "__main__":
    # Run the FastAPI server on localhost port 8090
    uvicorn.run(app, host="127.0.0.1", port=8090)