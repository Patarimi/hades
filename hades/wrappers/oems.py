# -*- coding: utf-8 -*-
### Import Libraries
import os
import shutil
import sys
from math import inf
from os.path import dirname
from pathlib import Path
from typing import Optional

from gdstk import read_gds
from skrf import Network
import numpy as np
from rich import print

from hades.parsers.process import layer_stack
from hades.techno import get_file

# define OPENEMS variable for correct CSXCAD import
if "OPENEMS_INSTALL_PATH" not in os.environ:
    os.environ["OPENEMS_INSTALL_PATH"] = dirname(shutil.which("openEMS"))

from CSXCAD import CSXCAD
from openEMS.openEMS import openEMS

from hades.layouts.tools import Port


def compute(
    input_file: Path,
    cell_name: str,
    freq: float | tuple[float],
    ports: Optional[list[Port | str]] = None,
    refresh_mesh: bool = True,
    sim_path: Optional[Path] = Path("./."),
    show_model: bool = False,
    skip_run: bool = False,
):
    """
    Run the simulation using openEMS
    :param input_file: gds file to be simulated.
    :param cell_name: name of the cell to simulate (default value: top cell of the layout)
    :param freq: frequency of the simulation.
    - If one frequency is given, simulate from 0 to the given frequency.
    - If a tuple of two frequencies is given, simulate from the first to the second frequency.
    :param ports: list of ports to be used in simulation. Ports name and ref must be labels in the layout.
        If ports are not given, all the ports in the layout will be used.
    :param refresh_mesh: if True, the mesh will be refreshed before the simulation.
    :param sim_path: path to the simulation folder. If not given, the simulation will be done in the current folder.
    :param show_model: if True, the model will be shown before the simulation.
    :param skip_run: if True, the simulation will be skipped. Results will be loaded from the simulation folder.
    :return: Network object containing the simulation results.
    """
    unit = 1e-6  # all length in um

    # substrate setup
    substrate_epsR = 3.38

    ### Setup FDTD parameter & excitation function
    FDTD = openEMS(CoordSystem=0, EndCriteria=1e-4)  # init a rectangular FDTD
    if type(freq) is tuple:
        if freq[0] == freq[1] or freq[1] == 0:
            f_start = freq[0]
            f_stop = f_start
            FDTD.SetSinusExcite(f_start)
            print("Using Sinusoidal Excitation")
        else:
            f_start, f_stop = np.min(freq), np.max(freq)
            FDTD.SetGaussExcite((f_start + f_stop) / 2, (f_stop - f_start) / 2)
            print("Using Gaussian Pulse Excitation")
    else:
        f_start, f_stop = 0, freq
        FDTD.SetDiracExcite(f_stop)
        print("Using Dirac Pulse Excitation")

    FDTD.SetBoundaryCond(
        ["MUR", "MUR", "MUR", "MUR", "MUR", "MUR"]
    )  # boundary conditions

    CSX = make_geometry(gds_file=input_file, tech="mock")

    FDTD.SetCSX(CSX)

    # create substrate
    for prop in CSX.GetAllProperties():
        FDTD.AddEdges2Grid(dirs="all", properties=prop)

    # apply the excitation & resist as a current source
    wavelength_air = (3e8 / unit) / f_stop
    max_cellsize = np.minimum(0.2, wavelength_air / (np.sqrt(substrate_epsR) * 100))
    print(max_cellsize)
    start = [-20, 11, 81]
    stop = [-20 + max_cellsize, -11, 82]
    port = FDTD.AddLumpedPort(
        1, 50, start, stop, "y", 1.0, priority=5, edges2grid="all"
    )

    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(unit)
    mesh.SmoothMeshLines("z", 3 * max_cellsize)
    mesh.SmoothMeshLines("x", max_cellsize)
    mesh.SmoothMeshLines("y", max_cellsize)

    ### Run the simulation
    if show_model:
        CSX_file = os.path.join(sim_path, "bent_patch.xml")
        if not os.path.exists(sim_path):
            os.mkdir(sim_path)
        CSX.Write2XML(CSX_file)
        from CSXCAD import AppCSXCAD_BIN

        os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

    if not skip_run:
        try:
            FDTD.Run(sim_path)
        except AssertionError as e:
            print(
                "Error during OpenEMS run, try :[italic]python -O "
                + " ".join(sys.argv)
                + "[/italic]"
            )
            raise e

    ### Postprocessing & plotting
    f = np.linspace(f_start, f_stop, 401)
    port.CalcPort(sim_path, f)
    result = Network()
    result.frequency = f
    result.s = port.uf_ref / port.uf_inc
    return result


def make_geometry(
    gds_file: Path,
    tech: str = "mock",
    *,
    show_model: bool = False,
    sim_path: Path = None,
) -> CSXCAD.ContinuousStructure:
    """
    Create a geometry in OpenEMS from a gds and a technology.
    :param gds_file: The input gds file (the top cell is used by default).
    :param tech: Name of the technology (*hades pdk list* for a list of available techno).
    :param show_model: Open a 3D view of the model before running the simulation.
    :param sim_path: Folder use to write simulation file (same as gds file by default).
    :return:
    """
    gdsii = read_gds(gds_file).cells[0]

    CSX = CSXCAD.ContinuousStructure()
    if sim_path is None:
        sim_path = Path(gds_file).parent

    proc_file = get_file(tech, "process")
    diels, metals = layer_stack(proc_file)

    print(metals)
    altitude = 0
    csx_metal = dict()
    for name in metals:
        layer_n = int(metals[name].definition.strip("L").split("T")[0])
        csx_metal[layer_n] = (
            CSX.AddMaterial(name, kappa=metals[name].conductivity),
            altitude,
            metals[name].height,
        )
        altitude += metals[name].height
    print(csx_metal)

    for polygon in gdsii.polygons:
        if polygon.layer not in csx_metal.keys():
            print(f"Skipping layer {polygon.layer}/{polygon.datatype}")
            continue
        material, elevation, height = csx_metal[polygon.layer]
        x = [p[0] for p in polygon.points]
        y = [p[1] for p in polygon.points]
        material.AddLinPoly(
            points=[x, y],
            priority=200,
            norm_dir="z",
            elevation=elevation,
            length=height,
        )

    # Building Dielectric layers
    altitude = 0
    for i, diel in enumerate(diels):
        sub = CSX.AddMaterial(f"diel_{i}", epsilon=diel.permittivity)
        sub.AddBox(
            start=[-25, -80, altitude],
            stop=[
                140,
                80,
                altitude + diel.height if diel.height != inf else 2 * altitude,
            ],
            priority=1,
        )
        altitude += diel.height

    if show_model:
        CSX_file = os.path.join(sim_path, "bent_patch.xml")
        if not os.path.exists(sim_path):
            os.mkdir(sim_path)
        CSX.Write2XML(CSX_file)
        from CSXCAD import AppCSXCAD_BIN

        os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

    return CSX
