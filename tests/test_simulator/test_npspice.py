import pathlib

from hades.simulators.ngspice import NGSpice


def test_ngspice(tmp_path):
    spice = NGSpice()
    spice.compute("./tests/test_simulator/schem_test.net", tmp_path / "out.txt")
    assert pathlib.Path(tmp_path / "out.txt").exists()
