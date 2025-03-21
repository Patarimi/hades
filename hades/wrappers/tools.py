import logging
import os
from subprocess import run, CompletedProcess


def nix_check():
    if os.name == "nt":
        proc = run(["wsl", "-l"], capture_output=True, text=True)
        list_of_wsl = proc.stdout.replace("\0", "")
        if "NixOS" not in list_of_wsl:
            logging.error(list_of_wsl)
            return False
    try:
        proc = nix_run(["--version"])
        logging.info(proc.stdout)
        return True
    except Exception as e:
        logging.error(e)
        return False


def nix_run(cmd: list[str]) -> CompletedProcess:
    over_head = [
        "nix-shell",
        "--command",
    ]
    if os.name == "nt":
        over_head = ["wsl", "-d", "NixOS", "--shell-type", "login"] + over_head
    over_head.append(" ".join(cmd))
    logging.info(" ".join(over_head))
    proc = run(over_head, capture_output=True, text=True)
    return proc
