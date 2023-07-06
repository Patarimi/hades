from typing import Protocol, Union
import gdstk
from pathlib import Path


Parameters = dict[str, Union[int, float, str]]


class Device(Protocol):
    name: str
    specifications: Parameters
    dimensions: Parameters
    parameters: Parameters

    def update_model(self, specifications: Parameters) -> Parameters:
        ...

    def update_cell(self, dimensions: Parameters, techno: str) -> gdstk.Cell:
        ...

    def update_accurate(self, sim_file: Path, option: dict = None) -> Parameters:
        ...

    def recalibrate_model(self, performances: Parameters) -> Parameters:
        ...


def generate(
    dut: Device,
    specifications: Parameters,
    techno,
    dimensions: Parameters,
    stop: str,
) -> Parameters:
    for i in range(3):
        print(specifications)
        dimensions.update(dut.update_model(specifications))
        print(dimensions)
        if stop == "dimensions":
            break
        cell = dut.update_cell(dimensions, techno=techno)
        lib = gdstk.Library()
        lib.add(cell)
        lib.write_gds(dut.name + ".gds")
        if stop == "geometries":
            break
        res = dut.update_accurate(Path(dut.name + ".gds"))
        print(f"Accurate model completed with: {res}")
        dut.recalibrate_model(res)
        print(f"model recalibrate with {dut.parameters}")
    return dut.dimensions
