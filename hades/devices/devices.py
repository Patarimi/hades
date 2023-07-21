import enum
from typing import Protocol, Union
from enum import Enum
import gdstk
from pathlib import Path
from rich import print


Parameters = dict[str, Union[int, float, str]]


class Step(Enum):
    full = enum.auto()
    dimensions = enum.auto()
    geometries = enum.auto()


class Device(Protocol):
    name: str
    specifications: Parameters
    dimensions: Parameters
    parameters: Parameters
    techno: str

    def update_model(self, specifications: Parameters) -> Parameters:
        ...

    def update_cell(self, dimensions: Parameters) -> gdstk.Cell:
        ...

    def update_accurate(self, sim_file: Path) -> Parameters:
        ...

    def recalibrate_model(self, performances: Parameters) -> Parameters:
        ...


def generate(
    dut: Device,
    specifications: Parameters,
    dimensions: Parameters,
    stop: Step,
) -> Parameters:
    print(f"Generation started with :{specifications}")
    for i in range(3):
        dimensions.update(dut.update_model(specifications))
        print(f"\t{dimensions=}")
        if stop == Step.dimensions:
            break
        cell = dut.update_cell(dimensions)
        lib = gdstk.Library()
        lib.add(cell)
        lib.write_gds(dut.name + ".gds")
        if stop == Step.geometries:
            break
        res = dut.update_accurate(Path(dut.name + ".gds"))
        print(f"\tAccurate model completed with: {res}")
        dut.recalibrate_model(res)
        print(f"\tModel recalibrate with: {dut.parameters}")
    return dut.dimensions
