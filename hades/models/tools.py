"""
module for common rf functions.
"""
import numpy as np


def db20(*kwargs):
    """
    return the decibel value of the sum of the given complex number.
    :param kwargs: input complex numbers
    :return: sum of absolute value of the input complex numbers in decibel
    examples:
    db20(1) -> 0
    db20(0.5,0.5) -> 0
    """
    sm = sum(np.abs(k) ** 2 for k in kwargs)
    return 10 * np.log10(sm)


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
    return abs(a - b) / (abs(a) + abs(b))
