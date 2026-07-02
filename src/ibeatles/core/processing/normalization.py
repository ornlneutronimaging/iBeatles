#!/usr/bin/env python
"""Normalization functions for the TOF imaging data.

NeuNorm 2.0 port (route (a), issue #412): the transmission division runs
through ``neunorm.processing.normalizer.normalize_transmission`` on scipp
DataArrays. The 1.x behaviors that 2.0 dropped are pinned by
tests/unit/ibeatles/core/processing/test_normalization_contract.py:

- in-memory stacks (2.0 loaders are path-based), float32 working dtype
- pooled multi-ROI background ("air") correction in the 1.x
  ratio-of-means form, with INCLUSIVE extents — ROI (x0, y0, w, h)
  covers (w+1) x (h+1) pixels. As of NeuNorm 2.2.1 this is native:
  ``background_roi=[ROI(..., inclusive=True), ...]`` (pooled) and
  ``apply_background_roi`` (sample-only), so no local re-implementation
  remains (NeuNorm #159/#172).
- per-frame 1:1 OB pairing when stack counts match, nanmedian(OB)
  fallback when they don't
- zero-OB pixels (NaN/inf after division) zeroed in the output; the
  sample-only path does NOT zero, matching 1.x
- per-frame ``normalized_image_NNNN.tif`` export (1-based), the on-disk
  layout the GUI's step3 folder re-import depends on

No variances are attached to the DataArrays: iBeatles stacks may be
pre-smoothed (moving average) or contain negative pixels, so Poisson
(counts == variance) statistics would be wrong.
"""

import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipp as sc
from neunorm.data_models.roi import ROI
from neunorm.processing.normalizer import apply_background_roi, normalize_transmission

from ibeatles.core.config import IBeatlesUserConfig
from ibeatles.core.io.tiff import write_float32_tiff
from ibeatles.core.processing.moving_average import moving_average

# (x0, y0, width, height) with 1.x inclusive extents: the region spans
# columns x0..x0+width and rows y0..y0+height, boundaries included.
BackgroundROI = Tuple[int, int, int, int]


def normalize_data(
    sample_data: np.ndarray,
    ob_data: Optional[np.ndarray],
    time_spectra: Dict[str, Any],
    config: IBeatlesUserConfig,
    output_folder: str,
) -> Tuple[np.ndarray, str]:
    """
    Normalize the input data based on the provided configuration.

    Parameters:
    -----------
    sample_data : np.ndarray
        The raw sample data to be normalized.
    ob_data : Optional[np.ndarray]
        The open beam data, if available.
    time_spectra : Dict[str, Any]
        Time spectra information as returned by load_time_spectra function.
    config : IBeatlesUserConfig
        Configuration object containing normalization settings.
    output_folder : str
        Base output folder for normalized data.

    Returns:
    --------
    Tuple[np.ndarray, str]
        A tuple containing the normalized data and the full path to the output folder.
    """
    logging.info("Starting normalization process")

    sample_stack = np.asarray(sample_data, dtype=np.float32)
    ob_stack = np.asarray(ob_data, dtype=np.float32) if ob_data is not None else None

    # Apply moving average if configured
    if config.normalization.moving_average.active:
        if config.normalization.processing_order == "Moving average, Normalization":
            logging.info("Applying moving average")
            sample_stack = moving_average(sample_stack, config.normalization.moving_average)
            if ob_stack is not None:
                ob_stack = moving_average(ob_stack, config.normalization.moving_average)

    # Perform normalization
    logging.info("Performing normalization")
    normalized = normalize_stacks(
        sample_stack,
        ob_stack=ob_stack,
        background_rois=_get_background_rois(config),
    )

    # Apply moving average after normalization if configured
    if (
        config.normalization.moving_average.active
        and config.normalization.processing_order == "Normalization, Moving Average"
    ):
        logging.info("Applying moving average after normalization")
        normalized = moving_average(np.array(normalized), config.normalization.moving_average)

    # Export normalized data
    full_output_folder = _create_output_folder(output_folder, config)
    export_normalized_stack(normalized, full_output_folder)

    # Move time spectra file
    _copy_time_spectra(time_spectra, full_output_folder)

    return normalized, full_output_folder


