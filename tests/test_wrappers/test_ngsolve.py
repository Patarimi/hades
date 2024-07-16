from hades.wrappers.ngsolve_w import compute


def test_ngsolve(tmp_path):
    compute("./tests/test_layouts/ref_.gds", tmp_path / "out.txt")
