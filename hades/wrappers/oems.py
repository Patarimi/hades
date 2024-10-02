# -*- coding: utf-8 -*-
### Import Libraries
import os
import shutil
from os.path import dirname
from pathlib import Path
from typing import Optional
from skrf import Network
import matplotlib.pyplot as plt
import numpy as np

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
        **options,
):
    ### Setup the simulation
    Sim_Path = ".\inductor"

    refresh_mesh = False
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
    if "show_model" in options and options["show_model"]:  # debugging only
        CSX_file = os.path.join(Sim_Path, "bent_patch.xml")
        if not os.path.exists(Sim_Path):
            os.mkdir(Sim_Path)
        CSX.Write2XML(CSX_file)
        from CSXCAD import AppCSXCAD_BIN

        os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

    if "post_proc_only" not in options or not options["post_proc_only"]:
        FDTD.Run(Sim_Path)

    ### Postprocessing & plotting
    f = np.linspace(f_start, f_stop, 401)
    port.CalcPort(Sim_Path, f)
    result = Network()
    result.frequency = f
    result.s = port.uf_ref / port.uf_inc
    return result


if __name__ == "__main__":
    post_proc_only = False
    if not post_proc_only:
        s_res = compute(
            Path("../tests/test_layouts/ref_ind.gds"),
            "inductor",
            (0, 5e9),
            ports=[Port("in")],
            unit=1e-6,
            options={
                "show_model": False,
                "post_proc_only": True,
            }
        )
        s_res.write_touchstone("inductor.s2p")
    else:
        s_res = Network("inductor.s2p")

    Zin = s_res.z
    f = s_res.frequencyff

    # plot feed point impedance
    fig, ax = plt.subplots(2,1)
    plt.title("feed point impedance")
    ax[0].plot(f / 1e6, np.real(Zin), "k-", linewidth=2, label=r"$\Re(Z_{in})$")
    plt.grid()
    ax[0].legend()
    ax[0].grid()
    ax[1].plot(f / 1e6, np.imag(Zin) / (2*np.pi*f), "r--", linewidth=2, label=r"$\Im(Z_{in})$")
    plt.xlabel("frequency (MHz)")
    plt.ylabel("Inductance ($H$)")
    plt.legend()
    plt.tight_layout()
    plt.show()
