from typing import Protocol
import yaml
from os.path import isfile, join, dirname
from pathlib import Path
from typer import Typer, Option
from typing_extensions import Annotated

sim_app = Typer()

CONF_PATH = join(dirname(__file__), "simulator.yml")


class Simulator(Protocol):
    config: dict[str, str]

    def prepare(self):
        """
        Prepare the simulator with the technology files.
        :return:
        """
        ...

    def compute(self):
        """
        Compute a simulation from the simulation files.
        :return:
        """
        ...


def write_conf(conf: dict, conf_file: Path = CONF_PATH) -> Path:
    conf_old = load_conf(conf_file)
    for key in conf:
        # update key in conf, keep all the old keys
        conf_old[key] = conf[key]
    with open(conf_file, "w") as f:
        f.write(yaml.dump(conf_old, Dumper=yaml.Dumper))
    return conf_file


def load_conf(conf_file: Path = CONF_PATH, key: str = "") -> dict:
    if not (isfile(conf_file)):
        with open(conf_file, "w") as f:
            pass
    with open(conf_file) as f:
        conf = yaml.load(f, Loader=yaml.Loader)
    if conf is None:
        return dict()
    if key in conf:
        return conf[key]
    return conf


@sim_app.command("config")
def setup(
    simulator: str,
    base_dir: Annotated[Path, Option(prompt=True)],
    name: Annotated[str, Option(prompt=True)],
    option: Annotated[str, Option(prompt=True)],
) -> None:
    """
    Set up the simulator and write all configuration in a config.yml file at hades root.
    :return:
    """
    conf = {"base_dir": str(base_dir), "name": name, "options": option}
    conf_path = write_conf({simulator: conf})
    print(f"Configuration save at {conf_path}")
