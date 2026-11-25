"""
Dependency-free leaf localizer.

Why this exists: the CNN was trained on PlantVillage photos where the leaf fills
the frame against a plain background. A real phone photo has the leaf somewhere
in the middle of a cluttered, out-of-focus scene, so its embedding lands far from
the training distribution -- that mismatch is what dropped field accuracy to 55%.

The robust cue is *focus*, not colour: leaf tissue is sharply in focus while the
background is blurred. So we score local gradient energy, keep the sharp region,
and crop to it. Colour is used only as a tie-breaker, since a leafy-green
background would otherwise fool a pure colour mask.

Pure numpy -- no scipy, no OpenCV.
"""

from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageFilter

# Below this much sharp area we do not trust the estimate and return None, so
# callers fall back to the whole frame instead of cropping to noise.
MIN_REGION = 0.06
MAX_REGION = 0.80


def _gradient_energy(gray: np.ndarray) -> np.ndarray:
    """Local edge strength, smoothed so it forms blobs rather than speckle."""
    gx = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    gy = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
    energy = gx + gy
    # Box-blur via cumulative sums (fast, no dependency).
    k = 9
    pad = k // 2
    p = np.pad(energy, pad, mode="edge")
    c = p.cumsum(axis=0).cumsum(axis=1)
    c = np.pad(c, ((1, 0), (1, 0)))
    out = (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)
    return out


def _largest_region(mask: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """
    Bounding box of the biggest blob in a coarse boolean mask.

    Uses a cheap iterative flood fill on the small grid (<=48x48), which is more
    than precise enough because the box is refined against the full image later.
    """
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    best_area, best_box = 0, None

    for sy in range(h):
        for sx in range(w):
            if mask[sy, sx] and not seen[sy, sx]:
                stack = [(sy, sx)]
                seen[sy, sx] = True
                miny = maxy = sy
                minx = maxx = sx
                area = 0
                while stack:
                    y, x = stack.pop()
                    area += 1
                    miny, maxy = min(miny, y), max(maxy, y)
                    minx, maxx = min(minx, x), max(maxx, x)
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
                if area > best_area:
                    best_area = area
                    best_box = (minx, miny, maxx + 1, maxy + 1)

    if best_box is None:
        return None
    return best_box


def find_leaf_box(img: Image.Image) -> Optional[Tuple[int, int, int, int]]:
    """
    Return (left, top, right, bottom) in original pixel coordinates, or None when
    no confident leaf region can be found.
    """
    img = img.convert("RGB")
    W, H = img.size
    if min(W, H) < 32:
        return None

    small = img.resize((96, 96), Image.Resampling.BILINEAR)
    a = np.asarray(small, dtype=np.float32)
    gray = (0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2]) / 255.0

    energy = _gradient_energy(gray)

    # Sharp-region mask: top ~28% of gradient energy so the full leaf lamina
    # (not just one lesion spot) stays inside the bounding box.
    thr = np.percentile(energy, 72)
    sharp = energy >= max(thr, 1e-4)

    # Colour support, used only to reject a sharp but clearly non-plant region.
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    greenish = (g > r * 1.03) & (g > b * 1.03) & (g > 35)
    yellowgreen = (g > 60) & (r > 40) & (r < g * 1.3) & (b < g * 0.9)

    mask = sharp & (greenish | yellowgreen)
    area = float(mask.mean())
    if area < MIN_REGION:
        # Colour gate too strict (e.g. a diseased brown leaf) -- fall back to
        # pure sharpness so we still localize something.
        mask = sharp
        if float(mask.mean()) < MIN_REGION:
            return None

    # Coarse blob search, then map back to full resolution.
    coarse = 32
    cy, cx = 96 // coarse, 96 // coarse
    grid = mask.reshape(coarse, cy, coarse, cx).mean(axis=(1, 3)) > 0.35
    box = _largest_region(grid)
    if box is None:
        return None

    gx0, gy0, gx1, gy1 = box
    left = int(gx0 / coarse * W)
    top = int(gy0 / coarse * H)
    right = int(gx1 / coarse * W)
    bottom = int(gy1 / coarse * H)

    if right <= left or bottom <= top:
        return None
    frac = ((right - left) * (bottom - top)) / float(W * H)
    if frac < MIN_REGION:
        return None
    if frac > MAX_REGION:
        return None  # region is the whole frame; cropping would change nothing

    return left, top, right, bottom


def crop_to_leaf(img: Image.Image, pad: float = 0.22) -> Image.Image:
    """Crop to the detected leaf, with a little margin. Falls back to the input."""
    box = find_leaf_box(img)
    if box is None:
        return img
    left, top, right, bottom = box
    W, H = img.size
    dx, dy = (right - left) * pad, (bottom - top) * pad
    left = max(0, int(left - dx))
    top = max(0, int(top - dy))
    right = min(W, int(right + dx))
    bottom = min(H, int(bottom + dy))
    if right - left < 24 or bottom - top < 24:
        return img
    return img.crop((left, top, right, bottom))
