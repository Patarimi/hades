# -*- coding: utf-8 -*-
### Import Libraries
import logging
import os
import shutil
import sys
from math import inf
from os.path import dirname
from pathlib import Path
from typing import Optional

from cyclopts import App
from pydantic import confloat, BaseModel

from gdstk import read_gds
from skrf import Network
import numpy as np

from hades.parsers.process import layer_stack
from hades.techno import get_file

# define OPENEMS variable for correct CSXCAD import
if shutil.which("openEMS"):
    if "OPENEMS_INSTALL_PATH" not in os.environ:
        os.environ["OPENEMS_INSTALL_PATH"] = dirname(shutil.which("openEMS"))
else:
    logging.error("openEMS not found")
    paths = os.environ["PATH"].split(";" if os.name == "nt" else ":")
    [logging.info(f"{p}") for p in paths]
try:
    from CSXCAD import CSXCAD
    from openEMS.openEMS import openEMS
except ImportError:
    logging.error("CSXCAD or openEMS not found")


from hades.layouts.tools import Port

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO
)

oems_app = App("oems", help="Run OpenEMS simulations")


class Frequency(BaseModel):
    start: confloat(ge=0) = 0
    stop: confloat(gt=0)


@oems_app.default
def compute(
    input_file: Path,
    process: str,
    cell_name: str,
    freq: list[float, float] | float,
    ports: Optional[list[Port]] = None,
    sim_path: Optional[Path] = Path("./."),
    show_model: bool = False,
    skip_run: bool = False,
):
    """Run the simulation using openEMS"""
    """
    :param input_file: gds file to be simulated.
    :param cell_name: name of the cell to simulate (default value: top cell of the layout)
    :param freq: frequency of the simulation.
    - If one frequency is given, simulate from 0 to the given frequency.
    - If a tuple of two frequencies is given, simulate from the first to the second frequency.
    :param ports: list of ports to be used in simulation. Ports name and ref must be labels in the layout.
        If ports are not given, all the ports in the layout will be used.
    :param sim_path: path to the simulation folder. If not given, the simulation will be done in the current folder.
    :param show_model: if True, the model will be shown before the simulation.
    :param skip_run: if True, the simulation will be skipped. Results will be loaded from the simulation folder.
    :return: Network object containing the simulation results.
    """
    unit = 1e-6  # all length in um

    if type(freq) is float:
        freq = Frequency(stop=freq)
    else:
        freq = Frequency(start=freq[0], stop=freq[1])

    ### Setup FDTD parameter & excitation function
    FDTD = openEMS(CoordSystem=0, EndCriteria=1e-4)  # init a rectangular FDTD
    if freq.start == freq.stop:
        FDTD.SetSinusExcite(freq.start)
        logging.info("Using Sinusoidal Excitation")
    else:
        FDTD.SetGaussExcite((freq.start + freq.stop) / 2, (freq.stop - freq.start) / 2)
        logging.info("Using Gaussian Pulse Excitation")

    FDTD.SetBoundaryCond(
        ["MUR", "MUR", "MUR", "MUR", "PEC", "MUR"]
    )  # boundary conditions
    # setting z_min as a perfect electric conductor

    CSX = make_geometry(gds_file=input_file, tech=process, cell_name=cell_name)
    FDTD.SetCSX(CSX)
    for prop in CSX.GetAllProperties():
        FDTD.AddEdges2Grid(dirs="all", properties=prop)

    # apply the excitation & resist as a current source
    wavelength_air = (3e8 / unit) / freq.stop
    max_cellsize = np.minimum(1, wavelength_air / 1000)
    gdsii = read_gds(input_file).cells[0]
    proc_file = get_file("mock", "process")
    _, metals = layer_stack(proc_file)
    for i, label in enumerate(gdsii.get_labels(depth=0)):
        for name in metals:
            if int(metals[name].definition.strip("L").split("T")[0]) == label.layer:
                break
        else:
            raise ValueError(f"Metal {label.layer} not found in process file")
        start = [label.origin[0], label.origin[1] - max_cellsize, 0]
        stop = [
            label.origin[0] + max_cellsize,
            label.origin[1] + max_cellsize,
            metals[name].thickness / 2 + metals[name].elevation,
        ]
        port = FDTD.AddLumpedPort(
            i, 50, start, stop, "z", i, priority=5, edges2grid="all"
        )

    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(unit)
    mesh.SmoothMeshLines("z", 3 * max_cellsize)
    mesh.SmoothMeshLines("x", max_cellsize)
    mesh.SmoothMeshLines("y", max_cellsize)

    ### Display the 3D model before simulation
    if show_model:
        CSX_file = os.path.join(sim_path, "bent_patch.xml")
        if not os.path.exists(sim_path):
            os.mkdir(sim_path)
        CSX.Write2XML(CSX_file)
        from CSXCAD import AppCSXCAD_BIN

        os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

    # Run the simulation
    if not skip_run:
        try:
            FDTD.Run(sim_path)
        except AssertionError as e:
            logging.error(
                "Error during OpenEMS run, try :[italic]python -O "
                + " ".join(sys.argv)
                + "[/italic]"
            )
            raise e

    ### Export as a touchstone file
    f = np.linspace(freq.start, freq.stop, 401)
    result = Network()
    result.frequency = f
    try:
        port.CalcPort(sim_path, f)
        result.s = port.uf_ref / port.uf_inc
    except FileNotFoundError:
        logging.error("Ports files not found, run the simulation first")
    return result


