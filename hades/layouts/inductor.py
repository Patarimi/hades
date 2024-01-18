from .tools import LayerStack
import gdstk
from numpy import tan, pi


def octagonal_inductor(
    d_i: float, n_turn: int, width: float, gap: float, layer_stack: LayerStack
):
    """
    generate a one-turn octagonal inductor.
    :param d_i: inner diameter in micron
    :param n_turn: number of turn
    :param width: width of the track
    :param gap: gap between the track
    :param layer_stack: the inductor will be drawn on the highest layer of the stack.
    :return:
    """
    m_top = layer_stack.get_metal_layer(-1)
    ind = gdstk.Cell("ind")
    w = width * 1e6
    d_a = d_i * 1e6 + w
    si = d_a * tan(pi / 8) / 2
    p_ext, p_gap = 20, 10
    turn = gdstk.RobustPath(
        (-p_ext, p_gap), w, layer=m_top.layer, datatype=m_top.datatype
    )
    turn2 = gdstk.RobustPath(
        (-p_ext, -p_gap), w, layer=m_top.layer, datatype=m_top.datatype
    )
    path = (
        (0, p_gap),
        (0, si),
        (d_a / 2 - si, d_a / 2),
        (d_a / 2 + si, d_a / 2),
        (d_a, si),
        (d_a, 0),
    )
    for pts in path:
        turn.segment(pts)
        turn2.segment((pts[0], -pts[1]))
    ind.add(turn, turn2)
    ind.add(
        gdstk.Label("P1", (-p_ext, p_gap), layer=m_top.layer, texttype=m_top.datatype)
    )
    ind.add(
        gdstk.Label("P2", (-p_ext, -p_gap), layer=m_top.layer, texttype=m_top.datatype)
    )

    return ind
