"""
Stage 1 of the leaf-disease pipeline.

Scans every dataset zip in the project directory, de-duplicates images that
appear in more than one archive, splits them into train/val/test *by image
identity* (so the same photo can never be in both halves), and extracts
MobileNetV3-Small feature embeddings for a few augmented views of each image.

Output: data/embeddings.npz  (+ data/dataset_index.json for inspection)

Why this exists: the previous trainer averaged frozen embeddings per class and
called that "training". That is nearest-centroid lookup, not learning. Here we
cache features once, then train a real classifier head on top of them in
train_classifier.py.
"""

import io
import hashlib
import json
import os
import zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as T
from PIL import Image

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
ZIP_GLOBS = ["archive.zip", "Dataset.zip"]          # auto-discovered below
ZIP_NAMES = ["archive.zip", "Dataset.zip"]
LOCAL_IMAGES = [
    # (canonical class, path) -- single reference photos that live in the repo
    ("Strawberry___Leaf_spot", "strawberry-leaf-spot-widespread-fungal-disease-caused-by-mycosphaerella-fragariae-fungus.webp"),
    ("Strawberry___Leaf_spot", "data/strawberry_leaf.jpg"),
    ("Soybean___Brown_spot", "soybean-disease-soybean-brown-spot-brown-spot-soybean-soybeans-leaf-disease-brown-spot-leaf.webp"),
    ("Coffee___Leaf_rust", "Hemileia_vastatrix_-_coffee_leaf_rust.webp"),
    ("Tomato___Late_blight", "late-blight-of-tomato-5.webp"),
    ("Beech___Leaf_disease", "Litylenchus_crenatae_161966913.jpg"),
]

OUT_NPZ = None      # set below, once BACKBONE_NAME is known
OUT_INDEX = None

IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")

# Folder name -> canonical class id used by plantvillage_engine.py.
# Unmapped folders are auto-slugged instead of silently dropped.
FOLDER_TO_CANONICAL = {
    "Pepper__bell___Bacterial_spot": "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy": "Pepper__bell___healthy",
    "Potato___Early_blight": "Potato___Early_blight",
    "Potato___Late_blight": "Potato___Late_blight",
    "Potato___healthy": "Potato___healthy",
    "Tomato_Bacterial_spot": "Tomato___Bacterial_spot",
    "Tomato_Early_blight": "Tomato___Early_blight",
    "Tomato_Late_blight": "Tomato___Late_blight",
    "Tomato_Leaf_Mold": "Tomato___Leaf_Mold",
    "Tomato_Septoria_leaf_spot": "Tomato___Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Tomato___Spider_mites_Two-spotted_spider_mite",
    "Tomato__Target_Spot": "Tomato___Target_Spot",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato__Tomato_mosaic_virus": "Tomato___Tomato_mosaic_virus",
    "Tomato_healthy": "Tomato___healthy",
}

BATCH = 64
SEED = 1337

# Backbone is selectable so a stronger frozen feature extractor can be tried
# without editing code. convnext_tiny linear-probes far better than
# mobilenet_v3_small on this dataset.
BACKBONES = {
    "mobilenet_v3_small": (models.mobilenet_v3_small, models.MobileNet_V3_Small_Weights.DEFAULT, 576),
    "efficientnet_b0": (models.efficientnet_b0, models.EfficientNet_B0_Weights.DEFAULT, 1280),
    "convnext_tiny": (models.convnext_tiny, models.ConvNeXt_Tiny_Weights.DEFAULT, 768),
}

# NUM_VIEWS: view 0 is the deterministic clean view (used for val/test).
NUM_VIEWS_TRAIN = int(os.environ.get("NUM_VIEWS", "3"))
BACKBONE_NAME = os.environ.get("BACKBONE", "convnext_tiny")
_TAG = BACKBONE_NAME.replace(".", "_")
OUT_NPZ = f"data/embeddings_{_TAG}.npz"
OUT_INDEX = f"data/dataset_index_{_TAG}.json"

torch.manual_seed(SEED)
np.random.seed(SEED)
torch.set_num_threads(max(2, (os.cpu_count() or 4) - 1))


# ----------------------------------------------------------------------------
# Image loading helpers
# ----------------------------------------------------------------------------
def _load_from_zip(zf, member):
    """Decode a JPEG straight out of a zip, using draft() for fast DCT scaling."""
    raw = zf.read(member)
    img = Image.open(io.BytesIO(raw))
    img.draft("RGB", (224, 224))  # huge speedup on large JPEGs
    return img.convert("RGB")


