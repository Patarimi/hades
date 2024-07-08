import logging
import os
import shutil
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
        if type(input_file) is str:
            input_file = Path(input_file)
        if output_file is None:
            output_file = input_file.with_suffix(".out")
        if type(output_file) is str:
            output_file = Path(output_file)

        if shutil.which("ngspice") is None:
            raise RuntimeError("NGSpice is not installed.")

        cmd = [
            "ngspice" if os.name != "nt" else "ngspice_con",
            "-b",
            input_file if type(input_file) is str else str(input_file.absolute()),
            "-o",
            output_file if type(output_file) is str else str(output_file.absolute()),
        ]
        logging.info(" ".join(cmd))
        proc = run(cmd, capture_output=True, encoding="latin")
        if proc.returncode != 0:
            RuntimeWarning(str(cmd))
            with open(output_file) as f:
                strm = f.readlines()
            raise RuntimeError(strm)
