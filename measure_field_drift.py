"""
Measures how far real leaf photos drift once they look like field photos.

Used to decide the novelty-gate threshold: the old one was fitted on clean
PlantVillage images and rejected genuine phone photos.
"""

import io
import os
import zipfile

import numpy as np

import build_embeddings as B
from field_sim import simulate_field
from leaf_classifier import LeafClassifier, plant_pixel_ratio

N = 160
rng = np.random.default_rng(3)


def sample(n=N):
    d = np.load("data/embeddings_mobilenet_v3_small.npz", allow_pickle=True)
    splits = d["splits"]
    records, _ = B.discover()
    picks = [(z, m) for (c, z, m), s in zip(records, splits)
             if s == "val" and z != "__local__"]
    step = max(1, len(picks) // n)
    picks = picks[::step][:n]
    out, handles = [], {}
    try:
        for zname, member in picks:
            try:
                if zname not in handles:
                    handles[zname] = zipfile.ZipFile(zname)
                out.append(Image_open(handles[zname].read(member)))
            except Exception:
                continue
    finally:
        for h in handles.values():
            h.close()
    return out


def Image_open(raw):
    from PIL import Image
    return Image.open(io.BytesIO(raw)).convert("RGB")


def main():
    from PIL import Image
    clf = LeafClassifier()
    imgs = sample()
    print(f"sampled {len(imgs)} real val leaves\n")

    def cosines(images, extractor_feats=True):
        feats = clf._features(images)
        return (feats @ clf.protos.T).max(axis=1), np.array(
            [plant_pixel_ratio(i) for i in images])

    clean_cos, clean_plant = cosines(imgs)
    field_imgs = [simulate_field(i, np.random.default_rng(1000 + k)) for k, i in enumerate(imgs)]
    field_cos, field_plant = cosines(field_imgs)

    # Also check the current gate's verdict on field photos.
    rejected = 0
    for im in field_imgs:
        if not clf.predict(im)["detected"]:
            rejected += 1

    print(f"clean  cosine: p1={np.percentile(clean_cos,1):.3f} "
          f"p5={np.percentile(clean_cos,5):.3f} median={np.median(clean_cos):.3f}")
    print(f"FIELD  cosine: p1={np.percentile(field_cos,1):.3f} "
          f"p5={np.percentile(field_cos,5):.3f} p10={np.percentile(field_cos,10):.3f} "
          f"median={np.median(field_cos):.3f}")
    print(f"FIELD  plantness: p1={np.percentile(field_plant,1):.3f} "
          f"median={np.median(field_plant):.3f}")
    print(f"\ncurrent gate rejects {rejected}/{len(field_imgs)} field photos "
          f"({rejected/len(field_imgs)*100:.0f}%)")
    print(f"current thresholds: cos={clf.cos_threshold:.3f} "
          f"plant={clf.plant_threshold:.4f}")


if __name__ == "__main__":
    main()
