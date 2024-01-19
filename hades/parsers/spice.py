from pathlib import Path

from lark import Lark, Transformer, Tree
from os.path import join, dirname


def parse(file: str | Path, template: str = "spice") -> Tree:
    tpt_file = join(dirname(__file__), template + ".lark")
    with open(tpt_file, "r") as f:
        spice_parser = Lark(f)
    with open(file) as f:
        t = spice_parser.parse(f.read())
    return t


class SpiceTransformer(Transformer):
    def NAME(self, d):
        return str(d)

    def NET(self, d):
        return str(d)
