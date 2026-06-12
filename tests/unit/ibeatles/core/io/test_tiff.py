#!/usr/bin/env python
"""Unit tests for the float32 TIFF writer (the 1.x-compatible export format)."""

import numpy as np
import pytest
from PIL import Image

from ibeatles.core.io.tiff import write_float32_tiff


def test_round_trip_preserves_float32_pixels(tmp_path):
    frame = np.linspace(0.0, 1.0, 64, dtype=np.float64).reshape(8, 8)
    path = tmp_path / "frame.tif"

    write_float32_tiff(frame, path)

    with Image.open(str(path)) as img:
        on_disk = np.array(img)
    assert on_disk.dtype == np.float32
    np.testing.assert_array_equal(on_disk, frame.astype(np.float32))


def test_rejects_non_2d_input(tmp_path):
    with pytest.raises(ValueError, match="2D"):
        write_float32_tiff(np.ones((2, 4, 4)), tmp_path / "bad.tif")
