from pathlib import Path
from hades.wrappers.ngsolve_w import compute, make_geometry


geom = make_geometry(Path("test.gds"))
compute(geom, 2e9, debug=True)
