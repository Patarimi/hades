import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Layer:
    data: int
    d_type: int = 0

    def __str__(self):
        return f"{self.data}/{self.d_type}"


def check_diff(gds1: Path, gds2: Path):
    """
    Test if the 2 gds files are the same. Raise error if they differe.
    :param gds1: path of the first gds
    :param gds2: path of the second gds
    :return: None
    """
    cmd = f"strmxor {gds1} {gds2}"
    c = subprocess.run(cmd, shell=True, capture_output=True)
    if c.returncode != 0:
        raise ValueError(c.stdout)
