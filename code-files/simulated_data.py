from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
import uvicorn

app = FastAPI()

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

#routing demo endpoints
@app.get("/demo_mosdac_api")
async def mosdac(request: Request):
    if request.headers.get("Authorization") != "TEST_demo_KEY":
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["mosdac"]

@app.get("/demo_imd_api")
async def imd(request: Request):
    if request.headers.get("Authorization") != "TEST_demo_KEY":
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["imd"]

@app.get("/demo_cwc_api")
async def cwc(request: Request):
    if request.headers.get("Authorization") != "TEST_demo_KEY":
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["cwc"]

@app.get("/demo_nwic_api")
async def nwic(request: Request):
    if request.headers.get("Authorization") != "TEST_demo_KEY":
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["nwic"]

@app.get("/demo_bhuvan_api")
async def bhuvan(request: Request):
    if request.headers.get("Authorization") != "TEST_demo_KEY":
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["bhuvan"]

@app.get("/demo_bhashini_api")
async def bhashini(request: Request):
    if request.headers.get("Authorization") != "TEST_demo_KEY":
        return JSONResponse(status_code=403, content={"error": "Invalid API key"})
    return demo_data["bhashini"]

#Control Panel
@app.get("/CP", response_class=HTMLResponse)
async def control_panel():
    current = demo_data
    return f"""
    <html><head><title>Sim Control</title>
    <style>
    body {{ font-family: sans-serif; background: #f0f0f0; padding: 30px; }}
    .box {{ background: white; padding: 20px; border-radius: 10px; max-width: 500px; margin: auto; }}
    select, input {{ width: 100%; padding: 8px; margin-top: 10px; }}
    .custom {{ display: none; margin-top: 15px; }}
    button {{ margin-top: 20px; padding: 10px; background: #3498db; color: white; border: none; border-radius: 5px; }}
    .status {{ background: #ecf0f1; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
    </style></head><body>
    <div class="box">
    <h2>Simulated Data Control</h2>

    <div class="status">
        <strong>Current Status:</strong><br>
        Rainfall: {current["mosdac"]["rainfall_mm"]} mm<br>
        River Level: {current["cwc"]["river_level_m"]} m<br>
        Dam Release: {current["nwic"]["dam_release_cumecs"]} cumecs
    </div>

    <form action="/CP" method="post">
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
        <button type="submit">Apply</button>
    </form>
    </div></body></html>
    """


@app.post("/CP")
async def update_mode(mode: str = Form(...), rainfall: float = Form(0), river: float = Form(0), dam: float = Form(0)):
    if mode == "neutral":
        demo_data["mosdac"]["rainfall_mm"] = 10
        demo_data["cwc"]["river_level_m"] = 2.5
        demo_data["nwic"]["dam_release_cumecs"] = 300
    elif mode == "flood":
        demo_data["mosdac"]["rainfall_mm"] = 150
        demo_data["cwc"]["river_level_m"] = 7.5
        demo_data["nwic"]["dam_release_cumecs"] = 1800
    elif mode == "heavy_rain":
        demo_data["mosdac"]["rainfall_mm"] = 90
        demo_data["cwc"]["river_level_m"] = 5.0
        demo_data["nwic"]["dam_release_cumecs"] = 1000
    elif mode == "drought":
        demo_data["mosdac"]["rainfall_mm"] = 2
        demo_data["cwc"]["river_level_m"] = 1.0
        demo_data["nwic"]["dam_release_cumecs"] = 100
    elif mode == "custom":
        demo_data["mosdac"]["rainfall_mm"] = rainfall
        demo_data["cwc"]["river_level_m"] = river
        demo_data["nwic"]["dam_release_cumecs"] = dam
    return HTMLResponse(content="<script>window.location.href='/CP';</script>")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
