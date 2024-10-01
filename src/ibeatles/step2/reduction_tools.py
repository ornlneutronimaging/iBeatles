import numpy as np
import scipy.ndimage
import logging

from src.ibeatles.step2 import KernelType


def moving_average(data=None, kernel_type=KernelType.gaussian, kernel=None):
    """
    if both box_kernel and gaussian_kernel are provided, box_kernel will be used by default
    Parameters
    ----------
    data: if 3D, dimensions must be given as followed (x, y, tof)
    kernel_type: KernelType.box or KernelType.gaussian
    kernel: size of kernel

    Raises
    ------
    ValueError if input_array is not a 2 or 3D array
    Returns
    -------
    """

    if data is None:
        raise ValueError("Provide a signal")

    if len(np.shape(data)) == 1:
        raise ValueError(
            "Data must be 2D image or 3D volume, or TOF stack of 2D images."
        )

    if len(np.shape(data)) > 3:
        raise ValueError(
            "Data must be 2D image or 3D volume, or TOF stack of 2D images."
        )

    if kernel is None:
        raise ValueError("You need to provide a kernel!")

    if len(kernel) == 1:
        raise ValueError("Kernel must be at least of size 2.")

    if (len(np.shape(data)) == 2) and (len(kernel) == 3):
        raise ValueError("Data is 2d but filtering kernel is 3D.")

    # TOF data (3D), 2D kernel
    if len(np.shape(data)) == 3 and (len(kernel) == 2):
        logging.info(
            "-> Data is 3D but filtering kernel is 2D. Applying filter to each slice of the "
            "data (third dimension)."
        )

        outsignal = np.zeros((np.shape(data)[0], np.shape(data)[1], np.shape(data)[2]))

        if kernel_type == KernelType.box:
            kernel = np.ones((kernel[0], kernel[1]))
            kernel = kernel / np.sum(np.ravel(kernel))
            for i in range(0, np.shape(data)[2]):
                outsignal[:, :, i] = scipy.ndimage.convolve(data[:, :, i], kernel)
            return outsignal

        elif kernel_type == KernelType.gaussian:
            for i in range(0, np.shape(data)[2]):
                outsignal[:, :, i] = scipy.ndimage.gaussian_filter(
                    data[:, :, i], kernel
                )

            return outsignal

        else:
            raise ValueError(f"Kernel Type {kernel_type} not supported! ")

    # TOF data (3D), 3D kernel
    elif len(np.shape(data)) == 3 and (len(kernel) == 3):
        logging.info(
            "-> Data and filtering kernel are 3D. Applying 3D filter convolution."
        )

        if kernel_type == KernelType.box:
            kernel = np.ones((kernel[0], kernel[1], kernel[2]))
            kernel = kernel / np.sum(np.ravel(kernel))
            outsignal = scipy.ndimage.convolve(data, kernel)
            return outsignal

        elif kernel_type == KernelType.gaussian:
            outsignal = scipy.ndimage.gaussian_filter(data, kernel)
            return outsignal

        else:
            raise ValueError(f"Kernel Type {kernel_type} not supported! ")

    # image data (2D), 2D kernel
    elif len(np.shape(data)) == 2 and (len(kernel) == 2):
        logging.info(
            "-> Data and filtering kernel are 2D. Applying 2D filter convolution."
        )

        if kernel_type == KernelType.box:
            kernel = np.ones((kernel[0], kernel[1]))
            kernel = kernel / np.sum(np.ravel(kernel))
            outsignal = scipy.ndimage.convolve(data, kernel)
            return outsignal

        elif kernel_type == KernelType.gaussian:
            outsignal = scipy.ndimage.gaussian_filter(data, kernel)
            return outsignal

        else:
            raise ValueError(f"Kernel Type {kernel_type} not supported! ")

    return
