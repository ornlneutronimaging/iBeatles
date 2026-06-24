class ParametersToDisplay:
    d = "d"
    strain_mapping = "strain_mapping"
    integrated_image = "integrated_image"


# strain is dimensionless (delta_d / d0); the step6 GUI and its exports
# report it as micro-strain (strain x 1e6)
MICRO_STRAIN_FACTOR = 1.0e6


INTERPOLATION_METHODS = [
    "none",
    "nearest",
    "bilinear",
    "bicubic",
    "spline16",
    "spline36",
    "hanning",
    "hamming",
    "hermite",
    "kaiser",
    "quadric",
    "catrom",
    "gaussian",
    "bessel",
    "mitchell",
    "sinc",
    "lanczos",
]


DEFAULT_INTERPOLATION_INDEX = 0


CMAPS = ["viridis", "jet"]

DEFAULT_CMAP_INDEX = 0
