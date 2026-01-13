from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn
import json
from datetime import datetime, timezone, timedelta

app = FastAPI()

# Load district list from JSON
with open("districts.json", "r", encoding="utf-8") as f:
    district_list = json.load(f)

# Simulated data

def _iso_now_hour():
    return datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

_today = datetime.now(timezone.utc).date()

demo_data = {
    "mosdac": {
        "datasetId": "rainfall_daily",
        "location": "Assam",
        "timestamp": _iso_now_hour(),
        "rainfall_mm": 42.5,
        "source": "MOSDAC-INSAT3D"
    },
    "imd": {
        "stationId": "IMD_Guwahati",
        "stationName": "Guwahati",
        "timestamp": _iso_now_hour(),
        "temperature_c": 28,
        "humidity_percent": 78,
        "rainfall_mm": 65,
        "windSpeed_kmph": 12,
        "forecast": [
            {"date": (_today + timedelta(days=1)).isoformat(), "rainfall_mm": 80, "condition": "Heavy Rain"},
            {"date": (_today + timedelta(days=2)).isoformat(), "rainfall_mm": 20, "condition": "Cloudy"}
        ]
    },
    "cwc": {
        "stationId": "CWC_Brahmaputra_Dhemaji",
        "riverName": "Brahmaputra",
        "location": "Dhemaji",
        "timestamp": _iso_now_hour(),
        "waterLevel_m": 5.8,
        "discharge_cumecs": 1200,
        "dangerLevel_m": 5.5,
        "status": "Above Danger Level"
    },
    "nwic": {
        "records": [
            {
                "date": _today.isoformat(),
                "river": "Brahmaputra",
                "district": "Majuli",
                "waterLevel_m": 4.9,
                "groundWaterLevel_m": 2.1,
                "rainfall_mm": 72,
                "temperature_c": 27,
                "humidity_percent": 82
            }
        ]
    },
    "bhuvan": {
        "district": "Dhemaji",
        "latitude": 27.48,
        "longitude": 94.58,
        "landUse": "Floodplain Agriculture",
        "floodProneZone": True,
        "nearestReliefCamp_km": 3.2,
        "populationAffected": 12000
    },
    "bhashini": {
        "pipelineId": "translation_en_as",
        "inputText": "Flood warning in Dhemaji district",
        "outputText": "ধেমাজি জিলাত বানৰ সতৰ্কবাণী",
        "language": "Assamese"
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
    return request.headers.get("Authorization") == "Bearer TEST_demo_KEY"

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
    input_text = request.query_params.get("text", "")
    return {
        "text": input_text,
        "english": input_text,
        "hindi": f"हिंदी अनुवाद: {input_text}",
        "assamese": f"অসমীয়া অনুবাদ: {input_text}",
        "bengali": f"বাংলা অনুবাদ: {input_text}",
        "gujarati": f"ગુજરાતી અનુવાદ: {input_text}",
        "marathi": f"मराठी अनुवाद: {input_text}",
        "tamil": f"தமிழ் மொழிபெயர்ப்பு: {input_text}",
        "telugu": f"తెలుగు అనువాదం: {input_text}",
        "kannada": f"ಕನ್ನಡ ಅನುವಾದ: {input_text}",
        "malayalam": f"മലയാളം പരിഭാഷ: {input_text}",
        "punjabi": f"ਪੰਜਾਬੀ ਅਨੁਵਾਦ: {input_text}",
        "odia": f"ଓଡ଼ିଆ ଅନୁବାଦ: {input_text}",
        "urdu": f"اردو ترجمہ: {input_text}"
    }

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

    def _mode_from_data(d):
        try:
            if d["rainfall_mm"] == 10 and d["river_level_m"] == 2.5 and d["dam_release_cumecs"] == 300:
                return "neutral"
            if d["rainfall_mm"] == 150 and d["river_level_m"] == 7.5 and d["dam_release_cumecs"] == 1800:
                return "flood"
            if d["rainfall_mm"] == 90 and d["river_level_m"] == 5.0 and d["dam_release_cumecs"] == 1000:
                return "heavy_rain"
            if d["rainfall_mm"] == 2 and d["river_level_m"] == 1.0 and d["dam_release_cumecs"] == 100:
                return "drought"
        except Exception:
            pass
        return "custom"

    mode = _mode_from_data(d)

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
    .custom {{ margin-top: 15px; }}
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
        <select name="mode" onchange="onModeChange(this.value)">
            <option value="neutral" {"selected" if mode == "neutral" else ""}>Neutral</option>
            <option value="flood" {"selected" if mode == "flood" else ""}>Flood</option>
            <option value="heavy_rain" {"selected" if mode == "heavy_rain" else ""}>Heavy Rain</option>
            <option value="drought" {"selected" if mode == "drought" else ""}>Drought</option>
            <option value="custom" {"selected" if mode == "custom" else ""}>Custom</option>
        </select>
        <div class="custom">
            <label>Rainfall (mm): <input type="number" step="any" name="rainfall" value="{d.get('rainfall_mm', '')}"></label>
            <label>River Level (m): <input type="number" step="any" name="river" value="{d.get('river_level_m', '')}"></label>
            <label>Dam Release (cumecs): <input type="number" step="any" name="dam" value="{d.get('dam_release_cumecs', '')}"></label>
        </div>
        <button type="submit" name="action" value="apply">Apply</button>
        <button type="submit" name="action" value="sms">Send Demo SMS</button>
    </form>
    </div>

    <script>
    function onModeChange(val){{
        var r = document.querySelector('input[name="rainfall"]');
        var rv = document.querySelector('input[name="river"]');
        var damInput = document.querySelector('input[name="dam"]');
        if(val === 'neutral'){{
            r.value = 10; rv.value = 2.5; damInput.value = 300;
        }} else if(val === 'flood'){{
            r.value = 150; rv.value = 7.5; damInput.value = 1800;
        }} else if(val === 'heavy_rain'){{
            r.value = 90; rv.value = 5.0; damInput.value = 1000;
        }} else if(val === 'drought'){{
            r.value = 2; rv.value = 1.0; damInput.value = 100;
        }} else if(val === 'custom'){{
            // keep current values editable
        }}
    }}
    document.addEventListener('DOMContentLoaded', function(){{ onModeChange("{mode}"); }});
    </script>

    </body></html>
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
