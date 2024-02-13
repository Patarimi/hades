"""
List of function to parse technological lef (TLEF) files.
TLEF files give the information on the back-end composition and associated design rules.
"""

import dataclasses
import logging
from enum import Enum
from pathlib import Path
from .tools import parse
from lark import Discard, Transformer

logging.basicConfig(level=logging.INFO)


@dataclasses.dataclass
class Layer:
    name: str
    ltype: Enum("ROUTING", "CUT")
    width: float


class TechLef(Transformer):
    NAME = str
    FLOAT = float
    WORD = str
    BLOCKNAME = str
    KEYWORD = str
    item = list

    def table(self, _):
        return Discard

    def list(self, _):
        return Discard

    def setting(self, setting):
        return setting[0] if len(setting) == 1 else setting

    def lef58_property(self, _):
        return Discard

    def block(self, block):
        if block[0] != "LAYER":
            # print(f"Discarding block: {block}")
            return Discard
        if block[1] != block[-1]:
            raise ValueError(f"Block name does not match ({block[1]} and {block[-1]}")
        item_dict = dict()
        # print(f"In block: {block=}")
        for item in block[2:-1]:
            if not item:
                print("list is empty, skipping")
                continue
            # print(f"In block: {item=}")
            key = item[0]
            if key in item_dict:
                print(f"In block: {item_dict[key]=}\t{item[1:]=}")
                if item_dict[key] == item[1:] or item_dict[key] == item[1]:
                    # redundant item, skip
                    continue
                print(type(item_dict[key]))
                if isinstance(item_dict[key], float):
                    # previous item was a float, convert to list
                    item_dict[key] = [item_dict[key], "UP_TO", item[3]] + item[1:]
                else:
                    item_dict[key] += item[1:]

            else:
                item_dict.update({item[0]: item[1:] if len(item) > 2 else item[1]})
        # print(f"In block: {item_dict=}")
        return {block[1]: item_dict}

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
    if not layers:
        raise ValueError(f"No layer of type {l_type} found in {full_stack}")
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
    layers = get_all_by_type(l_type, tlef_path)
    try:
        return layers[nbr - 1 if nbr > 0 else nbr]
    except IndexError:
        raise IndexError(f"List out of range with {nbr} in {layers}")


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
