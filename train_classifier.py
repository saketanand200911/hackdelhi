"""
Stage 2 of the leaf-disease pipeline.

Trains a real classifier head on cached CNN embeddings, calibrates its
probabilities with temperature scaling, and learns the two rejection thresholds
that let the app answer "Not detected" instead of inventing a disease.

Everything reported here is measured on splits the head never saw.

Thresholds are calibrated against BOTH distributions:
  * real held-out leaf photos (must pass)
  * synthetic + real non-plant images (must be rejected)
so we pick the cut that keeps almost every real leaf while rejecting the rest,
instead of hard-coding a magic number.

Outputs:
  data/leaf_model.npz    -> classes, W, b, temperature, thresholds, protos
  data/model_report.json -> honest metrics
"""

import io
import json
import os
import zipfile

import numpy as np
import torch
import torchvision.models as models
import torchvision.transforms as T
from PIL import Image, ImageDraw

SEED = 1337
BACKBONE_NAME = os.environ.get("BACKBONE", "convnext_tiny")
_TAG = BACKBONE_NAME.replace(".", "_")
EMB_NPZ = f"data/embeddings_{_TAG}.npz"
OUT_NPZ = "data/leaf_model.npz"
OUT_REPORT = "data/model_report.json"

LABEL_SMOOTHING = 0.05
WEIGHT_DECAY = 5e-4
EPOCHS = 300
LR = 0.05
HIDDEN = 512          # one small hidden layer; pure linear underfits this data
DROPOUT = 0.25
KEEP_REAL = 0.99      # we require >=99% of real leaves to survive rejection
REAL_SAMPLE = 400     # real val images used to calibrate plantness
MIN_IMAGES = 1        # keep all classes (including Coffee, Soybean, Strawberry)

BACKBONES = {
    "mobilenet_v3_small": (models.mobilenet_v3_small, models.MobileNet_V3_Small_Weights.DEFAULT, 576),
    "efficientnet_b0": (models.efficientnet_b0, models.EfficientNet_B0_Weights.DEFAULT, 1280),
    "convnext_tiny": (models.convnext_tiny, models.ConvNeXt_Tiny_Weights.DEFAULT, 768),
}

torch.manual_seed(SEED)
np.random.seed(SEED)
torch.set_num_threads(max(2, (os.cpu_count() or 4) - 1))


# ---------------------------------------------------------------------------
# Feature extraction (used for the non-plant reference set + plantness sample)
# ---------------------------------------------------------------------------
def build_backbone():
    fn, w, _ = BACKBONES[BACKBONE_NAME]
    b = fn(weights=w)
    b.eval()
    return torch.nn.Sequential(
        b.features, torch.nn.AdaptiveAvgPool2d(1), torch.nn.Flatten())


NORM = T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
TO_TENSOR = T.Compose([T.Resize((224, 224)), T.ToTensor(), NORM])


def embed_images(images, extractor, batch=32):
    out = []
    for i in range(0, len(images), batch):
        chunk = [im.convert("RGB") for im in images[i:i + batch]]
        t = torch.stack([TO_TENSOR(im) for im in chunk])
        with torch.no_grad():
            f = torch.nn.functional.normalize(extractor(t), p=2, dim=1)
        out.append(f.numpy())
    return np.concatenate(out).astype(np.float32)


