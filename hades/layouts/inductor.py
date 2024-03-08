from .tools import LayerStack
from hades.layouts.general import via
import gdstk
from numpy import tan, pi
from typing import Optional
import logging


def octagonal_inductor(
    d_i: float,
    n_turn: int,
    width: float,
    gap: float,
    layer_stack: LayerStack,
    layer_nb: int = -1,
    pin_name: [str, str] = ("P1", "P2"),
    port_ext: float = 15e-6,
    port_gap: float = -1,
    bridge_nb: Optional[int] = None,
) -> gdstk.Cell:
    """
    generate a multi-turn octagonal inductor.
    :param d_i: inner diameter in micron
    :param n_turn: number of turn
    :param width: width of the track
    :param gap: gap between the track
    :param layer_stack: the inductor will be drawn on the highest layer of the stack.
    :param pin_name: name of the two ports of the inductor (default "P1" and "P2")
    :param port_gap: gap between the two ports (default value : gap).
    :param port_ext: port extension outward the inductor (default value :µm)
    :param layer_nb: layer index for inductor core drawing.
    :param bridge_nb: layer index o the bridge (for multi-turn inductor).
    :return: gdstk.Cell of the inductor
    """
    m_top = layer_stack.get_metal_layer(layer_nb)
    if bridge_nb == 0:
        m_bridge = layer_stack.get_pad_layer()
    else:
        m_bridge = layer_stack.get_metal_layer(
            layer_nb - 1 if bridge_nb is None else bridge_nb
        )
    ind = gdstk.Cell("ind")
    w, g = width * 1e6, gap * 1e6
    d_a = d_i * 1e6 + w
    si = tan(pi / 8) / 2
    p_ext, p_gap = port_ext * 1e6, g + w if port_gap == -1 else port_gap * 1e6 + w
    b_gap = 2 * w + g
    even_turn = n_turn % 2 == 0
    for i in range(n_turn):
        d_a = d_i * 1e6 + w + 2 * i * (w + g)
        end = i == n_turn - 1
        start = i == 0
        logging.debug(
            f"{end=}\t{even_turn=} {0 if (not end) and even_turn else p_gap / 2}"
        )
        path = [
            (-i * (w + g), 0 if (not end) and even_turn else p_gap / 2),
            (-i * (w + g), d_a * si),
            (d_a * (0.5 - si) - i * (w + g), d_a / 2),
            (d_a * (0.5 + si) - i * (w + g), d_a / 2),
            (d_a - i * (w + g), d_a * si),
            (d_a - i * (w + g), b_gap / 2 if even_turn or not start else 0),
        ]
        if end:
            path.insert(0, (-p_ext, p_gap / 2))
        for j in (-1, 1):
            rp = gdstk.RobustPath((path[0][0], j * path[0][1]), w, **m_top.map)
            [rp.segment((x, j * y)) for x, y in path[1:]]
            if not start:
                if j == 1:
                    rp.segment((path[-1][0], path[-1][1] - w / 2))
                    rp.segment((path[-1][0] - w - g, -path[-1][1] + w / 2))
                    rp.segment((path[-1][0] - w - g, -path[-1][1]))
                else:
                    cross = gdstk.RobustPath(
                        (path[-1][0], -path[-1][1] - w), w, **m_bridge.map
                    )
                    cross.segment((path[-1][0], -path[-1][1] + w / 2))
                    cross.segment((path[-1][0] - w - g, path[-1][1] - w / 2))
                    cross.segment((path[-1][0] - w - g, path[-1][1] + w))
                    via_layer = (
                        layer_stack.get_via_layer(layer_nb-1)
                    )
                    v1 = via(via_layer, (w, w))
                    ind.add(
                        cross,
                        gdstk.Reference(
                            v1, origin=(path[-1][0] - 1.5 * w - g, path[-1][1])
                        ),
                        gdstk.Reference(
                            v1, origin=(path[-1][0] - w / 2, -path[-1][1] - w)
                        ),
                    )
            ind.add(rp)
    ind.add(
        gdstk.Label(
            pin_name[0], (-p_ext, p_gap / 2), layer=m_top.layer, texttype=m_top.datatype
        )
    )
    ind.add(
        gdstk.Label(
            pin_name[1],
            (-p_ext, -p_gap / 2),
            layer=m_top.layer,
            texttype=m_top.datatype,
        )
    )

    return ind.flatten()
