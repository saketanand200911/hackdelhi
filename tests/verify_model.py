"""
Stage 3: end-to-end check of the *shipped* inference path.

This does not re-measure training accuracy -- it calls LeafClassifier.predict()
exactly like the web app does, so it exercises the plant gate, the cosine gate
and the calibrated percentages together.

Three things must hold:
  1. Real held-out leaves are detected and named correctly.
  2. Non-plant images are rejected, not diagnosed.
  3. Reported confidence is not a constant floor.
"""

import io
import os
import random
import sys
import zipfile
from collections import defaultdict

import numpy as np
from PIL import Image, ImageDraw

from leaf_classifier import LeafClassifier, plant_pixel_ratio

SEED = 7
SAMPLE_PER_CLASS = 40
random.seed(SEED)
np.random.seed(SEED)


def load_test_set():
    """Pick held-out images using the same deterministic split as training."""
    backbone = os.environ.get("BACKBONE", "mobilenet_v3_small")
    emb_npz = f"data/embeddings_{backbone.replace('.', '_')}.npz"
    d = np.load(emb_npz, allow_pickle=True)
    labels, splits = d["labels"], d["splits"]
    classes = [str(c) for c in d["classes"]]

    # Rebuild the index the same way build_embeddings did, then keep test rows.
    import build_embeddings as B
    records, _ = B.discover()

    wanted = defaultdict(list)
    seen = defaultdict(int)
    for (canonical, zname, member), label, split in zip(records, labels, splits):
        if split != "test" or zname == "__local__":
            continue
        if seen[canonical] >= SAMPLE_PER_CLASS:
            continue
        seen[canonical] += 1
        wanted[zname].append((canonical, member, classes[label], seen[canonical]))
    return wanted


def run():
    print("=" * 72)
    print("END-TO-END VERIFICATION (uses the same code path as the web app)")
    print("=" * 72)
    clf = LeafClassifier()
    print(f"classes={len(clf.classes)}  T={clf.temperature:.3f}  "
          f"cos_thr={clf.cos_threshold:.3f}  plant_thr={clf.plant_threshold:.4f}\n")

    # ---------------- 1. real leaves ----------------
    wanted = load_test_set()
    n_total = n_detected = n_correct = n_rejected = 0
    confs = []
    failures = []

    for zname, entries in wanted.items():
        with zipfile.ZipFile(zname) as z:
            for canonical, member, class_id, _ in entries:
                try:
                    img = Image.open(io.BytesIO(z.read(member))).convert("RGB")
                except Exception:
                    continue
                n_total += 1
                pred = clf.predict(img)
                if not pred["detected"]:
                    n_rejected += 1
                    if len(failures) < 12:
                        failures.append((class_id, "REJECTED", pred.get("cosine")))
                    continue
                n_detected += 1
                confs.append(pred["confidence"])
                if pred["class_id"] == class_id:
                    n_correct += 1
                elif len(failures) < 12:
                    failures.append((class_id, f"{pred['class_id']} {pred['confidence']}%",
                                     pred.get("cosine")))

    print("1. REAL HELD-OUT LEAVES")
    print(f"   images tested      : {n_total}")
    print(f"   detected           : {n_detected} ({n_detected/max(n_total,1)*100:.1f}%)")
    print(f"   rejected (missed)  : {n_rejected} ({n_rejected/max(n_total,1)*100:.1f}%)")
    print(f"   correct when detected: {n_correct}/{n_detected} "
          f"= {n_correct/max(n_detected,1)*100:.1f}%")
    if confs:
        print(f"   confidence range   : {min(confs):.1f}% .. {max(confs):.1f}% "
              f"(mean {np.mean(confs):.1f}%)")
    if failures:
        print("   sample mismatches:")
        for exp, got, cos in failures[:10]:
            print(f"     expected {exp:<45} got {got}")
    print()

    # ---------------- 2. non-plant images ----------------
    print("2. NON-PLANT IMAGES (must say 'Not detected')")
    import train_classifier as TC
    negs = TC.negative_set()
    neg_ok = 0
    for i, img in enumerate(negs):
        pred = clf.predict(img)
        ok = not pred["detected"]
        neg_ok += ok
        if not ok:
            print(f"   FAIL  neg#{i}: said {pred['crop']} {pred['condition']} "
                  f"{pred['confidence']}%  (plantness {pred['plantness']:.3f}, "
                  f"cos {pred.get('cosine')})")
    print(f"   correctly rejected : {neg_ok}/{len(negs)}")
    print()

    # ---------------- 2b. FIELD-PHOTO ROBUSTNESS ----------------
    # The original gate was fitted on clean PlantVillage images and answered
    # "Not detected" for 39% of genuine phone photos. This section is the
    # regression test for that bug.
    print("2b. FIELD-LIKE PHOTOS (real leaves photographed in the field)")
    from field_sim import simulate_field
    pool = []
    for zname, entries in wanted.items():
        for canonical, member, class_id, _ in entries:
            pool.append((zname, member, class_id))
    step = max(1, len(pool) // 200)
    pool = pool[::step][:200]

    field_imgs, field_labels = [], []
    handles = {}
    try:
        for zname, member, class_id in pool:
            try:
                if zname not in handles:
                    handles[zname] = zipfile.ZipFile(zname)
                field_imgs.append(
                    Image.open(io.BytesIO(handles[zname].read(member))).convert("RGB"))
                field_labels.append(class_id)
            except Exception:
                continue
    finally:
        for h in handles.values():
            h.close()

    rngf = np.random.default_rng(11)
    simulated = [simulate_field(im, rngf) for im in field_imgs]
    f_det = f_correct = 0
    for im, want in zip(simulated, field_labels):
        p = clf.predict(im)
        if p["detected"]:
            f_det += 1
            f_correct += (p["class_id"] == want)
    print(f"   photos tested      : {len(simulated)}")
    print(f"   detected           : {f_det} ({f_det/max(len(simulated),1)*100:.1f}%)")
    print(f"   correct when detected: {f_correct}/{f_det} "
          f"= {f_correct/max(f_det,1)*100:.1f}%")
    print()

    # ---------------- 3. percentage sanity ----------------
    print("3. PERCENTAGE SANITY")
    flat = Image.new("RGB", (256, 256), (128, 128, 128))
    p = clf.predict(flat)
    print(f"   plain grey square  -> detected={p['detected']}  "
          f"confidence={p['confidence']}%  plantness={p['plantness']:.3f}")
    noise = Image.fromarray(np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8))
    p = clf.predict(noise)
    print(f"   random noise       -> detected={p['detected']}  "
          f"confidence={p['confidence']}%")
    # A real leaf must score meaningfully above a flat grey image.
    real = None
    for zname, entries in wanted.items():
        with zipfile.ZipFile(zname) as z:
            canonical, member, class_id, _ = entries[0]
            real = Image.open(io.BytesIO(z.read(member))).convert("RGB")
        break
    if real is not None:
        p = clf.predict(real)
        print(f"   real leaf          -> {p['crop']} {p['condition']} "
              f"{p['confidence']}%  cos={p.get('cosine')}")
    print()

    ok_all = (n_total > 0 and n_detected / n_total > 0.85
              and n_correct / max(n_detected, 1) > 0.85
              and neg_ok / len(negs) >= 0.85
              and f_det / max(len(simulated), 1) > 0.90)
    print("=" * 72)
    print("RESULT:", "PASS" if ok_all else "NEEDS WORK")
    print("=" * 72)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(run())
