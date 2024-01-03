import subprocess
from dataclasses import dataclass
from pathlib import Path
import os
from shutil import which


@dataclass
class Layer:
    data: int
    d_type: int = 0

    def __str__(self):
        return f"{self.data}/{self.d_type}"


@dataclass
class Port:
    name: str
    ref: str = None

    def __post_init__(self):
        if self.ref is None:
            self.ref = self.name + "_r"


def check_diff(gds1: Path, gds2: Path):
    """
    Test if the 2 gds files are the same. Raise error if they differe.
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
