import shutil

from cyclopts import App
from pathlib import Path
from hades.devices.mos import Mos
from hades.devices.inductor import Inductor
from hades.devices.micro_strip import MicroStrip
from hades.devices.device import generate, Step
import yaml
from os.path import join
from os import makedirs
import hades.techno as techno
import hades.wrappers.simulator as sim

app = App()
app.command(techno.pkd_app)
app.command(sim.sim_app)
if shutil.which("openEMS"):
    from hades.wrappers.oems import oems_app

    app.command(oems_app)


@app.command(name="generate")
def generate_cli(design_yaml: Path = "./design.yml", stop: str = "full") -> None:
    """Main command. Run the flow until convergence using _design.yaml_. The design can be stopped at a specific step using the _stop_ option."""
    with open(design_yaml) as f:
        conf = yaml.load(f, Loader=yaml.Loader)
    design = conf["design"]
    if design["device"] == "mos":
        dut = Mos()
    elif design["device"] == "inductor":
        dut = Inductor(name=conf["name"], techno=conf["techno"])
    elif design["device"] == "micro-strip":
        dut = MicroStrip(name=conf["name"], techno=conf["techno"])
    else:
        raise RuntimeError("Unknown device, choice are mos, inductor")
    dimensions = design["dimensions"]
    generate(dut, design["specifications"], dimensions, Step[stop])


@app.command(name="new")
def template(project_name: Path = "./working_dir"):
    """Create a template directory called _project_name_."""
    """
    TODO: Re-write with cookiecutter
    :param project_name: Name of the project.
    """
    template_file = """
        name: #insert name of the design
        techno: #path to the yaml tech files
        design:
            
    """
    makedirs(project_name)
    with open(join(project_name, "design.yml"), "w") as f:
        yaml.dump(yaml.load(template_file, yaml.Loader), f)
