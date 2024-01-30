from numpy import pi

from .tools import LayerStack, Port
from .general import via_stack
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
    rf = gdstk.RobustPath((0, 0), w, layer=m_top.layer, datatype=m_top.datatype)
    rf.segment((le, 0))
    gnd = gdstk.RobustPath((0, 0), 3 * w, layer=m_bott.layer, datatype=m_bott.datatype)
    gnd.segment((le, 0))
    ms.add(rf, gnd)
    for i in range(2):
        if ports[i].name == "":
            continue
        ms.add(
            gdstk.Label(
                ports[i].name, (i * le, 0), layer=m_top.layer, texttype=m_top.datatype
            )
        )
        ms.add(
            gdstk.Label(
                ports[i].ref, (i * le, 0), layer=m_bott.layer, texttype=m_bott.datatype
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


diff_port = tuple(
    Port(name, ref)
    for name, ref in (("in", "ref1"), ("out_p", "ref2"), ("out_n", "ref2"))
)


def marchand_balun(
        width: float,
        length: float,
        gap: float,
        space: float,
        layerstack: LayerStack,
        widths: float = -1,
        ports: list[Port] = diff_port,
        name: str = "marchand",
) -> gdstk.Cell:
    """
    Implements a marchand balun, for a 50Ω balun, 2 -4.8 dB 90° coupler are required.
    :param width: width of the signal lines.
    :param length: length of the signal line (the coupler length is twice this value).
    :param gap: gap between the two lines.
    :param space: space between the two couplers.
    :param layerstack: LayerStack object. The highest metal layer will be used for the signal line.
        The lowest metal layer will be used for the ground plane.
    :param widths: width of the line in-between the two couplers.
    :param ports: name of each port.
    :param name: name of the cell.
    :return: a gdstk.Cell object with the marchand balun.
    """
    m_top = layerstack.get_metal_layer(-1)
    m_bott = layerstack.get_metal_layer(1)
    w, l, g, s = width * 1e6, length * 1e6, gap * 1e6, space * 1e6
    ws = w if widths < 0 else widths * 1e6
    bln = gdstk.Cell(name)
    emp_port = Port("")
    cpl = lange_coupler(width, length, gap, layerstack, [emp_port for k in range(4)], ext=0)
    cpl1 = gdstk.Reference(cpl, (0, -l), pi / 2, x_reflection=True)
    cpl1_bb = cpl1.bounding_box()
    cpl2 = gdstk.Reference(cpl, (s + cpl1_bb[1][0] - cpl1_bb[0][0], -w - g), -pi / 2)
    cpl2_bb = cpl2.bounding_box()
    r1 = gdstk.rectangle(
        (cpl1_bb[1][0], cpl1_bb[0][1] + 1.5 * w + g + ws / 2),
        (cpl2_bb[0][0], cpl2_bb[0][1] + 1.5 * w + g - ws / 2),
        **m_top.map,
    )
    bln.add(cpl1, cpl2, r1)
    r2 = gdstk.rectangle(
        bln.bounding_box()[0],
        bln.bounding_box()[1],
        **m_bott.map,
    )
    bln.add(r2)
    for i in range(3):
        coord = (
            (cpl1_bb[1][0] - 1.5 * w - g, cpl1_bb[1][1]),
            (cpl1_bb[0][0] + 1.5 * w + g, cpl1_bb[0][1]),
            (cpl2_bb[1][0] - 1.5 * w - g, cpl2_bb[0][1]),
        )
        lab = gdstk.Label(
            ports[i].name,
            coord[i],
            layer=m_top.layer,
            texttype=m_top.datatype,
        )
        bln.add(lab)
    bln.add(
        gdstk.Reference(
            via_stack(layerstack, -2, 1, (2 * g + 3 * w, w)),
            (cpl1_bb[0][0], cpl1_bb[1][1] - g - 2 * w),
        )
    )
    bln.add(
        gdstk.Reference(
            via_stack(layerstack, -2, 1, (2 * g + 3 * w, w)),
            (cpl2_bb[1][0] - 2 * g - 3 * w, cpl2_bb[1][1] - g - 2 * w),
        )
    )
    return bln.flatten()


def lange_coupler(
        width: float,
        length: float,
        gap: float,
        layerstack: LayerStack,
        ports: list[Port] = def_port,
        name: str = "lange",
        ext: float = 5,
) -> gdstk.Cell:
    """
    Generate a flat symmetrical lange coupler with two strips per track.
    :param width: track width (in µm)
    :param length: total length of the lines.
    :param gap: space between each track.
    :param layerstack: LayerStack object. The highest metal layer will be used for the signal line.
    The lowest metal layer will be used for the ground plane. The second higher metal layer will be used for bridging.
    :param ports: name of each port.
    :param name: name of the returned cell.
    :param ext: extension of the ports
    :return:
    """
    w, l, g = width * 1e6, length * 1e6, gap * 1e6
    top_metal = layerstack.get_metal_layer(-1)
    bridge = layerstack.get_metal_layer(-2)
    top_via = layerstack.get_via_layer(-1)
    bot_metal = layerstack.get_metal_layer(1)
    first_met = gdstk.FlexPath(
        (0, 0),
        w,
        layer=top_metal.layer,
        datatype=top_metal.datatype,
        ends="extended",
    )
    first_met.horizontal(l, relative=True)
    first_met.vertical(2 * (w + g), relative=True)
    first_met.horizontal(-l, relative=True)
    first_met.vertical(ext, relative=True)
    port = gdstk.FlexPath(
        (l, 2.5 * w + 2 * g), w, layer=top_metal.layer, datatype=top_metal.datatype
    )
    port.vertical(ext, relative=True)
    sec_met = gdstk.FlexPath(
        [(0, 0), (0, 2 * (w + g))],
        w,
        layer=bridge.layer,
        datatype=bridge.datatype,
        ends="extended",
    )
    via_w = 0.4
    via_g = 0.4
    via_s = 0.02
    rep = math.floor((w - 2 * via_s - via_w) / (via_w + via_g)) + 1
    shift = -via_w - (rep - 1) * (via_w + via_g)
    via = gdstk.rectangle(
        (0, 0), (via_w, via_w), layer=top_via.layer, datatype=top_via.datatype
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
        if ports[i].name == "":
            continue
        lab = gdstk.Label(
            ports[i].name,
            coord[i],
            layer=top_metal.layer,
            texttype=top_metal.datatype,
        )
        ref = gdstk.Label(
            ports[i].ref, coord[i], layer=bot_metal.layer, texttype=bot_metal.datatype
        )
        lange.add(lab, ref)
    dim = lange.bounding_box()
    gnd = gdstk.rectangle(
        dim[0], dim[1], layer=bot_metal.layer, datatype=bot_metal.datatype
    )
    lange.add(gnd)
    return lange
