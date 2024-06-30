import os
from pathlib import Path
from typing import Optional

from .nix import run_command
from hades.layouts.tools import Port


class Meep:
    config: dict[str, str]

    def prepare(self):
        """
        Prepare the simulator with the technology files.
        :return:
        """
        ...

    def compute(
        self,
        input_file: Path,
        cell_name: str,
        freq: float | tuple[float],
        ports: Optional[list[Port | str]] = None,
        **options,
    ):
        """
        Compute a simulation from the simulation files.
        :return:
        """
        if os.name == "nt":
            return run_command(["python -c 'from hades.wrappers.meeper import main; main()'"])
        else:
            return main()


def main():
    import meep as mp

    cell = mp.Vector3(16, 8, 0)
    geometry = [
        mp.Block(
            mp.Vector3(mp.inf, 1, mp.inf),
            center=mp.Vector3(),
            material=mp.Medium(epsilon=12),
        )
    ]
    # frequency normalize to 2πc !
    sources = [
        mp.Source(
            mp.ContinuousSource(frequency=0.15),
            component=mp.Ez,
            center=mp.Vector3(-7, 0),
        )
    ]
    pml_layers = [mp.PML(1.0)]
    resolution = 10
    sim = mp.Simulation(
        cell_size=cell,
        boundary_layers=pml_layers,
        geometry=geometry,
        sources=sources,
        resolution=resolution,
    )
    res = sim.run(until=200)
    return res
