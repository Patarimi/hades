import os
from pathlib import Path

from hades.wrappers.ngsolve_w import write_mesh, make_geometry
from pyelmer import elmer
from pyelmer import execute
from pyelmer.post import scan_logfile
from objectgmsh import add_physical_group


###############
# set up working directory
sim_dir = Path("./simdata")

if not os.path.exists(sim_dir):
    os.mkdir(sim_dir)

write_mesh(make_geometry("ref_ind.gds"), sim_dir / "inductor.msh", debug=True)

###############
# elmer setup
elmer.data_dir="./simdata"

sim = elmer.load_simulation("3D_steady")

air = elmer.load_material("air", sim)
water = elmer.load_material("copper", sim)

solver_heat = elmer.load_solver("VectorialHelmholtzSolver", sim)
solver_output = elmer.load_solver("ResultOutputSolver", sim)
eqn = elmer.Equation(sim, "main", [solver_heat])

T0 = elmer.InitialCondition(sim, "T0", {"Temperature": 273.15})

body_ind = elmer.Body(sim, "copper", [add_physical_group(2, )])
bdy_water.material = water
bdy_water.initial_condition = T0
bdy_water.equation = eqn

bdy_air = elmer.Body(sim, "air", [ph_air])
bdy_air.material = air
bdy_air.initial_condition = T0
bdy_air.equation = eqn

bndry_bottom = elmer.Boundary(sim, "bottom", [ph_bottom])
bndry_bottom.data.update({"Temperature": 353.15})  # 80 °C
bndry_top = elmer.Boundary(sim, "top", [ph_top])
bndry_top.data.update({"Temperature": 293.15})  # 20 °C

sim.write_startinfo(sim_dir)
sim.write_sif(sim_dir)

##############
# execute ElmerGrid & ElmerSolver
execute.run_elmer_grid(sim_dir, "inductor.msh")
execute.run_elmer_solver(sim_dir)

###############
# scan log for errors and warnings
err, warn, stats = scan_logfile(sim_dir)
print("Errors:", err)
print("Warnings:", warn)
print("Statistics:", stats)