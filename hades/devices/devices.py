from typing import Protocol, Union

parameters = dict[str, Union[int, float, str]]


class Device(Protocol):

    def set_dimensions(self, specifications: parameters) -> parameters:
        ...

    def set_geometries(self, dimensions: parameters, layers: dict):
        ...

    def get_accurate(self, ):
        ...

    def recalibrate(self):
        ...


def generate(device: Device, specification, layers_set) -> parameters:
    dimensions = device.set_dimensions(specification)
    device.set_geometries(dimensions, layers_set)
    device.get_accurate()
    device.recalibrate()

    return dimensions

