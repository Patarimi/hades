import enum
import logging
from typing import Protocol
from enum import Enum
import gdstk
from pathlib import Path
import pydantic

ParamSet = pydantic.BaseModel


class Step(Enum):
    full = enum.auto()
    dimensions = enum.auto()
    geometries = enum.auto()


class Device(Protocol):
    name: str
    specifications: ParamSet
    dimensions: ParamSet
    parameters: ParamSet
    techno: str

    def update_model(self, specifications: ParamSet) -> ParamSet: ...

    def update_cell(self, dimensions: ParamSet) -> gdstk.Cell: ...

    def update_accurate(self, sim_file: Path) -> ParamSet: ...

    def recalibrate_model(self, performances: ParamSet) -> ParamSet: ...


def generate(
    dut: Device,
    specifications: ParamSet,
    dimensions: ParamSet = None,
    stop: Step = Step.full,
) -> ParamSet:
    if dimensions is None:
        dimensions = {}
    logging.info(f"Generation started with :{specifications}")
    for i in range(5):
        dimensions.update(dut.update_model(specifications))
        logging.info(f"\t{dimensions=}")
        if stop == Step.dimensions:
            break
        cell = dut.update_cell(dimensions)
        lib = gdstk.Library()
        lib.add(cell)
        lib.write_gds(dut.name + ".gds")
        if stop == Step.geometries:
            break
        res = dut.update_accurate(Path(dut.name + ".gds"))
        logging.info(f"\tAccurate model completed with: {res}")
        dut.recalibrate_model(res)
        logging.info(f"\tModel recalibrate with: {dut.parameters}")
    return dut.dimensions
