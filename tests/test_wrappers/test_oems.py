import shutil
from os.path import dirname
from pathlib import Path
import pytest

from hades.wrappers.oems import compute, Frequency


@pytest.mark.skipif(shutil.which("openEMS") is None, reason="OpenEMS not found in PATH")
def test_compute(tmp_path):
    compute(
        Path(dirname(__file__)) / "../test_layouts/ref_ind2.gds",
        "ind",
        Frequency(start=0, stop=1e9),
        sim_path=tmp_path,
        skip_run=True,
    )
