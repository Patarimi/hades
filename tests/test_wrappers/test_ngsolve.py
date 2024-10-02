from pathlib import Path
from hades.wrappers.ngsolve_w import write_stl
from hades.layouts import tools
from filecmp import cmp


def test_ngsolve(tmp_path):
    layer_stack = tools.LayerStack("mock")
    write_stl(Path("tests/test_layouts/ref_ind.gds"), layer_stack, Path(tmp_path / "test_mesh.stl"))
    assert (tmp_path / "test_mesh.stl").exists()
    assert cmp(tmp_path / "test_mesh.stl", "tests/test_wrappers/ref_mesh.stl")
