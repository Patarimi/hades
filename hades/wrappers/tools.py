import logging
import os
from os.path import dirname, join
from subprocess import run, CompletedProcess


def nix_run(cmd: list[str]) -> CompletedProcess:
    os.environ["PDK_ROOT"] = join(dirname(dirname(dirname(__file__))), "pdk")
    over_head = [
        "nix",
        "shell",
        "nixpkgs#magic-vlsi",
        "--extra-experimental-features",
        "nix-command",
        "--extra-experimental-features",
        "flakes",
        "--command",
    ]
    if os.name == "nt":
        over_head = ["wsl", "-d", "NixOS", "--shell-type", "login"] + over_head
    over_head += cmd
    logging.info(" ".join(over_head))
    proc = run(over_head, capture_output=True, text=True)
    return proc
