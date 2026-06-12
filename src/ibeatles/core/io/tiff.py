#!/usr/bin/env python
"""Float32 TIFF writing for analysis exports.

This is the on-disk format every iBeatles export site produced through
NeuNorm 1.x (PIL ``Image.fromarray`` on float32 frames): plain
single-page TIFFs that step3's folder re-import and downstream tools
read back. Keep the writer and dtype stable unless those readers move
with it.
"""

from pathlib import Path
from typing import Union

import numpy as np
from PIL import Image


def write_float32_tiff(data: np.ndarray, file_path: Union[str, Path]) -> None:
    """Write a 2D array as a single-page float32 TIFF.

    Parameters
    ----------
    data : np.ndarray
        2D image to write. Cast to float32, matching the NeuNorm 1.x
        writer this replaces.
    file_path : str or Path
        Full output path, extension included.
    """
    frame = np.asarray(data, dtype=np.float32)
    if frame.ndim != 2:
        raise ValueError(f"Expected a 2D image, got shape {frame.shape}")
    Image.fromarray(frame).save(str(file_path))
