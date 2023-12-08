from hades.parser.netlist import Component, Netlist


def test_component():
    c5 = Component("C", "5", 5e-12, ("gnd", "5"))
    r_mid = Component("R", "mid", 5e3, ("5", "6"))
    assert str(c5) == "C5 gnd 5 5.000 pF"
    assert str(r_mid) == "Rmid 5 6 5.000 kΩ"


def test_netlist():
    net = Netlist("test")
    net.append(Component("C", "5", 5e-12, ("gnd", "5")))
    assert net.name == "test"
    assert net.spice() == "#test\nC5 gnd 5 5.000 pF\n"
