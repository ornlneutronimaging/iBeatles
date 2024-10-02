#!/usr/bin/env python
"""Unit tests for the normalization functions."""

import numpy as np
import pytest
from ibeatles.core.processing.normalization import moving_average, KernelType
from ibeatles.core.config import MovingAverage


@pytest.mark.parametrize(
    "data_shape, kernel, kernel_type, dimension",
    [
        ((10, 10), {"y": 3, "x": 3}, KernelType.box, "2D"),
        ((10, 10), {"y": 3, "x": 3}, KernelType.gaussian, "2D"),
        ((10, 10, 5), {"y": 3, "x": 3}, KernelType.box, "2D"),
        ((10, 10, 5), {"y": 3, "x": 3}, KernelType.gaussian, "2D"),
        ((10, 10, 5), {"y": 3, "x": 3, "lambda": 3}, KernelType.box, "3D"),
        ((10, 10, 5), {"y": 3, "x": 3, "lambda": 3}, KernelType.gaussian, "3D"),
    ],
)
def test_moving_average(data_shape, kernel, kernel_type, dimension):
    data = np.random.rand(*data_shape)
    config = MovingAverage(
        active=True, dimension=dimension, size=kernel, type=kernel_type
    )
    result = moving_average(data, config)
    assert result.shape == data_shape


def test_moving_average_inactive():
    data = np.random.rand(10, 10)
    config = MovingAverage(
        active=False, dimension="2D", size={"y": 3, "x": 3}, type=KernelType.box
    )
    result = moving_average(data, config)
    np.testing.assert_array_equal(result, data)


def test_moving_average_invalid_input():
    data = np.random.rand(10)
    config = MovingAverage(
        active=True, dimension="2D", size={"y": 3, "x": 3}, type=KernelType.box
    )
    with pytest.raises(ValueError, match="Data must be 2D image or 3D volume"):
        moving_average(data, config)


def test_moving_average_invalid_kernel():
    data = np.random.rand(10, 10)
    config = MovingAverage(
        active=True,
        dimension="3D",
        size={"y": 3, "x": 3, "lambda": 3},
        type=KernelType.box,
    )
    with pytest.raises(ValueError, match="Cannot apply 3D kernel to 2D data"):
        moving_average(data, config)


def test_moving_average_unsupported_kernel_type():
    data = np.random.rand(10, 10)
    config = MovingAverage(
        active=True, dimension="2D", size={"y": 3, "x": 3}, type=KernelType.box
    )
    config.type = "invalid"
    with pytest.raises(ValueError, match="Unsupported kernel type"):
        moving_average(data, config)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
