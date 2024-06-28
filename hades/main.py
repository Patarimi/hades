import os
import shutil
import subprocess

import logging
from rich.prompt import Confirm
from typer import Typer
from pathlib import Path
import wget
from hades.devices.mos import Mos
from hades.devices.inductor import Inductor
from hades.devices.micro_strip import MicroStrip
from hades.devices.device import generate, Step
import yaml
from os.path import join
from os import makedirs
import hades.techno as techno
import hades.wrappers.simulator as sim

app = Typer()
app.add_typer(techno.pkd_app, name="pdk")
app.add_typer(sim.sim_app, name="sim")

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[logging.FileHandler(join(os.getcwd(), "hades.log"))],
)


@app.command("generate")
def generate_cli(design_yaml: Path = "./design.yml", stop: str = "full") -> None:
    """
    Main command. Run the flow until convergence using _design_yaml_.
    The design can be stopped at a specific step using the _stop_ option.
    """
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


@app.command("new")
def template(project_name: Path = "./working_dir"):
    """
    Create a template directory called _project_name_.
    TODO: Re-write with cookiecutter
    """
    template_file = """
        name: #insert name of the design
        techno: #path to the yaml tech files
        design:
            
    """
    makedirs(project_name)
    with open(join(project_name, "design.yml"), "w") as f:
        yaml.dump(yaml.load(template_file, yaml.Loader), f)


@app.command("init")
def first_time_run():
    if os.name == "nt":
        if shutil.which("wsl") is None:
            raise SystemError("Please install wsl.")
        proc = subprocess.run(["wsl", "--list"], capture_output=True)
        str_out = proc.stdout.decode("utf-16").splitlines()
        logging.info(str_out)
        if "NixOS" not in str_out:
            if not Confirm.ask("NixOS not detected. Install NixOS?"):
                return None
            wget.download(
                "https://github.com/nix-community/NixOS-WSL/releases/download/2311.5.3/nixos-wsl.tar.gz"
            )
            subprocess.run(
                [
                    "wsl",
                    "--import",
                    "NixOS",
                    ".\\NixOS\\",
                    "nixos-wsl.tar.gz",
                    "--version 2",
                ]
            )
            os.remove("nixos-wsl.tar.gz")
            subprocess.run(
                [
                    "wsl",
                    "-d",
                    "NixOS",
                    "sudo nix-channel --add",
                    "https://nixos.org/channels/nixos-24.05 nixos",
                ]
            )
            subprocess.run(["wsl", "-d", "NixOS", "sudo nix-channel --update"])
            subprocess.run(["wsl", "-d", "NixOS", "sudo nixos-rebuild switch"])
    else:
        if shutil.which("nix-shell") is None:
            raise SystemError("Please install nix.")
    run_command("echo Hades successfully Installed !")


@app.command("run")
def run_command(cmd: str, shell: bool = True, base_dir: bool = True):
    """
    Run a command in the nix-shell.
    """
    if os.name == "nt":
        bas_cmd = ["wsl", "-d", "NixOS"]
        if base_dir:
            bas_cmd.append("--cd")
            bas_cmd.append(os.path.dirname(os.path.dirname(__file__)))
        if shell:
            bas_cmd.append("nix-shell")
            bas_cmd.append("--run")
        subprocess.run(bas_cmd + [cmd])
    else:
        subprocess.run(["nix-shell", "--run", cmd])
