#!/usr/bin/env python
"""Unit tests for the normalize_stacks/export helpers added by the
NeuNorm 2.0 port. The 1.x numeric semantics themselves are pinned by
test_normalization_contract.py; these cover the public-surface edges."""

import numpy as np
import pytest

from ibeatles.core.processing.normalization import (
    export_normalized_stack,
    normalize_stacks,
)

FRAMES, HEIGHT, WIDTH = 3, 8, 8


class TestInputHandling:
    def test_2d_input_promoted_to_single_frame(self):
        sample = np.full((HEIGHT, WIDTH), 6.0)
        ob = np.full((HEIGHT, WIDTH), 3.0)

        normalized = normalize_stacks(sample, ob_stack=ob)

        assert normalized.shape == (1, HEIGHT, WIDTH)
        np.testing.assert_allclose(normalized, 2.0, rtol=1e-6)

    def test_mismatched_frame_shapes_raise(self):
        sample = np.ones((FRAMES, HEIGHT, WIDTH))
        ob = np.ones((FRAMES, HEIGHT, WIDTH + 2))

        with pytest.raises(ValueError, match="same shape"):
            normalize_stacks(sample, ob_stack=ob)

    def test_output_is_float32(self):
        sample = np.ones((FRAMES, HEIGHT, WIDTH), dtype=np.float64)
        ob = np.ones((FRAMES, HEIGHT, WIDTH), dtype=np.float64)

        assert normalize_stacks(sample, ob_stack=ob).dtype == np.float32


class TestRoiBounds:
    """1.x inclusive-bounds rule: ROI (x0, y0, w, h) spans x0..x0+w, so a
    width-(N-1) ROI fills an N-wide image and width-N falls outside it."""

    def test_widest_fitting_roi_accepted(self):
        sample = np.ones((FRAMES, HEIGHT, WIDTH))

        normalized = normalize_stacks(sample, background_rois=[(0, 0, WIDTH - 1, HEIGHT - 1)])

        np.testing.assert_allclose(normalized, 1.0, rtol=1e-6)

    def test_roi_exceeding_image_raises(self):
        sample = np.ones((FRAMES, HEIGHT, WIDTH))

        with pytest.raises(ValueError, match="does not fit"):
            normalize_stacks(sample, background_rois=[(0, 0, WIDTH, HEIGHT - 1)])

    def test_negative_origin_raises(self):
        sample = np.ones((FRAMES, HEIGHT, WIDTH))

        with pytest.raises(ValueError, match="does not fit"):
            normalize_stacks(sample, background_rois=[(-1, 0, 2, 2)])


class TestSampleOnlyEdge:
    def test_sample_only_path_does_not_zero_inf(self):
        """1.x never zeroed NaN/inf in use_only_sample mode — a zero-count
        background ROI propagates inf instead of being masked. Pinned so
        the (deliberate) asymmetry with the OB path is not 'fixed' silently."""
        sample = np.ones((FRAMES, HEIGHT, WIDTH))
        sample[:, :3, :3] = 0.0  # ROI mean -> 0 -> division by zero

        normalized = normalize_stacks(sample, background_rois=[(0, 0, 2, 2)])

        assert np.isinf(normalized).any()


class TestExportNaming:
    def test_one_based_zero_padded_layout(self, tmp_path):
        stack = np.ones((FRAMES, HEIGHT, WIDTH), dtype=np.float32)

        paths = export_normalized_stack(stack, str(tmp_path))

        assert [p.split("/")[-1] for p in paths] == [
            "normalized_image_0001.tif",
            "normalized_image_0002.tif",
            "normalized_image_0003.tif",
        ]
