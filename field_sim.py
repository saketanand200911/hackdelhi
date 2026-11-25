"""
Field-photo simulation.

The original rejection threshold was fitted on PlantVillage validation images,
which are shot on a plain background. Real phone photos of the same leaf have
clutter, bokeh, stems and different lighting, so their embedding similarity to a
class prototype is much lower -- and the gate wrongly answered "Not detected".

This module degrades a clean leaf photo into something that looks like a field
shot, so the threshold can be fitted against what users actually upload.
"""

import io
import os

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


def _background(kind, size, rng):
    """Synthetic but realistic photographic backgrounds."""
    w, h = size
    if kind == "soil":
        base = np.zeros((h, w, 3), dtype=np.float32)
        base[:, :, 0] = rng.uniform(70, 125)
        base[:, :, 1] = base[:, :, 0] * rng.uniform(0.62, 0.80)
        base[:, :, 2] = base[:, :, 0] * rng.uniform(0.42, 0.60)
        base += rng.normal(0, 16, (h, w, 3))
        img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
        return img.filter(ImageFilter.GaussianBlur(rng.uniform(3, 9)))
    if kind == "foliage":
        base = np.zeros((h, w, 3), dtype=np.float32)
        for _ in range(rng.integers(25, 60)):
            cx, cy = rng.uniform(0, w), rng.uniform(0, h)
            r = rng.uniform(w * 0.08, w * 0.35)
            g = rng.uniform(70, 165)
            base[:, :, 1] = np.maximum(
                base[:, :, 1],
                g * np.exp(-(((np.arange(w)[None, :] - cx) ** 2 +
                              (np.arange(h)[:, None] - cy) ** 2) / (2 * r ** 2))))
            base[:, :, 0] = np.maximum(base[:, :, 0], base[:, :, 1] * rng.uniform(0.35, 0.7))
            base[:, :, 2] = np.maximum(base[:, :, 2], base[:, :, 1] * rng.uniform(0.20, 0.45))
        base += rng.normal(0, 10, (h, w, 3))
        img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
        return img.filter(ImageFilter.GaussianBlur(rng.uniform(4, 11)))
    if kind == "sky":
        grad = np.linspace(110, 235, h).reshape(h, 1, 1)
        base = np.repeat(np.repeat(grad, w, axis=1), 3, axis=2)
        base[:, :, 0] *= 0.80
        base[:, :, 2] *= 1.06
        base += rng.normal(0, 6, (h, w, 3))
        return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    # shadowed ground / generic dark
    base = np.full((h, w, 3), rng.uniform(28, 70), dtype=np.float32)
    base += rng.normal(0, 12, (h, w, 3))
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(rng.uniform(5, 12)))


def simulate_field(img: Image.Image, rng, canvas=384) -> Image.Image:
    """
    Turn a clean close-up leaf shot into something resembling a real field photo:
    the leaf is cropped, scaled down, sitting off-centre on a blurred cluttered
    background, at a slight angle, with phone-camera lighting and JPEG noise.
    """
    img = img.convert("RGB")
    w, h = img.size

    # 1. Aggressive random crop -- users rarely frame the leaf perfectly.
    scale = rng.uniform(0.55, 1.0)
    cw, ch = max(32, int(w * scale)), max(32, int(h * scale))
    left = int(rng.integers(0, max(1, w - cw + 1)))
    top = int(rng.integers(0, max(1, h - ch + 1)))
    leaf = img.crop((left, top, left + cw, top + ch))

    # 2. Cluttered, out-of-focus background.
    kind = ["soil", "foliage", "sky", "shadow"][int(rng.integers(0, 4))]
    bg = _background(kind, (canvas, canvas), rng)

    # 3. Place the leaf on it, occupying 45-92% of the frame, off-centre.
    fill = rng.uniform(0.45, 0.92)
    target = int(canvas * fill)
    lw, lh = leaf.size
    ratio = target / max(lw, lh)
    leaf = leaf.resize((max(16, int(lw * ratio)), max(16, int(lh * ratio))),
                       Image.Resampling.BILINEAR)
    if rng.random() < 0.6:
        leaf = leaf.rotate(rng.uniform(-22, 22), expand=True,
                           resample=Image.Resampling.BILINEAR)

    ox = int(rng.integers(0, max(1, canvas - leaf.size[0] + 1)))
    oy = int(rng.integers(0, max(1, canvas - leaf.size[1] + 1)))
    bg.paste(leaf, (ox, oy))

    # 4. Phone-camera exposure/white balance, motion blur, JPEG crawl.
    out = bg
    if rng.random() < 0.85:
        out = ImageEnhance.Brightness(out).enhance(float(rng.uniform(0.60, 1.45)))
    if rng.random() < 0.85:
        out = ImageEnhance.Contrast(out).enhance(float(rng.uniform(0.72, 1.35)))
    if rng.random() < 0.55:
        out = ImageEnhance.Color(out).enhance(float(rng.uniform(0.65, 1.30)))
    if rng.random() < 0.35:
        out = out.filter(ImageFilter.GaussianBlur(rng.uniform(0.4, 1.5)))
    if rng.random() < 0.25:  # vignette-ish shadow in a corner
        d = ImageDraw.Draw(out, "RGBA")
        cx, cy = rng.uniform(0, canvas), rng.uniform(0, canvas)
        d.ellipse([cx - canvas, cy - canvas, cx + canvas, cy + canvas],
                  fill=(0, 0, 0, int(rng.uniform(10, 55))))

    buf = io.BytesIO()
    out.save(buf, "JPEG", quality=int(rng.integers(55, 92)))
    return Image.open(io.BytesIO(buf.getvalue())).convert("RGB")
