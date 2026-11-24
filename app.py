import os
import json
import uuid
import base64
import time
import io
import urllib.request
import urllib.error
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
from visual_features import extract_visual_signature
from plantvillage_engine import diagnose_with_master_engine, PLANTVILLAGE_MASTER_DB

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
REF_FILE = os.path.join(DATA_DIR, "references.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
REF_IMG_DIR = os.path.join(DATA_DIR, "reference_images")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")

for d in [DATA_DIR, REF_IMG_DIR, UPLOADS_DIR]:
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
VISION_MODEL = os.environ.get("VISION_MODEL", "moondream")
LLM_MODEL = os.environ.get("LLM_MODEL", "leafguard-ai")

# Load Trained PlantVillage MobileNet Feature Classifier
TRAINED_MODEL_PATH = os.path.join(DATA_DIR, "trained_plantvillage_model.pt")
VISUAL_CLF_PATH = os.path.join(DATA_DIR, "visual_classifier.json")
torch_device = torch.device("cpu") if HAS_TORCH else None
leaf_model_data = None
leaf_feature_extractor = None
visual_clf_data = None

try:
    if os.path.exists(VISUAL_CLF_PATH):
        with open(VISUAL_CLF_PATH, "r", encoding="utf-8") as f:
            raw_vc = json.load(f)
            visual_clf_data = {
                "classes": raw_vc["classes"],
                "weights": np.array(raw_vc["weights"], dtype=np.float32),
                "bias": np.array(raw_vc["bias"], dtype=np.float32),
            }
        print(f"Loaded pure-NumPy visual classifier with {len(visual_clf_data['classes'])} classes.")
except Exception as e:
    print("Notice loading visual classifier:", e)

if HAS_TORCH:
    mobilenet_preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    try:
        if os.path.exists(TRAINED_MODEL_PATH):
            leaf_model_data = torch.load(TRAINED_MODEL_PATH, map_location=torch_device)
            _mobilenet = models.mobilenet_v3_small(weights='DEFAULT').eval()
            leaf_feature_extractor = torch.nn.Sequential(
                _mobilenet.features,
                _mobilenet.avgpool,
                torch.nn.Flatten()
            ).to(torch_device)
            print(f"Loaded trained PlantVillage neural model with {len(leaf_model_data.get('classes', []))} classes.")
    except Exception as e:
        print("Notice loading trained leaf model (pt):", e)

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
    return {"success": True, "reference": new_item}

@app.delete("/api/references/{ref_id}")
def delete_reference(ref_id: str):
    refs = load_references()
    new_refs = [r for r in refs if r.get("id") != ref_id]
    save_references(new_refs)
    return {"success": True, "remaining": len(new_refs)}

@app.get("/api/outbreaks")
def get_outbreaks():
    return LOCAL_ALERTS

@app.post("/api/outbreaks")
def create_outbreak(alert: OutbreakAlertItem):
    new_alert = {
        "id": f"alt_{uuid.uuid4().hex[:6]}",
        "crop": alert.crop,
        "disease": alert.disease,
        "distance": alert.distance,
        "plot_size": alert.plot_size,
        "risk_level": alert.risk_level,
        "timestamp": "Just now",
        "advisory": alert.advisory,
        "lat_offset": 0.002,
        "lon_offset": -0.003
    }
    LOCAL_ALERTS.insert(0, new_alert)
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

    # 2. Deep Feature Neural Classifier (MobileNetV3 locally, Pure-NumPy Visual Classifier on Vercel)
    neural_pred_class = None
    neural_confidence = 0.0
    if leaf_feature_extractor is not None and leaf_model_data is not None:
        try:
            tensor = mobilenet_preprocess(img).unsqueeze(0).to(torch_device)
            with torch.no_grad():
                feat = leaf_feature_extractor(tensor)
                feat = feat / feat.norm(p=2, dim=1, keepdim=True)
                sims = torch.mm(feat, leaf_model_data["centroids"].t())[0]
                top_idx = torch.argmax(sims).item()
                neural_pred_class = leaf_model_data["classes"][top_idx]
                probs = torch.softmax(sims * 25.0, dim=0)
                sim_pct = float(sims[top_idx].item()) * 100.0
                prob_pct = float(probs[top_idx].item()) * 100.0
                neural_confidence = round(min(99.0, max(55.0, 0.55 * sim_pct + 0.45 * prob_pct)), 1)
        except Exception as e:
            print("Neural feature inference error:", e)
    elif visual_clf_data is not None:
        try:
            v_feat = extract_visual_signature(img)
            logits = np.dot(v_feat, visual_clf_data["weights"]) + visual_clf_data["bias"]
            top_idx = int(np.argmax(logits))
            neural_pred_class = visual_clf_data["classes"][top_idx]
            sorted_logits = np.sort(logits)
            margin = float(sorted_logits[-1] - sorted_logits[-2]) if len(sorted_logits) > 1 else 0.0
            exp_l = np.exp((logits - np.max(logits)) * 10.0)
            probs = exp_l / np.sum(exp_l)
            prob_pct = float(probs[top_idx]) * 100.0
            raw_strength = float(np.clip(logits[top_idx], 0.0, 1.0)) * 100.0
            margin_bonus = min(18.0, margin * 35.0)
            neural_confidence = round(min(98.5, max(52.0, 0.65 * prob_pct + 0.25 * raw_strength + margin_bonus)), 1)
        except Exception as e:
            print("Visual classifier inference error:", e)

    # 3. Vision inspection via Moondream (optional local enhancement)
    vision_description = ""
    try:
        vision_prompt = (
            "Examine this agricultural plant leaf closely. "
            "Describe the leaf shape (serrated, lobed, or smooth), its colors, and all spots, dots, or disease symptoms visible on it."
        )
        vision_description = query_ollama(
            model=VISION_MODEL,
            prompt=vision_prompt,
            images=[processed_b64],
            format_json=False,
            timeout=5
        )
        vision_description = vision_description.replace("!!!IMAGE!!!", "").strip()

        if len(vision_description) < 25 or vision_description.startswith(("1. Yes", "Yes", "1. No", "No")):
            vision_prompt2 = "Describe the spots, colors, holes, and leaf disease symptoms visible in this image."
            v2 = query_ollama(model=VISION_MODEL, prompt=vision_prompt2, images=[processed_b64], format_json=False, timeout=5)
            if len(v2) > 20:
                vision_description = v2.replace("!!!IMAGE!!!", "").strip()
    except Exception as e:
        print("Moondream vision inspection skipped/failed:", e)
        vision_description = req.farmer_notes or ""

    # 4. Master PlantVillage Agronomic Diagnostic Engine
    match_result = diagnose_with_master_engine(
        vision_description=vision_description,
        pixel_stats=pixel_stats,
        crop_hint=req.crop_hint,
        farmer_notes=req.farmer_notes,
        neural_class=neural_pred_class,
        neural_sim=neural_confidence
    )
    best = match_result["best_match"]
    top_candidates = match_result["top_candidates"]

    # 5. Construct Structured Diagnosis from Ground Truth Dataset
    if neural_confidence > 0:
        final_conf = neural_confidence + (3.0 if req.crop_hint else 0.0)
        final_conf = min(99, max(52, int(round(final_conf))))
    else:
        scores = match_result.get("scores", [])
        margin = (scores[0][0] - scores[1][0]) if len(scores) > 1 else 20
        final_conf = min(94, max(62, 65 + int(margin * 0.5)))
    confidence_val = f"{final_conf}%"
    summary_text = (
        f"Identified {best['crop']} foliage with {best['lesion_pattern'].lower()} "
        f"and {best['color_signature'].lower()}."
    )
    if best["is_healthy"]:
        summary_text = f"Vibrant {best['crop']} foliage with healthy green chlorophyll tissue and no active fungal or bacterial lesions."

    diagnosis_json = {
        "crop": best["crop"],
        "condition": best["disease"],
        "is_healthy": best["is_healthy"],
        "confidence": confidence_val,
        "severity": best["severity"],
        "visual_summary": summary_text,
        "symptoms": [
            f"Color Spectrum: {best['color_signature']}",
            f"Lesion Pattern: {best['lesion_pattern']}",
            f"Leaf Morphology: {best['leaf_morphology']}"
        ],
        "organic_treatment": best["organic_treatment"],
        "chemical_treatment": best["chemical_treatment"],
        "outbreak_risk": best["outbreak_risk"],
        "neighbor_alert": best["neighbor_alert"],
        "hindi_summary": best["hindi_summary"]
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
    diagnosis_json["neural_class"] = neural_pred_class
    diagnosis_json["neural_similarity"] = neural_confidence

    return diagnosis_json

# Mount static files and reference images if present
if os.path.exists(REF_IMG_DIR):
    app.mount("/static/reference_images", StaticFiles(directory=REF_IMG_DIR), name="ref_images")

static_path = os.path.join(BASE_DIR, "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
