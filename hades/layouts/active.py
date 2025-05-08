import klayout.db as db
import numpy as np
from enum import Enum
from hades.layouts.tools import LayerStack, ViaLayer, Layer
from hades.layouts.general import via
import gdsfactory as gf


class DiffEnum(str, Enum):
    N = "n"
    P = "p"


def mosfet(
    layout: db.Layout,
    layers: LayerStack,
    nf: int = 5,
    diff_type: DiffEnum = DiffEnum.N,
    width=2,
    length=0.13,
    active_layer: Layer = Layer(22, 0, "active", spacing=0.5),
    doping_layer: Layer = Layer(32, 0, "nplus", spacing=0.38),
    poly_layer: Layer = Layer(30, 0, "poly", spacing=0.5),
):
    doping_ext = doping_layer.spacing
    gate_ext = poly_layer.spacing
    m1_layer = layers.get_metal_layer(1)
    m1_width = m1_layer.width if m1_layer.width > 0 else 0.4
    diff_space = active_layer.spacing
    via_layer = ViaLayer(33, 0, "con", 0.3, 0.15)

    mos = layout.create_cell(f"{diff_type.value}mos_{nf}")
    gate = layout.create_cell("gate")
    gate.shapes(poly_layer.tuple).insert(db.DBox(0, 0, length, width + 2 * gate_ext))
    pitch = length + diff_space
    gates = db.DCellInstArray(
        gate.cell_index(),
        db.DTrans(diff_space, -gate_ext),
        db.DVector(pitch, 0),
        db.DVector(0, 1),
        nf,
        1,
    )
    mos.insert(gates)
    dr_con = layout.create_cell("dr_con")
    dr_con.shapes(m1_layer.tuple).insert(db.DBox(0, 0, m1_width, width))
    con = via(layout, via_layer, (m1_width, width))
    dr_con.insert(db.DCellInstArray(con, db.DVector(0, 0)))
    dr_cons = db.DCellInstArray(
        dr_con.cell_index(),
        db.DTrans((diff_space - m1_width) / 2, 0),
        db.DVector(pitch, 0),
        db.DVector(0, 1),
        nf + 1,
        1,
    )
    mos.insert(dr_cons)
    mos.shapes(active_layer.tuple).insert(db.DBox(0, 0, diff_space + nf * pitch, width))
    mos.shapes(doping_layer.tuple).insert(
        db.DBox(
            -doping_ext,
            -doping_ext,
            diff_space + nf * pitch + doping_ext,
            width + doping_ext,
        )
    )
    for i in range(nf):
        mos.shapes(poly_layer.tuple).insert(
            db.DText(f"g{i}", i * pitch + diff_space + length / 2, -gate_ext)
        )
        mos.shapes(m1_layer.tuple).insert(
            db.DText(f"dr{i}", i * pitch + diff_space / 2, width / 2)
        )
    mos.flatten(-1, True)
    return mos
