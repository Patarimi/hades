import os
from enum import Enum
from pathlib import Path
from typing import Callable

import gdstk
from pydantic import BaseModel


class Technology(str, Enum):
    sky130 = "sky130"
    gf180mcu = "gf180mcu"


class Parameters(BaseModel):
    """
    List of parameters for a device.
    """

    name: str


def load(path: str) -> Parameters:
    """Load a parameter file.

    :param path: Path to the parameter file.
    :return: A dictionary with the parameters.
    """

    with open(path) as f:
        return Parameters.model_validate_json(f.read())


class Generator(BaseModel):
    name: str
    techno: Technology
    targets: Parameters
    parameters_model: Parameters
    approx_model: Callable[[Parameters, Parameters], Parameters]
    layout: Callable[[Parameters], gdstk.Cell]
    accu_model: Callable[[gdstk.Cell], Parameters]
    calibrator: Callable[[Parameters, Parameters], Parameters]

    def generate(self, conf_file: Path | str) -> gdstk.Cell:
        """
        Generate the device.
        :return: a gds cell with the device generated.
        """
        self.targets = load(conf_file)
        cell = gdstk.Cell(self.name)
        return cell


if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    print(load(root + "/test.json"))
