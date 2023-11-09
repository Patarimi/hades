"""
This module implements function to ease the design of passive filter using the insertion loss method.
```mermaid
flowchart LR
S[Filter Specifications] --> L[Low-Pass Prototype] --> C["Conversion\nScaling"] --> I[Implementation]
```
"""
import skrf as rf
import scipy.signal as si
import numpy as np

# parametre d'entrée
R0 = 65
f_c = 96e9
order = 5
style = "ripple"
w_ind_l = (False,)
w_cap_l = (True,)
epsilon = 4.2
Z_low = 42
Z_high = 90


def prototype(order: int, style: str, ripple: float = 0.2):
    """
    Compute a low pass filter prototype. The equations are from [source](https://ia803103.us.archive.org/15/items/MicrowaveFiltersImpedanceMatchingNetworksAndCouplingStructures/Microwave%20Filters%2C%20Impedance-Matching%20Networks%2C%20and%20Coupling%20Structures.pdf).
    :param order: order of the filter
    :param style: either "flat" for maximally flat filter or ripple for equal ripple (Tchebysheff) filter
    :param ripple: in-band ripple in dB
    :return: a list of coefficients
    """
    if style == "flat":
        return -2 * np.real(si.buttap(order)[1])
    if style == "ripple":
        beta = -np.log(np.tanh(ripple / (40 * np.log10(np.e))))
        gamma = np.sinh(beta / (2 * order))
        k = np.arange(order) + 1
        a = np.sin((2 * k - 1) * np.pi / (2 * order))
        b = gamma**2 + np.sin(k * np.pi / order) ** 2
        g = np.ones(order + 1)
        for i in range(order):
            if i == 0:
                g[i] = 2 * a[i] / gamma
            else:
                g[i] = 4 * a[i - 1] * a[i] / (b[i - 1] * g[i - 1])
        if order % 2 == 0:
            g[order] = 1 / np.tanh(beta / 4) ** 2
        return g
    raise ValueError(f"Unkwon filter type {style}, available are flat, ripple")


def scaling(prototype: np.array, f: float, r_0: float):
    """
    properly scale a low-pass filter prototype.
    :param prototype: list of coefficient of the prototype (see [prototype](#hades.devices.app_models.filter.prototype))
    :param f:
    :param r_0:
    :return:
    """
    w_c = 2 * np.pi * f
    denorm_f = prototype / w_c
    denorm = list()
    for i, d in enumerate(denorm_f):
        denorm.append(d * r_0 if i % 2 == 1 else d / r_0)
    return np.array(denorm)


def to_stepped_impedance(
    prototype: np.array, z_high: float, z_low: float, r_0: float = 50
):
    """
    Convert a low-pass prototype to a stepped_impedance line filter. The exact function is implemented instead of the
     approximation presented in Pozar 2012 chapter. 8.6.
    :param prototype: prototype of the filter
    :param z_high: impedance of the high impedance section
    :param z_low: impedance of the low impedance section
    :param r_0: characteristic impedance
    :return: list of required delay in degrees ($beta l$)
    """
    denorm = list()
    for i, g in enumerate(prototype):
        if i % 2 == 1:
            # approx -> denorm.append(g * r_0 / z_high)
            denorm.append(2 * np.arctan(g * r_0 / (2 * z_high)))
        else:
            # approx -> denorm.append(g * z_low / r_0)
            denorm.append(np.arcsin(g * z_low / r_0))
    return np.degrees(np.array(denorm))


if __name__ == "__main__":
    w_c = 2 * np.pi * f_c
    beta = w_c * np.sqrt(epsilon) / rf.c

    step = 0.01e9
    freq = rf.Frequency(start=step, stop=1.5 * f_c, unit="Hz", npoints=int(f_c / step))
    freq.unit = "GHz"
    med = rf.DefinedGammaZ0(freq, z0=R0, gamma=1j * freq.w * np.sqrt(epsilon) / rf.c)
    elm_list = list()
    for w_cap in w_cap_l:
        for w_ind in w_ind_l:
            # short line at the input
            cir = med.line(10, z0=R0)
            for i, g in enumerate(norm_coeff):
                if i == order:
                    print("skipping last g (it's a resistor)")
                    break
                if i % 2 == 0:
                    C = g / (R0 * w_c)
                    if w_cap:
                        elm = med.shunt_capacitor(C, name=f"c{i}")
                        print(f"C{i}={C * 1e15:.1f} fF")
                    else:
                        Z = Z_low
                        l = 0.89 * np.arcsin(g * Z / R0) / beta
                        elm = med.line(l, name=f"l{i}", unit="m", z0=Z)
                        print(f"Z{i}={Z}\tl={l * 1e3:.2f} mm\t{beta*l=:.3f}")
                else:
                    L = R0 * g / w_c
                    if w_ind:
                        elm = med.inductor(L, name=f"l{i}")
                        print(f"L{i}={L * 1e12:.1f} pH")
                    else:
                        Z = Z_high
                        l = 2 * np.arctan(g * R0 / (2 * Z)) / beta
                        elm = med.line(l, name=f"l{i}", unit="m", z0=Z)
                        print(f"Z{i}={Z}\tl={l * 1e3:.2f} mm\t{beta*l=:.3f}")
                cir = cir.copy() ** elm
            cir.name = f"{'cap' if w_cap else 'z_l'} - {'ind' if w_ind else 'z_h'}"
            cir = cir.copy() ** med.line(10, z0=R0)
