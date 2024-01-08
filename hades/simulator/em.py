from pathlib import Path

import numpy as np
import skrf as rf
from .simulator import load_conf
from subprocess import run
from os.path import join
from dotenv import load_dotenv
from ..techno import load_pdk
import glob


class Emx:
    """
    Base class for emx simulation.
    :param proc: path to the process file.
    """

    proc: Path

    def prepare(self, techno: str):
        """
        Automatically set the process file for the given technology.
        :param techno: name of technology to be used in the simulation.
        :return: None
        """
        load_dotenv()
        tech = load_pdk(techno)
        self.proc = join(tech["base_dir"], tech["process"])

    def compute(
        self, input_file: Path, cell_name: str, freq: float | tuple[float], **options
    ):
        """
        Run the simulation
        :param input_file: gds file to be simulated.
        :param cell_name: name of the cell to simulate.
        :param freq: simulation frequency.
            - If one frequency is given, simulate from 0 to the given frequency.
            - If two frequencies are given, simulate in-between the two frequencies.
            - If more frequencies are given, simulate only at the given frequencies.
        :param options:
        :return: Scikit RF data structure.
        """
        if type(freq) is float:
            f_s = [
                str(freq),
            ]
        else:
            f_s = [str(f) for f in freq]
        conf = load_conf(key="emx")
        emx_base = join(conf["base_dir"], conf["name"])
        # %d enable automatic numbering matching the port number
        path_file = "res.s%dp"
        cmd = (
            [
                emx_base,
                str(input_file),
                cell_name,
                self.proc,
                "--sweep",
            ]
            + f_s
            + [
                "--format=touchstone",
                "-s" + path_file,
            ]
        )
        if "port" in options:
            for port in options["port"]:
                cmd += ["-p " + port]
        if "mode" in options:
            cmd += ["--mode=" + options["mode"]]
        if "debug" in options and options["debug"]:
            str_cmd = "Running EMX with command:\n\t"
            for elt in cmd:
                str_cmd += str(elt) + " "
        proc = run(cmd + conf["options"], capture_output=True, encoding="latin")
        if proc.returncode != 0:
            print(cmd + conf["options"])
            print(proc.stderr)
        # get back the real name.
        res_path = glob.glob(path_file.replace("%d", "[0-9]"))
        y_param = rf.Network(res_path[0])
        return y_param


def parse(stream: str) -> rf.Network:
    f = list()
    ports = list()
    y = list()
    port_list_next = False
    for line in stream.splitlines():
        words = line.split()
        if port_list_next:
            ports = words
            port_list_next = False
        if words[0] == "Frequency":
            f.append(float(words[1].strip(":")) * 1e-9)
            port_list_next = True
        if words[0] in ports and len(words) == len(ports) + 1:
            y.append([complex(w) for w in words[1:]])
    if len(y) > 0:
        y_t = np.squeeze(y)
        net = rf.Network(f=f, y=y_t, units="Hz")
        return net
    raise RuntimeError(stream)
