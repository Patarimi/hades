import logging
import os
from os.path import dirname, join
from subprocess import run, CompletedProcess


def nix_run(cmd: list[str]) -> CompletedProcess:
    over_head = [
        "nix-shell",
        "--command",
    ]
    if os.name == "nt":
        over_head = ["wsl", "-d", "Ubuntu-24.04", "--shell-type", "login"] + over_head
    over_head.append(" ".join(cmd))
    logging.info(" ".join(over_head))
    proc = run(over_head, capture_output=True, text=True)
    return proc
