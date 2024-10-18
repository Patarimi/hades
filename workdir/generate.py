import os
from os.path import join, dirname
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt
from skrf import Network

from hades.wrappers.oems import compute
from hades.layouts.tools import Port


if __name__ == "__main__":
    if os.getcwd() is not Path(dirname(__file__)):
        print(
            "Running from the wrong directory, changing to the directory of the script"
        )
        os.chdir(dirname(__file__))
    post_proc_only = False
    if not post_proc_only:
        s_res = compute(
            Path("../tests/test_layouts/ref_ind.gds"),
            "inductor",
            (0, 5e9),
            ports=[Port("P1", "P2")],
            sim_path=Path("./inductor"),
            show_model=True,
            skip_run=False,
        )
        s_res.write_touchstone("inductor")
    else:
        s_res = Network("inductor")

    Zin = s_res.z[:, 0, 0]
    f = s_res.frequency.f

    # plot feed point impedance
    fig, ax = plt.subplots(2, 1)
    plt.title("feed point impedance")
    ax[0].plot(f / 1e6, np.real(Zin), "k-", linewidth=2, label=r"$\Re(Z_{in})$")
    plt.grid()
    ax[0].legend()
    ax[0].grid()
    ax[1].plot(
        f / 1e6,
        np.imag(Zin) / (2 * np.pi * f),
        "r--",
        linewidth=2,
        label=r"$\Im(Z_{in})$",
    )
    plt.xlabel("frequency (MHz)")
    plt.ylabel("Inductance ($H$)")
    plt.legend()
    plt.tight_layout()
    plt.show()
