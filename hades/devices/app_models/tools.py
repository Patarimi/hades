"""
module for common rf functions.
"""


def quality(z: complex) -> float:
    """
    return the quality factor of an impedance.
    :param z:
    :return:
    """
    return z.imag / z.real


def norm_diff(a: float, b: float, /) -> float:
    """
    return the normalized difference of two numbers.
    :param a:
    :param b:
    :return:
    """
    return (a - b) ** 2 / (a + b)
