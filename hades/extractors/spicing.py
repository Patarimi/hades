"""
This module is used to extract the equivalent spice schematic of a gdsii file.
"""
from os.path import dirname
from pathlib import Path
from klayout import db as kl
from hades.layouts.tools import LayerStack


def extract_spice(gds_file: Path, techno: str, stack: LayerStack = None, output_path: Path = None) -> str:
    """
    Extract the equivalent spice schematic of a gdsii file.
    :param gds_file: Input file to be simulated
    :param techno: name of technology to be used in the simulation.
    :param stack: Layer Stack use to construct the 3D model
    :return: A spice schematic to be used by ngspice
    """
    if output_path is None:
        output_path = Path(f"{dirname(gds_file)}/{gds_file.name}.spice")
    layout = kl.Layout()
    layout.read(gds_file)
    RSI = kl.RecursiveShapeIterator(layout, layout.top_cell(), layout.layer_indices())
    spice = kl.LayoutToNetlist(RSI)
    spice.extract_netlist()
    spice.write(output_path)


if __name__ == "__main__":
    extract_spice(Path("tests/test_layouts/ref_ind.gds"), "sky130A")