def _load_local(path):
    img = Image.open(path)
    img.draft("RGB", (224, 224))
    return img.convert("RGB")


def _views(img, rng):
    """Return NUM_VIEWS_TRAIN tensors: one deterministic + the rest augmented."""
    clean = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])(img)

    w, h = img.size
    out = [clean]
    for _ in range(NUM_VIEWS_TRAIN - 1):
        # Random-resized-crop mimics the framing variance of a phone camera.
        scale = rng.uniform(0.62, 1.0)
        cw, ch = int(w * scale), int(h * scale)
        left = int(rng.integers(0, max(1, w - cw + 1)))
        top = int(rng.integers(0, max(1, h - ch + 1)))
        crop = img.crop((left, top, left + cw, top + ch))
        aug = T.Compose([
            T.Resize((224, 224)),
            T.RandomHorizontalFlip(p=1.0) if rng.random() < 0.5 else T.Lambda(lambda x: x),
            T.ColorJitter(brightness=0.22, contrast=0.22, saturation=0.18, hue=0.03),
            T.RandomRotation(degrees=12),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])(crop)
        out.append(aug)
    return out


# ----------------------------------------------------------------------------
# Index building
# ----------------------------------------------------------------------------
def discover():
    """Build a de-duplicated list of (canonical_class, source, member, key)."""
    seen_keys = set()
    records = []          # (canonical, zipname, member)
    per_class = defaultdict(int)
    duplicates = 0

    for zname in ZIP_NAMES:
        if not os.path.exists(zname):
            continue
        with zipfile.ZipFile(zname) as z:
            for member in z.namelist():
                if not member.lower().endswith(IMG_EXTS):
                    continue
                parts = [p for p in member.split("/") if p]
                folder = None
                for part in parts[:-1]:
                    if part in FOLDER_TO_CANONICAL:
                        folder = part
                        break
                    # Auto-map any other "<Crop>___<Condition>" folder so a newly
                    # dropped-in dataset is picked up instead of ignored.
                    if "___" in part:
                        folder = part
                        break
                if folder is None:
                    continue

                canonical = FOLDER_TO_CANONICAL.get(folder, _slug(folder))
                basename = os.path.basename(member)
                key = canonical + "|" + basename
                if key in seen_keys:
                    duplicates += 1
                    continue
                seen_keys.add(key)
                records.append((canonical, zname, member))
                per_class[canonical] += 1

    for canonical, path in LOCAL_IMAGES:
        if os.path.exists(path):
            key = canonical + "|local|" + os.path.basename(path)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            records.append((canonical, "__local__", path))
            per_class[canonical] += 1

    print(f"[index] {len(records)} unique images across {len(per_class)} classes "
          f"({duplicates} duplicate copies skipped)")
    for c, n in sorted(per_class.items(), key=lambda x: -x[1]):
        flag = "  <-- very low data" if n < 40 else ""
        print(f"        {c:<48} {n:>6}{flag}")
    return records, duplicates


def _slug(folder):
    """'Corn___Common_rust' -> 'Corn___Common_rust' with single separators."""
    crop, _, cond = folder.partition("___")
    cond = cond or "unknown"
    crop = crop.replace("_", " ").strip().title().replace(" ", "_")
    cond = cond.strip().replace(" ", "_")
    return f"{crop}___{cond}"


def split_of(key, canonical):
    """
    Deterministic split by image identity. Everything with the same basename
    lands in the same split, so near-duplicate frames cannot leak.

    Uses md5 rather than hash(): Python salts str hashing per process, so
    hash() would give a different split on every run and train/val/test would
    silently overlap between scripts.
    """
    h = int(hashlib.md5((canonical + "|" + key).encode()).hexdigest()[:8], 16) % 100
    if h < 75:
        return "train"
    if h < 87:
        return "val"
    return "test"


