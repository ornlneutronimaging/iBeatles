#!/usr/bin/env python
"""Unit tests for TPX1 detector uncertainty calculations."""

import numpy as np
import pytest

from ibeatles.core.detector.uncertainty import (
    OCCUPANCY_THRESHOLD_CAUTION,
    OCCUPANCY_THRESHOLD_SAFE,
    OCCUPANCY_THRESHOLD_WARNING,
    ZeroCountMethod,
    aggregate_roi_uncertainty,
    calculate_relative_uncertainty,
    calculate_transmission_std,
    calculate_transmission_variance,
    check_occupancy_validity,
    handle_zero_counts,
)


class TestCalculateTransmissionVariance:
    """Tests for calculate_transmission_variance function."""

    def test_basic_variance_calculation(self):
        """Test basic variance formula: Var(T) = T / ((1 - P) * s)."""
        transmission = np.array([100.0, 150.0, 200.0])
        occupancy = np.array([0.1, 0.2, 0.3])
        shutter_n_ratio = 1.0

        variance = calculate_transmission_variance(transmission, occupancy, shutter_n_ratio)

        expected = transmission / ((1 - occupancy) * shutter_n_ratio)
        np.testing.assert_allclose(variance, expected)

    def test_variance_with_array_shutter_ratio(self):
        """Test variance with per-frame shutter ratio."""
        transmission = np.array([100.0, 150.0, 200.0])
        occupancy = np.array([0.1, 0.2, 0.3])
        shutter_n_ratio = np.array([1.0, 1.01, 1.05])

        variance = calculate_transmission_variance(transmission, occupancy, shutter_n_ratio)

        expected = transmission / ((1 - occupancy) * shutter_n_ratio)
        np.testing.assert_allclose(variance, expected)

    def test_variance_2d_array(self):
        """Test variance calculation with 2D image data."""
        transmission = np.ones((10, 10)) * 100.0
        occupancy = np.ones((10, 10)) * 0.2
        shutter_n_ratio = 1.0

        variance = calculate_transmission_variance(transmission, occupancy, shutter_n_ratio)

        assert variance.shape == (10, 10)
        expected_value = 100.0 / (0.8 * 1.0)  # 125.0
        np.testing.assert_allclose(variance, expected_value)

    def test_variance_3d_array(self):
        """Test variance calculation with 3D stack (frames, height, width)."""
        n_frames, height, width = 5, 10, 10
        transmission = np.ones((n_frames, height, width)) * 100.0
        occupancy = np.linspace(0.1, 0.3, n_frames)[:, np.newaxis, np.newaxis]
        occupancy = np.broadcast_to(occupancy, (n_frames, height, width)).copy()
        shutter_n_ratio = 1.0

        variance = calculate_transmission_variance(transmission, occupancy, shutter_n_ratio)

        assert variance.shape == (n_frames, height, width)

    def test_variance_rejects_high_occupancy(self):
        """Test that occupancy >= 1.0 raises ValueError."""
        transmission = np.array([100.0])
        occupancy = np.array([1.0])  # Invalid
        shutter_n_ratio = 1.0

        with pytest.raises(ValueError, match="Occupancy values must be < 1.0"):
            calculate_transmission_variance(transmission, occupancy, shutter_n_ratio)

    def test_variance_rejects_negative_shutter_ratio(self):
        """Test that non-positive shutter ratio raises ValueError."""
        transmission = np.array([100.0])
        occupancy = np.array([0.1])
        shutter_n_ratio = 0.0  # Invalid

        with pytest.raises(ValueError, match="Shutter ratio must be positive"):
            calculate_transmission_variance(transmission, occupancy, shutter_n_ratio)

    def test_variance_non_negative(self):
        """Test that variance is always non-negative."""
        transmission = np.array([0.0, 1.0, 100.0])
        occupancy = np.array([0.1, 0.2, 0.3])
        shutter_n_ratio = 1.0

        variance = calculate_transmission_variance(transmission, occupancy, shutter_n_ratio)

        assert np.all(variance >= 0)


class TestCalculateTransmissionStd:
    """Tests for calculate_transmission_std function."""

    def test_std_is_sqrt_variance(self):
        """Test that std equals sqrt(variance)."""
        transmission = np.array([100.0, 150.0, 200.0])
        occupancy = np.array([0.1, 0.2, 0.3])
        shutter_n_ratio = 1.0

        std = calculate_transmission_std(transmission, occupancy, shutter_n_ratio)
        variance = calculate_transmission_variance(transmission, occupancy, shutter_n_ratio)

        np.testing.assert_allclose(std, np.sqrt(variance))


