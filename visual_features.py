"""
Pure Pillow + NumPy visual feature extractor for leaf disease classification.
Includes center-weighted & illumination-normalized processing for camera photos.
Zero heavy dependencies (works identically on local FastAPI and Vercel Serverless).
"""

import numpy as np
from PIL import Image, ImageOps


def _center_crop_for_camera(img: Image.Image) -> Image.Image:
    """
    Crop slightly inward (82% center) when aspect ratio is non-square (typical 4:3 or 16:9 camera frame)
    to reduce desk/hand/room background clutter around the leaf.
    """
    w, h = img.size
    if abs(w - h) > min(w, h) * 0.12:
        side = int(min(w, h) * 0.82)
        left = (w - side) // 2
        top = (h - side) // 2
        return img.crop((left, top, left + side, top + side))
    return img


def extract_visual_signature(img: Image.Image) -> np.ndarray:
    """
    Extract a 96-dimensional L2-normalized visual signature using only Pillow + NumPy.
    Captures:
      - HSV color histograms (32 H + 16 S + 16 V = 64 dims)
      - Botanical lesion color ratios & spatial patch variance (16 dims)
      - Edge / texture gradient statistics (16 dims)
    """
    img_focused = _center_crop_for_camera(img.convert("RGB"))
    # Gentle autocontrast (1% cutoff) helps normalize indoor webcam lighting/glare
    img_norm = ImageOps.autocontrast(img_focused, cutoff=1)
    img_rgb = img_norm.resize((128, 128), Image.Resampling.BILINEAR)
    img_hsv = img_rgb.convert("HSV")

    rgb = np.asarray(img_rgb, dtype=np.float32) / 255.0
    hsv = np.asarray(img_hsv, dtype=np.float32)

    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]

    # 1. HSV Histograms (64 dims)
    h_hist, _ = np.histogram(h, bins=32, range=(0, 256))
    s_hist, _ = np.histogram(s, bins=16, range=(0, 256))
    v_hist, _ = np.histogram(v, bins=16, range=(0, 256))
    h_hist = h_hist.astype(np.float32) / (h_hist.sum() + 1e-6)
    s_hist = s_hist.astype(np.float32) / (s_hist.sum() + 1e-6)
    v_hist = v_hist.astype(np.float32) / (v_hist.sum() + 1e-6)

    # 2. Botanical Lesion & Spatial Features (16 dims)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    green_mask = (g > r * 1.12) & (g > b * 1.12) & (g > 0.22)
    yellow_mask = (r > 0.45) & (g > 0.42) & (b < np.minimum(r, g) * 0.72)
    orange_rust_mask = (r > 0.50) & (g > 0.22) & (g < r * 0.78) & (b < 0.30)
    brown_mask = (r > g * 0.95) & (np.maximum(r, g) < 0.55) & (b < 0.35) & ((r > 0.15) | (g > 0.15))
    dark_spot_mask = (r < 0.22) & (g < 0.22) & (b < 0.22)
    white_mold_mask = (r > 0.75) & (g > 0.75) & (b > 0.75)

    grid_green = []
    for i in range(0, 128, 32):
        for j in range(0, 128, 32):
            patch = green_mask[i:i+32, j:j+32]
            grid_green.append(float(patch.mean()))
    grid_green_arr = np.array(grid_green, dtype=np.float32)

    lesion_feats = np.array([
        float(green_mask.mean()),
        float(yellow_mask.mean()),
        float(orange_rust_mask.mean()),
        float(brown_mask.mean()),
        float(dark_spot_mask.mean()),
        float(white_mold_mask.mean()),
        float(r.mean()), float(g.mean()), float(b.mean()),
        float(r.std()), float(g.std()), float(b.std()),
        float(grid_green_arr.std()),
        float(grid_green_arr.min()),
        float(grid_green_arr.max()),
        float((yellow_mask | brown_mask | orange_rust_mask).mean()),
    ], dtype=np.float32)

    # 3. Edge & Texture Gradient Statistics (16 dims)
    gray = 0.299 * r + 0.587 * g + 0.114 * b
    dx = np.abs(np.diff(gray, axis=1))
    dy = np.abs(np.diff(gray, axis=0))
    dx_hist, _ = np.histogram(dx, bins=8, range=(0, 0.5))
    dy_hist, _ = np.histogram(dy, bins=8, range=(0, 0.5))
    dx_hist = dx_hist.astype(np.float32) / (dx_hist.sum() + 1e-6)
    dy_hist = dy_hist.astype(np.float32) / (dy_hist.sum() + 1e-6)

    vec = np.concatenate([h_hist, s_hist, v_hist, lesion_feats, dx_hist, dy_hist])
    norm = np.linalg.norm(vec) + 1e-8
    return (vec / norm).astype(np.float32)
