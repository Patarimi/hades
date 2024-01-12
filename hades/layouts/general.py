"""
This module contains function to generate general purpose cells.
(Via, via stack, ground plane, etc.)
"""

import gdstk

from hades.layouts.tools import LayerStack


def via(layer: LayerStack, id_via: int, size: [float, float]) -> gdstk.Cell:
    """
    This function generates a via cell.
    :param layer: The stack of layers to use.
    :param id_via: The id of the via in the stack.
    :param size: tuple of the size (length and width) of the via.
    :return: a gdstk.Cell containing the via.
    """
    v = gdstk.Cell("via")
    v.add(
        gdstk.rectangle(
            (0, 0),
            size,
            layer=layer.get_via_layer(id_via).data,
            datatype=layer.get_via_layer(id_via).d_type,
        )
    )
    return v


def via_stack(
    layers: LayerStack,
    id_top: int,
    id_bot: int,
    size: [float, float],
) -> gdstk.Cell:
    """
    This function generates a via stack cell.
    :param layers: The stack of layers to use.
    :param id_top: id of the top metal layer.
    :param id_bot: id of the bottom metal layer.
    :param size: tuple of the size (length and width) of the via.
    :return: a gdstk.Cell containing the via stack.
    """
    v = gdstk.Cell("via")
    id_top = id_top if id_top > 0 else int((len(layers) + 1) / 2 + id_top)
    id_bot = id_bot if id_bot > 0 else int((len(layers) + 1) / 2 + id_bot)
    for i in range(id_bot, id_top):
        lyr = layers.get_metal_layer(i)
        v.add(gdstk.rectangle((0, 0), size, layer=lyr.data, datatype=lyr.d_type))
        if i == id_top - 1:
            continue
        lyr = layers.get_via_layer(i)
        v.add(gdstk.rectangle((0, 0), size, layer=lyr.data, datatype=lyr.d_type))
    return v


def ground_plane(
    layers: LayerStack, size: [float, float], id_gnd: int = 1
) -> gdstk.Cell:
    """
    This function generates a ground plane cell.
    :param layers: The stack of layers to use.
    :param size: size (length and width) of the ground plane.
    :param id_gnd: id of the ground metal layer.
    :return:
    """
    # option vertical/horizontal/both
    # gestion of density
    # option substrate connection
    gnd = gdstk.Cell("ground")
    gnd.add(
        gdstk.rectangle(
            (0, 0),
            size,
            layer=layers.get_metal_layer(0).data,
            datatype=layers.get_metal_layer(0).d_type,
        )
    )
    return gnd
