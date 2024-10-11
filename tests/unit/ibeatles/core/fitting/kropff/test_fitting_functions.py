#!/usr/bin/env python
"""Unit test for Bragg peak detection and fitting module."""

import numpy as np
import pytest
from ibeatles.core.fitting.kropff.fitting_functions import (
    kropff_high_lambda_transmission,
    kropff_high_lambda_attenuation,
    kropff_low_lambda_transmission,
    kropff_low_lambda_attenuation,
    kropff_bragg_peak_tof,
)


def test_kropff_high_lambda_transmission():
    lda = np.array([1.0, 2.0, 3.0])
    a0 = 1.0
    b0 = 0.5

    expected = np.exp(-(a0 + b0 * lda))
    result = kropff_high_lambda_transmission(lda, a0, b0)

    np.testing.assert_allclose(result, expected)


def test_kropff_high_lambda_attenuation():
    lda = np.array([1.0, 2.0, 3.0])
    a0 = 1.0
    b0 = 0.5

    expected = a0 + b0 * lda
    result = kropff_high_lambda_attenuation(lda, a0, b0)

    np.testing.assert_allclose(result, expected)


def test_kropff_low_lambda_transmission():
    lda = np.array([1.0, 2.0, 3.0])
    a0 = 1.0
    b0 = 0.5
    ahkl = 2.0
    bhkl = 0.3

    expected = np.exp(-(a0 + b0 * lda)) * np.exp(-(ahkl + bhkl * lda))
    result = kropff_low_lambda_transmission(lda, a0, b0, ahkl, bhkl)

    np.testing.assert_allclose(result, expected)


def test_kropff_low_lambda_attenuation():
    lda = np.array([1.0, 2.0, 3.0])
    a0 = 1.0
    b0 = 0.5
    ahkl = 2.0
    bhkl = 0.3

    expected = (a0 + b0 * lda) + (ahkl + bhkl * lda)
    result = kropff_low_lambda_attenuation(lda, a0, b0, ahkl, bhkl)

    np.testing.assert_allclose(result, expected)


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


if __name__ == "__main__":
    pytest.main([__file__])
