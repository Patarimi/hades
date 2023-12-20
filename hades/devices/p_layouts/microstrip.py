from .tools import Layer, Port
import gdstk


def straight_line(
    width: float,
    length: float,
    top_metal: Layer,
    bot_metal: Layer,
    ports: [Port, Port] = (Port("S1"), Port("S2")),
) -> gdstk.Cell:
    """
    Generate a micro-strip straight line cell. Can be exported as a gds files.
    :param width: Width of the signal line (Reference line is three time wider).
    :param length: Length of the micro-strip.
    :param top_metal: Layer of the signal line
    :param bot_metal: Layer of the reference line
    :param ports: name of the
    :return:
    """
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
    ms.add(gdstk.Label(ports[0].name, (0, 0), layer=m_top.data, texttype=m_top.d_type))
    ms.add(gdstk.Label(ports[1].name, (le, 0), layer=m_top.data, texttype=m_top.d_type))
    ms.add(gdstk.Label(ports[0].ref, (0, 0), layer=m_bott.data, texttype=m_bott.d_type))
    ms.add(
        gdstk.Label(ports[1].ref, (le, 0), layer=m_bott.data, texttype=m_bott.d_type)
    )
    return ms


def coupled_line():
    ...
