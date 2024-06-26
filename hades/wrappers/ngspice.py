import logging
import os
from subprocess import run
from pathlib import Path


class NGSpice:
    """
    Base class for NGSpice simulation.
    """

    def prepare(self):
        pass

    def parse(self):
        pass

    def compute(self, input_file: Path, output_file: Path = None) -> None:
        """
        Simulate the spice input file with ngspice.
        :param input_file: a path to the spice input file.
        :param output_file: result file.
        :return: None
        """
        if output_file is None:
            output_file = input_file.with_suffix(".out")
        cmd = [
            "ngspice",
            "-b",
            to_posix(input_file),
            "-o",
            to_posix(output_file),
        ]
        if os.name == "nt":
            cmd = ["wsl"] + cmd
        logging.info(" ".join(cmd))
        proc = run(cmd, capture_output=True, encoding="latin")
        if proc.returncode != 0:
            RuntimeWarning(str(cmd))
            with open(output_file) as f:
                strm = f.readlines()
            raise RuntimeError(strm)


def to_posix(path: Path) -> str:
    if type(path) is not Path:
        path = Path(path)
    if os.name == "posix":
        return str(path.absolute())
    if path.is_absolute():
        return path.relative_to(os.getcwd()).as_posix()
    return path.as_posix()
