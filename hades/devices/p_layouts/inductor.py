from .tools import Layer
import gdstk
from numpy import tan, pi


def octagonal_inductor(d_i: float, n_turn: int, width: float, gap: float, layer: Layer):
    """

    :param d_i: inner diameter in micron
    :param n_turn: number of turn
    :param width: width of the track
    :param gap: gap between the track
    :param layer: the inductor will be drawn on this layer
    :return:
    """
    m_top = layer
    ind = gdstk.Cell("ind")
    w = width * 1e6
    d_a = d_i * 1e6 + w
    si = d_a * tan(pi / 8) / 2
    p_ext, p_gap = 20, 10
    turn = gdstk.RobustPath((-p_ext, p_gap), w, layer=m_top.data, datatype=m_top.d_type)
    turn2 = gdstk.RobustPath((-p_ext, -p_gap), w, layer=m_top.data, datatype=m_top.d_type)
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
    ind.add(gdstk.Label("P1", (-p_ext, p_gap), layer=m_top.data, texttype=m_top.d_type))
    ind.add(gdstk.Label("P2", (-p_ext, -p_gap), layer=m_top.data, texttype=m_top.d_type))

    return ind