# ----------------------------------------------------------------------------
# Embedding extraction
# ----------------------------------------------------------------------------
def build():
    os.makedirs("data", exist_ok=True)
    records, duplicates = discover()
    if not records:
        raise SystemExit("No images found. Put archive.zip / Dataset.zip next to this script.")

    classes = sorted({r[0] for r in records})
    cls_to_idx = {c: i for i, c in enumerate(classes)}

    # Group records by zip so we can open each archive once.
    by_zip = defaultdict(list)
    for i, (canonical, zname, member) in enumerate(records):
        by_zip[zname].append((i, canonical, member))

    backbone_fn, backbone_w, feat_dim = BACKBONES[BACKBONE_NAME]
    backbone = backbone_fn(weights=backbone_w)
    backbone.eval()
    extractor = torch.nn.Sequential(
        backbone.features, torch.nn.AdaptiveAvgPool2d(1), torch.nn.Flatten())
    for p in extractor.parameters():
        p.requires_grad_(False)

    n = len(records)
    embeds = np.zeros((n, NUM_VIEWS_TRAIN, feat_dim), dtype=np.float32)
    labels = np.array([cls_to_idx[c] for c, _, _ in records], dtype=np.int64)
    splits = np.array([split_of(os.path.basename(m), c) for c, _, m in records])
    done = np.zeros(n, dtype=bool)

    print(f"\n[extract] backbone={BACKBONE_NAME} dim={feat_dim} views={NUM_VIEWS_TRAIN}")
    print(f"[extract] {n} images x {NUM_VIEWS_TRAIN} views = {n * NUM_VIEWS_TRAIN} forward passes")

    def run_batch(items, imgs):
        """items: (record_index, view_index) list -> fill embeds."""
        if not imgs:
            return
        batch = torch.stack(imgs)
        with torch.no_grad():
            f = extractor(batch)
            f = torch.nn.functional.normalize(f, p=2, dim=1)
        for (ri, vi), vec in zip(items, f.numpy()):
            embeds[ri, vi] = vec
            done[ri] = True

    processed = 0
    for zname, entries in by_zip.items():
        # Reading a ZipFile is NOT thread-safe, so raw bytes are pulled
        # sequentially (zlib decompress is C and fast), and only the JPEG
        # decode + augmentation run on the thread pool.
        zf = None if zname == "__local__" else zipfile.ZipFile(zname)

        def deliver(ent, _zf=zf):
            i, canonical, member = ent
            raw = open(member, "rb").read() if _zf is None else _zf.read(member)
            return i, raw

        def render(ent, _zf=zf):
            i, raw = ent
            try:
                img = Image.open(io.BytesIO(raw))
                img.draft("RGB", (224, 224))
                img = img.convert("RGB")
                rng = np.random.default_rng((SEED + i) % (2 ** 32))
                return i, _views(img, rng)
            except Exception as e:
                print(f"\n[extract] decode failed for image {i}: {e}")
                return i, None

        with ThreadPoolExecutor(max_workers=8) as pool:
            pending_items, pending_imgs = [], []
            for chunk_start in range(0, len(entries), 128):
                chunk = entries[chunk_start:chunk_start + 128]
                # Sequential safe read, then parallel render.
                raw_chunk = [deliver(e) for e in chunk]
                for ri, views in pool.map(render, raw_chunk):
                    if views is None:
                        continue
                    for vi, t in enumerate(views):
                        pending_items.append((ri, vi))
                        pending_imgs.append(t)
                    processed += 1
                    while len(pending_imgs) >= BATCH:
                        run_batch(pending_items[:BATCH], pending_imgs[:BATCH])
                        pending_items = pending_items[BATCH:]
                        pending_imgs = pending_imgs[BATCH:]
                print(f"[extract]   {zname}: {processed}/{n} images", end="\r", flush=True)
            run_batch(pending_items, pending_imgs)

        if zf is not None:
            zf.close()

    missing = int((~done).sum())
    if missing:
        print(f"\n[extract] WARNING: {missing} images failed to decode and were zero-filled")

    np.savez_compressed(
        OUT_NPZ,
        embeds=embeds,
        labels=labels,
        splits=splits,
        classes=np.array(classes),
    )
    with open(OUT_INDEX, "w", encoding="utf-8") as f:
        json.dump({
            "classes": classes,
            "counts": {c: int((labels == cls_to_idx[c]).sum()) for c in classes},
            "splits": {s: int((splits == s).sum()) for s in ["train", "val", "test"]},
            "duplicates_skipped": duplicates,
            "total_unique_images": n,
            "num_views": NUM_VIEWS_TRAIN,
            "backbone": BACKBONE_NAME,
            "feature_dim": feat_dim,
        }, f, indent=2)

    print(f"\n[extract] saved {OUT_NPZ}  shape={embeds.shape}")
    print(f"[extract] split sizes: "
          f"train={int((splits=='train').sum())} "
          f"val={int((splits=='val').sum())} "
          f"test={int((splits=='test').sum())}")
    print("[extract] NOTE: val/test embeddings are the clean view (index 0).")


if __name__ == "__main__":
    build()
