from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn
import json

app = FastAPI()

# Load district list from JSON
with open("districts.json", "r", encoding="utf-8") as f:
    district_list = json.load(f)

# Simulated data
demo_data = {
    "mosdac": {"rainfall_mm": 10, "cloud_density": "medium"},
    "imd": {"forecast": "Light rain", "temperature": 28},
    "cwc": {"river_level_m": 2.5, "flood_risk": "low"},
    "nwic": {"dam_release_cumecs": 300, "reservoir_level": 75},
    "bhuvan": {"flood_zone": "Zone 2", "elevation_m": 60},
    "bhashini": {
        "input_text": "Flood alert in your area",
        "translations": {
            "assamese": "আপোনাৰ অঞ্চলত বানৰ সতৰ্কবাণী",
            "bengali": "আপনার এলাকায় বন্যার সতর্কতা",
            "hindi": "आपके क्षेत्र में बाढ़ की चेतावनी"
        }
    }
}

# District-level simulated data
district_data = {
    district: {
        "rainfall_mm": 10,
        "river_level_m": 2.5,
        "dam_release_cumecs": 300
    }
    for district in district_list
}

# API key check
def is_authorized(request: Request):
    return request.headers.get("Authorization") == "TEST_demo_KEY"

# Simulated API endpoints
@app.get("/demo_mosdac_api")
async def mosdac(request: Request):
    if not is_authorized(request):
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["mosdac"]

@app.get("/demo_imd_api")
async def imd(request: Request):
    if not is_authorized(request):
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["imd"]

@app.get("/demo_cwc_api")
async def cwc(request: Request):
    if not is_authorized(request):
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["cwc"]

@app.get("/demo_nwic_api")
async def nwic(request: Request):
    if not is_authorized(request):
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["nwic"]

@app.get("/demo_bhuvan_api")
async def bhuvan(request: Request):
    if not is_authorized(request):
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["bhuvan"]

@app.get("/demo_bhashini_api")
async def bhashini(request: Request):
    if not is_authorized(request):
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["bhashini"]

# District-level API
@app.get("/demo_district_api")
async def get_district_data(request: Request, district: str = None):
    if not is_authorized(request):
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    if district:
        if district not in district_data:
            return JSONResponse(status_code=404, content={"error": f"District '{district}' not found"})
        return district_data[district]
    return district_data

# Control Panel UI
@app.get("/CP", response_class=HTMLResponse)
async def control_panel(selected: str = "Sonitpur"):
    d = district_data.get(selected, {"rainfall_mm": "-", "river_level_m": "-", "dam_release_cumecs": "-"})
    options = "\n".join(
        f'<option value="{dist}" {"selected" if dist == selected else ""}>{dist}</option>'
        for dist in district_list
    )
    return f"""
    <html><head><title>District Sim Control</title>
    <style>
    body {{ font-family: sans-serif; background: #f0f0f0; padding: 30px; }}
    .box {{ background: white; padding: 20px; border-radius: 10px; max-width: 500px; margin: auto; }}
    select, input {{ width: 100%; padding: 8px; margin-top: 10px; }}
    .custom {{ display: none; margin-top: 15px; }}
    button {{ margin-top: 20px; padding: 10px; background: #3498db; color: white; border: none; border-radius: 5px; }}
    .status {{ background: #ecf0f1; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
    </style></head><body>
    <div class="box">
    <h2>District Simulation Control</h2>

    <form method="get" action="/CP">
        <label>Select District:</label>
        <select name="selected" onchange="this.form.submit()">
            {options}
        </select>
    </form>

    <div class="status">
        <strong>Current Data for {selected}:</strong><br>
        Rainfall: {d["rainfall_mm"]} mm<br>
        River Level: {d["river_level_m"]} m<br>
        Dam Release: {d["dam_release_cumecs"]} cumecs
    </div>

    <form action="/CP" method="post">
        <input type="hidden" name="district" value="{selected}">
        <label>Mode:</label>
        <select name="mode" onchange="document.querySelector('.custom').style.display = this.value === 'custom' ? 'block' : 'none'">
            <option value="neutral">Neutral</option>
            <option value="flood">Flood</option>
            <option value="heavy_rain">Heavy Rain</option>
            <option value="drought">Drought</option>
            <option value="custom">Custom</option>
        </select>
        <div class="custom">
            <label>Rainfall (mm): <input type="number" name="rainfall" value="0"></label>
            <label>River Level (m): <input type="number" name="river" value="0"></label>
            <label>Dam Release (cumecs): <input type="number" name="dam" value="0"></label>
        </div>
        <button type="submit" name="action" value="apply">Apply</button>
        <button type="submit" name="action" value="sms">Send Demo SMS</button>
    </form>
    </div></body></html>
    """

@app.post("/CP")
async def update_district_mode(
    district: str = Form(...),
    mode: str = Form(...),
    rainfall: float = Form(0),
    river: float = Form(0),
    dam: float = Form(0),
    action: str = Form("apply")
):
    if district not in district_data:
        return HTMLResponse(content=f"<script>alert('Invalid district'); window.location.href='/CP';</script>")

    if action == "sms":
        d = district_data[district]
        msg = f"[DEMO SMS] ALERT for {district}: Rainfall={d['rainfall_mm']}mm, River={d['river_level_m']}m, Dam={d['dam_release_cumecs']} cumecs"
        print(msg)
        return HTMLResponse(content=f"<script>alert('Demo SMS sent for {district}!'); window.location.href='/CP?selected={district}';</script>")

    if mode == "neutral":
        district_data[district] = {"rainfall_mm": 10, "river_level_m": 2.5, "dam_release_cumecs": 300}
    elif mode == "flood":
        district_data[district] = {"rainfall_mm": 150, "river_level_m": 7.5, "dam_release_cumecs": 1800}
    elif mode == "heavy_rain":
        district_data[district] = {"rainfall_mm": 90, "river_level_m": 5.0, "dam_release_cumecs": 1000}
    elif mode == "drought":
        district_data[district] = {"rainfall_mm": 2, "river_level_m": 1.0, "dam_release_cumecs": 100}
    elif mode == "custom":
        district_data[district] = {"rainfall_mm": rainfall, "river_level_m": river, "dam_release_cumecs": dam}

    return HTMLResponse(content=f"<script>window.location.href='/CP?selected={district}';</script>")

# Message API
class Message(BaseModel):
    text: str

@app.post("/MESSAGE_APi")
async def receive_message(request: Request, msg: Message):
    if not is_authorized(request):
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    print(f"[MESSAGE_API] Received message: {msg.text}")
    return {"status": "received", "message": msg.text}
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
