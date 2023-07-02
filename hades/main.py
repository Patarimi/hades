from typer import Typer
from .devices import Mos, generate
import gdstk

app = Typer()
layers_set = {"poly": (0, 0),
              "pplus": (1, 0)}

dimensions = {"n": 1,
              "w": 130,
              "l": 140,
              }


@app.command("generate")
def generate_cli(name: str, device: str):
    lib = gdstk.Library()
    if device == "mos":
        mos = Mos()
        cell = mos.set_geometries(dimensions, layers=layers_set)
        lib.add(cell)
    lib.write_gds(name+".gds")


@app.command("template")
def template(name: str):
    ...
