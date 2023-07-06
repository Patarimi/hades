from typing import Protocol
import yaml
from os.path import isfile, join, dirname
from pathlib import Path

CONF_PATH = join(dirname(__file__), "simulator.yml")


class Simulator(Protocol):
    def setup(self) -> Path:
        """
        Set up the simulator and write all configuration in a config.yml file at hades root.
        :return:
        """
        ...

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
