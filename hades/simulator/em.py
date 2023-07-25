from pathlib import Path

import numpy as np
import skrf as rf
from .simulator import write_conf, load_conf
from subprocess import run
from os.path import join
from dotenv import load_dotenv
from ..techno import load


class Emx:
    proc: Path

    def setup(self, base_dir: Path, name: str = "emx", option: str = ""):
        conf = {"base_dir": base_dir, "name": name, "option": option}
        conf_path = write_conf({"emx": conf})
        return conf_path

    def prepare(self, techno: str):
        load_dotenv()
        tech = load(techno)
        self.proc = join(tech["base_dir"], tech["process"])

    def compute(self, input_file: Path, cell_name: str, f_0: float, **options):
        conf = load_conf(key="emx")
        emx_base = join(conf["base_dir"], conf["name"])
        cmd = [emx_base, input_file, cell_name, self.proc, f_0]
        if "port" in options:
            for port in options["port"]:
                cmd += ["--port=" + port]
        if "mode" in options:
            cmd += ["--mode="+options["mode"]]
        if "debug" in options and options["debug"]:
            str_cmd = "Running EMX with command:\n\t"
            for elt in cmd:
                str_cmd += str(elt) + " "
            print(str_cmd)
        proc = run(cmd + conf["options"], capture_output=True, encoding="latin")
        y_param = parse(proc.stderr)
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
            f.append(float(words[1].strip(":"))*1e-9)
            port_list_next = True
        if words[0] in ports and len(words) == len(ports)+1:
            y.append([complex(w) for w in words[1:]])
    if "y" in locals():
        y_t = np.squeeze(y)
        net = rf.Network(f=f, y=y_t, units="Hz")
        return net
    raise RuntimeError("emx exit with error: " + stream)
