"""
List of function to parse layer map file.
Layer map files give the link between layer name and (data, data-type) numbers for gdsii generation.
"""
from pathlib import Path
from hades.techno import load_pdk
from os.path import join, dirname, isabs


def load_map(techno: str) -> dict:
    """
    Read all layer numbers from layermap file.
    :param techno: name of the selected technology.
    :return: list of layer numbers
    """
    layer_info = dict()
    pdk = load_pdk(techno)
    if isabs(pdk["base_dir"]):
        map_path = join(pdk["base_dir"], pdk["layermap"])
    else:
        map_path = join(dirname(dirname(__file__)), pdk["base_dir"], pdk["layermap"])
    with open(map_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        part = line.split()
        if len(part) < 4 or part[0] in ("NAME", "DIEAREA"):
            continue
        if part[0] not in layer_info:
            layer_info[part[0]] = {part[1]: (int(part[2]), int(part[3]))}
        else:
            layer_info[part[0]][part[1]] = (int(part[2]), int(part[3]))
    return layer_info


def get_number(techno: str, name: str, datatype: str = "drawing") -> tuple[int, int]:
    """
    Read layer information (layer number and datatype) from layermap file.
    :param techno: name of the selected technology.
    :param name: name of the layer
    :param datatype: type of the data (drawing, pin, etc.)
    :return: layer number and datatype
    """
    layer_info = load_map(techno)
    if name not in layer_info:
        raise KeyError(f"Layer {name} not found in {techno}")
    datatypes = layer_info[name]
    for d_type in datatypes:
        if datatype in d_type.split(","):
            return datatypes[d_type]
    raise KeyError(
        f"Datatype {datatype} not found for layer {name} in {techno}.\n"
        "Available datatypes are: {datatypes.keys()}."
    )
