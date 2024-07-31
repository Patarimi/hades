from pathlib import Path
from gdstk import read_gds
from netgen import csg, occ
import ngsolve as ng
from hades.layouts.tools import LayerStack
import matplotlib.pyplot as plt
from math import pi


NGGeom = csg.CSGeometry | occ.OCCGeometry


def make_geometry(gds_file: Path, stack: LayerStack = None) -> NGGeom:
    """
    Make a netgen geometry from a gds file.
    :param gds_file:
    :return:
    """
    gdsii = read_gds(gds_file)
    face = list()
    z_lim = (0, 0)
    for polygon in gdsii.cells[0].polygons:
        elevation = polygon.layer
        height = 1
        wp = occ.WorkPlane(occ.Axes((0, 0, elevation), n=occ.Z, h=occ.X))
        pts = polygon.points
        wp.MoveTo(*(pts[0]))
        [wp.LineTo(*pt) for pt in pts[1:]]
        wp.LineTo(*(pts[0]))
        face.append(wp.Face().Extrude(height).mat("metal"))
        z_lim = (min(z_lim[0], elevation), max(z_lim[1], elevation + height))
    metal = occ.Fuse(face)
    # append z to 2D bounding box
    limit = [(xy[0], z) for xy, z in zip(gdsii.cells[0].bounding_box(), z_lim)]
    oxyde = occ.Box(*limit).mat("air") - metal
    oxyde.bc("air")
    return occ.OCCGeometry(occ.Glue([metal, oxyde]))


def compute(geom: NGGeom, *, debug: bool = False):
    mu0 = pi * 4e-7  # H/m
    c0 = 299792458  # m/s
    mesh = ng.Mesh(geom.GenerateMesh())
    if debug:
        ng.Draw(mesh)
    fes = ng.HCurl(mesh, order=3, dirichlet="air", nograds=True)
    u, v = fes.TnT()
    gfu = ng.GridFunction(fes)
    mur = ng.CoefficientFunction(
        [1000 if mat == "metal" else 1 for mat in mesh.GetMaterials()]
    )
    a = ng.BilinearForm(fes)
    a += ng.SymbolicBFI(
        1 / (mu0 * mur) * ng.curl(u) * ng.curl(v) + 1e-8 / (mu0 * mur) * u * v
    )
    c = ng.Preconditioner(a, "bddc")
    f = ng.LinearForm(fes)
    mag = ng.CoefficientFunction((1, 0, 0)) * ng.CoefficientFunction(
        [1 if mat == "metal" else 0 for mat in mesh.GetMaterials()]
    )
    f += ng.SymbolicLFI(mag * ng.curl(v), definedon=mesh.Materials("metal"))
    with ng.TaskManager():
        a.Assemble()
        f.Assemble()
        ng.solvers.CG(sol=gfu.vec, rhs=f.vec, mat=a.mat, pre=c.mat)
    if debug:
        ng.Draw(ng.curl(gfu), mesh, "B-field", draw_surf=False)
    return gfu.vec


geom = make_geometry(Path("./tests/test_layouts/ref_ind.gds"))
res = compute(geom, debug=True)
# plt.plot(res)
# plt.show()
print("hello")
