#!/usr/bin/env python
"""Unit test for Bragg peak detection and fitting module."""

import numpy as np
import pytest
from ibeatles.core.fitting.kropff.fitting_functions import (
    kropff_high_lambda,
    kropff_low_lambda,
    kropff_bragg_peak_tof,
)


def test_kropff_high_lambda():
    lda = np.array([1.0, 2.0, 3.0])
    a0 = 1.0
    b0 = 0.5

    expected = np.exp(-(a0 + b0 * lda))
    result = kropff_high_lambda(lda, a0, b0)

    np.testing.assert_allclose(result, expected)


def test_kropff_high_lambda_invalid_input():
    assert kropff_high_lambda(np.array([np.nan]), 1.0, 0.5) is None
    assert kropff_high_lambda(np.array([1.0]), np.inf, 0.5) is None


def test_kropff_low_lambda():
    lda = np.array([1.0, 2.0, 3.0])
    a0 = 1.0
    b0 = 0.5
    ahkl = 2.0
    bhkl = 0.3

    expected = np.exp(-(a0 + b0 * lda)) * np.exp(-(ahkl + bhkl * lda))
    result = kropff_low_lambda(lda, a0, b0, ahkl, bhkl)

    np.testing.assert_allclose(result, expected)


def test_kropff_low_lambda_invalid_input():
    assert kropff_low_lambda(np.array([np.nan]), 1.0, 0.5, 2.0, 0.3) is None
    assert kropff_low_lambda(np.array([1.0]), 1.0, np.inf, 2.0, 0.3) is None


def test_kropff_bragg_peak_tof():
    lda = np.array([1.0, 2.0, 3.0])
    a0 = 1.0
    b0 = 0.5
    ahkl = 2.0
    bhkl = 0.3
    ldahkl = 2.5
    sigma = 0.1
    tau = 0.05

    result = kropff_bragg_peak_tof(lda, a0, b0, ahkl, bhkl, ldahkl, sigma, tau)

    # We can't easily calculate the expected result by hand, so we'll just check
    # that the output has the correct shape and doesn't contain any NaNs or infs
    assert result is not None
    assert result.shape == lda.shape
    assert not np.any(np.isnan(result))
    assert not np.any(np.isinf(result))


def test_kropff_bragg_peak_tof_invalid_input():
    assert (
        kropff_bragg_peak_tof(np.array([np.nan]), 1.0, 0.5, 2.0, 0.3, 2.5, 0.1, 0.05)
        is None
    )
    assert (
        kropff_bragg_peak_tof(np.array([1.0]), 1.0, 0.5, 2.0, 0.3, np.inf, 0.1, 0.05)
        is None
    )


if __name__ == "__main__":
    pytest.main([__file__])
