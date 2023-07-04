from typing import Protocol, Union
import gdstk

Parameters = dict[str, Union[int, float, str]]


class Device(Protocol):
    specifications: Parameters
    dimensions: Parameters
    parameters: Parameters

    def update_model(self, specifications: Parameters) -> Parameters:
        ...

    def update_cell(self, dimensions: Parameters, layers: dict) -> gdstk.Cell:
        ...

    def update_accurate(self, cell: gdstk.Cell) -> Parameters:
        ...

    def recalibrate_model(self, performances: Parameters) -> Parameters:
        ...


def generate(device: Device, specification, layers_set) -> Parameters:
    dimensions = device.update_model(specification)
    cell = device.update_cell(dimensions, layers_set)
    perf = device.update_accurate(cell)
    parameters = device.recalibrate_model(perf)

    return dimensions
