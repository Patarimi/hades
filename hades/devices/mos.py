import gdstk
from pydantic import BaseModel


class Specifications(BaseModel):
    gm_Id: float = 20

class Dimensions(BaseModel):
    n: int = 1
    w: float = 130e-9
    le: float = 2e-6

class Parameters(BaseModel):
    mu_ox: float

class Mos:
    specifications: Specifications
    dimensions: Dimensions
    parameters: Parameters

    def update_model(self, specifications: Specifications) -> Dimensions:
        # calculate geometries from gm/id and Vds constraint
        ...

    def update_cell(self, dimensions: Dimensions, layers: dict) -> gdstk.Cell:
        self.dimensions = dimensions if type(dimensions) is Dimensions else Dimensions(**dimensions)
        mos = gdstk.Cell("mos")
        n = self.dimensions.n
        w = self.dimensions.w * 1e6
        le = self.dimensions.le * 1e6
        ext_a, ext_g = (1, 0.8)
        active = gdstk.rectangle(
            (-ext_a, 0), (n * (w + ext_a), le), layer=int(layers["pplus"][0])
        )
        mos.add(active)
        for i in range(n):
            mos.add(
                gdstk.rectangle(
                    (i * (ext_a + w), -ext_g),
                    (w + i * (ext_a + w), le + ext_g),
                    layer=int(layers["poly"][0]),
                )
            )
        return mos

    def update_accurate(self, cell: gdstk.Cell) -> Specifications:
        # extract spice schematic from gds (?)
        # run spice simulation, output gm/id, vds
        ...

    def recalibrate_model(self, performances: Specifications) -> Parameters:
        # update model parameter
        ...