class TestHandleZeroCounts:
    """Tests for handle_zero_counts function."""

    def test_none_method_preserves_zeros(self):
        """Test NONE method preserves zero values."""
        transmission = np.array([0.0, 100.0, 0.0])
        occupancy = np.array([0.1, 0.2, 0.3])
        shutter_n_ratio = 1.0

        result = handle_zero_counts(transmission, occupancy, shutter_n_ratio, ZeroCountMethod.NONE)

        np.testing.assert_array_equal(result, transmission)

    def test_anscombe_method(self):
        """Test Anscombe transform adds 0.375."""
        transmission = np.array([0.0, 100.0, 200.0])
        occupancy = np.array([0.1, 0.2, 0.3])
        shutter_n_ratio = 1.0

        result = handle_zero_counts(transmission, occupancy, shutter_n_ratio, ZeroCountMethod.ANSCOMBE)

        expected = transmission + 0.375
        np.testing.assert_allclose(result, expected)

    def test_small_constant_method(self):
        """Test SMALL_CONSTANT method replaces zeros with 0.5."""
        transmission = np.array([0.0, 100.0, 0.0])
        occupancy = np.array([0.1, 0.2, 0.3])
        shutter_n_ratio = 1.0

        result = handle_zero_counts(transmission, occupancy, shutter_n_ratio, ZeroCountMethod.SMALL_CONSTANT)

        expected = np.array([0.5, 100.0, 0.5])
        np.testing.assert_allclose(result, expected)

    def test_minimum_count_method(self):
        """Test MINIMUM_COUNT method replaces zeros with T_min."""
        transmission = np.array([0.0, 100.0, 0.0])
        occupancy = np.array([0.1, 0.2, 0.3])
        shutter_n_ratio = 1.0

        result = handle_zero_counts(transmission, occupancy, shutter_n_ratio, ZeroCountMethod.MINIMUM_COUNT)

        # T_min = 1 / ((1 - P) * s) for each zero position
        T_min_0 = 1.0 / ((1.0 - 0.1) * 1.0)  # ~1.111
        T_min_2 = 1.0 / ((1.0 - 0.3) * 1.0)  # ~1.429
        expected = np.array([T_min_0, 100.0, T_min_2])
        np.testing.assert_allclose(result, expected)


class TestCheckOccupancyValidity:
    """Tests for check_occupancy_validity function."""

    def test_safe_occupancy(self):
        """Test safe occupancy level detection."""
        occupancy = np.random.uniform(0.0, 0.4, size=(100, 100))

        warning = check_occupancy_validity(occupancy)

        assert warning.level == "safe"
        assert warning.max_occupancy < OCCUPANCY_THRESHOLD_SAFE

    def test_caution_occupancy(self):
        """Test caution occupancy level detection."""
        occupancy = np.full((100, 100), 0.6)  # Between safe and caution thresholds

        warning = check_occupancy_validity(occupancy)

        assert warning.level == "caution"
        assert OCCUPANCY_THRESHOLD_SAFE <= warning.max_occupancy < OCCUPANCY_THRESHOLD_CAUTION

    def test_warning_occupancy(self):
        """Test warning occupancy level detection."""
        occupancy = np.full((100, 100), 0.8)  # Between caution and warning thresholds

        warning = check_occupancy_validity(occupancy)

        assert warning.level == "warning"
        assert OCCUPANCY_THRESHOLD_CAUTION <= warning.max_occupancy < OCCUPANCY_THRESHOLD_WARNING

    def test_critical_occupancy(self):
        """Test critical occupancy level detection."""
        occupancy = np.full((100, 100), 0.95)  # Above warning threshold

        warning = check_occupancy_validity(occupancy)

        assert warning.level == "critical"
        assert warning.max_occupancy >= OCCUPANCY_THRESHOLD_WARNING

    def test_affected_fraction_calculation(self):
        """Test that affected fraction is calculated correctly."""
        # Create array where 25% of pixels are above safe threshold
        occupancy = np.zeros((10, 10))
        occupancy[:5, :5] = 0.6  # 25 pixels above threshold

        warning = check_occupancy_validity(occupancy)

        assert warning.affected_fraction == 0.25

    def test_warning_dataclass_fields(self):
        """Test that OccupancyWarning has all expected fields."""
        occupancy = np.array([0.3, 0.4, 0.5])

        warning = check_occupancy_validity(occupancy)

        assert hasattr(warning, "level")
        assert hasattr(warning, "max_occupancy")
        assert hasattr(warning, "affected_fraction")
        assert hasattr(warning, "message")
        assert isinstance(warning.message, str)


