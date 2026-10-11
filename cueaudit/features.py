"""Image proxies extracted from the original screening/foreground scripts."""
import numpy as np
import cv2
from PIL import Image


def measure(path, module):
    with Image.open(path) as source:
        image = source.convert("RGB")
    if module == "foreground":
        w, h = image.size
        scale = min(1.0, 512 / max(w, h))
        if scale < 1:
            image = image.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.BILINEAR)
        rgb = np.asarray(image, dtype=np.uint8)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        r, g, b = [rgb[:, :, i].astype(float) for i in range(3)]
        green = (g > r * 1.05) & (g > b * 1.05) & (g > 60)
        yellow = (r > 110) & (g > 90) & (b < 130) & (np.abs(r - g) < 70)
        brown = (r > 70) & (g > 35) & (b < 95) & (r > g * 1.05) & (g > b * 1.05) & ((r - g) < 95)
        dark = (0.299 * r + 0.587 * g + 0.114 * b) < 45
        return float((green | yellow | brown | dark | ((hsv[:, :, 1] > 35) & (hsv[:, :, 2] < 245))).mean())
    if module == "color":
        rgb = np.asarray(image.resize((32, 32)), dtype=np.float32) / 255
        return str(int(np.argmax(rgb.mean(axis=(0, 1)))))
    if module == "corner_patch":
        gray = np.asarray(image.convert("L").resize((32, 32)), dtype=np.float32) / 255
        corners = [gray[:6, :6].mean(), gray[:6, -6:].mean(),
                   gray[-6:, :6].mean(), gray[-6:, -6:].mean()]
        return str(int(np.argmax(corners)))
    raise ValueError("Unknown image measurement")
