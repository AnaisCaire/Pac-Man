"""Resource loading fallbacks independent of a display window."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import numpy as np

from src.ui.gfx import raster


class RasterLoadingTests(unittest.TestCase):
    """Broken optional images remain visible and never stop startup."""

    def test_missing_and_corrupt_images_return_visible_rgba_placeholder(self) -> None:
        """Every loader failure shares one opaque, visible fallback contract."""
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.png"
            corrupt = Path(directory) / "corrupt.png"
            corrupt.write_bytes(b"not an image")

            with self.assertLogs("src.ui.gfx.raster", level="WARNING"):
                missing_image = raster.load_rgba(str(missing))
                corrupt_image = raster.load_rgba(str(corrupt))

        for image in (missing_image, corrupt_image):
            self.assertEqual(image.shape, (16, 16, 4))
            self.assertEqual(image.dtype, np.uint8)
            self.assertTrue(np.all(image[:, :, 3] == 255))
            self.assertGreater(np.count_nonzero(image[:, :, :3]), 0)


if __name__ == "__main__":
    unittest.main()