class TestAggregateRoiUncertainty:
    """Tests for aggregate_roi_uncertainty function."""

    def test_full_array_aggregation(self):
        """Test aggregation over entire array without mask."""
        # 100 pixels with variance = 10 each
        # Expected: roi_var = 10 / 100 = 0.1
        variance = np.ones((10, 10)) * 10.0

        roi_var, roi_std = aggregate_roi_uncertainty(variance)

        np.testing.assert_allclose(roi_var, 0.1)
        np.testing.assert_allclose(roi_std, np.sqrt(0.1))

    def test_masked_aggregation(self):
        """Test aggregation with ROI mask."""
        variance = np.ones((10, 10)) * 10.0
        roi_mask = np.zeros((10, 10), dtype=bool)
        roi_mask[4:6, 4:6] = True  # 4 pixels

        # Expected: roi_var = 10 / 4 = 2.5
        roi_var, roi_std = aggregate_roi_uncertainty(variance, roi_mask)

        np.testing.assert_allclose(roi_var, 2.5)
        np.testing.assert_allclose(roi_std, np.sqrt(2.5))

    def test_correlation_factor(self):
        """Test that correlation factor reduces effective N."""
        variance = np.ones((10, 10)) * 10.0  # 100 pixels

        # Without correlation: roi_var = 10 / 100 = 0.1
        roi_var_uncorrelated, _ = aggregate_roi_uncertainty(variance, correlation_factor=1.0)

        # With correlation factor 2: N_eff = 50, roi_var = 10 / 50 = 0.2
        roi_var_correlated, _ = aggregate_roi_uncertainty(variance, correlation_factor=2.0)

        np.testing.assert_allclose(roi_var_uncorrelated, 0.1)
        np.testing.assert_allclose(roi_var_correlated, 0.2)

    def test_empty_roi(self):
        """Test that empty ROI returns zeros."""
        variance = np.ones((10, 10)) * 10.0
        roi_mask = np.zeros((10, 10), dtype=bool)  # No pixels selected

        roi_var, roi_std = aggregate_roi_uncertainty(variance, roi_mask)

        assert roi_var == 0.0
        assert roi_std == 0.0

    def test_3d_variance_with_2d_mask(self):
        """Test 3D variance array with 2D ROI mask."""
        n_frames = 5
        variance = np.ones((n_frames, 10, 10)) * 10.0
        roi_mask = np.zeros((10, 10), dtype=bool)
        roi_mask[4:6, 4:6] = True  # 4 pixels per frame

        roi_var, roi_std = aggregate_roi_uncertainty(variance, roi_mask)

        # mean(var) = 10, n_pixels = 4
        # roi_var = 10 / 4 = 2.5
        np.testing.assert_allclose(roi_var, 2.5)


class TestCalculateRelativeUncertainty:
    """Tests for calculate_relative_uncertainty function."""

    def test_relative_uncertainty(self):
        """Test relative uncertainty calculation."""
        transmission = np.array([100.0, 200.0, 50.0])
        std = np.array([10.0, 10.0, 10.0])

        relative = calculate_relative_uncertainty(transmission, std)

        expected = np.array([0.1, 0.05, 0.2])
        np.testing.assert_allclose(relative, expected)

    def test_handles_zero_transmission(self):
        """Test that zero transmission doesn't cause division by zero."""
        transmission = np.array([0.0, 100.0])
        std = np.array([1.0, 10.0])

        # Should not raise
        relative = calculate_relative_uncertainty(transmission, std)

        # Zero transmission should give large but finite relative uncertainty
        assert np.isfinite(relative[0])
        assert np.isfinite(relative[1])


class TestIntegration:
    """Integration tests for the uncertainty module."""

    def test_full_uncertainty_pipeline(self):
        """Test complete uncertainty calculation pipeline."""
        # Simulate realistic data
        n_frames = 100
        height, width = 50, 50

        # Corrected transmission (typical values 50-200)
        np.random.seed(42)
        transmission = np.random.uniform(50, 200, (n_frames, height, width))

        # Occupancy increasing over frames (0.1 to 0.4)
        occupancy = np.linspace(0.1, 0.4, n_frames)[:, np.newaxis, np.newaxis]
        occupancy = np.broadcast_to(occupancy, (n_frames, height, width)).copy()

        # Shutter ratio (slightly varying around 1.0)
        shutter_n_ratio = np.linspace(1.0, 1.05, n_frames)[:, np.newaxis, np.newaxis]

        # Calculate uncertainty
        variance = calculate_transmission_variance(transmission, occupancy, shutter_n_ratio)
        std = calculate_transmission_std(transmission, occupancy, shutter_n_ratio)

        # Check occupancy validity
        warning = check_occupancy_validity(occupancy)

        # Aggregate over ROI
        roi_mask = np.zeros((height, width), dtype=bool)
        roi_mask[20:30, 20:30] = True  # 100 pixel ROI

        roi_var, roi_std = aggregate_roi_uncertainty(variance, roi_mask)

        # Assertions
        assert variance.shape == transmission.shape
        assert std.shape == transmission.shape
        assert np.all(variance >= 0)
        assert np.all(std >= 0)
        assert warning.level == "safe"  # max occupancy is 0.4
        assert roi_var > 0
        assert roi_std > 0

    def test_uncertainty_scales_with_occupancy(self):
        """Test that uncertainty increases with occupancy (as expected)."""
        transmission = 100.0
        shutter_n_ratio = 1.0

        occupancies = [0.1, 0.3, 0.5, 0.7]
        variances = []

        for occ in occupancies:
            var = calculate_transmission_variance(
                np.array([transmission]),
                np.array([occ]),
                shutter_n_ratio,
            )
            variances.append(var[0])

        # Variance should increase with occupancy
        for i in range(len(variances) - 1):
            assert variances[i + 1] > variances[i], (
                f"Variance should increase with occupancy: "
                f"var({occupancies[i]})={variances[i]} vs var({occupancies[i + 1]})={variances[i + 1]}"
            )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
