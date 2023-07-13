import os
import re
import yaml
from os.path import join, dirname, isdir
from os import makedirs
import urllib.request
import tarfile
from typer import Typer

pkd_app = Typer()


@pkd_app.command("install")
def install():
    """
    install the sky130a technology in its default location.
    """
    base_install = join(dirname(__file__), "../pdk/")
    pdk_name = "sky130a"
    base_url = "https://anaconda.org/LiteX-Hub/open_pdks.sky130a/1.0.421_0_gb662727/download/noarch/open_pdks.sky130a-1.0.421_0_gb662727-20230606_125334.tar.bz2"
    if not (isdir(base_install + pdk_name)):
        makedirs(base_install + pdk_name)
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)')]
    urllib.request.install_opener(opener)
    print("downloading files, might take some times...")
    urllib.request.urlretrieve(base_url, base_install+pdk_name+".tar.bz2")
    print("extracting, please wait...")
    with tarfile.open(base_install + pdk_name + ".tar.bz2", mode="r") as bz:
        bz.extractall(base_install + pdk_name)
    os.remove(base_install+pdk_name+".tar.bz2")


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
