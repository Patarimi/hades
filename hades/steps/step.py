from collections.abc import Callable
from pathlib import Path

import pandas as pd
from klayout import db
from hades.layouts.tools import LayerStack
from hades.extractors.spicing import extract_spice_magic
from hades.parsers.raw import parse_out
from hades.wrappers.ngspice import NGSpice
from hades.techno import get_file


def layout_generation(techno: str, layout: Callable, top_cell_name: str = "top"):
    layerstack = LayerStack(techno)

    lib = db.Layout()
    lib.dbu = layerstack.grid * 1e6
    layout(lib.create_cell(top_cell_name), layerstack)
    lib.write(f"{top_cell_name}.gds")


def extract_from_layout(techno: str, top_cell_name: str = "top"):
    extract_spice_magic(
        Path(f"{top_cell_name}.gds"),
        get_file(techno, "magic_rc"),
        top_cell_name,
        Path(f"{top_cell_name}.cir"),
        options="RC",
    )


def run_bench(bench_name: str = "bench.cir", output_dir: Path = None):
    sim = NGSpice()
    if output_dir is None:
        data_file = Path(bench_name).with_suffix(".raw")
    else:
        data_file = Path(output_dir) / Path(bench_name).with_suffix(".raw").name
    sim.compute(bench_name, data_file)


def load_result(data_name: str = "bench.raw") -> pd.DataFrame:
    return parse_out(data_name)
