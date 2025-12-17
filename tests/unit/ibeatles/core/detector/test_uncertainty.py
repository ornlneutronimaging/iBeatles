#!/usr/bin/env python
"""Unit tests for TPX1 detector uncertainty calculations."""

import numpy as np
import pandas as pd
import pytest

from ibeatles.core.detector.uncertainty import (
    _compute_variance,
    _recover_raw_counts,
    compute_counts_with_uncertainty,
    load_shutter_counts,
)


class TestLoadShutterCounts:
    """Tests for load_shutter_counts function."""

    def test_loads_valid_file(self, tmp_path):
        """Test loading a valid shutter counts file."""
        # Create test file
        file_path = tmp_path / "ShutterCount.txt"
        file_path.write_text("0\t100000\n1\t101000\n2\t105000\n3\t0\n4\t0\n")

        df = load_shutter_counts(file_path)

        # Should have 3 rows (zeros filtered out)
        assert len(df) == 3
        assert list(df.columns) == ["shutter_index", "shutter_counts", "shutter_n_ratio"]

        # Check values
        assert df.loc[0, "shutter_counts"] == 100000
        assert df.loc[1, "shutter_counts"] == 101000
        assert df.loc[2, "shutter_counts"] == 105000

        # Check ratio calculation
        assert df.loc[0, "shutter_n_ratio"] == 1.0
        assert df.loc[1, "shutter_n_ratio"] == pytest.approx(1.01)
        assert df.loc[2, "shutter_n_ratio"] == pytest.approx(1.05)

    def test_raises_on_missing_file(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError):
            load_shutter_counts("/nonexistent/path/ShutterCount.txt")

    def test_raises_on_empty_file(self, tmp_path):
        """Test that ValueError is raised if no valid counts."""
        file_path = tmp_path / "ShutterCount.txt"
        file_path.write_text("0\t0\n1\t0\n")

        with pytest.raises(ValueError, match="No valid shutter counts"):
            load_shutter_counts(file_path)


class TestRecoverRawCounts:
    """Tests for _recover_raw_counts function."""

    def test_simple_case(self):
        """Test recovery with simple uniform data."""
        # Create simple test case: 5 frames, 2x2 pixels
        # All corrected values = 100, shutter_counts = 1000000 (low occupancy)
        n_frames, height, width = 5, 2, 2
        corrected = np.full((n_frames, height, width), 100.0)
        shutter_counts = 1000000
        shutter_n_ratio = 1.0

        raw, occupancy = _recover_raw_counts(corrected, shutter_counts, shutter_n_ratio)

        # Check shapes
        assert raw.shape == corrected.shape
        assert occupancy.shape == corrected.shape

        # With low occupancy, raw should be close to corrected
        # F_i ≈ T_i when P_i ≈ 0
        assert np.allclose(raw[0], corrected[0], rtol=0.01)

        # Occupancy should increase with frame index
        for i in range(1, n_frames):
            assert np.all(occupancy[i] > occupancy[i - 1])

    def test_occupancy_increases_monotonically(self):
        """Test that occupancy increases with each frame."""
        n_frames, height, width = 10, 4, 4
        corrected = np.random.uniform(50, 150, (n_frames, height, width))
        shutter_counts = 500000
        shutter_n_ratio = 1.0

        _, occupancy = _recover_raw_counts(corrected, shutter_counts, shutter_n_ratio)

        # Occupancy should be monotonically increasing
        for i in range(1, n_frames):
            assert np.all(occupancy[i] >= occupancy[i - 1])

    def test_with_varying_shutter_ratio(self):
        """Test with array of shutter ratios."""
        n_frames, height, width = 3, 2, 2
        corrected = np.full((n_frames, height, width), 100.0)
        shutter_counts = 1000000
        shutter_n_ratio = np.array([1.0, 1.01, 1.02])

        raw, occupancy = _recover_raw_counts(corrected, shutter_counts, shutter_n_ratio)

        # Should complete without error
        assert raw.shape == corrected.shape
        assert occupancy.shape == corrected.shape


