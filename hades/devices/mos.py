import gdstk
from .devices import Parameters


class Mos:
    specifications: Parameters
    dimensions: Parameters
    parameters: Parameters

    def update_model(self, specifications: Parameters) -> Parameters:
            #calculate geometries from gm/id and Vds constraint

    def update_cell(self, dimensions: Parameters, layers: dict) -> gdstk.Cell:
        self.dimensions = dimensions
        mos = gdstk.Cell("mos")
        n = dimensions["n"]
        w = dimensions["w"]
        l = dimensions["l"]
        ext_a, ext_g = (100, 80)
        active = gdstk.rectangle(
            (-ext_a, 0), (n * (w + ext_a), l), layer=int(layers["pplus"][0])
        )
        mos.add(active)
        for i in range(n):
            mos.add(
                gdstk.rectangle(
                    (i * (ext_a + w), -ext_g),
                    (w + i * (ext_a + w), l + ext_g),
                    layer=int(layers["poly"][0]),
                )
            )
        return mos

    def update_accurate(self, cell: gdstk.Cell) -> Parameters:
        #extract spice schematic from gds (?)
        #run spice simulation, output gm/id, vds

    def recalibrate_model(self, performances: Parameters) -> Parameters:
        #update model parameter
