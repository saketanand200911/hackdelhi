"""
Inference wrapper for the trained leaf-disease model.

Loads data/leaf_model.npz (MobileNetV3-Small embeddings + trained linear head +
temperature + rejection thresholds) and turns a photo into either a calibrated
diagnosis or an explicit "Not detected".

Two independent guards decide "Not detected", because a softmax over 18 known
classes will always name *some* class no matter what you show it:

  1. plant-pixel gate  - is there any foliage-coloured tissue in the frame?
  2. cosine gate       - is the image anywhere near a class it was trained on?

Only if both pass do we report a disease, and the percentage we report is the
temperature-calibrated probability, never a hand-tuned floor.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional

import numpy as np
from PIL import Image
from leaf_crop import crop_to_leaf

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "data", "leaf_model.npz")

_TORCH_BACKBONES = {
    "mobilenet_v3_small": ("mobilenet_v3_small", "MobileNet_V3_Small_Weights"),
    "efficientnet_b0": ("efficientnet_b0", "EfficientNet_B0_Weights"),
    "convnext_tiny": ("convnext_tiny", "ConvNeXt_Tiny_Weights"),
}

_torch = None
_backbone = None
_transform = None


def _lazy_torch(backbone_name: str):
    """Import torch lazily so the app still starts on machines without it."""
    global _torch, _backbone, _transform
    if _torch is not None:
        return _torch
    import torch
    import torchvision.models as models
    import torchvision.transforms as T

    fn_name, weights_name = _TORCH_BACKBONES.get(
        backbone_name, _TORCH_BACKBONES["mobilenet_v3_small"])
    fn = getattr(models, fn_name)
    weights = getattr(models, weights_name).DEFAULT
    b = fn(weights=weights)
    b.eval()
    _backbone = torch.nn.Sequential(
        b.features, torch.nn.AdaptiveAvgPool2d(1), torch.nn.Flatten())
    for p in _backbone.parameters():
        p.requires_grad_(False)
    _transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    _torch = torch
    return torch


def plant_pixel_ratio(img: Image.Image) -> float:
    small = img.convert("RGB").resize((96, 96))
    a = np.asarray(small, dtype=np.float32)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    greenish = (g > r * 1.06) & (g > b * 1.06) & (g > 45)
    yellowgreen = (g > 70) & (r > 50) & (r < g * 1.25) & (b < g * 0.85)
    return float((greenish | yellowgreen).mean())


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


class LeafClassifier:
    def __init__(self, model_path: str = MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"{model_path} not found. Run build_embeddings.py then train_classifier.py.")
        d = np.load(model_path, allow_pickle=True)
        self.classes: List[str] = [str(c) for c in d["classes"]]
        self.W1 = d["W1"].astype(np.float32)
        self.b1 = d["b1"].astype(np.float32)
        self.W2 = d["W2"].astype(np.float32)
        self.b2 = d["b2"].astype(np.float32)
        self.temperature = float(d["temperature"][0])
        self.cos_threshold = float(d["cos_threshold"][0])
        # When the user locks a crop we already know what plant they hold, so the
        # novelty gate can be far more permissive -- it only has to catch an image
        # that is not that crop at all.
        self.cos_threshold_hint = float(d["cos_threshold_hint"][0]) \
            if "cos_threshold_hint" in d else max(0.15, self.cos_threshold - 0.15)
        self.plant_threshold = float(d["plant_threshold"][0])
        self.protos = d["protos"].astype(np.float32)
        self.backbone = str(d["backbone"][0]) if "backbone" in d else "mobilenet_v3_small"
        # Never claim more certainty than the held-out test set actually supports.
        self.confidence_ceiling = float(d["confidence_ceiling"][0]) \
            if "confidence_ceiling" in d else 99.0

    # -- helpers ---------------------------------------------------------
    @staticmethod
    def split_class(class_id: str):
        crop, _, condition = class_id.partition("___")
        crop = re.sub(r"\s+", " ", crop.replace("_", " ")).strip()
        condition = re.sub(r"\s+", " ", condition.replace("_", " ")).strip() or "Unknown"
        return crop, condition

    def _features(self, imgs: List[Image.Image]) -> np.ndarray:
        torch = _lazy_torch(self.backbone)
        batch = torch.stack([_transform(i.convert("RGB")) for i in imgs])
        with torch.no_grad():
            f = _backbone(batch)
            f = torch.nn.functional.normalize(f, p=2, dim=1)
        return f.numpy().astype(np.float32)

    def _logits(self, feat: np.ndarray) -> np.ndarray:
        """Two-layer head, matching train_classifier.py exactly."""
        feat = feat.astype(np.float64)
        h = feat @ self.W1.T.astype(np.float64) + self.b1.astype(np.float64)
        h = np.clip(h, -60.0, 60.0)          # guard against float overflow
        h = 0.5 * h * (1.0 + np.tanh(0.7978845608 * (h + 0.044715 * h ** 3)))
        return h @ self.W2.T.astype(np.float64) + self.b2.astype(np.float64)

    # -- main API --------------------------------------------------------
    def predict(self, img: Image.Image, crop_hint: str = "") -> Dict[str, Any]:
        img = img.convert("RGB")
        plantness = plant_pixel_ratio(img)

        if plantness < self.plant_threshold:
            return {
                "detected": False,
                "is_plant": False,
                "reason": (
                    "Koi paudha/leaf nahi mila is photo mein — "
                    "frame mein foliage dikhai nahi de rahi."
                ),
                "confidence": 0.0,
                "plantness": round(plantness, 4),
                "top_k": [],
            }

        cropped = crop_to_leaf(img)
        if cropped is not img:
            feats = self._features([img, cropped])
            feat_full, feat_crop = feats[0], feats[1]
            cos_full = float((self.protos @ feat_full).max())
            cos_crop = float((self.protos @ feat_crop).max())
            if cos_crop >= cos_full - 0.03:
                feat = feat_crop
                logits = 0.30 * self._logits(feat_full) + 0.70 * self._logits(feat_crop)
            else:
                feat = feat_full
                logits = self._logits(feat_full)
        else:
            feat = self._features([img])[0]
            logits = self._logits(feat)

        # Crop hint narrows the decision instead of adding a fake bonus. When the
        # user locks a crop we already know the plant, so the novelty gate is
        # judged against that crop's classes with a far more permissive cut.
        allowed_idx = None
        hint = (crop_hint or "").strip().lower()
        if hint:
            masks = np.array([hint in c.lower().replace("_", " ")
                              for c in self.classes])
            if masks.sum() >= 1:
                allowed_idx = np.where(masks)[0]

        if allowed_idx is not None:
            cos_sub = self.protos[allowed_idx] @ feat
            cosine_all = np.full(len(self.classes), -1.0, dtype=np.float64)
            cosine_all[allowed_idx] = cos_sub
            top_cos = float(cos_sub.max())
            cos_thr = self.cos_threshold_hint
            masked = np.full_like(logits, -1e9)
            masked[allowed_idx] = logits[allowed_idx]
        else:
            cosine_all = (self.protos @ feat).astype(np.float64)
            top_cos = float(cosine_all.max())
            cos_thr = self.cos_threshold
            masked = logits

        probs = _softmax(masked / self.temperature)

        order = np.argsort(-probs)
        top_idx = int(order[0])
        top_prob = float(probs[top_idx])

        if top_cos < cos_thr:
            return {
                "detected": False,
                "is_plant": True,
                "reason": (
                    f"Leaf dikh rahi hai, par ye kisi known disease se match nahi hui "
                    f"(closest similarity {top_cos*100:.0f}%, zaroorat "
                    f"{cos_thr*100:.0f}%)."
                ),
                # A rejected image has no class confidence. Reporting the top
                # class probability here would look like a (bogus) match.
                "confidence": 0.0,
                "best_guess_confidence": round(top_prob * 100, 1),
                "cosine": round(top_cos, 4),
                "plantness": round(plantness, 4),
                "top_k": self._topk(order, probs, cosine_all, allowed_idx, 5),
                "cos_threshold": round(cos_thr, 4),
            }

        # Crop-level rollup: how sure are we about the *plant* itself.
        crop = self.split_class(self.classes[top_idx])[0]
        crop_prob = float(sum(
            probs[i] for i, c in enumerate(self.classes)
            if self.split_class(c)[0] == crop))

        return {
            "detected": True,
            "is_plant": True,
            "class_id": self.classes[top_idx],
            "crop": crop,
            "condition": self.split_class(self.classes[top_idx])[1],
            "confidence": self._pct(top_prob),
            "crop_confidence": self._pct(crop_prob),
            "cosine": round(top_cos, 4),
            "plantness": round(plantness, 4),
            "top_k": self._topk(order, probs, cosine_all, allowed_idx, 5),
        }

    def _pct(self, prob: float) -> float:
        """Probability -> displayed percentage, capped at measured test accuracy."""
        return round(min(float(prob) * 100.0, self.confidence_ceiling), 1)

    def _topk(self, order, probs, cosine_all, allowed_idx, k) -> List[Dict[str, Any]]:
        out = []
        for i in order[:k]:
            ci = int(i)
            crop, condition = self.split_class(self.classes[ci])
            out.append({
                "class_id": self.classes[ci],
                "crop": crop,
                "condition": condition,
                "confidence": self._pct(probs[ci]),
                "cosine": round(float(cosine_all[ci]), 4),
            })
        return out


_singleton: Optional[LeafClassifier] = None


def get_classifier() -> Optional[LeafClassifier]:
    global _singleton
    if _singleton is None:
        try:
            _singleton = LeafClassifier()
            print(f"Loaded leaf classifier: {len(_singleton.classes)} classes, "
                  f"T={_singleton.temperature:.2f}, "
                  f"cos>={_singleton.cos_threshold:.2f}, "
                  f"plant>={_singleton.plant_threshold:.3f}")
        except Exception as e:
            print("Leaf classifier unavailable:", e)
            return None
    return _singleton
