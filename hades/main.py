from typer import Typer
from pathlib import Path
from .devices import Mos
import gdstk
import yaml
from os.path import join
from os import makedirs


app = Typer()


@app.command("generate")
def generate_cli(design_yaml: Path = "./design.yml"):
    lib = gdstk.Library()
    with open(design_yaml) as f:
        conf = yaml.load(f, Loader=yaml.Loader)
    with open(conf["techno"]) as f:
        tech = yaml.load(f, Loader=yaml.Loader)
    layers_set = tech["layers"]
    design = conf["design"]
    if design["device"] == "mos":
        mos = Mos()
        cell = mos.set_geometries(design["dimensions"], layers=layers_set)
        lib.add(cell)
    lib.write_gds(conf["name"] + ".gds")


@app.command("new")
def template(project_name: Path = "./working_dir"):
    template_file = """
        name: #insert name of the design
        techno: #path to the yaml tech files
        design:
            
    """
    makedirs(project_name)
    with open(join(project_name, "design.yml"), "w") as f:
        yaml.dump(yaml.load(template_file, yaml.Loader), f)
