"""
Populates data/leaf_vector_db.npz from cached clean + field-augmented MobileNetV3 embeddings.
Runs in <1 second without re-running CNN inference.
"""

import os
from collections import defaultdict
import numpy as np

from leaf_classifier import LeafClassifier
from plantvillage_engine import PLANTVILLAGE_MASTER_DB
from vector_rag import LeafVectorDB, VECTOR_DB_PATH

EMB_NPZ = "data/embeddings_mobilenet_v3_small.npz"
FIELD_NPZ = "data/field_aug_embeddings.npz"


def main():
    if os.path.exists(VECTOR_DB_PATH):
        os.remove(VECTOR_DB_PATH)
    vdb = LeafVectorDB(VECTOR_DB_PATH)

    rng = np.random.default_rng(101)
    vecs_all, cids_all, crops_all, diseases_all, sources_all = [], [], [], [], []

    def add_meta(cid: str, src: str, vec: np.ndarray):
        info = PLANTVILLAGE_MASTER_DB.get(cid)
        if info:
            crop, dis = info["crop"], info["disease"]
        else:
            crop, dis = LeafClassifier.split_class(cid)
        vecs_all.append(vec)
        cids_all.append(cid)
        crops_all.append(crop)
        diseases_all.append(dis)
        sources_all.append(src)

    # 1. Clean train exemplars (up to 40 per class)
    d = np.load(EMB_NPZ, allow_pickle=True)
    embeds, labels, splits = d["embeds"], d["labels"], d["splits"]
    classes = [str(c) for c in d["classes"]]
    by_cls = defaultdict(list)
    for i, (s, l) in enumerate(zip(splits, labels)):
        if s == "train":
            by_cls[classes[int(l)]].append(embeds[i, 0, :])
    for cid, items in sorted(by_cls.items()):
        if len(items) > 40:
            idx = rng.choice(len(items), size=40, replace=False)
            items = [items[k] for k in idx]
        for v in items:
            add_meta(cid, "plantvillage_train", v)

    # 2. Field + crop augmented & extra 23-class clean exemplars (up to 35 per class)
    if os.path.exists(FIELD_NPZ):
        fa = np.load(FIELD_NPZ, allow_pickle=True)
        fa_classes = [str(c) for c in fa["classes"]]
        for key_x, key_y, src_name in [
            ("X", "y", "field_augmented"),
            ("X_clean_extra", "y_clean_extra", "plantvillage_extra"),
        ]:
            if key_x not in fa:
                continue
            Xf, yf = fa[key_x], fa[key_y]
            by_cls_f = defaultdict(list)
            for v, yi in zip(Xf, yf):
                by_cls_f[fa_classes[int(yi)]].append(v)
            for cid, items in sorted(by_cls_f.items()):
                if len(items) > 35:
                    idx = rng.choice(len(items), size=35, replace=False)
                    items = [items[k] for k in idx]
                for v in items:
                    add_meta(cid, src_name, v)

    vdb.add_vectors(
        np.array(vecs_all, dtype=np.float32),
        cids_all,
        crops_all,
        diseases_all,
        sources_all,
        persist=True,
    )
    print("Built LeafVectorDB:", vdb.stats())


if __name__ == "__main__":
    main()
