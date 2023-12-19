from hades.devices.p_layouts import tools


def test_tools():
    lay = tools.Layer(100, 4)
    assert str(lay) == "100/4"
    lay2 = tools.Layer(141)
    assert str(lay2) == "141/0"
