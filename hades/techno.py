import logging
import os
from subprocess import run
import tarfile
import urllib.request
import zipfile
from os import makedirs
from os.path import join, dirname, isdir
import yaml
from typer import Typer
from typing import Optional

pkd_app = Typer()


@pkd_app.command("install")
def install(pdk_name: str):
    """
    install the _pdk_name_ technology in its default location.
    """
    base_install = join(dirname(__file__), "../pdk/")
    tech = load_pdk(pdk_name)
    base_url = tech["source_url"]
    if base_url == "volare":
        cmd = [
            "poetry",
            "run",
            "volare",
            "enable",
            "--pdk",
            pdk_name,
            "--pdk-root",
            base_install,
            tech["version"],
        ]
        if os.name == "nt":
            cmd = ["wsl"] + cmd
        ret = run(cmd, capture_output=True)
        return ret
    if not (isdir(base_install + pdk_name)):
        makedirs(base_install + pdk_name)
    opener = urllib.request.build_opener()
    opener.addheaders = [
        (
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
        )
    ]
    urllib.request.install_opener(opener)
    logging.info("downloading files, might take some times...")
    ext = ".zip" if ".zip" in base_url else ".tar.bz2"
    file_name = base_install + pdk_name + ext
    urllib.request.urlretrieve(base_url, file_name)
    logging.info("extracting, please wait...")
    if ext == ".tar.bz2":
        with tarfile.open(file_name, mode="r") as bz:
            bz.extractall(base_install + pdk_name)
    else:
        with zipfile.open(file_name, mode="r") as zp:
            zp.extractall(base_install + pdk_name)
    os.remove(file_name)


@pkd_app.command("list")
def list_pdk() -> list:
    """
    Display the list of available PDK.
    """
    process_d = _read_tech()
    print("Available PDKs are:")
    for k in process_d:
        print(f"- {k}")
    return list(process_d.keys())


def load_pdk(pdk_name: str):
    try:
        tech = _read_tech()[pdk_name]
    except KeyError:
        tech = _read_tech(join(os.getcwd(), "design.yml"))[pdk_name]
    return tech


def _read_tech(tech_file: Optional[str] = None) -> dict:
    if tech_file is None:
        tech_yml = join(dirname(__file__), "techno.yml")
    else:
        tech_yml = tech_file
    with open(tech_yml, "r") as f:
        process_d = yaml.load(f, Loader=yaml.Loader)
    return process_d
