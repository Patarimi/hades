from pathlib import Path
import pytest

from hades.wrappers.ngsolve_w import write_stl
from hades.layouts import tools


@pytest.mark.skip(reason="Too slow")
def test_ngsolve(tmp_path):
    layer_stack = tools.LayerStack("mock")
    write_stl(
        Path("tests/test_layouts/ref_ind.gds"),
        layer_stack,
        Path(tmp_path / "test_mesh.stl"),
    )
    assert (tmp_path / "test_mesh.stl").exists()


if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[logging.StreamHandler(), logging.FileHandler("test.log")],
    )
    test_ngsolve(Path("./tmp"))
