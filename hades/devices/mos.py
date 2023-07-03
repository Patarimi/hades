import gdstk
from .devices import Parameters


class Mos:
    def set_dimensions(
        self, specifications: Parameters, parameters: Parameters
    ) -> Parameters:
        ...

    def set_geometries(self, dimensions: Parameters, layers: dict):
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

    def get_accurate(
        self,
    ):
        ...

    def recalibrate(self):
        ...
