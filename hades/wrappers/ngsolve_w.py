from pathlib import Path
from gdstk import read_gds
from netgen import csg, occ
import ngsolve as ng
from hades.layouts.tools import LayerStack
import matplotlib.pyplot as plt


NGGeom = csg.CSGeometry | occ.OCCGeometry


def make_geometry(gds_file: Path, stack: LayerStack = None) -> NGGeom:
    """
    Make a netgen geometry from a gds file.
    :param gds_file:
    :return:
    """
    gdsii = read_gds(gds_file)
    face = None
    z_lim = (0, 0)
    for polygon in gdsii.cells[0].polygons:
        elevation = polygon.layer
        height = 1
        wp = occ.WorkPlane(occ.Axes((0, 0, elevation), n=occ.Z, h=occ.X))
        pts = polygon.points
        wp.MoveTo(*(pts[0]))
        [wp.LineTo(*pt) for pt in pts[1:]]
        wp.LineTo(*(pts[0]))
        face = wp.Face().Extrude(1) if face is None else face + wp.Face().Extrude(height)
        z_lim = (min(z_lim[0], elevation), max(z_lim[1], elevation+height))
    limit = gdsii.cells[0].bounding_box()
    oxyde = occ.Box(occ.gp_Pnt(*(limit[0]), z_lim[0]),
                    occ.gp_Pnt(*(limit[1]), z_lim[1])
                    ).mat("air") - face
    oxyde.bc('air')
    model = face.mat("metal")
    return occ.OCCGeometry(occ.Glue([model, oxyde]))


def compute(geom: NGGeom, /, debug: bool = False):
    mesh = ng.Mesh(geom.GenerateMesh())
    if debug:
        ng.Draw(mesh)
    fes = ng.H1(mesh, order=2, dirichlet="bottom|right")
    u, v = fes.TnT()
    gfu = ng.GridFunction(fes)
    a = ng.BilinearForm(fes)
    a += ng.SymbolicBFI(ng.grad(u) * ng.grad(v))
    a.Assemble()
    f = ng.LinearForm(fes)
    f += ng.SymbolicLFI(ng.x * v)
    f.Assemble()
    gfu.vec.data = a.mat.Inverse(freedofs=fes.FreeDofs()) * f.vec
    if debug:
        ng.Draw(gfu)
    return gfu.vec


geom = make_geometry(Path("./tests/test_layouts/ref_ind.gds"))
res = compute(geom, True)
