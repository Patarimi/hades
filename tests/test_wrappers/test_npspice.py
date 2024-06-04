import pathlib

from hades.wrappers.ngspice import NGSpice


def test_ngspice(tmp_path):
    spice = NGSpice()
    spice.compute(pathlib.Path("./tests/test_simulator/schem_test.net"), tmp_path / "out.txt")
    assert pathlib.Path(tmp_path / "out.txt").exists()
