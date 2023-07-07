import re
import yaml
from os.path import join, dirname


def load(techno: str):
    tech_yml = join(dirname(__file__), "techno.yml")
    with open(tech_yml, "r") as f:
        process_d = yaml.load(f, Loader=yaml.Loader)
    return process_d[techno]


def get_layer(techno: str, name: str, datatype: str = "drawing"):
    process = load(techno)
    with open(join(process["base_dir"], process["layermap"]), "r") as f:
        for line in f:
            if re.match(rf"{name}[ ]*{datatype}", line, re.IGNORECASE) is not None:
                res = list(filter(None, line.split()))
                return int(res[2]), int(res[3])
