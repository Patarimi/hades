import subprocess
from dataclasses import dataclass
from os.path import join, dirname, realpath
from pathlib import Path
import os
from shutil import which
from hades.techno import load_pdk
from hades.parsers.tlef import load_tlef
from hades.parsers.layermap import load_map, get_number


@dataclass
class Layer:
    layer: int
    datatype: int = 0
    name: str = ""
    width: float = 0
    spacing: float = 0

    def __str__(self):
        return f"{self.name}: {self.layer}/{self.datatype}"

    @property
    def map(self):
        return {"layer": self.layer, "datatype": self.datatype}


@dataclass
class ViaLayer(Layer):
    enclosure: float | tuple[float, float] = 0


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
            if layer.name in layer_map:
                layer_type = None
                if layer.type == "ROUTING" and layer.name[0].upper() == "M":
                    layer_type = "Metal"
                if layer.type == "CUT" and layer.name[0].upper() == "V":
                    layer_type = "Via"
                if layer_type is None:
                    continue
                for dtype in ("VIA", "drawing", "pin", "net"):
                    try:
                        dt = get_number(layer_map, layer.name, dtype)
                        break
                    except KeyError:
                        continue
                if "dt" not in locals():
                    raise KeyError(
                        f"Type not found in stack. Available type are {list(layer_map[layer].keys())}."
                    )
                if layer_type == "Metal":
                    lyr = Layer(
                        layer=dt[0],
                        datatype=dt[1],
                        name=layer.name,
                        width=layer.width,
                        spacing=layer.spacing,
                    )
                else:
                    lyr = ViaLayer(
                        layer=dt[0],
                        datatype=dt[1],
                        name=layer.name,
                        width=layer.width,
                        spacing=layer.spacing,
                        enclosure=layer.enclosure,
                    )
                self.stack.append(lyr)

    def __len__(self):
        return len(self.stack)

    def get_metal_layer(self, num: int):
        if num == 0:
            raise ValueError("nbr cannot be 0")
        try:
            return self.stack[2 * (num - 1) if num > 0 else 2 * num + 1]
        except IndexError:
            raise IndexError(
                f"Layer {num} not found. Available layers are {self.stack}"
            )

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
