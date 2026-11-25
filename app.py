import os
import json
import uuid
import base64
import time
import io
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

try:
    import torch
    import torchvision.models as models
    import torchvision.transforms as transforms
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None

import numpy as np
from plantvillage_engine import PLANTVILLAGE_MASTER_DB
from leaf_classifier import get_classifier
from leaf_crop import crop_to_leaf
from vector_rag import get_vector_db, get_rag

app = FastAPI(title="VoiceKeep Ag - Leaf Disease Detection & Hyper-Local Outbreak Warning")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IS_VERCEL = bool(os.environ.get("VERCEL") or os.environ.get("VERCEL_ENV"))
WRITABLE_DIR = "/tmp/leafguard_data" if IS_VERCEL else DATA_DIR
REF_FILE = os.path.join(WRITABLE_DIR, "references.json")
HISTORY_FILE = os.path.join(WRITABLE_DIR, "history.json")
REF_IMG_DIR = os.path.join(WRITABLE_DIR, "reference_images")
UPLOADS_DIR = os.path.join(WRITABLE_DIR, "uploads")

for d in [WRITABLE_DIR, REF_IMG_DIR, UPLOADS_DIR]:
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass

if IS_VERCEL:
    import shutil
    for fname in ["references.json", "history.json", "outbreaks.json"]:
        src = os.path.join(DATA_DIR, fname)
        dst = os.path.join(WRITABLE_DIR, fname)
        if os.path.exists(src) and not os.path.exists(dst):
            try:
                shutil.copy2(src, dst)
            except Exception:
                pass

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
VISION_MODEL = os.environ.get("VISION_MODEL", "moondream")
LLM_MODEL = os.environ.get("LLM_MODEL", "leafguard-ai")

def _load_dotenv():
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
        except Exception:
            pass

_load_dotenv()
GOOGLE_WEATHER_API_KEY = os.environ.get("GOOGLE_WEATHER_API_KEY", "")
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
OUTBREAKS_FILE = os.path.join(WRITABLE_DIR, "outbreaks.json")
_TRANSLATE_CACHE: Dict[str, str] = {}

# Trained leaf classifier: MobileNetV3 embeddings + trained linear head + calibration.
# Loaded lazily on first request so the server starts even without torch installed.
leaf_clf = None


def ensure_classifier():
    global leaf_clf
    if leaf_clf is None:
        leaf_clf = get_classifier()
    return leaf_clf

