"""
List of function to parse technological lef (TLEF) files.
TLEF files give the information on the back-end composition and associated design rules.
"""
from pathlib import Path


def load_tlef(tlef_path: str | Path) -> dict:
    """
    Load a TLEF file and return a dictionary of layer names.
    :param tlef_path: path to the TLEF file
    """
    with open(tlef_path) as f:
        lines = f.readlines()
    layers = {}
    layer_name = None
    for line in lines:
        remove_comment = line.split("#")[0]
        if not remove_comment:
            continue
        line_slip = remove_comment.upper().replace(";", "").split()
        match line_slip:
            case "LAYER", _:
                layer_name = line.split()[1]
                if layer_name not in layers:
                    layers[layer_name] = {}
            case "END", _:
                layer_name = None
            case "TYPE", y:
                layers[layer_name]["TYPE"] = y
            case "WIDTH", width:
                layers[layer_name]["WIDTH"] = float(width)
            case "SPACING", spacing:
                layers[layer_name]["SPACING"] = float(spacing)
            case "ENCLOSURE", *y:
                if y[0] in ("BELOW", "ABOVE"):
                    layers[layer_name]["ENCLOSURE"] = float(y[1])
                else:
                    layers[layer_name]["ENCLOSURE"] = float(y[0])
            case _:
                pass
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
