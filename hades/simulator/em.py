from pathlib import Path
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

    def compute(self, input_file: Path, cell_name: str, f_0: float):
        conf = load_conf(key="emx")
        emx_base = join(conf["base_dir"], conf["name"])
        proc = run(
            [emx_base, input_file, cell_name, self.proc, f_0] + conf["options"],
            capture_output=True,
            encoding="latin",
        )
        y_param = parse(proc.stderr)
        return y_param


def parse(stream: str):
    for line in stream.splitlines():
        words = line.split(
            " ",
        )
        if words[0] == "P2":
            y1 = complex(words[3])
            y2 = complex(words[1])
            break
    if "y1" in locals():
        return y1, y2
    raise RuntimeError("emx exit with error: " + stream)
