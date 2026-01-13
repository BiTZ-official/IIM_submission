import json
import requests
import tkinter as tk
from tkinter import messagebox
import threading
import time
import math

PROCESS_API = "http://127.0.0.1:8090/process_api"


# ---------- LOAD & NORMALIZE API_links.json ----------
def load_api_links():
    with open("API_links.json", "r") as f:
        raw_list = json.load(f)

    api_map = {}
    for api in raw_list:
        api_map[api["name"]] = {
            "url": "http://" + api["Link"] if not 
            api["Link"].startswith("http") else api["Link"],
            "api_key": api.get("API_key", "")
        }
    return api_map


# ---------- GENERIC FETCH ----------
def fetch_json(api, params=None):
    try:
        headers = {}
        if api["api_key"]:
            headers["Authorization"] = f"Bearer {api['api_key']}"

        r = requests.get(api["url"], headers=headers, params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    except Exception as e:
        print(f"[ERROR] Failed fetching {api['url']} → {e}")
        return None


# ---------- DATA EXTRACTION ----------
def extract_data(mosdac, imd, cwc):
    return {
        "location": cwc.get("location", "Unknown"),
        "rainfall": imd.get("rainfall_mm") or mosdac.get("rainfall_mm", 0),
        "river_level": cwc.get("waterLevel_m", 0),
        "danger_level": cwc.get("dangerLevel_m", 0),
        "nearestReliefCamp_km": 3.9,   # static for now
        "dam_release": cwc.get("discharge_cumecs", 0)
    }


# ---------- PROCESS API ----------
def call_process_api(payload):
    params = {
        "location": payload["location"],
        "rainfall": payload["rainfall"],
        "river_level": payload["river_level"],
        "dam_release": payload["dam_release"]
    }
    return requests.get(PROCESS_API, params=params).json()


# ---------- BHASHINI ----------
def call_bhashini(message, bhashini_api):
    payload = {"text": message}
    headers = {"Authorization": f"Bearer {bhashini_api['api_key']}"}
    r = requests.get(bhashini_api["url"], params=payload, headers=headers)
    return r.json()


# ---------- MESSAGE API ----------
def send_message(message, msg_api):
    headers = {"Authorization": f"Bearer {msg_api['api_key']}"}
    requests.post(msg_api["url"], json={"text": message}, headers=headers)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Flood Monitoring Control Panel")
        self.geometry("900x700")
        self.districts = json.load(open("districts.json"))
        self.apis = load_api_links()
        self.district_risks = {}  # district: {"risk": bool, "data": {...}, "result": {...}}
        self.next_scan = time.time() + 6 * 3600  # 6 hours
        self.create_widgets()
        self.scan_thread = threading.Thread(target=self.auto_scan, daemon=True)
        self.scan_thread.start()
        self.update_timer()
        self.scan_all()

    def create_widgets(self):
        self.frame = tk.Frame(self)
        self.frame.pack(pady=20)
        num_districts = len(self.districts)
        cols = int(math.ceil(math.sqrt(num_districts)))
        max_len = max(len(d) for d in self.districts) if self.districts else 10
        btn_width = max(10, max_len + 2)
        self.buttons = {}
        for i, district in enumerate(self.districts):
            row = i // cols
            col = i % cols
            btn = tk.Button(self.frame, text=district, width=btn_width, height=2, command=lambda d=district: self.show_detail(d))
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.buttons[district] = btn
        self.force_btn = tk.Button(self, text="Force Scan", command=self.scan_all)
        self.force_btn.pack(side=tk.BOTTOM, pady=10)
        self.timer_label = tk.Label(self, text="Next scan in: --")
        self.timer_label.pack(side=tk.BOTTOM)

    def scan_all(self):
        for district in self.districts:
            self.scan_district(district)
        self.next_scan = time.time() + 6 * 3600
        self.update_colors()

    def scan_district(self, district):
        district_data = fetch_json(self.apis["District"], {"district": district})
        if not district_data:
            self.district_risks[district] = {"risk": False, "data": None, "result": None}
            return
        params = {
            "location": district,
            "rainfall": district_data["rainfall_mm"],
            "river_level": district_data["river_level_m"],
            "dam_release": district_data["dam_release_cumecs"]
        }
        result = call_process_api(params)
        risk = result.get("flood_risk") in ["Yes", "Likely"]
        self.district_risks[district] = {"risk": risk, "data": district_data, "result": result}

    def update_colors(self):
        for district, info in self.district_risks.items():
            color = "yellow" if info["risk"] else "lightgray"
            self.buttons[district].config(bg=color)

    def show_detail(self, district):
        info = self.district_risks.get(district, {})
        if not info.get("data"):
            messagebox.showinfo("Info", f"No data for {district}")
            return
        win = tk.Toplevel(self)
        win.title(f"Details for {district}")
        win.geometry(f"{max(500, len(district)*10 + 300)}x350")
        tk.Label(win, text=f"Rainfall: {info['data']['rainfall_mm']} mm").pack()
        tk.Label(win, text=f"River Level: {info['data']['river_level_m']} m").pack()
        tk.Label(win, text=f"Dam Release: {info['data']['dam_release_cumecs']} cumecs").pack()
        if info["result"]:
            tk.Label(win, text=f"Flood Risk: {info['result'].get('flood_risk', 'Unknown')}").pack()
            tk.Label(win, text=f"Message: {info['result'].get('message', '')}", wraplength=400).pack()
        tk.Button(win, text="Send Message", command=lambda: self.send_alert(district)).pack()
        tk.Button(win, text="Dismiss", command=win.destroy).pack()
        tk.Button(win, text="Rescan", command=lambda: [self.scan_district(district), self.update_colors(), win.destroy()]).pack()

    def send_alert(self, district):
        info = self.district_risks[district]
        if info["result"] and info["result"].get("flood_risk") in ["Yes", "Likely"]:
            message = info["result"]["message"]
            if "Estimated time left:" in message:
                time_left = message.split("Estimated time left: ")[1].strip()
            else:
                time_left = "Unknown"
            relief_km = info["data"].get("nearestReliefCamp_km", "Unknown") if info["data"] else "Unknown"
            relief_link = f"https://www.google.com/maps/search/relief+camp+near+{district}/"
            formatted_msg = f"""--- Flood Alert ---
Flood alert for             : {district}
Time left before flood : {time_left}
Nearest relief camp     : {relief_km} KM
{relief_link}"""
            translated = call_bhashini(formatted_msg, self.apis["Bhashini"])
            if isinstance(translated, dict) and "text" in translated:
                final_msg = "\n".join([f"[{lang.upper()}-ALERT]\n{trans}" for lang, trans in translated.items() if lang != "text"])
            else:
                final_msg = translated.get("outputText", formatted_msg)
            send_message(final_msg, self.apis["MESSAGE_APi"])
            messagebox.showinfo("Alert", f"Alert sent for {district}")

    def auto_scan(self):
        while True:
            time.sleep(6 * 3600)
            self.scan_all()

    def update_timer(self):
        remaining = max(0, self.next_scan - time.time())
        hours, rem = divmod(int(remaining), 3600)
        mins, secs = divmod(rem, 60)
        self.timer_label.config(text=f"Next scan in: {hours:02d}:{mins:02d}:{secs:02d}")
        self.after(1000, self.update_timer)


# ---------- MAIN PIPELINE ----------
def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()