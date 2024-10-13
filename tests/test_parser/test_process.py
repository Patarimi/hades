from pathlib import Path

import hades.parsers.process as process

def test_process():
    diels, metals = process.layer_stack(Path("pdk/mock/mock.proc"))
    assert len(diels) == 5
    assert len(metals) == 10
