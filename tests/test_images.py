import tempfile
import unittest
from pathlib import Path

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError:
    np = None


@unittest.skipIf(np is None, 'Optional image dependencies not installed')
class ImageTests(unittest.TestCase):
    def test_features_on_invented_images(self):
        from cueaudit.features import measure
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'image.png'
            rgb = np.full((32, 32, 3), 255, dtype=np.uint8)
            Image.fromarray(rgb).save(path)
            self.assertEqual(measure(path, 'foreground'), 0)
            rgb[:] = [0, 150, 0]
            Image.fromarray(rgb).save(path)
            self.assertEqual(measure(path, 'foreground'), 1)
            self.assertEqual(measure(path, 'color'), '1')
            rgb[:] = 0
            rgb[-6:, -6:] = 255
            Image.fromarray(rgb).save(path)
            self.assertEqual(measure(path, 'corner_patch'), '3')

    def test_color_transfer_preserves_unmasked_region(self):
        from cueaudit.interventions import reinhard_color_transfer
        source = np.full((8, 8, 3), [50, 80, 100], dtype=np.uint8)
        donor = np.full((8, 8, 3), [180, 120, 60], dtype=np.uint8)
        mask = np.zeros((8, 8), dtype=np.uint8)
        mask[:4] = 255
        result = reinhard_color_transfer(source, donor, mask, mask)
        np.testing.assert_array_equal(result[4:], source[4:])
        self.assertFalse(np.array_equal(result[:4], source[:4]))
        empty = np.zeros_like(mask)
        np.testing.assert_array_equal(reinhard_color_transfer(source, donor, empty, mask), source)

    def test_grayscale_normalization_shape_and_type(self):
        from cueaudit.interventions import equalize_luminance_and_grayscale
        source = np.full((8, 8, 3), [20, 100, 200], dtype=np.uint8)
        result = equalize_luminance_and_grayscale(source)
        self.assertEqual(result.shape, source.shape)
        self.assertEqual(result.dtype, np.uint8)
        self.assertLessEqual(int(np.abs(result.astype(int)[:, :, 0] - result[:, :, 1]).max()), 2)
