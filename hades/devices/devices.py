from typing import Protocol, Union

Parameters = dict[str, Union[int, float, str]]


class Device(Protocol):
    def set_dimensions(self, specifications: Parameters) -> Parameters:
        ...

    def set_geometries(self, dimensions: Parameters, layers: dict):
        ...

    def get_accurate(
        self,
    ):
        ...

    def recalibrate(self):
        ...


def generate(device: Device, specification, layers_set) -> Parameters:
    dimensions = device.set_dimensions(specification)
    device.set_geometries(dimensions, layers_set)
    device.get_accurate()
    device.recalibrate()

    return dimensions
