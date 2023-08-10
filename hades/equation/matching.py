from math import sqrt, pi


def lumped_l(
    z_load: complex, r_0: float
) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    Return the two solutions to match a complex load to a line. The value of needed capacitor and inductor
    can be computed using denorm function.

    *Source* : Microwave engineering, Fourth Edition, David Pozar, Chapter 5.1
    :param z_load: impedance of the load.
    :param r_0: impedance of the line.
    :return: two tuples (B, X), respectively the shunt and series element of the matching.
    """
    r_l = z_load.real
    x_l = z_load.imag

    if r_l > r_0:
        b_n = sqrt(r_l / r_0) * sqrt(r_l**2 + x_l**2 - r_0 * r_l)
        b_1 = (x_l + b_n) / (r_l**2 + x_l**2)
        b_2 = (x_l - b_n) / (r_l**2 + x_l**2)
        x_1 = 1 / b_1 + x_l * r_0 / r_l - r_0 / (b_1 * r_l)
        x_2 = 1 / b_2 + x_l * r_0 / r_l - r_0 / (b_2 * r_l)
        return (b_1, x_1), (b_2, x_2)
    else:
        x_n = sqrt(r_l * (r_0 - r_l))
        b = sqrt((r_0 - r_l) / r_l) / r_0
        return (b, x_n - x_l), (-b, -x_n - x_l)


def denorm(x: float, f: float) -> float:
    """
    Return the lumped element value (capacity or inductance) of an element reactance.
    :param x: reactance
    :param f: frequency
    :return: capacity or inductance
    """
    if x > 0:
        return abs(x / (2 * pi * f))
    else:
        return abs(1 / (x * 2 * pi * f))
