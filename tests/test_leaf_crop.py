"""Does leaf-cropping actually recover field accuracy? Measure, don't assume."""

import io
import zipfile

import numpy as np
from PIL import Image

import build_embeddings as B
from field_sim import simulate_field
from leaf_classifier import LeafClassifier
from leaf_crop import crop_to_leaf, find_leaf_box

N = 150
rng = np.random.default_rng(5)


def sample(n=N):
    d = np.load("data/embeddings_mobilenet_v3_small.npz", allow_pickle=True)
    splits, labels = d["splits"], d["labels"]
    classes = [str(c) for c in d["classes"]]
    records, _ = B.discover()
    picks = [(c, z, m, classes[l]) for (c, z, m), s, l in zip(records, splits, labels)
             if s == "val" and z != "__local__"]
    step = max(1, len(picks) // n)
    picks = picks[::step][:n]
    out, handles = [], {}
    try:
        for shape, zname, member, cls in picks:
            try:
                if zname not in handles:
                    handles[zname] = zipfile.ZipFile(zname)
                out.append((Image.open(io.BytesIO(handles[zname].read(member))).convert("RGB"), cls))
            except Exception:
                continue
    finally:
        for h in handles.values():
            h.close()
    return out


def score(clf, images, labels, tag):
    feats = clf._features(images)
    logits = clf._logits(feats)
    pred = logits.argmax(1)
    cls_index = {c: i for i, c in enumerate(clf.classes)}
    want = np.array([cls_index[l] for l in labels])
    acc = float((pred == want).mean())
    cos = (feats @ clf.protos.T).max(1)
    print(f"  {tag:<26} top1={acc*100:5.1f}%  cos_med={np.median(cos):.3f} "
          f"cos_p1={np.percentile(cos,1):.3f}")
    return acc


def main():
    clf = LeafClassifier()
    pairs = sample()
    print(f"sampled {len(pairs)} real val leaves\n")

    clean = [p[0] for p in pairs]
    labels = [p[1] for p in pairs]

    rng2 = np.random.default_rng(77)
    field = [simulate_field(im, rng2) for im in clean]

    found = sum(1 for im in field if find_leaf_box(im) is not None)
    print(f"localizer found a leaf region in {found}/{len(field)} field photos "
          f"({found/len(field)*100:.0f}%)\n")

    field_cropped = [crop_to_leaf(im) for im in field]
    avg_crop = np.mean([np.prod(c.size) / np.prod(f.size) for c, f in zip(field_cropped, field)])
    print(f"mean area kept after crop: {avg_crop*100:.0f}%\n")

    print("accuracy:")
    score(clf, clean, labels, "clean (no crop)")
    score(clf, [crop_to_leaf(i) for i in clean], labels, "clean + crop")
    score(clf, field, labels, "FIELD (no crop)")
    score(clf, field_cropped, labels, "FIELD + crop")


if __name__ == "__main__":
    main()
