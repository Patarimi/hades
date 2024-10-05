import dataclasses
from pathlib import Path
import matplotlib.pyplot as plt
from lark import Transformer
from numpy.matlib import empty

from hades.parsers.tools import parse


@dataclasses.dataclass
class DielectricLayer:
    height: float
    permittivity: float
    permeability: float = 1.
    conductivity: float = 0.


@dataclasses.dataclass
class MetalLayer:
    name: str
    definition: str
    height: float = 0
    thickness: float = 0
    conductivity: float = 0


class Process(Transformer):
    def NAME(self, name):
        return str(name)

    def EQUATION(self, equation):
        return str(equation)

    def NUMBER(self, number):
        return float(number)

    def __init__(self):
        self.scale = {"length": 1}
        self.DielectricLayers = []
        self.MetalLayers: dict[str, MetalLayer] = {}
        self.Definitions: dict[str, str] = {}

    def UNIT(self, unit):
        return str(unit)

    def assume(self, unit):
        match unit[0]:
            case "microns":
                self.scale["length"] = 1e-6
            case _:
                print(f"Unknown unit: {unit}")

    def VALUE(self, number):
        if str(number) == "infinity":
            return float("inf")
        return float(number)

    def define(self, define):
        self.Definitions[define[0]] = define[1]

    def layer(self, layer):
        height = layer[0] if not self.DielectricLayers else self.DielectricLayers[-1].height + layer[0]
        self.DielectricLayers.append(DielectricLayer(height=height, permittivity=layer[1]))

    def OFFSET(self, offset):
        val = str(offset).split(" ")
        return float(val[1]) * self.scale["length"]

    def conductor(self, conductor):
        if type(conductor[-1]) is str:
            name = conductor[-1]
            offset = 0
        else:
            name = conductor[-2]
            offset = conductor[-1]
        self.MetalLayers[name] = MetalLayer(
            name=name,
            definition=self.Definitions[name],
            height=self.DielectricLayers[-1].height + offset,
            conductivity=conductor[1],
            thickness=conductor[0],
            )

    def via(self, via):
        below, above, cond, name = via
        height = self.MetalLayers[below].height + self.MetalLayers[below].thickness
        self.MetalLayers[name] = MetalLayer(
            name=name,
            definition=self.Definitions[name],
            height=height,
            conductivity=cond,
            thickness=self.MetalLayers[above].height - height,
        )

    def start(self, start):
        return self.DielectricLayers, self.MetalLayers, self.scale


def layer_stack(proc_file: Path):
    t = parse(proc_file, "process")
    return Process().transform(t)

if __name__ == "__main__":
    print(layer_stack(Path("pdk/mock/mock.proc")))
