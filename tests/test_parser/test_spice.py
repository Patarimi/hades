from os.path import join, dirname

from hades.parsers.spice import parse, SpiceTransformer


def test_spice_parser():
    test_dir = join(dirname(__file__), "test_data")
    tree = parse(test_dir + "/inv.cir", "spice")
    pp = SpiceTransformer().transform(tree)
    print(pp)
    assert pp
