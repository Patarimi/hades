"""
List of function to parse technological lef (TLEF) files.
TLEF files give the information on the back-end composition and associated design rules.
"""
from pathlib import Path


def load_tlef(tlef_path: Path) -> dict:
    """
    Load a TLEF file and return a dictionary of layer names.
    :param tlef_path: path to the TLEF file
    """
    with open(tlef_path) as f:
        lines = f.readlines()
    layers = {}
    layer_name = None
    for line in lines:
        if line.startswith("LAYER"):
            layer_name = line.split()[1]
            layers[layer_name] = {}
        elif line.startswith("END"):
            layer_name = None
        elif line.lstrip().startswith("TYPE"):
            layer_type = line.split()[1]
            layers[layer_name]["type"] = layer_type
    return layers


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
        if full_stack[layer]["type"] == l_type:
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