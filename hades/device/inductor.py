from .device import Parameters
import gdstk
from math import pi, tan
from pathlib import Path
from scipy.optimize import minimize_scalar
from ..simulator import Emx
from hades.techno import get_layer


class Inductor:
    name: str
    specifications: Parameters
    dimensions: Parameters  # n, W, G, d_i
    parameters: Parameters
    techno: str

    def __init__(self, name: str, techno: str, L: float = 1e-9, f_0: float = 1e9):
        self.name = name
        self.specifications = {"L": float(L), "f_0": float(f_0)}
        self.parameters = {"K1": 2.3, "K2": 3.83}
        self.techno = techno
        self.em = Emx()
        self.em.prepare(techno)

    def update_model(self, specifications: Parameters = None) -> Parameters:
        if specifications is not None:
            self.specifications = specifications
        self.dimensions = {"n": 1, "W": 10e-6}

        def ind_di(x):
            return abs(
                self.ind_value(x, self.parameters["K1"])
                - float(self.specifications["L"])
            )

        res = minimize_scalar(ind_di, bounds=(0, 1e-3))
        self.dimensions["d_i"] = res.x
        return self.dimensions

    def ind_value(self, d_i: float, k1: float) -> float:
        k2 = self.parameters["K2"]
        u_0 = 4 * pi * 1e-7
        if "W" in self.dimensions:
            d_o = self.dimensions["W"] + d_i
        else:
            self.dimensions["W"] = 10e-6
            d_o = d_i + 10
        rho = (d_o - d_i) / (d_o + d_i)
        d_avg = (d_o + d_i) / 2
        return k1 * u_0 * d_avg / (1 + k2 * rho)

    def update_cell(self, dimensions: Parameters) -> gdstk.Cell:
        self.dimensions = dimensions
        m_top = get_layer(self.techno, dimensions["m_path"])
        m_bott = get_layer(self.techno, dimensions["m_bridge"])
        ind = gdstk.Cell(self.name)
        d_i = dimensions["d_i"] * 1e6
        w = dimensions["W"] * 1e6
        d_a = d_i + w
        si = d_a * tan(pi / 8) / 2
        p_ext, p_gap = 20, 10
        turn = gdstk.RobustPath((-p_ext, p_gap), w, layer=m_top[0], datatype=m_top[1])
        turn2 = gdstk.RobustPath((-p_ext, -p_gap), w, layer=m_top[0], datatype=m_top[1])
        path = (
            (0, p_gap),
            (0, si),
            (d_a / 2 - si, d_a / 2),
            (d_a / 2 + si, d_a / 2),
            (d_a, si),
            (d_a, 0),
        )
        for pts in path:
            turn.segment(pts)
            turn2.segment((pts[0], -pts[1]))
        ind.add(turn, turn2)
        ind.add(gdstk.Label("P1", (-p_ext, p_gap), layer=m_top[0], texttype=m_top[1]))
        ind.add(gdstk.Label("P2", (-p_ext, -p_gap), layer=m_top[0], texttype=m_top[1]))

        return ind

    def update_accurate(self, sim_file: Path) -> Parameters:
        f_0 = self.specifications["f_0"]
        Y = self.em.compute(sim_file, self.name, f_0)
        return {"L": -(1 / Y.y[0,0,1]).imag / (2 * pi * float(f_0)), "f_0": f_0}

    def recalibrate_model(self, performances: Parameters) -> Parameters:
        def ind_k1(x):
            return abs(self.ind_value(self.dimensions["d_i"], x) - performances["L"])

        res = minimize_scalar(ind_k1, bounds=(0, 20))
        self.parameters["K1"] = res.x
        return self.parameters