def normalize_stacks(
    sample_stack: np.ndarray,
    ob_stack: Optional[np.ndarray] = None,
    background_rois: Optional[Sequence[BackgroundROI]] = None,
) -> np.ndarray:
    """Normalize an in-memory sample stack, with 1.x NeuNorm semantics.

    This is the single math path shared by the headless pipeline
    (``normalize_data``) and the GUI (step2). Inputs are cast to float32
    (the 1.x working dtype), the division runs through NeuNorm 2.0 on
    float64 scipp DataArrays, and the result is cast back to float32.

    Parameters
    ----------
    sample_stack : np.ndarray
        Sample images, shape (n_frames, height, width).
    ob_stack : np.ndarray, optional
        Open beam images, shape (n_ob, height, width). Frame shape must
        match the sample. When n_ob != n_frames, the nanmedian of the
        (ROI-corrected) OB stack is used as a single open beam.
    background_rois : sequence of (x0, y0, width, height), optional
        Background regions with inclusive 1.x extents. With an OB, each
        sample and OB frame is divided by its own pooled mean over all
        ROIs before the transmission division. Without an OB, at least
        one ROI is required and each sample frame is divided by its
        pooled ROI mean.

    Returns
    -------
    np.ndarray
        float32 stack, shape (n_frames, height, width).

    Raises
    ------
    ValueError
        If no OB and no background ROI is provided, if a ROI does not
        fit inside the image, or if sample and OB frame shapes differ.
    """
    sample_stack = _as_float32_stack(sample_stack)
    rois = [tuple(int(value) for value in roi) for roi in (background_rois or [])]
    _validate_rois(rois, frame_shape=sample_stack.shape[1:])
    # NeuNorm pools a sequence of ROIs as sum(counts)/sum(pixels) per frame — the 1.x
    # ratio-of-means form — and inclusive=True keeps the 1.x (w+1) x (h+1) extents.
    background_roi = [ROI(x0=x0, y0=y0, width=width, height=height, inclusive=True) for x0, y0, width, height in rois]

    sample = _make_data_array(sample_stack)

    if ob_stack is None:
        if not background_roi:
            raise ValueError("You need to provide at least 1 background ROI to normalize without open beam data!")
        # strict=False: 1.x lets a zero-count ROI propagate inf here (pinned by tests)
        corrected = apply_background_roi(sample, background_roi, strict=False)
        # 1.x does not zero NaN/inf in the sample-only path
        return corrected.values.astype(np.float32)

    ob_stack = _as_float32_stack(ob_stack)
    if ob_stack.shape[1:] != sample_stack.shape[1:]:
        raise ValueError("Sample and open beam frames do not have the same shape!")

    ob = _make_data_array(ob_stack)

    if ob_stack.shape[0] != sample_stack.shape[0]:
        # 1.x fallback: flux-flatten each stack by its pooled ROI mean, then collapse
        # the (ROI-corrected) OB to its per-pixel nanmedian and divide every sample
        # frame by it
        if background_roi:
            sample = apply_background_roi(sample, background_roi, strict=False)
            ob = apply_background_roi(ob, background_roi, strict=False)
        ob = _collapse_to_nanmedian(ob)
        transmission = normalize_transmission(sample, ob)
    else:
        # 1:1 pairing: NeuNorm applies the pooled flux proxy on both sides natively,
        # T = (S / pool(S[B])) / (O / pool(O[B]))
        transmission = normalize_transmission(
            sample, ob, background_roi=background_roi or None, background_roi_strict=False
        )

    # 1.x zeroes the NaN/inf that zero-OB pixels produce
    normalized = np.nan_to_num(transmission.values, nan=0.0, posinf=0.0, neginf=0.0)
    return normalized.astype(np.float32)


def export_normalized_stack(normalized: np.ndarray, folder: str) -> List[str]:
    """Export one float32 TIFF per frame, in the 1.x on-disk layout.

    Files are named ``normalized_image_NNNN.tif`` with a 1-based index —
    the layout step3's folder re-import and the existing tests expect.

    Returns the list of file paths written.
    """
    paths = []
    for index, frame in enumerate(normalized, start=1):
        path = Path(folder) / f"normalized_image_{index:04d}.tif"
        write_float32_tiff(frame, path)
        paths.append(str(path))
    return paths


def _as_float32_stack(data: np.ndarray) -> np.ndarray:
    """Cast to the 1.x float32 working dtype and promote 2D to a 1-frame stack."""
    stack = np.asarray(data, dtype=np.float32)
    if stack.ndim == 2:
        stack = stack[np.newaxis, :, :]
    if stack.ndim != 3:
        raise ValueError(f"Expected a 2D image or 3D stack, got shape {stack.shape}")
    return stack


def _make_data_array(stack: np.ndarray) -> sc.DataArray:
    """Build a scipp DataArray from an in-memory stack (no variances)."""
    values = np.ascontiguousarray(stack, dtype=np.float64)
    _, n_y, n_x = values.shape
    return sc.DataArray(
        data=sc.array(dims=["N_image", "y", "x"], values=values, unit=sc.units.counts),
        coords={
            "y": sc.arange("y", n_y, unit=None),
            "x": sc.arange("x", n_x, unit=None),
        },
    )


def _collapse_to_nanmedian(images: sc.DataArray) -> sc.DataArray:
    """Collapse a stack to its per-pixel nanmedian (the 1.x mismatched-counts OB)."""
    median = np.nanmedian(images.values, axis=0)
    return sc.DataArray(
        data=sc.array(dims=["y", "x"], values=median, unit=images.unit),
        coords={"y": images.coords["y"], "x": images.coords["x"]},
    )


def _validate_rois(rois: Sequence[BackgroundROI], frame_shape: Tuple[int, int]) -> None:
    """Reject ROIs that do not fit, with the 1.x inclusive-bounds rule."""
    n_y, n_x = frame_shape
    for x0, y0, width, height in rois:
        if x0 < 0 or y0 < 0 or x0 + width >= n_x or y0 + height >= n_y:
            raise ValueError("roi does not fit into sample image!")


def _get_background_rois(config: IBeatlesUserConfig) -> Optional[List[BackgroundROI]]:
    """Extract background ROIs from configuration."""
    if config.normalization.sample_background:
        return [(bg.x0, bg.y0, bg.width, bg.height) for bg in config.normalization.sample_background]
    return None


def _create_output_folder(base_folder: str, config: IBeatlesUserConfig) -> str:
    """Create and return the full path to the output folder."""
    sample_name = Path(config.raw_data.raw_data_dir).name
    full_output_folder = Path(base_folder) / f"{sample_name}_normalized"
    full_output_folder.mkdir(parents=True, exist_ok=True)
    return str(full_output_folder)


def _copy_time_spectra(time_spectra: Dict[str, Any], output_folder: str) -> None:
    """Copy time spectra file to the output folder."""
    source_file = time_spectra["filename"]
    dest_file = Path(output_folder) / time_spectra["short_filename"]
    shutil.copy(str(source_file), str(dest_file))
    logging.info(f"Copied time spectra file to {dest_file}")
