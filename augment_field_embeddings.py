"""
Generates clean + field-simulated + leaf-cropped MobileNetV3-Small embeddings
for:
  1. `train` split of data/embeddings_mobilenet_v3_small.npz (15 Solanaceae classes)
  2. All 23 classes in data/plantvillage_extra/ (deterministic 75% train / 25% val split)
  3. Low-count local classes (Beech, Coffee, Soybean Brown Spot, Strawberry Leaf Spot)
Saves to data/field_aug_embeddings.npz.
"""

import io
import os
import zipfile
from collections import defaultdict

import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as T
from PIL import Image, ImageOps

import build_embeddings as B
from field_sim import simulate_field
from leaf_crop import crop_to_leaf

EMB_NPZ = "data/embeddings_mobilenet_v3_small.npz"
EXTRA_DIR = "data/plantvillage_extra"
OUT_NPZ = "data/field_aug_embeddings.npz"
MAX_PER_CLASS = 150
SEED = 42


def main():
    d = np.load(EMB_NPZ, allow_pickle=True)
    splits, labels = d["splits"], d["labels"]
    classes = [str(c) for c in d["classes"]]
    cls_to_id = {c: i for i, c in enumerate(classes)}
    records, _ = B.discover()

    by_cls = defaultdict(list)
    for (canonical, zname, member), s, l in zip(records, splits, labels):
        if s == "train" and zname != "__local__":
            by_cls[int(l)].append((zname, member))

    rng = np.random.default_rng(SEED)
    picked = []
    for l, items in sorted(by_cls.items()):
        if len(items) > MAX_PER_CLASS:
            idx = rng.choice(len(items), size=MAX_PER_CLASS, replace=False)
            items = [items[i] for i in idx]
        for zname, member in items:
            picked.append((l, zname, member))

    extra_train, extra_val = [], []
    if os.path.isdir(EXTRA_DIR):
        for cls_name in sorted(os.listdir(EXTRA_DIR)):
            cls_path = os.path.join(EXTRA_DIR, cls_name)
            if not os.path.isdir(cls_path):
                continue
            files = sorted([
                os.path.join(cls_path, f)
                for f in os.listdir(cls_path)
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
            ])
            if not files:
                continue
            if cls_name not in cls_to_id:
                cls_to_id[cls_name] = len(classes)
                classes.append(cls_name)
            cid = cls_to_id[cls_name]
            n_val = max(5, int(len(files) * 0.25))
            for fp in files[:n_val]:
                extra_val.append((cid, fp))
            for fp in files[n_val:]:
                extra_train.append((cid, fp))

    print(f"[field_aug] 15 zip classes={len(picked)} imgs | 23 extra classes train={len(extra_train)} val={len(extra_val)} | total classes={len(classes)}")

    b = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    b.eval()
    extractor = torch.nn.Sequential(
        b.features, torch.nn.AdaptiveAvgPool2d(1), torch.nn.Flatten()
    )
    transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    def embed_batch(imgs_list):
        out = []
        for i in range(0, len(imgs_list), 64):
            chunk = imgs_list[i:i + 64]
            t = torch.stack([transform(im) for im in chunk])
            with torch.no_grad():
                f = torch.nn.functional.normalize(extractor(t), p=2, dim=1).numpy().astype(np.float32)
            out.append(f)
        return np.concatenate(out, axis=0) if out else np.zeros((0, 576), dtype=np.float32)

    handles = {}
    zip_imgs, zip_labels = [], []
    try:
        for l, zname, member in picked:
            try:
                if zname not in handles:
                    handles[zname] = zipfile.ZipFile(zname)
                img = Image.open(io.BytesIO(handles[zname].read(member))).convert("RGB")
                zip_imgs.append(crop_to_leaf(simulate_field(img, rng)))
                zip_labels.append(l)
            except Exception:
                continue
    finally:
        for h in handles.values():
            h.close()

    ex_clean_imgs, ex_clean_labels = [], []
    ex_field_imgs, ex_field_labels = [], []
    for cid, fp in extra_train:
        try:
            img = Image.open(fp).convert("RGB")
            ex_clean_imgs.append(img)
            ex_clean_labels.append(cid)
            ex_clean_imgs.append(ImageOps.mirror(img))
            ex_clean_labels.append(cid)
            ex_field_imgs.append(crop_to_leaf(simulate_field(img, rng)))
            ex_field_labels.append(cid)
        except Exception:
            continue

    val_imgs, val_labels = [], []
    for cid, fp in extra_val:
        try:
            val_imgs.append(Image.open(fp).convert("RGB"))
            val_labels.append(cid)
        except Exception:
            continue

    local_list = list(B.LOCAL_IMAGES)
    if ("Beech___Leaf_disease", "Litylenchus_crenatae_161966913.jpg") not in local_list:
        local_list.append(("Beech___Leaf_disease", "Litylenchus_crenatae_161966913.jpg"))
    for cls_name, lpath in local_list:
        if cls_name == "Tomato___Late_blight" or not os.path.exists(lpath):
            continue
        if cls_name not in cls_to_id:
            cls_to_id[cls_name] = len(classes)
            classes.append(cls_name)
        li = cls_to_id[cls_name]
        base_img = Image.open(lpath).convert("RGB")
        for _ in range(15):
            zip_imgs.append(crop_to_leaf(base_img.rotate(float(rng.uniform(-18, 18)))))
            zip_labels.append(li)
            zip_imgs.append(crop_to_leaf(simulate_field(base_img, rng)))
            zip_labels.append(li)

    X_field = np.concatenate([embed_batch(zip_imgs), embed_batch(ex_field_imgs)], axis=0)
    y_field = np.array(zip_labels + ex_field_labels, dtype=np.int64)
    X_clean_extra = embed_batch(ex_clean_imgs)
    y_clean_extra = np.array(ex_clean_labels, dtype=np.int64)
    X_val_extra = embed_batch(val_imgs)
    y_val_extra = np.array(val_labels, dtype=np.int64)

    np.savez(
        OUT_NPZ,
        X=X_field,
        y=y_field,
        X_clean_extra=X_clean_extra,
        y_clean_extra=y_clean_extra,
        X_val_extra=X_val_extra,
        y_val_extra=y_val_extra,
        classes=np.array(classes),
    )
    print(f"[field_aug] Saved field={len(X_field)}, clean_extra={len(X_clean_extra)}, val_extra={len(X_val_extra)} across {len(classes)} classes to {OUT_NPZ}")


if __name__ == "__main__":
    main()
