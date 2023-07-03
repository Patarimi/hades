from typer import Typer
from pathlib import Path
from .devices import Mos
import gdstk
import yaml


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


@app.command("template")
def template(name: str):
    ...
