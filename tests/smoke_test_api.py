"""Quick live-API smoke test: posts real leaf photos and a non-leaf photo."""
import base64
import io
import json
import sys
import urllib.request
import zipfile

from PIL import Image

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8099/api/diagnose"


def post(img, crop_hint=""):
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=88)
    b64 = base64.b64encode(buf.getvalue()).decode()
    body = json.dumps({"image_base64": "data:image/jpeg;base64," + b64,
                       "crop_hint": crop_hint, "farmer_notes": ""}).encode()
    req = urllib.request.Request(URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def leaf_from_zip(zname, wanted, skip=0):
    with zipfile.ZipFile(zname) as z:
        hits = [n for n in z.namelist() if wanted in n and n.lower().endswith(".jpg")]
        return Image.open(io.BytesIO(z.read(hits[skip]))).convert("RGB")


CASES = [
    ("Tomato_Late_blight", leaf_from_zip("archive.zip", "Tomato_Late_blight", 5)),
    ("Tomato___healthy", leaf_from_zip("archive.zip", "Tomato_healthy", 5)),
    ("Potato___Early_blight", leaf_from_zip("archive.zip", "Potato___Early_blight", 5)),
    ("Pepper__bell___Bacterial_spot", leaf_from_zip("archive.zip", "Pepper__bell___Bacterial_spot", 5)),
    ("tomato fruit (not a leaf)", Image.open("rotten-tomato-spoiled-tomatoes-free-photo.jpg")),
    ("plain grey", Image.new("RGB", (400, 400), (120, 120, 120))),
]

for label, img in CASES:
    d = post(img)
    print(f"{label:<32} -> detected={str(d.get('detected')):<5} "
          f"{(d.get('crop') or '-')} / {(d.get('condition') or '-')[:42]:<42} "
          f"conf={d.get('confidence')}")
    if d.get("top_k"):
        for k in d["top_k"][:3]:
            print(f"{'':>36}    {k['crop']} {k['condition']} {k['confidence']}%  cos={k['cosine']}")
    print()

d = post(leaf_from_zip("archive.zip", "Tomato_Early_blight", 5), crop_hint="Potato")
print("crop_hint='Potato' forced ->", d.get("crop"), "/", d.get("condition"), d.get("confidence"))
