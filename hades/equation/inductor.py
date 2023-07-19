from numpy import pi


WHEELER_REF = {"hexagonal": (2.3, 3.83)}


def wheeler(n: int, d_avg: float, rho: float, shape: str = "custom", k: tuple = None):
    u_0 = 4 * pi * 1e-7
    if shape == "custom" or k is not None:
        k1, k2 = k
    else:
        try:
            k1, k2 = WHEELER_REF[shape]
        except KeyError:
            raise KeyError(f"Unknown shape, available shape are: {WHEELER_REF.keys()}")
    return k1 * u_0 * d_avg * n**2 / (1 + k2 * rho)
