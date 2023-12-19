from .tools import Layer
import gdstk


def straight_line(width: float, length: float, top_metal: Layer, bot_metal: Layer) -> gdstk.Cell:
    m_top = top_metal
    m_bott = bot_metal
    ms = gdstk.Cell("ms")
    le = length * 1e6
    w = width * 1e6
    rf = gdstk.RobustPath((0, 0), w, layer=m_top.data, datatype=m_top.d_type)
    rf.segment((le, 0))
    gnd = gdstk.RobustPath((0, 0), 3 * w, layer=m_bott.data, datatype=m_bott.d_type)
    gnd.segment((le, 0))
    ms.add(rf, gnd)
    ms.add(gdstk.Label("S1", (0, 0), layer=m_top.data, texttype=m_top.d_type))
    ms.add(gdstk.Label("S2", (le, 0), layer=m_top.data, texttype=m_top.d_type))
    ms.add(gdstk.Label("G1", (0, 0), layer=m_bott.data, texttype=m_bott.d_type))
    ms.add(gdstk.Label("G2", (le, 0), layer=m_bott.data, texttype=m_bott.d_type))
    return ms
