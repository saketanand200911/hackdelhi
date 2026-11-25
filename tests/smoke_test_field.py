"""Tests the live API the way a user actually uses it: field-like photos."""
import base64
import io
import json
import sys
import urllib.request
import zipfile

import numpy as np
from PIL import Image

from field_sim import simulate_field

URL = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8080/api/diagnose")


def post(img, crop_hint=""):
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=88)
    body = json.dumps({
        "image_base64": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(),
        "crop_hint": crop_hint,
        "farmer_notes": "",
    }).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode())


def leaf(wanted, skip=5):
    with zipfile.ZipFile("archive.zip") as z:
        hits = [n for n in z.namelist() if wanted in n and n.lower().endswith(".jpg")]
        return Image.open(io.BytesIO(z.read(hits[skip]))).convert("RGB")


CASES = [
    ("Tomato_Late_blight", "Tomato"),
    ("Tomato_Early_blight", "Tomato"),
    ("Potato___Early_blight", "Potato"),
    ("Pepper__bell___Bacterial_spot", "Pepper"),
    ("Tomato_healthy", "Tomato"),
]

rng = np.random.default_rng(42)
print("FIELD-LIKE PHOTOS (leaf on cluttered background, phone lighting)")
print("-" * 74)
for cls, hint in CASES:
    for k in range(2):
        img = simulate_field(leaf(cls, 5 + k), rng)
        d = post(img, crop_hint=hint)
        status = "DETECTED" if d.get("detected") else "NOT DETECTED"
        print(f"{cls:<32} hint={hint:<8} -> {status:<13} "
              f"{(d.get('condition') or '-')[:40]:<40} {d.get('confidence')}")

print()
print("NON-LEAF INPUTS")
print("-" * 74)
for label, img in [("rotten tomatoes", Image.open("rotten-tomato-spoiled-tomatoes-free-photo.jpg")),
                   ("plain grey", Image.new("RGB", (400, 400), (120, 120, 120)))]:
    d = post(img)
    print(f"{label:<32} -> {'DETECTED' if d.get('detected') else 'NOT DETECTED':<13} "
          f"{(d.get('condition') or '-')[:46]}")
