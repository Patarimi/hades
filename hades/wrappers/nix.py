"""
Run a command in the nix-shell.
"""

import logging
from os import name as os_name
from os.path import dirname
import subprocess


def run_command(cmd: list[str], shell: bool = True, base_dir: bool = True):
    """
    Run a command in the nix-shell.
    """
    if not os_name == "nt":
        base_cmd = []
    else:
        base_cmd = ["wsl", "-d", "NixOS"]
        if base_dir:
            base_cmd.append("--cd")
            base_cmd.append(dirname(dirname(dirname(__file__))))
    if shell:
        base_cmd.append("nix-shell")
        base_cmd.append("--run")
    base_cmd += cmd
    proc = subprocess.run(base_cmd, capture_output=True, shell=True)
    if proc.returncode:
        logging.error(proc.stderr.decode("cp1252"))
        raise SystemError(proc.stderr.decode("cp1252"))
    return proc.stdout.decode("cp1252")
