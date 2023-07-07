from typer import Typer
from pathlib import Path
from .devices import *
from .simulator import *
import yaml
from os.path import join
from os import makedirs
import hades.techno as techno

app = Typer()


@app.command("generate")
def generate_cli(design_yaml: Path = "./design.yml", stop: STEP = "") -> None:
    """
    Main command. Run the flow until convergence using _design_yaml_.
    The design can be stopped at a specific step using the _stop_ option.
    """
    with open(design_yaml) as f:
        conf = yaml.load(f, Loader=yaml.Loader)
    tech = techno.load(conf["techno"])
    design = conf["design"]
    if design["device"] == "mos":
        dut = Mos()
    if design["device"] == "inductor":
        dut = Inductor(
            name=conf["name"], proc_file=join(tech["base_dir"], tech["process"])
        )
    dimensions = design["dimensions"]
    generate(dut, design["specifications"], conf["techno"], dimensions, stop)


@app.command("new")
def template(project_name: Path = "./working_dir"):
    """
    Create a template directory called _project_name_.
    """
    template_file = """
        name: #insert name of the design
        techno: #path to the yaml tech files
        design:
            
    """
    makedirs(project_name)
    with open(join(project_name, "design.yml"), "w") as f:
        yaml.dump(yaml.load(template_file, yaml.Loader), f)


@app.command("config")
def setup(simulator_name: str):
    if simulator_name == "emx":
        sim = Emx()
    path = sim.setup(base_dir=Path("."))
    print(f"Configuration save at {path}")