# Ensure files exist safely
try:
    if not os.path.exists(REF_FILE):
        with open(REF_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
except OSError:
    pass

PLANTVILLAGE_FILE = os.path.join(DATA_DIR, "plantvillage_knowledge.json")

def load_plantvillage_knowledge() -> Dict[str, Any]:
    try:
        with open(PLANTVILLAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def load_references() -> List[Dict[str, Any]]:
    try:
        with open(REF_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_references(refs: List[Dict[str, Any]]):
    try:
        with open(REF_FILE, "w", encoding="utf-8") as f:
            json.dump(refs, f, indent=2, ensure_ascii=False)
    except OSError:
        pass

def load_history() -> List[Dict[str, Any]]:
    for path in [HISTORY_FILE, "/tmp/history.json"]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return []

def save_history(entry: Dict[str, Any]):
    history = load_history()
    history.insert(0, entry)
    if len(history) > 50:
        history = history[:50]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except OSError:
        try:
            with open("/tmp/history.json", "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

# Local mock neighborhood outbreaks data (hyper-local <2 hectares)
LOCAL_ALERTS = [
    {
        "id": "alt_1",
        "crop": "Tomato",
        "disease": "Early Blight Outbreak",
        "distance": "600m East (Sector 4B)",
        "plot_size": "1.2 ha",
        "risk_level": "High",
        "timestamp": "2 hours ago",
        "advisory": "High spore count detected in morning mist. Farmers within 1.5km advised to avoid overhead watering and spray preventive bio-fungicide.",
        "lat_offset": 0.005,
        "lon_offset": 0.007
    },
    {
        "id": "alt_2",
        "crop": "Chilli",
        "disease": "Whitefly & Leaf Curl Cluster",
        "distance": "1.2km North-West",
        "plot_size": "0.8 ha",
        "risk_level": "Moderate",
        "timestamp": "5 hours ago",
        "advisory": "Pest migration observed along wind corridor. Check underside of chilli leaves and install yellow sticky cards.",
        "lat_offset": -0.008,
        "lon_offset": 0.004
    },
    {
        "id": "alt_3",
        "crop": "Wheat",
        "disease": "Suspected Yellow Rust",
        "distance": "1.9km South",
        "plot_size": "1.8 ha",
        "risk_level": "Critical",
        "timestamp": "12 hours ago",
        "advisory": "Wind-borne fungal threat. Inspect wheat flag leaves for orange pustule lines immediately.",
        "lat_offset": -0.012,
        "lon_offset": -0.006
    }
]

def analyze_image_pixels(img: Image.Image) -> Dict[str, Any]:
    """Extract physical color and leaf health characteristics directly from image pixels."""
    img_rgb = img.convert("RGB").resize((150, 150))
    pixels = list(img_rgb.getdata())
    total_pixels = len(pixels)

    green_count = 0
    yellow_pale_count = 0
    brown_dark_count = 0
    white_mold_count = 0

    for r, g, b in pixels:
        # Healthy green
        if g > r * 1.15 and g > b * 1.15 and g > 60:
            green_count += 1
        # Pale yellow / chlorotic (high red + green, low blue)
        elif r > 120 and g > 110 and b < min(r, g) * 0.75:
            yellow_pale_count += 1
        # Brown / Necrotic / Dried spots
        elif (r > g or abs(r - g) < 25) and max(r, g) < 140 and (r > 40 or g > 40) and b < 90:
            brown_dark_count += 1
        # White / Powdery mildew
        elif r > 190 and g > 190 and b > 190:
            white_mold_count += 1

    green_pct = round((green_count / total_pixels) * 100, 1)
    yellow_pct = round((yellow_pale_count / total_pixels) * 100, 1)
    brown_pct = round((brown_dark_count / total_pixels) * 100, 1)
    white_pct = round((white_mold_count / total_pixels) * 100, 1)

    return {
        "healthy_green_pct": green_pct,
        "pale_yellow_pct": yellow_pct,
        "brown_dried_pct": brown_pct,
        "powdery_white_pct": white_pct,
        "has_high_discoloration": (yellow_pct + brown_pct + white_pct) > 15
    }

def query_ollama(model: str, prompt: str, images: Optional[List[str]] = None, format_json: bool = False, timeout: int = 40) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    if images:
        payload["images"] = images
    if format_json:
        payload["format"] = "json"

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("response", "").strip()

class DiagnoseRequest(BaseModel):
    image_base64: str
    crop_hint: Optional[str] = ""
    farmer_notes: Optional[str] = ""

class ReferenceItem(BaseModel):
    crop: str
    disease: str
    visual_symptoms: str
    treatment: str
    risk_level: Optional[str] = "Moderate"
    image_base64: Optional[str] = None

class OutbreakAlertItem(BaseModel):
    crop: str
    disease: str
    plot_size: str
    distance: str
    risk_level: str
    advisory: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    location_name: Optional[str] = ""
    sender_id: Optional[str] = ""

class RagAskRequest(BaseModel):
    question: str
    crop: Optional[str] = ""

class TranslateRequest(BaseModel):
    texts: List[str]
    target_lang: str

@app.get("/")
@app.head("/")
def get_index():
    index_path = os.path.join(BASE_DIR, "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>VoiceKeep Ag Server Running</h1>")

@app.get("/api/health")
def health_check():
    ollama_ok = False
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as r:
            ollama_ok = (r.status == 200)
    except Exception:
        ollama_ok = False

    return {
        "status": "online",
        "ollama_available": ollama_ok,
        "vision_model": VISION_MODEL,
        "llm_model": LLM_MODEL,
        "vector_db": get_vector_db().stats(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/references")
def get_references():
    return load_references()

@app.post("/api/references")
def add_reference(ref: ReferenceItem):
    refs = load_references()
    ref_id = f"ref_{uuid.uuid4().hex[:8]}"
    img_filename = None

    if ref.image_base64:
        try:
            # strip data header if present
            raw_b64 = ref.image_base64
            if "," in raw_b64:
                raw_b64 = raw_b64.split(",", 1)[1]
            img_bytes = base64.b64decode(raw_b64)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            # Instant zero-retraining Vector DB indexing
            clf = ensure_classifier()
            if clf is not None:
                try:
                    c_img = crop_to_leaf(img)
                    vecs = clf._features([img, c_img])
                    cid = f"{ref.crop.strip().replace(' ', '_')}___{ref.disease.strip().replace(' ', '_')}"
                    get_vector_db().add_vectors(
                        vecs,
                        [cid, cid],
                        [ref.crop, ref.crop],
                        [ref.disease, ref.disease],
                        [f"teach_ai:{ref_id}", f"teach_ai:{ref_id}_crop"],
                        persist=True,
                    )
                except Exception as ve:
                    print("VectorDB teach_ai indexing warning:", ve)
            img.thumbnail((500, 500))
            img_filename = f"{ref_id}.jpg"
            img.save(os.path.join(REF_IMG_DIR, img_filename), "JPEG", quality=85)
        except Exception as e:
            print("Failed to save reference image:", e)

    new_item = {
        "id": ref_id,
        "crop": ref.crop,
        "disease": ref.disease,
        "visual_symptoms": ref.visual_symptoms,
        "treatment": ref.treatment,
        "risk_level": ref.risk_level,
        "image_url": f"/static/reference_images/{img_filename}" if img_filename else None,
        "created_at": datetime.now().isoformat()
    }
    refs.append(new_item)
    save_references(refs)
    get_rag().rebuild_index(extra_refs=refs)
    return {"success": True, "reference": new_item, "vector_db": get_vector_db().stats()}


@app.post("/api/rag/ask")
def rag_ask(req: RagAskRequest):
    """Retrieve grounded agronomy context via RAG and optionally generate answer with Ollama."""
    rag = get_rag()
    hits = rag.retrieve(req.question, crop=req.crop or "", top_k=3)
    context_text = "\n\n".join(h["text"] for h in hits)
    answer = ""
    used_llm = False
    try:
        prompt = (
            "You are LeafGuard Agronomy Assistant for smallholder farmers. "
            "Answer concisely in simple Hindi + English using ONLY the retrieved context below.\n\n"
            f"Context:\n{context_text}\n\nQuestion: {req.question}\nAnswer:"
        )
        answer = query_ollama(model=LLM_MODEL, prompt=prompt, format_json=False, timeout=15)
        used_llm = bool(answer)
    except Exception:
        used_llm = False

    if not answer and hits:
        top = hits[0]
        org = "; ".join(top.get("organic_treatment", [])[:2])
        chem = "; ".join(top.get("chemical_treatment", [])[:2])
        answer = (
            f"{top['crop']} — {top['disease']}: "
            f"Organic: {org}. Chemical: {chem}. {top.get('hindi_summary', '')}"
        ).strip()

    return {
        "question": req.question,
        "answer": answer,
        "used_llm": used_llm,
        "sources": [{"id": h["id"], "crop": h["crop"], "disease": h["disease"], "score": h["score"]} for h in hits],
    }

@app.delete("/api/references/{ref_id}")
def delete_reference(ref_id: str):
    refs = load_references()
    new_refs = [r for r in refs if r.get("id") != ref_id]
    save_references(new_refs)
    return {"success": True, "remaining": len(new_refs)}

def _compute_weather_disease_risks(temp_c: float, humidity: float, precip_prob: float, wind_kmh: float) -> List[Dict[str, Any]]:
    """Compute crop disease outbreak risks from real-time weather conditions."""
    risks = []
    if humidity >= 75 and 10 <= temp_c <= 24:
        risks.append({
            "disease": "Tomato & Potato Late Blight (Phytophthora)",
            "crops": ["Tomato", "Potato"],
            "risk": "CRITICAL",
            "reason": f"Cool & humid ({temp_c:.1f}°C, {humidity:.0f}% RH) triggers rapid sporangia spread."
        })
        risks.append({
            "disease": "Wheat Yellow Rust / Mustard White Rust",
            "crops": ["Wheat", "Mustard"],
            "risk": "HIGH",
            "reason": f"Cool moist air ({temp_c:.1f}°C, {humidity:.0f}% RH) favors rust pustule germination."
        })
    if humidity >= 70 and (22 <= temp_c <= 34 or precip_prob >= 30):
        risks.append({
            "disease": "Rice Blast & Bacterial Leaf Blight",
            "crops": ["Rice", "Paddy"],
            "risk": "HIGH",
            "reason": f"Warm humid weather ({temp_c:.1f}°C, {humidity:.0f}% RH, {precip_prob:.0f}% rain) spreads spores."
        })
        risks.append({
            "disease": "Coffee Leaf Rust & Banana Black Sigatoka",
            "crops": ["Coffee", "Banana", "Mango"],
            "risk": "HIGH",
            "reason": "High moisture and wind accelerate fungal spore splash across orchards."
        })
    if humidity <= 55 and temp_c >= 27:
        risks.append({
            "disease": "Two-Spotted Spider Mites & Powdery Mildew",
            "crops": ["Tomato", "Mango", "Squash", "Cherry"],
            "risk": "HIGH",
            "reason": f"Hot dry conditions ({temp_c:.1f}°C, {humidity:.0f}% RH) cause rapid mite & mildew buildup."
        })
    if wind_kmh >= 18:
        risks.append({
            "disease": "Wind-Borne Spore Drift Alert",
            "crops": ["Corn", "Apple", "Grape", "Soybean"],
            "risk": "MODERATE",
            "reason": f"Gusty wind ({wind_kmh:.0f} km/h) can carry fungal spores up to 2.5 km."
        })
    if not risks:
        risks.append({
            "disease": "Low-to-Moderate Baseline Fungal Watch",
            "crops": ["All Crops"],
            "risk": "LOW",
            "reason": f"Balanced conditions ({temp_c:.1f}°C, {humidity:.0f}% RH). Routine morning leaf inspection advised."
        })
    return risks


def _reverse_geocode_name(lat: float, lon: float) -> str:
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=12"
        req = urllib.request.Request(url, headers={"User-Agent": "LeafGuardAI/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            d = json.loads(r.read().decode("utf-8"))
            addr = d.get("address", {})
            parts = [addr.get("village") or addr.get("town") or addr.get("suburb") or addr.get("city") or addr.get("county"), addr.get("state")]
            name = ", ".join([p for p in parts if p])
            return name or f"{lat:.3f}, {lon:.3f}"
    except Exception:
        return f"{lat:.3f}, {lon:.3f}"


@app.get("/api/config")
def get_public_config():
    return {
        "maps_api_key": GOOGLE_MAPS_API_KEY,
        "weather_enabled": bool(GOOGLE_WEATHER_API_KEY),
    }


@app.get("/api/weather-risk")
def get_weather_risk(lat: float, lon: float):
    weather_data = {}
    source = "google_weather"
    if GOOGLE_WEATHER_API_KEY:
        try:
            url = (
                f"https://weather.googleapis.com/v1/currentConditions:lookup"
                f"?key={GOOGLE_WEATHER_API_KEY}&location.latitude={lat}&location.longitude={lon}"
            )
            with urllib.request.urlopen(url, timeout=8) as r:
                weather_data = json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print("Google Weather API error:", e)
            weather_data = {}

    if weather_data:
        temp_c = float(weather_data.get("temperature", {}).get("degrees", 25.0))
        humidity = float(weather_data.get("relativeHumidity", 60.0))
        wind_kmh = float(weather_data.get("wind", {}).get("speed", {}).get("value", 8.0))
        precip_prob = float(weather_data.get("precipitation", {}).get("probability", {}).get("percent", 10.0))
        cond_text = weather_data.get("weatherCondition", {}).get("description", {}).get("text", "Clear")
        icon_uri = weather_data.get("weatherCondition", {}).get("iconBaseUri", "")
    else:
        source = "open_meteo_fallback"
        try:
            om_url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation_probability"
            )
            with urllib.request.urlopen(om_url, timeout=8) as r:
                om = json.loads(r.read().decode("utf-8")).get("current", {})
            temp_c = float(om.get("temperature_2m", 25.0))
            humidity = float(om.get("relative_humidity_2m", 60.0))
            wind_kmh = float(om.get("wind_speed_10m", 8.0))
            precip_prob = float(om.get("precipitation_probability", 10.0))
            cond_text = "Live Field Weather"
            icon_uri = ""
        except Exception:
            temp_c, humidity, wind_kmh, precip_prob, cond_text, icon_uri = 26.0, 62.0, 10.0, 10.0, "Partly Cloudy", ""

    location_name = _reverse_geocode_name(lat, lon)
    risks = _compute_weather_disease_risks(temp_c, humidity, precip_prob, wind_kmh)

    return {
        "location_name": location_name,
        "lat": lat,
        "lon": lon,
        "source": source,
        "weather": {
            "temp_c": round(temp_c, 1),
            "humidity": round(humidity),
            "wind_kmh": round(wind_kmh, 1),
            "precip_prob": round(precip_prob),
            "condition": cond_text,
            "icon_url": f"{icon_uri}.png" if icon_uri else "",
        },
        "disease_risks": risks,
    }


@app.post("/api/translate")
def translate_texts(req: TranslateRequest):
    lang = (req.target_lang or "en").strip().lower()
    if lang == "en":
        return {"lang": "en", "translations": req.texts}
    # Map Santali/Dogri/Bodo/Kashmiri/etc. cleanly; Google gtx supports ISO codes
    out = []
    for txt in req.texts:
        if not txt or not txt.strip():
            out.append(txt)
            continue
        cache_key = f"{lang}::{txt}"
        if cache_key in _TRANSLATE_CACHE:
            out.append(_TRANSLATE_CACHE[cache_key])
            continue
        try:
            q = urllib.parse.quote(txt)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={urllib.parse.quote(lang)}&dt=t&q={q}"
            req_u = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_u, timeout=6) as r:
                res = json.loads(r.read().decode("utf-8"))
                translated = "".join(seg[0] for seg in res[0] if seg and seg[0])
                _TRANSLATE_CACHE[cache_key] = translated
                out.append(translated)
        except Exception:
            out.append(txt)
    return {"lang": lang, "translations": out}


def _load_persisted_outbreaks() -> List[Dict[str, Any]]:
    for path in [OUTBREAKS_FILE, "/tmp/outbreaks.json"]:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return LOCAL_ALERTS


def _save_persisted_outbreaks(alerts: List[Dict[str, Any]]):
    for path in [OUTBREAKS_FILE, "/tmp/outbreaks.json"]:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(alerts[:50], f, indent=2, ensure_ascii=False)
            return
        except OSError:
            continue


@app.get("/api/outbreaks")
def get_outbreaks(since: Optional[float] = None):
    alerts = _load_persisted_outbreaks()
    if since is not None:
        return [a for a in alerts if float(a.get("created_ts", 0)) > since]
    return alerts


@app.post("/api/outbreaks")
def create_outbreak(alert: OutbreakAlertItem):
    alerts = _load_persisted_outbreaks()
    now_ms = time.time() * 1000.0
    new_alert = {
        "id": f"alt_{uuid.uuid4().hex[:6]}",
        "crop": alert.crop,
        "disease": alert.disease,
        "distance": alert.distance,
        "plot_size": alert.plot_size,
        "risk_level": alert.risk_level,
        "timestamp": "Just now",
        "created_ts": now_ms,
        "advisory": alert.advisory,
        "lat": alert.lat,
        "lon": alert.lon,
        "location_name": alert.location_name or "",
        "sender_id": alert.sender_id or "",
        "lat_offset": 0.002,
        "lon_offset": -0.003
    }
    alerts.insert(0, new_alert)
    _save_persisted_outbreaks(alerts)
    return {"success": True, "alert": new_alert}

@app.get("/api/history")
def get_history_route():
    return load_history()

@app.post("/api/diagnose")
def diagnose_leaf(req: DiagnoseRequest):
    start_time = time.time()
    try:
        raw_b64 = req.image_base64
        if "," in raw_b64:
            raw_b64 = raw_b64.split(",", 1)[1]
        img_bytes = base64.b64decode(raw_b64)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")

    # Resize image for fast local AI processing (max 640px)
    img_resized = img.copy()
    img_resized.thumbnail((640, 640))
    buffer = io.BytesIO()
    img_resized.save(buffer, format="JPEG", quality=85)
    processed_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # 1. Computer Vision Pixel Health Analysis
    pixel_stats = analyze_image_pixels(img)

    # 2. Trained classifier + Image Vector DB k-NN retrieval
    clf = ensure_classifier()
    if clf is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run build_embeddings.py then train_classifier.py.")

    pred = clf.predict(img, crop_hint=req.crop_hint)

    vector_matches = []
    try:
        q_img = crop_to_leaf(img)
        q_feat = clf._features([q_img])[0]
        vector_matches = get_vector_db().search(q_feat, top_k=5, crop_hint=req.crop_hint or "")
        taught_hits = [m for m in vector_matches if m["source"].startswith("teach_ai:") and m["similarity"] >= 0.78]
        if taught_hits and (not pred["detected"] or taught_hits[0]["similarity"] > pred.get("cosine", 0.0)):
            top_v = taught_hits[0]
            pred = {
                "detected": True,
                "is_plant": True,
                "class_id": top_v["class_id"],
                "crop": top_v["crop"],
                "condition": top_v["disease"],
                "confidence": round(min(97.0, top_v["similarity"] * 100.0), 1),
                "crop_confidence": round(min(97.0, top_v["similarity"] * 100.0), 1),
                "cosine": top_v["similarity"],
                "plantness": pred.get("plantness", 0.3),
                "top_k": pred.get("top_k", []),
            }
    except Exception as ve:
        print("VectorDB search warning:", ve)

    # 3. Optional vision-model description. Purely cosmetic: it never decides
    #    the diagnosis, because keyword matching on free text was the source of
    #    most of this app's bogus answers.
    vision_description = ""
    if os.environ.get("ENABLE_VISION_DESCRIPTION", "0") == "1":
        try:
            vision_description = query_ollama(
                model=VISION_MODEL,
                prompt=(
                    "Describe this crop leaf in one sentence: its shape, its colour, "
                    "and any spots, lesions or discoloration you can see."),
                images=[processed_b64],
                format_json=False,
                timeout=20,
            ).replace("!!!IMAGE!!!", "").strip()
        except Exception as e:
            print("Vision description unavailable:", e)

    # 4. "Not detected" is a real answer, not a fallback.
    if not pred["detected"]:
        return _not_detected_response(
            pred=pred,
            pixel_stats=pixel_stats,
            vision_description=vision_description,
            start_time=start_time,
        )

    # 5. Annotate the detected class with agronomic guidance from the knowledge base.
    best = PLANTVILLAGE_MASTER_DB.get(pred["class_id"])
    if best is None:
        best = {
            "crop": pred["crop"],
            "disease": pred["condition"],
            "is_healthy": "healthy" in pred["condition"].lower(),
            "severity": "Moderate",
            "color_signature": "See reference image",
            "lesion_pattern": pred["condition"],
            "leaf_morphology": f"{pred['crop']} leaf",
            "organic_treatment": ["Consult your local agriculture extension officer."],
            "chemical_treatment": ["No dosage on file for this class."],
            "outbreak_risk": "Moderate",
            "neighbor_alert": "Confirm with a second photo from a different leaf.",
            "hindi_summary": "इस पत्ती के लिए उपचार जानकारी उपलब्ध नहीं है। स्थानीय कृषि अधिकारी से सलाह लें।",
        }

    confidence_val = f"{pred['confidence']:.1f}%"
    if best["is_healthy"]:
        summary_text = (f"Vibrant {best['crop']} foliage with healthy green chlorophyll "
                        f"tissue and no active fungal or bacterial lesions.")
    else:
        summary_text = (f"{best['crop']} foliage showing {best['lesion_pattern'].lower()} "
                        f"with {best['color_signature'].lower()}.")

    diagnosis_json = {
        "detected": True,
        "crop": best["crop"],
        "condition": best["disease"],
        "is_healthy": best["is_healthy"],
        "confidence": confidence_val,
        "crop_confidence": f"{pred.get('crop_confidence', pred['confidence']):.1f}%",
        "severity": best["severity"],
        "visual_summary": summary_text,
        "symptoms": [
            f"Color Spectrum: {best['color_signature']}",
            f"Lesion Pattern: {best['lesion_pattern']}",
            f"Leaf Morphology: {best['leaf_morphology']}",
        ],
        "organic_treatment": best["organic_treatment"],
        "chemical_treatment": best["chemical_treatment"],
        "outbreak_risk": best["outbreak_risk"],
        "neighbor_alert": best["neighbor_alert"],
        "hindi_summary": best["hindi_summary"],
    }

    # Save to history
    diag_id = f"diag_{uuid.uuid4().hex[:8]}"
    history_entry = {
        "id": diag_id,
        "timestamp": datetime.now().isoformat(),
        "crop": diagnosis_json.get("crop", "Plant Leaf"),
        "condition": diagnosis_json.get("condition", "Condition"),
        "severity": diagnosis_json.get("severity", "Moderate"),
        "is_healthy": diagnosis_json.get("is_healthy", False),
        "outbreak_risk": diagnosis_json.get("outbreak_risk", "Moderate"),
        "visual_summary": diagnosis_json.get("visual_summary", ""),
        "processing_seconds": round(time.time() - start_time, 2)
    }
    save_history(history_entry)

    diagnosis_json["diag_id"] = diag_id
    diagnosis_json["processing_seconds"] = round(time.time() - start_time, 2)
    diagnosis_json["vision_raw"] = vision_description
    diagnosis_json["pixel_metrics"] = pixel_stats
    diagnosis_json["neural_class"] = pred["class_id"]
    diagnosis_json["neural_similarity"] = pred["confidence"]
    diagnosis_json["top_k"] = pred["top_k"]
    diagnosis_json["vector_matches"] = vector_matches[:3]
    if req.farmer_notes:
        diagnosis_json["rag_sources"] = get_rag().retrieve(req.farmer_notes, crop=best["crop"], top_k=2)

    return diagnosis_json


def _not_detected_response(pred, pixel_stats, vision_description, start_time):
    """Honest answer when the plant/disease guards reject the image."""
    is_plant = pred.get("is_plant", False)
    if not is_plant:
        condition = "Not detected — no plant leaf in frame"
        crop = "—"
        summary = (
            "Is photo mein paudhe ki patti nahi mili. Model sirf patti (leaf) ki "
            "tasveerein padhta hai — fruit, tana, ya phool abhi support nahi hai. "
            "Ek saaf patti ki photo lein, achhi roshni mein, background hata kar."
        )
        hindi = ("तस्वीर में पत्ती नहीं मिली। अभी केवल पत्तियों की पहचान उपलब्ध है, "
                 "फल या तना नहीं। कृपया एक साफ़ पत्ती की तस्वीर लें।")
    else:
        condition = "Not detected — unknown plant or disease"
        crop = "—"
        summary = (
            "Leaf to dikh rahi hai, par ye model ke known diseases se match nahi hui. "
            "Model sirf unhi fasalon ko pehchanta hai jinpe usse train kiya gaya hai."
        )
        hindi = "पत्ती दिख रही है, लेकिन यह किसी ज्ञात रोग से मेल नहीं खाई।"

    diag_id = f"diag_{uuid.uuid4().hex[:8]}"
    return {
        "detected": False,
        "crop": crop,
        "condition": condition,
        "is_healthy": False,
        "confidence": "—",
        "severity": "Unknown",
        "visual_summary": summary,
        "symptoms": [pred.get("reason", "")],
        "organic_treatment": [
            "Ek saaf photo dobara lein: ek patta, poori frame mein, natural light.",
            "Agar patta kisi aur fasal ka hai, to 'Crop' lock set karke dobara try karein.",
        ],
        "chemical_treatment": ["Koi spray suggest nahi kiya jaata jab tak disease confirm na ho."],
        "outbreak_risk": "Unknown",
        "neighbor_alert": "Diagnosis confirm hone tak koi alert broadcast na karein.",
        "hindi_summary": hindi,
        "diag_id": diag_id,
        "processing_seconds": round(time.time() - start_time, 2),
        "vision_raw": vision_description,
        "pixel_metrics": pixel_stats,
        "neural_class": None,
        "neural_similarity": 0.0,
        "top_k": pred.get("top_k", []),
        "rejection_reason": pred.get("reason", ""),
        "cosine": pred.get("cosine"),
        "plantness": pred.get("plantness"),
    }

# Mount static files and reference images if present
if os.path.exists(REF_IMG_DIR):
    app.mount("/static/reference_images", StaticFiles(directory=REF_IMG_DIR), name="ref_images")

static_path = os.path.join(BASE_DIR, "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
