import filecmp
from os.path import curdir, join, dirname

from hades.extractors.spicing import extract_spice
from pathlib import Path

def test_spice_extractor(tmp_path):
    output_path = tmp_path / "spice.spice"
    extract_spice(Path("tests/test_layouts/ref_ind.gds"), techno="sky130", output_path=output_path)
    assert output_path.exists()
    filecmp.cmp(output_path, join(dirname(__file__), "../test_extractors/ref_ind.spice"))
