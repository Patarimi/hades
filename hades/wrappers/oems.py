# -*- coding: utf-8 -*-
### Import Libraries
import os
import shutil
import sys
from os.path import dirname
from pathlib import Path
from typing import Optional
from skrf import Network
import numpy as np
from rich import print

# define OPENEMS variable for correct CSXCAD import
if "OPENEMS_INSTALL_PATH" not in os.environ:
    os.environ["OPENEMS_INSTALL_PATH"] = dirname(shutil.which("openEMS"))

from CSXCAD import CSXCAD
from openEMS.openEMS import openEMS

from hades.wrappers.ngsolve_w import make_geometry
from hades.layouts.tools import Port
import ngsolve as ng


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
        else:
            f_start, f_stop = np.min(freq), np.max(freq)
            FDTD.SetGaussExcite((f_start + f_stop) / 2, (f_stop - f_start) / 2)
    else:
        f0 = freq
        FDTD.SetDiracExcite(f0)

    FDTD.SetBoundaryCond(["MUR", "MUR", "MUR", "MUR", "MUR", "MUR"])  # boundary conditions

    ### Setup the Geometry & Mesh
    if refresh_mesh:
        geom = make_geometry(input_file, only_metal=True)
        mesh = ng.Mesh(geom.GenerateMesh())
        mesh.ngmesh.Export("test.stl", "STL Format")


    CSX = CSXCAD.ContinuousStructure()
    FDTD.SetCSX(CSX)
    copper = CSX.AddMaterial("copper", kappa=3.0300E7)
    copper.AddPolyhedronReader("test.stl", priority=10)
    FDTD.AddEdges2Grid(dirs="all", properties=copper)


    # create substrate
    substrate = CSX.AddMaterial("substrate", epsilon=substrate_epsR)
    substrate.AddBox(start=[-25, -80, 70], stop=[140, 80, 90])
    FDTD.AddEdges2Grid(dirs="all", properties=substrate)

    # apply the excitation & resist as a current source
    start = [-20.1, 11, 81]
    stop = [-19.9, -11, 82]
    port = FDTD.AddLumpedPort(
        1, 50, start, stop, "x", 1.0, priority=500, edges2grid="all"
    )

    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(unit)
    mesh.SmoothMeshLines("all", 10)

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
            print("Error during OpenEMS run, try :[italic]python -O " + " ".join(sys.argv) + "[/italic]")
            raise e

    ### Postprocessing & plotting
    f = np.linspace(f_start, f_stop, 401)
    port.CalcPort(sim_path, f)
    result = Network()
    result.frequency = f
    result.s = port.uf_ref / port.uf_inc
    return result
