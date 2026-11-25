"""
Downloads 70 real color images per missing PlantVillage class (the 23 classes not in
archive.zip/Dataset.zip) directly from spMohanty/PlantVillage-Dataset on GitHub into
data/plantvillage_extra/<canonical_class>/ using parallel threads.
"""

import os
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

OUT_ROOT = "data/plantvillage_extra"
PER_CLASS = 70

GITHUB_TO_CANONICAL = {
    "Apple___Apple_scab": "Apple___Apple_scab",
    "Apple___Black_rot": "Apple___Black_rot",
    "Apple___Cedar_apple_rust": "Apple___Cedar_apple_rust",
    "Apple___healthy": "Apple___healthy",
    "Blueberry___healthy": "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew": "Cherry___Powdery_mildew",
    "Cherry_(including_sour)___healthy": "Cherry___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Corn___Cercospora_leaf_spot_Gray_leaf_spot",
    "Corn_(maize)___Common_rust_": "Corn___Common_rust",
    "Corn_(maize)___Northern_Leaf_Blight": "Corn___Northern_Leaf_Blight",
    "Corn_(maize)___healthy": "Corn___healthy",
    "Grape___Black_rot": "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)": "Grape___Esca_Black_Measles",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Grape___Leaf_blight_Isariopsis_Leaf_Spot",
    "Grape___healthy": "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)": "Orange___Haunglongbing_Citrus_greening",
    "Peach___Bacterial_spot": "Peach___Bacterial_spot",
    "Peach___healthy": "Peach___healthy",
    "Raspberry___healthy": "Raspberry___healthy",
    "Soybean___healthy": "Soybean___healthy",
    "Squash___Powdery_mildew": "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch": "Strawberry___Leaf_scorch",
    "Strawberry___healthy": "Strawberry___healthy",
}


def download_one(url: str, dst: str) -> bool:
    if os.path.exists(dst) and os.path.getsize(dst) > 500:
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "LeafGuard-Trainer"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
        if len(data) > 500:
            with open(dst, "wb") as f:
                f.write(data)
            return True
    except Exception:
        pass
    return False


def main():
    os.makedirs(OUT_ROOT, exist_ok=True)
    tasks = []
    for gh_folder, canonical in GITHUB_TO_CANONICAL.items():
        cls_dir = os.path.join(OUT_ROOT, canonical)
        os.makedirs(cls_dir, exist_ok=True)
        existing = [f for f in os.listdir(cls_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if len(existing) >= PER_CLASS:
            print(f"[skip] {canonical}: already has {len(existing)} images")
            continue

        api_url = (
            "https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/"
            + urllib.parse.quote(gh_folder)
        )
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "LeafGuard-Trainer"})
            with urllib.request.urlopen(req, timeout=15) as r:
                items = json.loads(r.read().decode("utf-8"))
            if not isinstance(items, list):
                print(f"[warn] {gh_folder}: unexpected API response")
                continue
            step = max(1, len(items) // PER_CLASS)
            picks = items[::step][:PER_CLASS]
            for idx, item in enumerate(picks):
                dl = item.get("download_url")
                if not dl:
                    continue
                ext = os.path.splitext(item["name"])[1] or ".jpg"
                dst = os.path.join(cls_dir, f"{idx:03d}{ext}")
                tasks.append((dl, dst))
            print(f"[queued] {canonical:<46} -> {len(picks)} images")
        except Exception as e:
            print(f"[err] listing {gh_folder}: {e}")

    print(f"\nDownloading {len(tasks)} images across {len(GITHUB_TO_CANONICAL)} classes...")
    ok = 0
    with ThreadPoolExecutor(max_workers=14) as pool:
        futs = [pool.submit(download_one, u, d) for u, d in tasks]
        for fut in as_completed(futs):
            if fut.result():
                ok += 1
    print(f"Downloaded/verified {ok}/{len(tasks)} images into {OUT_ROOT}/")


if __name__ == "__main__":
    main()
