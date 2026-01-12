from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import uvicorn
import os

app = FastAPI(title="Flood Prediction API", description="Predict flood risk based on rainfall, river level, and dam release.")

# Load training data safely
DATA_FILE = "training_data.json"
if os.path.exists(DATA_FILE):
    historical_df = pd.read_json(DATA_FILE)
else:
    historical_df = pd.DataFrame(columns=["hour", "location", "rainfall", "river_level", "dam_release", "flood_occurred"])

def predict_flood_and_time(location: str, rainfall: float, river_level: float, dam_release: float):
    # Normalize location strings
    df = historical_df[historical_df["location"].str.strip().str.lower() == location.strip().lower()]
    if df.empty:
        return "Unknown", "N/A", "gray"

    flood_cases = df[df["flood_occurred"] == 1]
    if flood_cases.empty:
        return "No", "N/A", "green"

    avg_rain = flood_cases["rainfall"].mean()
    avg_river = flood_cases["river_level"].mean()
    avg_dam = flood_cases["dam_release"].mean()

    score = 0
    if rainfall >= avg_rain: score += 1
    if river_level >= avg_river: score += 1
    if dam_release >= avg_dam: score += 1

    if score == 3:
        return "Yes", 18, "red"
    elif score == 2:
        return "Likely", 30, "orange"
    elif score == 1:
        return "Unlikely", 50, "yellow"
    else:
        return "No", "N/A", "green"


@app.get("/")
async def root():
    return {"message": "Flood Prediction API is running. Use /process_api with query parameters."}

@app.get("/process_api")
async def process_api(location: str, rainfall: float, river_level: float, dam_release: float):
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
    uvicorn.run(app, host="127.0.0.1", port=8090)