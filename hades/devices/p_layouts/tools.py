import subprocess
from dataclasses import dataclass
from os.path import join, dirname, realpath
from pathlib import Path
import os
from shutil import which
from hades.techno import load_pdk
from hades.parser.tlef import load_tlef
from hades.parser.map import load_map, get_number


@dataclass
class Layer:
    data: int
    d_type: int = 0
    name: str = None

    def __str__(self):
        return f"{self.data}/{self.d_type}"


@dataclass
class LayerStack:
    techno: str
    stack: list[Layer] = None

    def __post_init__(self):
        pdk = load_pdk(self.techno)
        path = realpath(
            join(dirname(__file__), "../..", pdk["base_dir"], pdk["techlef"])
        )
        layers = load_tlef(path)
        layer_map = load_map(self.techno)
        self.stack = []
        for layer in layers:
            if layer in layer_map:
                dt = get_number(self.techno, layer, "VIA")
                self.stack.append(Layer(dt[0], dt[1], layer))

    def get_metal_layer(self, num: int):
        if num == 0:
            raise ValueError("nbr cannot be 0")
        return self.stack[2 * (num - 1) if num > 0 else 2 * num + 1]

    def get_via_layer(self, num: int):
        if num == 0:
            raise ValueError("nbr cannot be 0")
        return self.stack[2 * num - 1 if num > 0 else 2 * num]


@dataclass
class Port:
    name: str
    ref: str = None

    def __post_init__(self):
        if self.ref is None:
            self.ref = self.name + "_r"


def check_diff(gds1: Path, gds2: Path):
    """
    Test if the 2 gds files are the same. Raise error if they differ.
    :param gds1: path of the first gds
    :param gds2: path of the second gds
    :return: None
    """
    cmd = f"strmxor {gds1} {gds2}"
    if which("strmxor") is None:
        # for CI
        os.environ["LD_LIBRARY_PATH"] = "/usr/lib/klayout"
        cmd = "/usr/lib/klayout/" + cmd
    c = subprocess.run(cmd, shell=True, capture_output=True)
    if c.returncode != 0:
        err_mess = c.stdout.decode("latin")
        raise ValueError(err_mess)
