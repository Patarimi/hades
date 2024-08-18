from pathlib import Path
from hades.wrappers.ngsolve_w import make_geometry


def test_ngsolve(tmp_path):
    geom = make_geometry(Path("tests/test_layouts/ref_ind.gds"))
    mesh = geom.GenerateMesh()
    mesh.Export(str(tmp_path / "test_mesh.stl"), format="STL Format")
