"""
This module is used to extract the equivalent spice schematic of a gdsii file.
"""
from pathlib import Path
from klayout import db as kl
from hades.layouts.tools import LayerStack


def extract_spice(gds_file: Path, techno: str, stack: LayerStack = None) -> str:
    """
    Extract the equivalent spice schematic of a gdsii file.
    :param gds_file: Input file to be simulated
    :param techno: name of technology to be used in the simulation.
    :param stack: Layer Stack use to construct the 3D model
    :return: A spice schematic to be used by ngspice
    """
    print(kl.LayoutToNetlist(gds_file, techno, stack=stack).write())


if __name__ == "__main__":
    extract_spice(Path("test.gds"), "sky130A")
