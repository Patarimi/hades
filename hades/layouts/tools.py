import subprocess
from dataclasses import dataclass
from os.path import join, dirname, realpath
from pathlib import Path
import os
from shutil import which
from hades.techno import load_pdk
from hades.parsers.tlef import load_tlef
from hades.parsers.map import load_map, get_number


@dataclass
class Layer:
    data: int
    d_type: int = 0
    name: str = None

    def __str__(self):
        return f"{self.name}: {self.data}/{self.d_type}"


@dataclass
class LayerStack:
    techno: str
    stack: list[Layer] = None

    def __post_init__(self):
        pdk = load_pdk(self.techno)
        path = realpath(join(dirname(__file__), "../", pdk["base_dir"], pdk["techlef"]))
        layers = load_tlef(path)
        layer_map = load_map(self.techno)
        self.stack = []
        for layer in layers:
            if layer in layer_map:
                is_met_or_via = False
                if "TYPE" not in layers[layer]:
                    raise KeyError(
                        f"Type not found in {layer}. Available option are {list(layers[layer].keys())}."
                        f"full layer stack is {layers}"
                    )
                if layers[layer]["TYPE"] == "ROUTING" and layer[0].upper() == "M":
                    is_met_or_via = True
                if layers[layer]["TYPE"] == "CUT" and layer[0].upper() == "V":
                    is_met_or_via = True
                if not is_met_or_via:
                    continue
                for dtype in ("VIA", "net", "drawing"):
                    try:
                        dt = get_number(self.techno, layer, dtype)
                    except KeyError:
                        continue
                if "dt" not in locals():
                    raise KeyError(
                        f"Type not found in stack. Available type are {list(layer_map[layer].keys())}."
                    )
                self.stack.append(Layer(dt[0], dt[1], layer))

    def __len__(self):
        return len(self.stack)

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

    def __str__(self):
        if self.ref == "":
            return self.name
        return f"{self.name}={self.name}:{self.ref}"


def check_diff(gds1: str | Path, gds2: str | Path):
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
