from math import sqrt, pi, atan
from hades.parser.netlist import Netlist, Component
from enum import Enum, auto


def lumped_l(
    z_load: complex, z_source: complex
) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    Return the two solutions to match a complex load to a line. The value of needed capacitor and inductor
    can be computed using denorm function.

    *Source* : Microwave engineering, Fourth Edition, David Pozar, Chapter 5.1
        + original work to include complex z_source.
    :param z_load: impedance of the load.
    :param z_source: impedance of the source.
    :return: two tuples (B, X), respectively the shunt and series element of the matching.
    """
    r_l, b_l = z_load.real, z_load.imag
    r_s, b_s = z_source.real, z_source.imag
    q_l = b_l / r_l

    if r_l > r_s:
        b_n = sqrt(r_l / r_s) * sqrt(r_l**2 + b_l**2 - r_s * r_l)
        b_1 = (b_l + b_n) / (r_l**2 + b_l**2)
        b_2 = (b_l - b_n) / (r_l**2 + b_l**2)
        x_1 = 1 / b_1 + b_l * r_s / r_l - r_s / (b_1 * r_l) - b_s
        x_2 = 1 / b_2 + b_l * r_s / r_l - r_s / (b_2 * r_l) - b_s
    elif b_s == 0:
        x_n = sqrt(r_l * (r_s - r_l))
        b = sqrt((r_s - r_l) / r_l) / r_s
        b_1, b_2 = b, -b
        x_1, x_2 = x_n - b_l, -x_n - b_l
    elif r_s > r_l * (1 + q_l**2):
        raise ValueError("The source resistance is too high.")
    else:
        b_n = sqrt(r_s**2 * b_l**2 + r_s * (r_l - r_s) * (r_l**2 + b_l**2))
        b_1 = (-r_s * b_l + b_n) / (r_s - r_l)
        b_2 = (-r_s * b_l - b_n) / (r_s - r_l)
        x_1 = 1 / (b_1 - r_s * (b_1 + b_l) / r_l - b_s)
        x_2 = 1 / (b_2 - r_s * (b_2 + b_l) / r_l - b_s)
    return (b_1, x_1), (b_2, x_2)


class Pos(Enum):
    series = auto()
    parallel = auto()


def denorm(x: float, f: float, pos: Pos = "series", name: str = "") -> Component:
    """
    Return a component (capacity or inductance) of an element reactance.
    :param x: reactance
    :param f: frequency
    :param pos: element placement, can be "series" or "parallel"
    :param name: name of the component, default value: pos
    :return: capacity or inductance
    """
    comp = ""
    value = 0
    if pos == Pos.series:
        comp = "C" if x > 0 else "L"
    else:
        comp = "C" if x < 0 else "L"
    if x > 0:
        value = abs(x / (2 * pi * f))
    else:
        value = abs(1 / (x * 2 * pi * f))
    return Component(
        comp,
        pos if name == "" else name,
        value,
        ("in", "0" if pos == Pos.series else "out"),
    )


def single_shunt_stub(
    z_load: complex, z_0: complex
) -> tuple[list[float, float], list[float, float], list[float, float]]:
    """
    Return the solution to match a load *z_load* to a line of impedance *z_0* using a parallel (shunt) stub.
    This is mainly used with micro-strip lines.
    Two solutions are given either using an open or a shorted stub.
    *Source* : Microwave engineering, Fourth Edition, David Pozar, Chapter 5.2
    :param z_load: impedance to be matched?
    :param z_0: impedance of the line.
    :return: a tuple containing :
        - d: the 2 electrical distances from the stub to the load
        - lo: the 2 electrical length of the open stub
        - ls: the 2 electrical  length of the shorted stub
    """
    r_l, x_l = z_load.real, z_load.imag
    r_0, b_0 = z_0.real, (1 / z_0).imag
    if r_l == r_0:
        t_l = (-x_l / (2 * r_0),)
    else:
        t_n = sqrt(r_l * ((r_0 - r_l) ** 2 + x_l**2) / r_0)
        t_l = (
            (x_l + t_n) / (r_l - r_0),
            (x_l - t_n) / (r_l - r_0),
        )
    d = list()
    lo = list()
    ls = list()
    for t in t_l:
        if t >= 0:
            d.append(atan(t) / (2 * pi))
        else:
            d.append((atan(t) + pi) / (2 * pi))
        B = (t * r_l**2 - (r_0 - x_l * t) * (x_l + r_0 * t)) / (
            r_0 * (r_l**2 + (x_l + r_0 * t) ** 2)
        )
        Bs = B - b_0
        le = atan(Bs * r_0) / pi % 1
        lo.append((1 - le) / 2)
        ls.append((-0.5 - le) / 2 % 0.5)
    return d, lo, ls


def single_series_stub(
    z_load: complex, z_0: float
) -> tuple[list[float, float], list[float, float], list[float, float]]:
    """
    Return the solution to match a load *z_load* to a line of impedance *z_0* using a series stub.
    Two solutions are given either using an open or a shorted stub.
    This is mainly used with coplanar waveguide.
    *Source* : Microwave engineering, Fourth Edition, David Pozar, Chapter 5.2
    :param z_load: impedance to be matched?
    :param z_0: impedance of the line.
    :return: a tuple containing :
        - d: the 2 electrical distances from the stub to the load
        - lo: the 2 electrical length of the open stub
        - ls: the 2 electrical  length of the shorted stub
    """
    d, lo, ls = single_shunt_stub(1 / z_load, 1 / z_0)
    return d, ls, lo
