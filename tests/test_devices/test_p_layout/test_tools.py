from hades.devices.p_layouts import tools


def test_tools():
    lay = tools.Layer(100, 4)
    assert str(lay) == "100/4"
    lay2 = tools.Layer(141)
    assert str(lay2) == "141/0"
    tools.check_diff("../tests/test_devices/test_p_layout/ind_ref.gds",
                     "../tests/test_devices/test_p_layout/ind_ref.gds")
