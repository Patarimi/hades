import dataclasses
from pathlib import Path
import matplotlib.pyplot as plt
from lark import Transformer
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
    conductivity: float = 0


class Process(Transformer):
    NAME: str
    EQUATION: str

    def NUMBER(self, number):
        return float(number)

    def __init__(self):
        self.scale = {"length": 1e-6}
        self.DielectricLayers = []
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
        self.DielectricLayers.append(DielectricLayer(height=layer[0]*self.scale["length"], permittivity=layer[1]))
        print(self.DielectricLayers)


def layer_stack(proc_file: Path):
    t = parse(proc_file, "process")
    return Process().transform(t)

if __name__ == "__main__":
    print(layer_stack(Path("pdk/mock/mock.proc")))
