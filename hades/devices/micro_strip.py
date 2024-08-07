import logging

import numpy as np

from .device import Parameters
from hades.wrappers.em import Emx
import gdstk
from pathlib import Path
from hades.models.micro_strip import wheeler
from scipy.optimize import minimize_scalar
from numpy import sqrt, nan
from ..layouts.microstrip import straight_line
from ..layouts.tools import LayerStack
from typing import Optional


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

    def update_model(self, specifications: Optional[Parameters] = None) -> Parameters:
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
        delay = float(specifications["phi"]) / (360 * float(self.specifications["f_c"]))
        res = minimize_scalar(
            lambda x: abs(wheeler(res.x, height, eps, 3e-6, x)[1] - delay)
        )
        logging.info(f"{res.x}\t{res.message}")
        # /!\ impedance is not accurate close to l/4 ou l/2
        self.dimensions["l"] = 40e-6  # res.x
        return self.dimensions

    def update_cell(self, dimensions: Parameters) -> gdstk.Cell:
        self.dimensions = dimensions
        ms = straight_line(
            width=float(dimensions["w"]),
            length=float(dimensions["l"]),
            layerstack=LayerStack(self.techno),
        )
        return ms

    def update_accurate(self, sim_file: Path) -> Parameters:
        f_0 = float(self.specifications["f_c"])
        res = self.em.compute(sim_file, self.name, f_0, port=("P1=S1:G1", "P2=S2:G2"))
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
            return abs(z - performances["z_c"])

        res = minimize_scalar(cost)
        if res.x is nan:
            raise ValueError(res)
        self.parameters["eps"] = res.x
        return self.parameters