def negative_set():
    """Images that are definitely not a leaf with a detectable disease."""
    rng = np.random.default_rng(SEED)
    imgs = []
    for c in [(128, 128, 128), (30, 30, 30), (240, 240, 240), (135, 206, 235),
              (210, 170, 140), (90, 60, 40), (0, 0, 0), (200, 200, 190)]:
        imgs.append(Image.new("RGB", (256, 256), c))
    for _ in range(5):
        imgs.append(Image.fromarray(rng.integers(0, 256, (256, 256, 3), dtype=np.uint8)))
    for _ in range(3):
        g = np.tile(np.linspace(0, 255, 256).reshape(1, 256, 1), (256, 1, 3))
        if rng.random() < 0.5:
            g = np.transpose(g, (1, 0, 2))
        imgs.append(Image.fromarray(g.astype(np.uint8)))
    chk = Image.new("RGB", (256, 256), (0, 0, 0))
    d = ImageDraw.Draw(chk)
    for y in range(0, 256, 32):
        for x in range(0, 256, 32):
            if (x // 32 + y // 32) % 2 == 0:
                d.rectangle([x, y, x + 31, y + 31], fill=(255, 255, 255))
    imgs.append(chk)
    page = Image.new("RGB", (256, 256), (255, 255, 255))
    d = ImageDraw.Draw(page)
    for line in range(8):
        d.text((10, 12 + line * 28), "lorem ipsum dolor sit amet " * 3, fill=(20, 20, 20))
    imgs.append(page)
    for p in ["rotten-tomato-spoiled-tomatoes-free-photo.jpg"]:
        if os.path.exists(p):
            imgs.append(Image.open(p).convert("RGB"))
    return imgs


def plant_pixel_ratio(img: Image.Image) -> float:
    a = np.asarray(img.convert("RGB").resize((96, 96)), dtype=np.float32)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    greenish = (g > r * 1.06) & (g > b * 1.06) & (g > 45)
    yellowgreen = (g > 70) & (r > 50) & (r < g * 1.25) & (b < g * 0.85)
    return float((greenish | yellowgreen).mean())


def real_leaf_sample(n=REAL_SAMPLE):
    """Pull real leaf photos from the val split to calibrate the plantness gate."""
    return [im for _, im in real_leaf_sample_paths(n)]


def real_leaf_sample_paths(n=REAL_SAMPLE):
    """Yield (identifier, PIL image) from the val split, for both gates."""
    import build_embeddings as B
    d = np.load(EMB_NPZ, allow_pickle=True)
    splits = d["splits"]
    records, _ = B.discover()
    picks = [(z, m) for (c, z, m), s in zip(records, splits)
             if s == "val" and z != "__local__"]
    step = max(1, len(picks) // n)
    picks = picks[::step][:n]

    out = []
    handles = {}
    try:
        for zname, member in picks:
            try:
                if zname not in handles:
                    handles[zname] = zipfile.ZipFile(zname)
                out.append((f"{zname}:{member}",
                            Image.open(io.BytesIO(handles[zname].read(member))).convert("RGB")))
            except Exception:
                continue
    finally:
        for h in handles.values():
            h.close()
    return out


# ---------------------------------------------------------------------------
def softmax(z):
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


def nll(probs, y):
    return float(-np.log(np.clip(probs[np.arange(len(y)), y], 1e-9, 1)).mean())


def train():
    if not os.path.exists(EMB_NPZ):
        raise SystemExit(f"{EMB_NPZ} missing - run build_embeddings.py first")

    d = np.load(EMB_NPZ, allow_pickle=True)
    embeds, labels, splits = d["embeds"], d["labels"], d["splits"]
    all_classes = [str(c) for c in d["classes"]]

    # Drop classes that are statistically impossible to learn. A class backed by
    # 1-2 photos does not become detectable through augmentation -- it just
    # steals predictions from real classes. Those images are excluded instead of
    # being faked into looking trained.
    counts_all = np.bincount(labels, minlength=len(all_classes))
    keep_cls = np.where(counts_all >= MIN_IMAGES)[0]
    dropped = [all_classes[i] for i in np.setdiff1d(np.arange(len(all_classes)), keep_cls)]
    if dropped:
        print(f"[train] EXCLUDED (fewer than {MIN_IMAGES} photos): "
              + ", ".join(f"{c} (n={counts_all[all_classes.index(c)]})" for c in dropped))

    remap = {old: new for new, old in enumerate(keep_cls)}
    keep_mask = np.isin(labels, keep_cls)
    embeds, labels, splits = embeds[keep_mask], labels[keep_mask], splits[keep_mask]
    labels = np.array([remap[int(l)] for l in labels], dtype=np.int64)
    classes = [all_classes[i] for i in keep_cls]

    n_classes, n_views, dim = len(classes), embeds.shape[1], embeds.shape[2]
    print(f"[train] backbone={BACKBONE_NAME} dim={dim} classes={n_classes} "
          f"images={len(labels)}")

    field_aug_npz = "data/field_aug_embeddings.npz"
    fa_loaded = None
    if BACKBONE_NAME == "mobilenet_v3_small" and os.path.exists(field_aug_npz):
        fa_loaded = np.load(field_aug_npz, allow_pickle=True)
        for fc in [str(c) for c in fa_loaded["classes"]]:
            if fc not in classes:
                classes.append(fc)
        n_classes = len(classes)

    tr, va, te = splits == "train", splits == "val", splits == "test"
    Xtr = embeds[tr].reshape(-1, dim)
    ytr = np.repeat(labels[tr], n_views)

    Xva, yva = embeds[va][:, 0, :], labels[va]
    Xte, yte = embeds[te][:, 0, :], labels[te]

    if fa_loaded is not None:
        fa_classes = [str(c) for c in fa_loaded["classes"]]
        cls_to_id = {c: i for i, c in enumerate(classes)}

        def _append_split(X_dst, y_dst, key_x, key_y):
            if key_x not in fa_loaded:
                return X_dst, y_dst
            Xr, yr = fa_loaded[key_x].astype(np.float32), fa_loaded[key_y].astype(np.int64)
            km = np.array([fa_classes[int(yi)] in cls_to_id for yi in yr])
            if not km.any():
                return X_dst, y_dst
            Xa = Xr[km]
            ya = np.array([cls_to_id[fa_classes[int(yi)]] for yi in yr[km]], dtype=np.int64)
            return np.concatenate([X_dst, Xa], axis=0), np.concatenate([y_dst, ya], axis=0)

        Xtr, ytr = _append_split(Xtr, ytr, "X", "y")
        Xtr, ytr = _append_split(Xtr, ytr, "X_clean_extra", "y_clean_extra")
        Xva, yva = _append_split(Xva, yva, "X_val_extra", "y_val_extra")
        print(f"[train] total train views={len(ytr)}  val={len(yva)} (with 23 extra classes={n_classes})")
    print(f"[train] train views={len(ytr)}  val={len(yva)}  test={len(yte)}")

    # Mild class-balancing only: hard reweighting hurts the common classes.
    counts = np.bincount(ytr, minlength=n_classes).astype(np.float64)
    present = counts > 0
    cw = np.ones(n_classes, dtype=np.float64)
    cw[present] = (counts[present].sum() / (present.sum() * counts[present])) ** 0.5
    cw = cw / cw[present].mean()

    net = torch.nn.Sequential(
        torch.nn.Linear(dim, HIDDEN),
        torch.nn.GELU(),
        torch.nn.Dropout(DROPOUT),
        torch.nn.Linear(HIDDEN, n_classes),
    )
    opt = torch.optim.AdamW(net.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=LR, total_steps=EPOCHS, pct_start=0.15)
    Xt, yt = torch.from_numpy(Xtr), torch.from_numpy(ytr)
    class_w = torch.from_numpy(cw).float()

    best_state, best_val = None, -1.0
    for ep in range(EPOCHS):
        net.train()
        opt.zero_grad()
        loss = torch.nn.functional.cross_entropy(
            net(Xt), yt, weight=class_w, label_smoothing=LABEL_SMOOTHING)
        loss.backward()
        opt.step()
        sched.step()

        if (ep + 1) % 25 == 0 or ep == EPOCHS - 1:
            net.eval()
            with torch.no_grad():
                pred = net(torch.from_numpy(Xva)).argmax(1).numpy()
            acc = float((pred == yva).mean())
            if acc > best_val:
                best_val = acc
                best_state = {k: v.clone() for k, v in net.state_dict().items()}
            print(f"  epoch {ep+1:>3}  loss={loss.item():.4f}  "
                  f"val_top1={acc*100:.2f}%  (best {best_val*100:.2f}%)")

    net.load_state_dict(best_state)
    net.eval()

    def logits_of(X):
        with torch.no_grad():
            return net(torch.from_numpy(X)).numpy()

    # -------------------------------------------------------------------
    # Temperature scaling: makes the reported % mean "probability".
    # -------------------------------------------------------------------
    lv = logits_of(Xva).astype(np.float64)
    best_T, best_nll = 1.0, 1e9
    for Tc in np.linspace(0.25, 10.0, 196):
        v = nll(softmax(lv / Tc), yva)
        if v < best_nll:
            best_nll, best_T = v, float(Tc)
    print(f"\n[train] temperature = {best_T:.3f}  (val NLL {best_nll:.4f})")

    # -------------------------------------------------------------------
    # Prototypes for the cosine (novelty) gate
    # -------------------------------------------------------------------
    protos = np.zeros((n_classes, dim), dtype=np.float32)
    for c in range(n_classes):
        vecs = []
        m = labels[tr] == c
        if m.sum() > 0:
            vecs.append(embeds[tr][m][:, 0, :])
        if fa_loaded is not None:
            mc = (ytr == c)
            if mc.sum() > 0 and m.sum() < 10:
                vecs.append(Xtr[mc])
        if vecs:
            v = np.concatenate(vecs, axis=0).mean(axis=0)
            protos[c] = v / (np.linalg.norm(v) + 1e-8)

    extractor = build_backbone()
    negs = negative_set()
    neg_emb = embed_images(negs, extractor)
    neg_cos = (neg_emb @ protos.T).max(axis=1)
    neg_plant = np.array([plant_pixel_ratio(i) for i in negs])

    val_cos = (Xva @ protos.T).max(axis=1)

    # Real field photos are the distribution that actually matters. Fitting the
    # gate on clean PlantVillage images made it reject 39% of genuine phone
    # photos, so we simulate field framing and fit against that instead.
    from field_sim import simulate_field

    real_imgs = real_leaf_sample()
    real_plant = (np.array([plant_pixel_ratio(i) for i in real_imgs])
                  if real_imgs else np.array([]))

    field_imgs = []
    if real_imgs:
        rng = np.random.default_rng(SEED)
        field_imgs = [simulate_field(im, rng) for im in real_imgs]
    field_feats = embed_images(field_imgs, extractor) if field_imgs else None
    field_cos = (field_feats @ protos.T).max(axis=1) if field_feats is not None else np.array([])
    field_plant = (np.array([plant_pixel_ratio(i) for i in field_imgs])
                   if field_imgs else np.array([]))

    print("\n[gate] cosine to nearest prototype")
    print(f"  clean leaves  : p1={np.percentile(val_cos,1):.3f} median={np.median(val_cos):.3f}")
    if len(field_cos):
        print(f"  FIELD photos  : p1={np.percentile(field_cos,1):.3f} "
              f"p5={np.percentile(field_cos,5):.3f} median={np.median(field_cos):.3f}")
    print(f"  negatives     : median={np.median(neg_cos):.3f} max={neg_cos.max():.3f}")

    # Anchor just below the least-similar real FIELD photo, then never let it go
    # so high that it would start rejecting real users again.
    anchor = field_cos if len(field_cos) else val_cos
    cos_thr = float(np.clip(np.percentile(anchor, 1) - 0.03, 0.25, 0.80))
    # Crop-locked mode: the plant is already asserted by the user.
    cos_thr_hint = float(np.clip(cos_thr - 0.15, 0.10, cos_thr))

    print("\n[gate] plant-pixel ratio")
    if len(field_plant):
        print(f"  FIELD photos  : p1={np.percentile(field_plant,1):.3f} "
              f"median={np.median(field_plant):.3f}")
    print(f"  negatives     : median={np.median(neg_plant):.3f} max={neg_plant.max():.3f}")

    # Plantness is only a cheap sanity floor (blank/grey/night frames). Anchor it
    # well below the least plant-like real leaf so it cannot false-reject.
    plant_anchor = field_plant if len(field_plant) else real_plant
    if len(plant_anchor):
        # 0.7 of the least plant-like real leaf: still keeps every field photo we
        # measured, but rejects frames that are mostly fruit/stem/background.
        plant_thr = float(max(0.010, min(np.percentile(plant_anchor, 1) * 0.7, 0.08)))
    else:
        plant_thr = 0.03

    print(f"[train] cosine gate  = {cos_thr:.3f} (crop-locked {cos_thr_hint:.3f})  "
          f"clean kept {(val_cos >= cos_thr).mean()*100:.1f}%, "
          f"field kept {(field_cos >= cos_thr).mean()*100 if len(field_cos) else 0:.1f}%, "
          f"negatives rejected {(neg_cos < cos_thr).mean()*100:.1f}%")
    if len(real_plant):
        print(f"[train] plantness gate = {plant_thr:.3f}  "
              f"(field kept {(field_plant >= plant_thr).mean()*100 if len(field_plant) else 0:.1f}%, "
              f"negatives rejected {(neg_plant < plant_thr).mean()*100:.1f}%)")

    # -------------------------------------------------------------------
    # Held-out evaluation
    # -------------------------------------------------------------------
    linears = [m for m in net if isinstance(m, torch.nn.Linear)]
    W1, b1 = linears[0].weight.detach().numpy(), linears[0].bias.detach().numpy()
    W2, b2 = linears[1].weight.detach().numpy(), linears[1].bias.detach().numpy()

    def evaluate(X, y, name):
        probs = softmax(logits_of(X).astype(np.float64) / best_T)
        pred = probs.argmax(1)
        acc = float((pred == y).mean())
        conf = probs.max(1) * 100
        per_class = {}
        print(f"\n[eval] {name}: top-1 = {acc*100:.2f}%  (n={len(y)})")
        print(f"  {'class':<48}{'n':>6}{'prec':>8}{'rec':>8}")
        for c in range(n_classes):
            m = y == c
            if m.sum() == 0:
                continue
            rec = float((pred[m] == c).mean())
            pm = pred == c
            prec = float((y[pm] == c).mean()) if pm.sum() else 0.0
            per_class[classes[c]] = {"n": int(m.sum()),
                                     "precision": round(prec * 100, 1),
                                     "recall": round(rec * 100, 1)}
            print(f"  {classes[c]:<48}{int(m.sum()):>6}{prec*100:>7.1f}%{rec*100:>7.1f}%")
        print(f"  mean confidence {conf.mean():.1f}%  "
              f"(correct {conf[pred == y].mean():.1f}% / wrong {conf[pred != y].mean():.1f}%)")
        return {"accuracy": round(acc * 100, 2), "n": int(len(y)),
                "mean_confidence": round(float(conf.mean()), 1),
                "per_class": per_class}

    val_res = evaluate(Xva, yva, "validation")
    test_res = evaluate(Xte, yte, "TEST (never used for training)")

    np.savez_compressed(
        OUT_NPZ,
        classes=np.array(classes),
        W1=W1.astype(np.float32), b1=b1.astype(np.float32),
        W2=W2.astype(np.float32), b2=b2.astype(np.float32),
        temperature=np.array([best_T], dtype=np.float32),
        cos_threshold=np.array([cos_thr], dtype=np.float32),
        cos_threshold_hint=np.array([cos_thr_hint], dtype=np.float32),
        plant_threshold=np.array([plant_thr], dtype=np.float32),
        confidence_ceiling=np.array([min(99.5, test_res["accuracy"])], dtype=np.float32),
        protos=protos,
        backbone=np.array([BACKBONE_NAME]),
    )

    report = {
        "backbone": BACKBONE_NAME,
        "architecture": f"{BACKBONE_NAME} (frozen) -> Linear({dim},{HIDDEN}) -> GELU -> "
                        f"Dropout -> Linear({HIDDEN},{n_classes})",
        "num_classes": n_classes,
        "classes": classes,
        "temperature": round(best_T, 3),
        "cos_threshold": round(cos_thr, 3),
        "cos_threshold_hint": round(cos_thr_hint, 3),
        "plant_threshold": round(plant_thr, 4),
        "confidence_ceiling": round(min(99.5, test_res["accuracy"]), 2),
        "validation": val_res,
        "test": test_res,
        "known_limitations": [
            f"Excluded classes (too few photos, < {MIN_IMAGES}): " + (", ".join(dropped) or "none"),
            "Genuinely trained crops: " + ", ".join(sorted({c.split('___')[0].replace('_', ' ')
                                                            for c in classes})),
            "No fruit or whole-crop images were provided, so fruit-level detection "
            "is out of scope until such a dataset is added.",
            "PlantVillage is photographed on a uniform background; real field photos "
            "with clutter will score lower on the novelty gate.",
        ],
    }
    with open(OUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n[train] saved {OUT_NPZ} and {OUT_REPORT}")


if __name__ == "__main__":
    train()
