# -*- coding: utf-8 -*-
### Import Libraries
import os
import shutil
from os.path import dirname
from pathlib import Path
from typing import Optional

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
        self,
        input_file: Path,
        cell_name: str,
        freq: float | tuple[float],
        ports: Optional[list[Port | str]] = None,
        **options,
):
    ...

### Setup the simulation
Sim_Path = ".\inductor"

post_proc_only = False
refresh_mesh = False
show_model = True
unit = 1e-6  # all length in um

f0 = 2.4e9  # center frequency, frequency of interest!
fc = 0.5e9  # 20 dB corner frequency

# substrate setup
substrate_epsR = 3.38

### Setup FDTD parameter & excitation function
FDTD = openEMS(CoordSystem=0, EndCriteria=1e-4)  # init a rectangular FDTD
FDTD.SetGaussExcite(f0, fc)
FDTD.SetBoundaryCond(["MUR", "MUR", "MUR", "MUR", "MUR", "MUR"])  # boundary conditions

### Setup the Geometry & Mesh
if refresh_mesh:
    geom = make_geometry("../tests/test_layouts/ref_ind.gds", only_metal=True)
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
mesh.SmoothMeshLines("all", 1)

### Run the simulation
if show_model:  # debugging only
    CSX_file = os.path.join(Sim_Path, "bent_patch.xml")
    if not os.path.exists(Sim_Path):
        os.mkdir(Sim_Path)
    CSX.Write2XML(CSX_file)
    from CSXCAD import AppCSXCAD_BIN

    os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))


if not post_proc_only:
    FDTD.Run(Sim_Path)

### Postprocessing & plotting
f = np.linspace(max(1e9, f0 - fc), f0 + fc, 401)
port.CalcPort(Sim_Path, f)
Zin = port.uf_tot / port.if_tot
s11 = port.uf_ref / port.uf_inc
s11_dB = 20.0 * np.log10(np.abs(s11))

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
