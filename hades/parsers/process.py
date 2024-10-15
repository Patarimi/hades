import dataclasses
from pathlib import Path
from lark import Transformer

from hades.parsers.tools import parse


@dataclasses.dataclass
class DielectricLayer:
    height: float
    permittivity: float
    permeability: float = 1.0
    conductivity: float = 0.0


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
        self.last_offset = 0

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
        height = (
            layer[0]
            if not self.DielectricLayers
            else self.DielectricLayers[-1].height + layer[0]
        )
        self.DielectricLayers.append(
            DielectricLayer(height=height, permittivity=layer[1])
        )

    def OFFSET(self, offset):
        val = str(offset).split(" ")
        self.last_offset = float(val[1])
        return float(val[1])

    def conductor(self, conductor):
        if type(conductor[-1]) is str:
            name = conductor[-1]
            offset = 0
        else:
            name = conductor[-2]
            offset = conductor[-1] + self.last_offset
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
        return self.DielectricLayers, self.MetalLayers


def layer_stack(proc_file: Path):
    t = parse(proc_file, "process")
    return Process().transform(t)
