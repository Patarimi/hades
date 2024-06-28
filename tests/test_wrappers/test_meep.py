from hades.wrappers.meeper import Meep


def test_meep():
    meep = Meep()
    meep.compute("tmp", "ee", 0.15)
