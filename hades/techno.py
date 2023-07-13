import os
import re
import yaml
from os.path import join, dirname, isdir
from os import makedirs
import urllib.request
import tarfile, zipfile
from typer import Typer

pkd_app = Typer()


@pkd_app.command("install")
def install(pdk_name: str):
    """
    install the sky130a technology in its default location.
    """
    base_install = join(dirname(__file__), "../pdk/")
    tech = load(pdk_name)
    base_url = tech["source_url"]
    if not (isdir(base_install + pdk_name)):
        makedirs(base_install + pdk_name)
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)')]
    urllib.request.install_opener(opener)
    print("downloading files, might take some times...")
    ext = ".zip" if ".zip" in base_url else ".tar.bz2"
    file_name=base_install+pdk_name+ext
    urllib.request.urlretrieve(base_url, file_name)
    print("extracting, please wait...")
    if ext == ".tar.bz2":
        with tarfile.open(file_name, mode="r") as bz:
            bz.extractall(base_install + pdk_name)
    else:
        with zipfile.open(file_name, mode="r") as zp:
            zp.extractall(base_install+pdk_name)
    os.remove(file_name)


@pkd_app.command("list")
def list_pdk():
    tech_yml = join(dirname(__file__), "techno.yml")
    with open(tech_yml, "r") as f:
        process_d = yaml.load(f, Loader=yaml.Loader)
    print("Available PDKs are:")
    for k in process_d:
        print(f"- {k}")


def load(techno: str):
    tech_yml = join(dirname(__file__), "techno.yml")
    with open(tech_yml, "r") as f:
        process_d = yaml.load(f, Loader=yaml.Loader)
    return process_d[techno]


def get_layer(techno: str, name: str, datatype: str = "drawing"):
    process = load(techno)
    with open(
        join(dirname(__file__), process["base_dir"], process["layermap"]), "r"
    ) as f:
        for line in f:
            if re.match(rf"{name}\s*{datatype}", line, re.IGNORECASE) is not None:
                res = list(filter(None, line.split()))
                return int(res[2]), int(res[3])
