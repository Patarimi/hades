import numpy as np

from .devices import Parameters
from ..simulator import Emx
import gdstk
from pathlib import Path
from ..equation.micro_strip import wheeler
from scipy.optimize import minimize_scalar, minimize
from ..techno import get_layer
from numpy import angle, sqrt, pi, arccosh, NaN


class MicroStrip:
    name: str
    specifications: Parameters
    dimensions: Parameters
    parameters: Parameters
    techno: str

    def __init__(
        self, name: str, techno: str, z_c: float = 50, f_c: float = 1e9, phi: float = 90
    ):
        self.name = name
        self.specifications = {"z_c": float(z_c), "f_c": float(f_c), "phi": float(phi)}
        self.parameters = {"eps": 4, "height": 9.11e-6}
        self.techno = techno
        self.em = Emx()
        self.em.prepare(techno)

    def update_model(self, specifications: Parameters = None) -> Parameters:
        if specifications is not None:
            self.specifications = specifications
        # todo: extraire h et epsilon depuis proc_file
        self.dimensions = dict()
        eps = float(self.parameters["eps"])
        height = float(self.parameters["height"])

        def cost(x):
            z_c, _ = wheeler(x, height, eps, 3e-6)
            return abs(z_c - specifications["z_c"])

        res = minimize_scalar(cost)
        self.dimensions["w"] = res.x
        delay = specifications["phi"] / (360 * float(self.specifications["f_c"]))
        res = minimize_scalar(
            lambda x: abs(wheeler(res.x, height, eps, 3e-6, x)[1] - delay)
        )
        print(res.x)
        # /!\ impedance is not accurate close to l/4 ou l/2
        self.dimensions["l"] = 40e-6  # res.x
        return self.dimensions

    def update_cell(self, dimensions: Parameters) -> gdstk.Cell:
        self.dimensions = dimensions
        m_top = get_layer(self.techno, dimensions["m_path"])
        m_bott = get_layer(self.techno, dimensions["m_gnd"])
        ms = gdstk.Cell(self.name)
        le = dimensions["l"] * 1e6
        w = dimensions["w"] * 1e6
        rf = gdstk.RobustPath((0, 0), w, layer=m_top[0], datatype=m_top[1])
        rf.segment((le, 0))
        gnd = gdstk.RobustPath((0, 0), 3 * w, layer=m_bott[0], datatype=m_bott[1])
        gnd.segment((le, 0))
        ms.add(rf, gnd)
        ms.add(gdstk.Label("S1", (0, 0), layer=m_top[0], texttype=m_top[1]))
        ms.add(gdstk.Label("S2", (le, 0), layer=m_top[0], texttype=m_top[1]))
        ms.add(gdstk.Label("G1", (0, 0), layer=m_bott[0], texttype=m_bott[1]))
        ms.add(gdstk.Label("G2", (le, 0), layer=m_bott[0], texttype=m_bott[1]))
        return ms

    def update_accurate(self, sim_file: Path) -> Parameters:
        f_0 = self.specifications["f_c"]
        res = self.em.compute(sim_file, self.name, f_0, port=("P1=S1:G1", "P2=S2:G2"))
        Y_0 = 0.02
        phi = np.angle(res.s[0, 0, 1], deg=True)
        z_c = sqrt(
            1 / (res.y[0, 0, 0] * res.y[0, 1, 1] - res.y[0, 1, 0] * res.y[0, 0, 1])
        ).real
        return {"z_c": z_c, "f_c": f_0, "phi": phi}

    def recalibrate_model(self, performances: Parameters) -> Parameters:
        def cost(eps):
            z, delay = wheeler(
                width=self.dimensions["w"],
                height=self.parameters["height"],
                k=eps,
                thick=3e-6,
                length=self.dimensions["l"],
            )
            phi = delay * 360 * float(self.specifications["f_c"])
            return abs(z - performances["z_c"])

        res = minimize_scalar(cost)
        if res.x is NaN:
            raise ValueError(res)
        self.parameters["eps"] = res.x
        # self.parameters["height"] = res.x[1]
        return self.parameters
