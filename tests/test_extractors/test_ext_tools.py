from hades.extractors.tools import check_diff

def test_check_diff():
    assert check_diff("tests/test_extractors/ref_sky130_fd.cir", "tests/test_extractors/ref_sky130_fd.cir")
    assert not check_diff("tests/test_extractors/ref_sky130_fd_wrong.cir", "tests/test_extractors/ref_sky130_fd.cir")
