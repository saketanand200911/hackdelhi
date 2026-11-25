# 🌿 LeafGuard AI — Leaf Disease Detection

[![Live App](https://img.shields.io/badge/Live%20Demo-voicekeep--six.vercel.app-10b981?style=for-the-badge)](https://voicekeep-six.vercel.app)

An image-recognition and agronomic-advisory web app: photograph a crop leaf, get
a diagnosis, a treatment protocol and a calibrated confidence score — or an
explicit **"Not detected"** when the photo isn't something the model knows.

---

## What this model actually does (measured, not claimed)

| Metric | Value |
|---|---|
| Test top-1 accuracy (held-out, never trained on) | **97.68%** |
| Validation top-1 accuracy | 97.88% |
| Real leaves accepted by the novelty gate | 99.5% |
| Correct answer given a detected leaf | 97.7% |
| Non-plant images correctly rejected | 20 / 20 |
| Mean confidence on correct answers | 98.1% |
| Mean confidence on wrong answers | 71.7% |

Classes: **15** (Tomato 9, Potato 3, Pepper 3), trained on **20,639 unique images**.

Full per-class precision/recall: [`data/model_report.json`](data/model_report.json).

---

## Honest limits

Read this before trusting an answer.

- **Only 3 crops are supported**: Tomato, Potato and Pepper (bell/chilli). Any
  other crop is not "misdiagnosed" — it is reported as `Not detected`, which is
  the correct behaviour.
- **Leaves only, not fruit.** No fruit or whole-plant images were supplied, so
  fruit-level detection is not implemented.
- **`archive.zip` and `Dataset.zip` are the same dataset.** The loader
  de-duplicates by filename and skips 39,650 duplicate copies, so the two
  archives do not double-count.
- **Photos in the field are harder than the benchmark.** PlantVillage images are
  shot on a plain background. A cluttered phone photo of the same disease scores
  lower on the novelty gate and may be returned as `Not detected` rather than
  guessed at. That trade-off is deliberate.
- Confidence is **capped at the measured test accuracy (97.68%)**, so the app
  never prints "100%".

---

## How detection works

Three stages, in order. Stage 1 and 2 can each produce `Not detected`.

```
photo
  │
  ├─ 1. plant-pixel gate ── no green/foliage tissue? ──► Not detected
  │       "no plant leaf in frame"
  │
  ├─ 2. cosine gate ── far from every known class? ──► Not detected
  │       "unknown plant or disease"
  │
  └─ 3. classifier ──► crop + condition + calibrated confidence
```

1. **Plant-pixel gate** (`plantness >= 0.069`) — a cheap colour test that
   catches blank walls, night frames and fruit close-ups.
2. **Cosine gate** (max similarity to any class prototype `>= 0.699`) — this is
   the real guard. A softmax over 15 classes will always name *some* class, so
   novelty is measured in embedding space, not by the percentage itself.
3. **Classifier** — frozen MobileNetV3-Small features → `Linear(576,512)` →
   GELU → Dropout → `Linear(512,15)`, with temperature scaling fitted on the
   validation split.

Both thresholds are *fitted*, not typed in by hand: the trainer computes the
real-leaf and non-plant similarity distributions and picks the most permissive
cut that still rejects the negatives.

---

## Setup

```bash
pip install -r requirements.txt
```

### Training (only needed once, or after adding data)

```bash
python3 build_embeddings.py     # ~11 min on CPU: 20,643 images x 3 views
python3 train_classifier.py     # ~1 min: trains head, calibrates, saves gates
python3 verify_model.py         # end-to-end check of the shipped code path
```

`build_embeddings.py` auto-discovers any `*.zip` in the project root and any
`<Crop>___<Condition>` folder inside it, so adding a new dataset means dropping
the zip next to `archive.zip` and re-running all three commands.

Classes with fewer than `MIN_IMAGES` (25) photos are **excluded** automatically
rather than faked into looking trained — 1-2 photos cannot make a class
detectable, they only steal predictions from real classes.

### Running the app

```bash
python3 app.py          # http://localhost:8080
```

Optional local LLM description (cosmetic only, never affects the diagnosis):

```bash
ollama run moondream
ENABLE_VISION_DESCRIPTION=1 python3 app.py
```

---

## Project layout

| File | Role |
|---|---|
| `build_embeddings.py` | Stage 1 — de-duplicate zips, split, cache CNN features |
| `train_classifier.py` | Stage 2 — train head, temperature scaling, fit rejection gates |
| `verify_model.py` | Stage 3 — end-to-end check through the real inference path |
| `smoke_test_api.py` | Posts real photos at a running server |
| `leaf_classifier.py` | Inference wrapper: calibrated % and `Not detected` |
| `app.py` | FastAPI server |
| `plantvillage_engine.py` | Knowledge base: symptoms, organic/chemical treatment, Hindi text |
| `static/` | Single-page frontend |
| `train_from_archive.py` | **Deprecated** — old nearest-centroid approach |
| `train_visual_classifier.py` | **Deprecated** — old colour-histogram approach |

---

## Deployment note

`api/index.py` is the Vercel entrypoint and imports `app`, which needs `torch`
plus `data/leaf_model.npz`. Vercel's Python runtime does not ship `torch` by
default and the bundle exceeds the size limit, so the serverless build needs
either a torch-free ONNX export of the model or an always-on host. Local and
any normal VM/container host work as-is.
