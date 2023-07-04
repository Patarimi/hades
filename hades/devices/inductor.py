from .devices import Parameters
import gdstk


class Inductor:
    specifications: Parameters
    dimensions: Parameters  # n, W, G, d_i
    parameters: Parameters

    def __init__(self, L: float = 1e-9, f_0: float = 1e9):
        self.specifications = {"L": L, "f_0": f_0}
        self.parameters = {"K1": 1, "K2": 2}

    def update_model(self, specifications: Parameters = None) -> Parameters:
        # on part de la formule L=k1*µ0*n^2*rho/(1+k2*d)
        # puis on optimise sur W et d_i
        if not (specifications is None):
            self.specifications = specifications
        dimensions = {"n": 0}
        return dimensions

    def update_cell(self, dimensions: Parameters, layers: dict) -> gdstk.Cell:
        # on trace le composant
        ...

    def update_accurate(self, cell: gdstk.Cell) -> Parameters:
        # on fait tourner la simulation on ressort les paramètres S associés
        # puis on calcule l'inductance et la fréquence d'auto-oscillation, le coefficient de qualité
        ...

    def recalibrate_model(self, performances: Parameters) -> Parameters:
        # on recalcule k1 et K2 en fonction des valeurs d'inductances trouvée
        ...
