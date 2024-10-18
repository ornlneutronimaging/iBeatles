#!/usr/bin/env python
import numpy as np
import pytest
from ibeatles.core.fitting.kropff.utils import generate_synthetic_data
from ibeatles.core.fitting.kropff.models import kropff_transmission_model


def test_generate_synthetic_data():
    # Set up test parameters
    wavelengths = np.linspace(3.0, 5.0, 100)
    true_params = {
        "a0": 0.15,
        "b0": 0.11,
        "a_hkl": 0.12,
        "b_hkl": 0.11,
        "bragg_edge_wavelength": 4.054,
        "sigma": 0.01,
        "tau": 0.02,
    }
    noise_level = 0.01

    # Generate synthetic data
    _, noisy_transmission = generate_synthetic_data(
        wavelengths, true_params, noise_level
    )

    # Calculate ideal transmission
    ideal_transmission = kropff_transmission_model(wavelengths, **true_params)

    # Test that the noisy transmission is close to the ideal transmission
    np.testing.assert_allclose(noisy_transmission, ideal_transmission, atol=0.05)

    # Test that all transmission values are between 0 and 1
    assert np.all((noisy_transmission >= 0) & (noisy_transmission <= 1))

    # Test that the noise level is approximately correct
    assert np.std(noisy_transmission - ideal_transmission) == pytest.approx(
        noise_level, abs=0.005
    )

    # Test with zero noise
    _, zero_noise_transmission = generate_synthetic_data(wavelengths, true_params, 0)
    np.testing.assert_allclose(zero_noise_transmission, ideal_transmission)

    # Test with different noise levels
    for noise in [0.001, 0.1, 0.5]:
        _, noisy_trans = generate_synthetic_data(wavelengths, true_params, noise)
        assert np.std(noisy_trans - ideal_transmission) == pytest.approx(
            noise, abs=0.1 * noise
        )
