#!/usr/bin/env python
"""Value-pinning contract tests for normalize_data ahead of the NeuNorm 2.0 port.

The existing normalization tests assert only shapes and file existence, so a
port that returns wrong NUMBERS would pass (2026-06-12 audit, H finding).
These tests pin the 1.x numeric semantics against pinned NeuNorm 1.6.12 with
formula-based expectations the reviewer can check by hand:

- plain open-beam division (equal stack counts -> per-frame 1:1)
- pooled multi-ROI background ("air") normalization, including the
  INCLUSIVE ROI slicing (a width-w ROI covers w+1 pixels) that any
  replacement must reproduce for bit-compatibility
- sample-only ROI normalization when no OB is provided
- zero-OB pixels zeroed in the output (1.x maps NaN/inf to 0)
- mismatched sample/OB stack counts -> nanmedian(OB) fallback
- float32 output dtype, per-frame "normalized_*.tif" export whose on-disk
  pixel values round-trip the returned arrays
- ValueError when neither OB nor a background ROI is available

The moving-average paths are deliberately NOT pinned here: the audit found
the smoothing axis itself is wrong (H), and that fix is being coordinated
with the maintainer — pinning today's values would enshrine the bug.
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ibeatles.core.config import (
    AnalysisConfig,
    FittingConfig,
    IBeatlesUserConfig,
    Material,
    MovingAverage,
    NormalizationConfig,
    OpenBeamData,
    PixelBinning,
    RawData,
    SampleBackground,
    StrainMapping,
)
from ibeatles.core.processing.normalization import normalize_data

FRAMES, HEIGHT, WIDTH = 4, 12, 12


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def time_spectra(temp_dir):
    file_path = temp_dir / "image_Spectra.txt"
    file_path.write_text("dummy time spectra content")
    return {
        "filename": str(file_path),
        "short_filename": file_path.name,
        "tof_array": np.linspace(0, 100, FRAMES),
        "counts_array": np.ones(FRAMES),
        "lambda_array": np.linspace(0.5, 5, FRAMES),
    }


def _make_config(temp_dir, sample_background):
    raw_data_dir = temp_dir / "raw_data"
    raw_data_dir.mkdir(exist_ok=True)
    ob_data_dir = temp_dir / "ob_data"
    ob_data_dir.mkdir(exist_ok=True)
    output_dir = temp_dir / "output"
    output_dir.mkdir(exist_ok=True)
    return IBeatlesUserConfig(
        raw_data=RawData(raw_data_dir=str(raw_data_dir), extension=".tif"),
        open_beam=OpenBeamData(open_beam_data_dir=str(ob_data_dir), extension=".tif"),
        normalization=NormalizationConfig(
            sample_background=sample_background,
            moving_average=MovingAverage(active=False),
        ),
        analysis=AnalysisConfig(
            material=Material(element="Fe"),
            pixel_binning=PixelBinning(x0=0, y0=0, width=WIDTH, height=HEIGHT, bins_size=1),
            fitting=FittingConfig(lambda_min=0.5, lambda_max=5.0),
            strain_mapping=StrainMapping(),
            distance_source_detector_in_m=10.0,
            detector_offset_in_us=4500.0,
        ),
        output={
            "normalized_data_dir": str(output_dir),
            "analysis_results_dir": str(output_dir),
        },
    )


def _pooled_roi_mean(frame, rois):
    """1.x pooled-ROI mean: total counts over ALL ROIs / total ROI pixels,
    with INCLUSIVE slicing — ROI(x0, y0, width, height) covers
    frame[y0:y0+height+1, x0:x0+width+1]."""
    total = 0.0
    npix = 0
    for x0, y0, w, h in rois:
        region = frame[y0 : y0 + h + 1, x0 : x0 + w + 1]
        total += region.sum()
        npix += region.size
    return total / npix


class TestPlainObNormalization:
    def test_equal_counts_divide_one_to_one(self, temp_dir, time_spectra):
        """sample = 2*ob everywhere -> normalized == 2.0 exactly, per frame"""
        ob = np.full((FRAMES, HEIGHT, WIDTH), 5.0)
        sample = 2.0 * ob
        config = _make_config(temp_dir, sample_background=None)

        normalized, out = normalize_data(sample, ob, time_spectra, config, str(temp_dir))
        stack = np.array(normalized)

        assert stack.shape == (FRAMES, HEIGHT, WIDTH)
        assert stack.dtype == np.float32
        np.testing.assert_allclose(stack, 2.0, rtol=1e-6)

    def test_per_frame_pairing_not_pooled(self, temp_dir, time_spectra):
        """frame k of the sample divides by frame k of the OB, not a pooled OB"""
        ob = np.stack([np.full((HEIGHT, WIDTH), 1.0 + k) for k in range(FRAMES)])
        sample = np.stack([np.full((HEIGHT, WIDTH), (1.0 + k) * (k + 2.0)) for k in range(FRAMES)])
        config = _make_config(temp_dir, sample_background=None)

        normalized, _ = normalize_data(sample, ob, time_spectra, config, str(temp_dir))
        stack = np.array(normalized)

        for k in range(FRAMES):
            np.testing.assert_allclose(stack[k], k + 2.0, rtol=1e-6)


class TestBackgroundRoiNormalization:
    def test_pooled_multi_roi_air_normalization_with_ob(self, temp_dir, time_spectra):
        """with OB + background ROIs: each frame (sample AND ob) divides by
        the pooled mean over ALL its ROIs (inclusive slices), then
        sample/ob — expectations computed from first principles"""
        rng = np.random.default_rng(42)
        sample = rng.uniform(10.0, 20.0, size=(FRAMES, HEIGHT, WIDTH))
        ob = rng.uniform(5.0, 10.0, size=(FRAMES, HEIGHT, WIDTH))
        rois = [(0, 0, 3, 3), (7, 7, 3, 3)]
        config = _make_config(
            temp_dir,
            sample_background=[SampleBackground(x0=x, y0=y, width=w, height=h) for x, y, w, h in rois],
        )

        normalized, _ = normalize_data(sample, ob, time_spectra, config, str(temp_dir))
        stack = np.array(normalized)

        sample32 = sample.astype(np.float32)
        ob32 = ob.astype(np.float32)
        for k in range(FRAMES):
            sample_corr = sample32[k] / _pooled_roi_mean(sample32[k], rois)
            ob_corr = ob32[k] / _pooled_roi_mean(ob32[k], rois)
            np.testing.assert_allclose(stack[k], sample_corr / ob_corr, rtol=1e-5)

    def test_roi_slicing_is_inclusive(self, temp_dir, time_spectra):
        """the off-by-one is load-bearing: a width-3 ROI covers 4 columns.
        The frame is crafted so inclusive vs exclusive slicing changes the
        ROI mean, and the expectation only matches the inclusive version."""
        sample = np.ones((FRAMES, HEIGHT, WIDTH))
        # boundary row/column (index 4) carries a different value: included
        # only under 1.x's inclusive slicing of ROI(0, 0, width=4, height=4)
        sample[:, 4, : 4 + 1] = 9.0
        sample[:, : 4 + 1, 4] = 9.0
        config = _make_config(temp_dir, sample_background=[SampleBackground(x0=0, y0=0, width=4, height=4)])

        normalized, _ = normalize_data(sample, None, time_spectra, config, str(temp_dir))
        stack = np.array(normalized)

        inclusive_mean = _pooled_roi_mean(sample[0].astype(np.float32), [(0, 0, 4, 4)])
        exclusive_mean = sample[0, :4, :4].mean()
        assert not np.isclose(inclusive_mean, exclusive_mean), "fixture must discriminate the two slicings"
        np.testing.assert_allclose(stack[0], sample[0] / inclusive_mean, rtol=1e-5)

    def test_sample_only_roi_normalization_without_ob(self, temp_dir, time_spectra):
        """no OB: each sample frame divides by its own pooled ROI mean"""
        rng = np.random.default_rng(7)
        sample = rng.uniform(1.0, 4.0, size=(FRAMES, HEIGHT, WIDTH))
        rois = [(2, 2, 3, 3)]
        config = _make_config(
            temp_dir,
            sample_background=[SampleBackground(x0=2, y0=2, width=3, height=3)],
        )

        normalized, _ = normalize_data(sample, None, time_spectra, config, str(temp_dir))
        stack = np.array(normalized)

        sample32 = sample.astype(np.float32)
        for k in range(FRAMES):
            np.testing.assert_allclose(stack[k], sample32[k] / _pooled_roi_mean(sample32[k], rois), rtol=1e-5)

    def test_no_ob_and_no_background_raises(self, temp_dir, time_spectra):
        """1.x requires a ROI for sample-only normalization; the port must
        keep this loud failure instead of silently normalizing by nothing"""
        sample = np.ones((FRAMES, HEIGHT, WIDTH))
        config = _make_config(temp_dir, sample_background=None)

        with pytest.raises(ValueError):
            normalize_data(sample, None, time_spectra, config, str(temp_dir))


class TestEdgeSemantics:
    def test_zero_ob_pixels_zero_the_output(self, temp_dir, time_spectra):
        """1.x maps the NaN/inf from zero-OB division to 0 — the port must
        not propagate inf/NaN into downstream fitting"""
        ob = np.full((FRAMES, HEIGHT, WIDTH), 4.0)
        ob[:, 3, 5] = 0.0
        sample = np.full((FRAMES, HEIGHT, WIDTH), 8.0)
        config = _make_config(temp_dir, sample_background=None)

        normalized, _ = normalize_data(sample, ob, time_spectra, config, str(temp_dir))
        stack = np.array(normalized)

        assert np.all(stack[:, 3, 5] == 0.0)
        mask = np.ones((HEIGHT, WIDTH), dtype=bool)
        mask[3, 5] = False
        np.testing.assert_allclose(stack[:, mask], 2.0, rtol=1e-6)
        assert np.isfinite(stack).all()

    def test_mismatched_stack_counts_use_nanmedian_ob(self, temp_dir, time_spectra):
        """n_sample != n_ob: 1.x divides every sample frame by the
        nanmedian of the OB stack instead of pairing frames"""
        ob = np.stack([np.full((HEIGHT, WIDTH), v) for v in (2.0, 4.0)])  # nanmedian = 3.0
        sample = np.full((FRAMES, HEIGHT, WIDTH), 6.0)
        config = _make_config(temp_dir, sample_background=None)

        normalized, _ = normalize_data(sample, ob, time_spectra, config, str(temp_dir))
        stack = np.array(normalized)

        assert stack.shape[0] == FRAMES
        np.testing.assert_allclose(stack, 6.0 / 3.0, rtol=1e-6)


class TestExportContract:
    def test_per_frame_tiffs_round_trip_returned_values(self, temp_dir, time_spectra):
        """one normalized_*.tif per frame, on-disk float32 pixels identical
        to the returned arrays, and the time-spectra file copied alongside"""
        ob = np.full((FRAMES, HEIGHT, WIDTH), 5.0)
        sample = 3.0 * ob
        config = _make_config(temp_dir, sample_background=None)

        normalized, out = normalize_data(sample, ob, time_spectra, config, str(temp_dir))
        stack = np.array(normalized)

        tiffs = sorted(Path(out).glob("normalized_*.tif"))
        assert len(tiffs) == FRAMES
        for k, tiff in enumerate(tiffs):
            with Image.open(str(tiff)) as img:
                on_disk = np.array(img)
            assert on_disk.dtype == np.float32
            np.testing.assert_array_equal(on_disk, stack[k])
        assert (Path(out) / time_spectra["short_filename"]).exists()
