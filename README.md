# Home Flood-Risk Monitoring System
A capstone project that combines **soil-moisture sensing**, **local climate data**, **soil-texture parameters**, and **storm-severity modelling** to estimate basement and foundation flood risk for individual homes. 
The system reads four soil-moisture sensors **(north, south, east, and west walls)** of a house—and merges the data with **24-hour rainfall forecasts**, **MTO IDF curves**, and **short-term soil reactivity** to compute a homeowner-facing flood-risk score.
The end product will connect to a **mobile app**, giving homeowners early warning when soil conditions and upcoming rainfall create a higher chance of seepage or basement water ingress.

---

## 🌧️ Project Overview

Traditional flood-risk models operate at watershed scale. Our goal is to create a **localized, homeowner-specific monitoring system** by integrating:

### **1. Soil Moisture Sensors (x4)**
Placed around the house foundation (north, south, east, west).  
Values represent *fractional VWC* (volumetric water content).

Quality control & smoothing:
- Remove invalid readings (NaN, out-of-range).
- Take **median** across all valid samples in each batch.  
  Implemented in `quality_control.py`.

### **2. Soil Texture Presets**
Each home’s soil type (e.g., clay loam) determines **field capacity (FC)** and **saturation (SAT)** thresholds.  
Moisture is converted into a normalized saturation index:
S = (θ - FC) / (SAT - FC)

Implemented in `normalization.py`.

### **3. 24-Hour Rainfall Forecast**
Pulled from the **[Open-Meteo GEM seamless model](https://open-meteo.com/en/docs/gem-api)**, using the home's lat/lon.  
We sum the next 24 hours of hourly precipitation.

Implemented in `forecast_extraction.py`.

### **4. Local IDF Curves (MTO)**
Using the official **[Ontario MTO IDF dataset](https://idfcurves.mto.gov.on.ca/map_acquisition.shtml)**, rainfall severity is compared against the **24h 2-year storm depth** for the home’s location.

Implemented in `idf_curve_extraction.py`.

### **5. Flood-Risk Scoring Model**
Three components combine into the final risk score:

1. **Soil saturation** (0–100) — how wet the foundation soil is  
   (`soil_saturation_component.py`)

2. **Storm severity factor** — ratio of forecast rainfall to local IDF  
   (`storm_severity.py`)

3. **Site sensitivity** — short-term soil reactivity (ΔS over 1 hour)  
   (`site_sensitivity.py`)

Combined in `risk_model.py`.

Mapped to categories:
- **Low**
- **Moderate**
- **High**
- **Severe**

---

## 🧠 System Pipeline

Implemented in `main.py` and orchestrated via `run_pipeline()`:

1. Load the most recent soil-moisture batch  
2. Clean and smooth readings  
3. Normalize to saturation values  
4. Compute features (asymmetry, averages, storm data)  
   (`features.py`)
5. Calculate flood-risk score  
6. Output to CSV or send upstream to Firebase  
7. Mobile app displays risk & alerts to the user

---

## 📱 Mobile-App Integration

The final system will:
- Push 15-min risk updates to Firebase  
- Trigger notifications when risk escalates (e.g., High or Severe)  
- Provide graphs of soil moisture, radar forecasts, and risk history  
- Provide homeowners with actionable flood-prevention tips

---

## 🏗️ Installation

```bash
git clone <your_repo>
cd home-flood-monitoring-system
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶️ Running the Pipeline
```bash
Copy code
python -m src.main
```
Outputs:

```bash
data/results/risk_results.csv
```

---

## 📂 Project Structure
```css
src/
  main.py
  quality_control.py
  normalization.py
  features.py
  risk_model.py
  utilities/
    forecast_extraction.py
    idf_curve_extraction.py
  risk_components/
    soil_saturation.py
    storm_severity.py
    site_sensitivity.py
```

---

📌 Future Work
- Integrate real sensor hardware (LoRaWAN / WiFi)
- Live mobile-app UI with real-time charts
