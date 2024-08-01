from pathlib import Path
from gdstk import read_gds
from netgen import csg, occ
import ngsolve as ng
from hades.layouts.tools import LayerStack
import matplotlib.pyplot as plt
from math import pi
from numpy import sign


NGGeom = csg.CSGeometry | occ.OCCGeometry


def make_geometry(gds_file: Path, stack: LayerStack = None, *, margin=0.1) -> NGGeom:
    """
    Make a netgen geometry from a gds file.
    :param gds_file: Input file to be simulated
    :param stack: Layer Stack use to construct the 3D model
    :param margin: (Default = 0.1) Size of air box around the model in percent.
    :return: A geometry that can be used by ngsolve
    """
    gdsii = read_gds(gds_file)
    face = list()
    z_lim = None
    for polygon in gdsii.cells[0].polygons:
        elevation = polygon.layer
        height = 1
        wp = occ.WorkPlane(occ.Axes((0, 0, elevation), n=occ.Z, h=occ.X))
        pts = polygon.points
        wp.MoveTo(*(pts[0]))
        [wp.LineTo(*pt) for pt in pts[1:]]
        wp.LineTo(*(pts[0]))
        face.append(wp.Face().Extrude(height).mat("metal"))
        z_lim = (elevation, elevation+height) if z_lim is None else (min(z_lim[0], elevation), max(z_lim[1], elevation + height))
    metal = occ.Fuse(face)
    # append z to 2D bounding box
    limit = [(*xy, z) for xy, z in zip(gdsii.cells[0].bounding_box(), z_lim)]
    lim_margin = [tuple([(1-sign(lim)*margin)*lim for lim in limit[0]]),
                  tuple([(1+sign(lim)*margin)*lim for lim in limit[1]])]
    oxyde = occ.Box(*lim_margin).mat("oxyde") - metal
    oxyde.bc("oxyde")
    return occ.OCCGeometry(occ.Glue([metal, oxyde]))


def compute(geom: NGGeom, *, debug: bool = False):
    mu0 = pi * 4e-7  # H/m
    eps0 = 8.854e-12 # F/m
    epsr = {"metal": 1, "oxyde": 4, "default": 1}
    mesh = ng.Mesh(geom.GenerateMesh())
    if debug:
        ng.Draw(mesh)
    fes = ng.HCurl(mesh, order=3, dirichlet="air")
    u, v = fes.TnT()
    gfu = ng.GridFunction(fes)
    eps_coeff = ng.CoefficientFunction([eps0*epsr[mat] for mat in mesh.GetMaterials()])
    mu_coeff = ng.CoefficientFunction([mu0 for _ in mesh.GetMaterials()])
    a = ng.BilinearForm(fes)
    a += ng.SymbolicBFI(
        1 / mu_coeff * ng.curl(u) * ng.curl(v) + 1e-8 / mu_coeff * u * v
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
