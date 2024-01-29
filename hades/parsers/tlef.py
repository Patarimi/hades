"""
List of function to parse technological lef (TLEF) files.
TLEF files give the information on the back-end composition and associated design rules.
"""
from pathlib import Path

import lark

from .tools import parse
from lark import Transformer


class TechLef(Transformer):
    NAME = str
    FLOAT = float
    WORD = str
    BLOCKNAME = str

    def setting(self, setting):
        if len(setting) > 2:
            if setting[1] == "RANGE":
                return {setting[0]: setting[2]}
            if setting[0] in ("BELOW", "ABOVE"):
                return {setting[0]: setting[1:]}
            else:
                return setting
        return setting[0] if len(setting) == 1 else {setting[0]: setting[1]}

    def item(self, item):
        return {item[0]: item[1]}

    def lef58_property(self, lef58_property):
        return {lef58_property[2]: lef58_property[3]}

    def block(self, block):
        if block[0] == "LAYER":
            item_dict = dict()
            for item in block[2:-1]:
                key = list(item.keys())[0]
                if key in item_dict:
                    if isinstance(item_dict[key], list):
                        item_dict[key].append(item[key])
                    elif isinstance(item_dict[key], dict):
                        item_dict[key].update(item[key])
                    else:
                        item_dict.update({key: [item_dict[key], item[key]]})
                else:
                    item_dict.update(item)
            return {block[1]: item_dict}
        return block

    def start(self, start):
        ss = dict()
        for layer in start:
            if isinstance(layer, list):
                continue
            if list(layer.keys())[0] in ("VERSION", "USEMINSPACING"):
                continue
            ss.update(layer)
        return ss


def load_tlef(tlef_path: str | Path) -> dict:
    """
    Load a TLEF file and return a dictionary of layer names.
    :param tlef_path: path to the TLEF file
    """
    t = parse(tlef_path, "tlef")
    return TechLef().transform(t)


def get_all_by_type(l_type: str, tlef_path: Path) -> list[str]:
    """
    Return the layers of the given type.
    :param l_type: type of the layer
    :param tlef_path: path to the TLEF file
    :return: list of layer names for the given type
    """
    layers = list()
    full_stack = load_tlef(tlef_path)
    for layer in full_stack:
        if full_stack[layer]["TYPE"] == l_type:
            layers.append(layer)
    return layers


def get_by_type(l_type: str, tlef_path: Path, nbr: int) -> str:
    """
    Return the $nbr^{th}$ layer of the given type.
    :param l_type: layer type
    :param tlef_path: path to the TLEF file
    :param nbr: indice of the layer to return
        if nbr is negative, the last layer of the given type is returned
    :return: layer name
    """
    if nbr == 0:
        raise ValueError("nbr cannot be 0")
    return get_all_by_type(l_type, tlef_path)[nbr - 1 if nbr > 0 else nbr]


def get_metal(nbr: int, tlef_path: Path) -> str:
    """
    Return the name of the $nbr^{th}$ metal (starting at 1).
    :param nbr: metal layer number
    :return: name of the metal layer
    """
    return get_by_type("ROUTING", tlef_path, nbr)


def get_via(nbr: int, tlef_path: Path) -> str:
    """
    Return the name of the $nbr^{th}$ via (starting at 1).
    :param nbr: via layer number
    :param tlef_path: path to the TLEF file
    :return: name of the via layer
    """
    return get_by_type("CUT", tlef_path, nbr)
