import fileinput
import pathlib
from filecmp import cmp

from hades.wrappers.ngspice import NGSpice


def test_ngspice(tmp_path):
    spice = NGSpice()
    data_file = tmp_path / "out.raw"
    spice.compute("./tests/test_wrappers/schem_test.net", data_file)
    assert pathlib.Path(data_file).exists()
    assert pathlib.Path(tmp_path / "out.log").exists()
    # remove the line with the date before comparaison
    for i, line in enumerate(fileinput.input(data_file, inplace=True)):
        if i != 1:
            print(line, end="")
    assert cmp("./tests/test_parser/test_data/inv.raw", tmp_path / "out.raw")