class TestComputeVariance:
    """Tests for _compute_variance function."""

    def test_variance_formula(self):
        """Test that variance follows Var(T) = T / ((1 - P) * s)."""
        corrected = np.array([[[100.0, 200.0], [150.0, 50.0]]])
        occupancy = np.array([[[0.1, 0.2], [0.15, 0.05]]])
        shutter_n_ratio = 1.0

        variance = _compute_variance(corrected, occupancy, shutter_n_ratio)

        expected = corrected / ((1 - occupancy) * shutter_n_ratio)
        np.testing.assert_allclose(variance, expected)

    def test_variance_increases_with_occupancy(self):
        """Test that variance increases with higher occupancy."""
        corrected = np.full((1, 2, 2), 100.0)
        occupancy_low = np.full((1, 2, 2), 0.1)
        occupancy_high = np.full((1, 2, 2), 0.5)
        shutter_n_ratio = 1.0

        var_low = _compute_variance(corrected, occupancy_low, shutter_n_ratio)
        var_high = _compute_variance(corrected, occupancy_high, shutter_n_ratio)

        assert np.all(var_high > var_low)

    def test_variance_non_negative(self):
        """Test that variance is always non-negative."""
        corrected = np.random.uniform(0, 200, (10, 4, 4))
        occupancy = np.random.uniform(0, 0.8, (10, 4, 4))
        shutter_n_ratio = 1.0

        variance = _compute_variance(corrected, occupancy, shutter_n_ratio)

        assert np.all(variance >= 0)


class TestComputeCountsWithUncertainty:
    """Tests for compute_counts_with_uncertainty function."""

    @pytest.fixture
    def shutter_file(self, tmp_path):
        """Create a temporary shutter counts file."""
        file_path = tmp_path / "ShutterCount.txt"
        file_path.write_text("0\t200000\n1\t0\n2\t0\n")
        return file_path

    def test_basic_usage(self, shutter_file):
        """Test basic usage with synthetic data."""
        n_frames, height, width = 10, 8, 8
        tiff_stack = np.random.uniform(50, 150, (n_frames, height, width))
        tof_array = np.linspace(1000, 2000, n_frames)

        result = compute_counts_with_uncertainty(
            tiff_stack=tiff_stack,
            tof_array=tof_array,
            shutter_counts_file=shutter_file,
        )

        # Check output structure
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["tof", "counts", "uncertainty"]
        assert len(result) == n_frames

        # Check values are reasonable
        assert np.all(result["counts"] > 0)
        assert np.all(result["uncertainty"] > 0)
        assert np.all(np.isfinite(result["counts"]))
        assert np.all(np.isfinite(result["uncertainty"]))

    def test_with_roi_mask(self, shutter_file):
        """Test with ROI mask."""
        n_frames, height, width = 5, 10, 10
        tiff_stack = np.ones((n_frames, height, width)) * 100.0
        tof_array = np.arange(n_frames)

        # Create ROI: 4x4 box = 16 pixels
        roi_mask = np.zeros((height, width), dtype=bool)
        roi_mask[3:7, 3:7] = True

        result = compute_counts_with_uncertainty(
            tiff_stack=tiff_stack,
            tof_array=tof_array,
            shutter_counts_file=shutter_file,
            roi_mask=roi_mask,
        )

        # Counts should be 16 pixels * 100 = 1600 per frame
        np.testing.assert_allclose(result["counts"], 1600.0)

    def test_uncertainty_scales_with_roi_size(self, shutter_file):
        """Test that smaller ROI has larger relative uncertainty."""
        n_frames, height, width = 5, 20, 20
        tiff_stack = np.ones((n_frames, height, width)) * 100.0
        tof_array = np.arange(n_frames)

        # Small ROI: 2x2 = 4 pixels
        roi_small = np.zeros((height, width), dtype=bool)
        roi_small[9:11, 9:11] = True

        # Large ROI: 10x10 = 100 pixels
        roi_large = np.zeros((height, width), dtype=bool)
        roi_large[5:15, 5:15] = True

        result_small = compute_counts_with_uncertainty(
            tiff_stack=tiff_stack,
            tof_array=tof_array,
            shutter_counts_file=shutter_file,
            roi_mask=roi_small,
        )

        result_large = compute_counts_with_uncertainty(
            tiff_stack=tiff_stack,
            tof_array=tof_array,
            shutter_counts_file=shutter_file,
            roi_mask=roi_large,
        )

        # Relative uncertainty should be larger for smaller ROI
        rel_unc_small = result_small["uncertainty"] / result_small["counts"]
        rel_unc_large = result_large["uncertainty"] / result_large["counts"]

        assert np.all(rel_unc_small > rel_unc_large)

    def test_raises_on_shape_mismatch(self, shutter_file):
        """Test that shape mismatches raise errors."""
        tiff_stack = np.ones((10, 8, 8))
        tof_array = np.arange(5)  # Wrong length

        with pytest.raises(ValueError, match="tof_array length"):
            compute_counts_with_uncertainty(
                tiff_stack=tiff_stack,
                tof_array=tof_array,
                shutter_counts_file=shutter_file,
            )

    def test_raises_on_invalid_roi_shape(self, shutter_file):
        """Test that invalid ROI shape raises error."""
        tiff_stack = np.ones((10, 8, 8))
        tof_array = np.arange(10)
        roi_mask = np.ones((4, 4), dtype=bool)  # Wrong shape

        with pytest.raises(ValueError, match="roi_mask shape"):
            compute_counts_with_uncertainty(
                tiff_stack=tiff_stack,
                tof_array=tof_array,
                shutter_counts_file=shutter_file,
                roi_mask=roi_mask,
            )