def make_geometry(
    gds_file: Path,
    tech: str = "mock",
    cell_name: str = None,
    *,
    margin: float = 0.2,
):
    """
    Create a geometry in OpenEMS from a gds and a technology.
    :param cell_name: Name of the cell to simulate (default value: top cell of the layout).
    :param gds_file: The input gds file (the top cell is used by default).
    :param tech: Name of the technology (*hades pdk list* for a list of available techno).
    :param margin: margin around the model. The simulation box is the bounding box of the model time (1 + margin).
    :return:
    """
    logging.info(f"Creating geometry from {gds_file}")
    if cell_name is None:
        gdsii = read_gds(gds_file).cells[0]
    else:
        gdsii = read_gds(gds_file)[cell_name]

    CSX = CSXCAD.ContinuousStructure()

    proc_file = get_file(tech, "process")
    diels, metals = layer_stack(proc_file)

    csx_metal = dict()
    for name in metals:
        layer_n, data_type = [
            int(i) for i in metals[name].definition.strip("L").split("T")
        ]
        polygons = gdsii.get_polygons(layer=layer_n, datatype=data_type)
        if len(polygons) == 0:
            logging.info(f"No drawing found, skipping layer {layer_n}/{data_type}")
        else:
            csx_metal[layer_n] = CSX.AddMaterial(name, kappa=metals[name].conductivity)
            for poly in polygons:
                x = [p[0] for p in poly.points]
                y = [p[1] for p in poly.points]
                csx_metal[layer_n].AddLinPoly(
                    points=[x, y],
                    priority=200,
                    norm_dir="z",
                    elevation=metals[name].elevation,
                    length=metals[name].thickness,
                )

    # Building Dielectric layers
    altitude = 0
    bb_min, bb_max = gdsii.bounding_box()
    center = (bb_min[0] + bb_max[0]) / 2, (bb_min[1] + bb_max[1]) / 2
    size = bb_min[0] - bb_max[0], bb_min[1] - bb_max[1]
    start = [
        center[0] - (1 + margin) * size[0] / 2,
        center[1] - (1 + margin) * size[1] / 2,
    ]
    stop = [
        center[0] + (1 + margin) * size[0] / 2,
        center[1] + (1 + margin) * size[1] / 2,
    ]
    for i, diel in enumerate(diels):
        sub = CSX.AddMaterial(
            f"diel_{i}",
            epsilon=diel.permittivity,
            mue=diel.permeability,
            kappa=diel.conductivity,
        )
        sub.AddBox(
            start=[start[0], start[1], altitude],
            stop=[
                stop[0],
                stop[1],
                altitude + diel.elevation if diel.elevation != inf else 2 * altitude,
            ],
            priority=1,
        )
        altitude += diel.elevation

    return CSX
