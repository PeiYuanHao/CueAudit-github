"""LAB color transformations extracted from the original color template.

Inputs are RGB uint8 arrays; masks are uint8 arrays with values 0 or 255.
Supply the foreground mask or its complement for foreground/background swaps.
Full swaps use all-255 masks. Callers must review label preservation.
"""
import numpy as np
import cv2


def equalize_luminance_and_grayscale(img_np: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB).astype(np.float32)
    L = lab[:, :, 0]
    mean, std = cv2.meanStdDev(L)
    std_val = std[0][0] if std[0][0] > 0 else 1.0
    L_new = ((L - mean[0][0]) * (64.0 / std_val)) + 128.0
    L_new = np.clip(L_new, 0, 255)

    lab[:, :, 0] = L_new
    lab[:, :, 1] = 128.0
    lab[:, :, 2] = 128.0
    return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2RGB)


def reinhard_color_transfer(src_rgb: np.ndarray, dst_rgb: np.ndarray, src_mask: np.ndarray,
                            dst_mask: np.ndarray) -> np.ndarray:
    src_lab = cv2.cvtColor(src_rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    dst_lab = cv2.cvtColor(dst_rgb, cv2.COLOR_RGB2LAB).astype(np.float32)

    if cv2.countNonZero(src_mask) == 0 or cv2.countNonZero(dst_mask) == 0:
        return src_rgb.copy()

    s_mean, s_std = cv2.meanStdDev(src_lab, mask=src_mask)
    d_mean, d_std = cv2.meanStdDev(dst_lab, mask=dst_mask)
    s_std = np.where(s_std == 0, 1.0, s_std)

    result_lab = src_lab.copy()
    for i in range(3):
        result_lab[:, :, i] = ((result_lab[:, :, i] - s_mean[i][0]) * (d_std[i][0] / s_std[i][0])) + d_mean[i][0]

    result_lab = np.clip(result_lab, 0, 255).astype(np.uint8)
    result_rgb = cv2.cvtColor(result_lab, cv2.COLOR_LAB2RGB)

    final = src_rgb.copy()
    mask_bool = src_mask > 128
    final[mask_bool] = result_rgb[mask_bool]
    return final
