"""

"""

import gdstk

from hades.layouts.tools import LayerStack


def via():
    pass


def via_stack(layers: LayerStack, id_top: int, id_bot: int, corner1: [float, float],
              corner2: [float, float]) -> gdstk.Cell:
    v = gdstk.Cell("via")
    id_top = id_top if id_top > 0 else int((len(layers) + 1) / 2 + id_top)
    id_bot = id_bot if id_bot > 0 else int((len(layers) + 1) / 2 + id_bot)
    for i in range(id_bot, id_top):
        lyr = layers.get_metal_layer(i)
        v.add(gdstk.rectangle(corner1, corner2, layer=lyr.data, datatype=lyr.d_type))
        if i == id_top - 1:
            continue
        lyr = layers.get_via_layer(i)
        v.add(gdstk.rectangle(corner1, corner2, layer=lyr.data, datatype=lyr.d_type))
    return v


def ground_plane():
    # option vertical/horizontal/both
    # gestion of density
    # option substrate connection
    pass