class TestIntegration:
    """Integration tests simulating real workflow."""

    def test_round_trip_consistency(self, tmp_path):
        """Test that the pipeline produces consistent results."""
        # Create shutter file
        shutter_file = tmp_path / "ShutterCount.txt"
        shutter_file.write_text("0\t500000\n")

        # Create synthetic data
        np.random.seed(42)
        n_frames, height, width = 20, 16, 16
        tiff_stack = np.random.uniform(80, 120, (n_frames, height, width))
        tof_array = np.linspace(1000, 5000, n_frames)

        # Full image (no ROI)
        result1 = compute_counts_with_uncertainty(
            tiff_stack=tiff_stack,
            tof_array=tof_array,
            shutter_counts_file=shutter_file,
        )

        # Run again - should get same result
        result2 = compute_counts_with_uncertainty(
            tiff_stack=tiff_stack,
            tof_array=tof_array,
            shutter_counts_file=shutter_file,
        )

        pd.testing.assert_frame_equal(result1, result2)

    def test_csv_export(self, tmp_path):
        """Test that result can be exported to CSV."""
        # Create shutter file
        shutter_file = tmp_path / "ShutterCount.txt"
        shutter_file.write_text("0\t200000\n")

        # Create data
        n_frames = 10
        tiff_stack = np.ones((n_frames, 4, 4)) * 100.0
        tof_array = np.arange(n_frames)

        result = compute_counts_with_uncertainty(
            tiff_stack=tiff_stack,
            tof_array=tof_array,
            shutter_counts_file=shutter_file,
        )

        # Export to CSV
        csv_path = tmp_path / "output.csv"
        result.to_csv(csv_path, index=False)

        # Read back and verify
        loaded = pd.read_csv(csv_path)
        assert list(loaded.columns) == ["tof", "counts", "uncertainty"]
        assert len(loaded) == n_frames


if __name__ == "__main__":
    pytest.main(["-v", __file__])
