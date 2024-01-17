from .tools import LayerStack, Port, Layer
import gdstk
import math


def straight_line(
    width: float,
    length: float,
    layerstack: LayerStack,
    ports: [Port, Port] = (Port("S1"), Port("S2")),
    name: str = "ms",
) -> gdstk.Cell:
    """
    Generate a micro-strip straight line cell. Can be exported as a gds files.
    :param name: name of the cell generated
    :param width: Width of the signal line (Reference line is three time wider).
    :param length: Length of the micro-strip.
    :param layerstack: LayerStack object. The highest metal layer will be used for the signal line.
    The lowest metal layer will be used for the ground plane.
    :param ports: name of the ports
    :return:
    """
    m_top = layerstack.get_metal_layer(-1)
    m_bott = layerstack.get_metal_layer(1)
    ms = gdstk.Cell(name)
    le = length * 1e6
    w = width * 1e6
    rf = gdstk.RobustPath((0, 0), w, layer=m_top.data, datatype=m_top.d_type)
    rf.segment((le, 0))
    gnd = gdstk.RobustPath((0, 0), 3 * w, layer=m_bott.data, datatype=m_bott.d_type)
    gnd.segment((le, 0))
    ms.add(rf, gnd)
    for i in range(2):
        if ports[i].name == "":
            continue
        ms.add(
            gdstk.Label(
                ports[i].name, (i * le, 0), layer=m_top.data, texttype=m_top.d_type
            )
        )
        ms.add(
            gdstk.Label(
                ports[i].ref, (i * le, 0), layer=m_bott.data, texttype=m_bott.d_type
            )
        )
    return ms


def_port = tuple(
    Port(name, ref)
    for name, ref in (("in", "ref1"), ("out", "ref1"), ("cpl", "ref2"), ("iso", "ref2"))
)


def coupled_lines(
    width1: float,
    length: float,
    gap: float,
    layerstack: LayerStack,
    width2: float = -1,
    ports: list[Port] = def_port,
    name: str = "cpl",
) -> gdstk.Cell:
    """
    Generate a cell with two micro-strip lines coupled by a gap. Can be exported as a gds files.
    :param width1: width of the first line.
    :param length: length of the two lines.
    :param gap: gap between the two lines.
    :param layerstack: LayerStack object. The highest metal layer will be used for the signal line.
    The lowest metal layer will be used for the ground plane.
    :param width2: width of the second line.
    :param ports: name of each port.
    :param name: name of the cell.
    :return:
    """
    w2 = width2 if width2 > 0 else width1
    ms1 = straight_line(width1, length, layerstack, ports[0:2])
    ms2 = straight_line(w2, length, layerstack, ports[2:])
    cpl = gdstk.Cell(name)
    ms_rf = gdstk.Reference(ms1, (0, (width1 * 1e6 + gap * 1e6) / 2))
    ms_rf2 = gdstk.Reference(ms2, (0, -(w2 * 1e6 + gap * 1e6) / 2))
    cpl.add(ms_rf, ms_rf2)
    return cpl.flatten()


def lange_coupler(
    width: float,
    length: float,
    gap: float,
    layerstack: LayerStack,
    ports: list[Port] = def_port,
    name: str = "lange",
) -> gdstk.Cell:
    """
    Generate a flat symmetrical lange coupler.
    :param width: track width (in µm)
    :param length: total length of the lines.
    :param gap: space between each track.
    :param layerstack: LayerStack object. The highest metal layer will be used for the signal line.
    The lowest metal layer will be used for the ground plane. The second higher metal layer will be used for bridging.
    :param ports: name of each port.
    :param name: name of the returned cell.
    :return:
    """
    ext = 5
    w, l, g = width * 1e6, length * 1e6, gap * 1e6
    top_metal = layerstack.get_metal_layer(-1)
    bridge = layerstack.get_metal_layer(-2)
    top_via = layerstack.get_via_layer(-1)
    bot_metal = layerstack.get_metal_layer(1)
    first_met = gdstk.FlexPath(
        (0, 0),
        w,
        layer=top_metal.data,
        datatype=top_metal.d_type,
        ends="extended",
    )
    first_met.horizontal(l, relative=True)
    first_met.vertical(2 * (w + g), relative=True)
    first_met.horizontal(-l, relative=True)
    first_met.vertical(ext, relative=True)
    port = gdstk.FlexPath(
        (l, 2.5 * w + 2 * g), w, layer=top_metal.data, datatype=top_metal.d_type
    )
    port.vertical(ext, relative=True)
    sec_met = gdstk.FlexPath(
        [(0, 0), (0, 2 * (w + g))],
        w,
        layer=bridge.data,
        datatype=bridge.d_type,
        ends="extended",
    )
    via_w = 0.4
    via_g = 0.4
    via_s = 0.02
    rep = math.floor((w - 2 * via_s - via_w) / (via_w + via_g)) + 1
    shift = -via_w - (rep - 1) * (via_w + via_g)
    via = gdstk.rectangle(
        (0, 0), (via_w, via_w), layer=top_via.data, datatype=top_via.d_type
    )
    via.repetition = gdstk.Repetition(rep, rep, spacing=(via_g + via_w, via_g + via_w))
    via.translate(shift / 2, shift / 2)
    via2 = via.copy()
    via2.translate(0, 2 * (w + g))
    lange = gdstk.Cell(name)
    thg = gdstk.Cell("thg")
    thg.add(first_met, sec_met, via, via2, port)
    cpl = gdstk.Reference(thg, rotation=math.pi, origin=(l - w - g, w + g))
    thg_r = gdstk.Reference(thg)
    lange.add(cpl, thg_r)
    lange.flatten()
    for i in range(4):
        coord = (
            (0, ext + 2.5 * w + 2 * g),
            (l, ext + 2.5 * w + 2 * g),
            (-w - g, -ext - 1.5 * w - g),
            (l - w - g, -ext - 1.5 * w - g),
        )
        lab = gdstk.Label(
            ports[i].name,
            coord[i],
            layer=top_metal.data,
            texttype=top_metal.d_type,
        )
        ref = gdstk.Label(
            ports[i].ref, coord[i], layer=bot_metal.data, texttype=bot_metal.d_type
        )
        lange.add(lab, ref)
    dim = lange.bounding_box()
    gnd = gdstk.rectangle(
        dim[0], dim[1], layer=bot_metal.data, datatype=bot_metal.d_type
    )
    lange.add(gnd)
    return lange
