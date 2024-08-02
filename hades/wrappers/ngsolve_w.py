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
    for polygon in gdsii.cells[0].polygons:
        elevation = polygon.layer
        height = 1
        wp = occ.WorkPlane(occ.Axes((0, 0, elevation), n=occ.Z, h=occ.X))
        pts = polygon.points
        wp.MoveTo(*(pts[0]))
        [wp.LineTo(*pt) for pt in pts[1:]]
        wp.LineTo(*(pts[0]))
        face.append(wp.Face().Extrude(height).mat("metal"))
    metal = occ.Fuse(face)
    # append z to 2D bounding box
    limit = metal.bounding_box
    lim_margin = [tuple([(1-sign(lim)*margin)*lim for lim in limit[0]]),
                  tuple([(1+sign(lim)*margin)*lim for lim in limit[1]])]
    oxyde = occ.Box(*lim_margin).mat("oxyde") - metal
    oxyde.bc("oxyde")
    print(oxyde.Properties.__dir__())
    return occ.OCCGeometry(occ.Compound([metal, oxyde]))


def compute(geom: NGGeom, *, debug: bool = False):
    # permeability
    mu0 = pi * 4e-7  # H/m
    # permittivity
    eps0 = 8.854e-12 # F/m
    # relative permittivity
    epsr = {"metal": 1, "oxyde": 4, "default": 1}
    # conductivity
    rho = {"metal": 10e3, "oxyde": 1e-6, "default": 1e-6}
    mesh = ng.Mesh(geom.GenerateMesh())
    if debug:
        ng.Draw(mesh)
    fes = ng.HCurl(mesh, order=3, dirichlet="air")

    u, v = fes.TnT()
    gfu = ng.GridFunction(fes)
    eps_coeff = ng.CoefficientFunction([eps0*epsr[mat] for mat in mesh.GetMaterials()])
    # Magnetic vector potential
    a_vec = ng.BilinearForm(fes)
    a_vec += ng.SymbolicBFI(
        1 / mu0 * ng.curl(u) * ng.curl(v) + 1e-8 / mu0 * u * v
    )
    # Scalar Potential
    v_scal = ng.BilinearForm(fes)
    v_scal += ng.SymbolicBFI(

    )
    # TODO add initial condition
    c = ng.Preconditioner(a_vec, "bddc")
    f = ng.LinearForm(fes)
    mag = ng.CoefficientFunction((1, 0, 0)) * ng.CoefficientFunction(
        [1 if mat == "metal" else 0 for mat in mesh.GetMaterials()]
    )
    f += ng.SymbolicLFI(mag * ng.curl(v), definedon=mesh.Materials("metal"))
    with ng.TaskManager():
        a_vec.Assemble()
        v_scal.Assemble()
        f.Assemble()
        ng.solvers.CG(sol=gfu.vec, rhs=f.vec, mat=a_vec.mat, pre=c.mat)
    if debug:
        ng.Draw(ng.curl(gfu), mesh, "B-field", draw_surf=False)
    return gfu.vec


geom = make_geometry(Path("./tests/test_layouts/ref_ind.gds"))
res = compute(geom, debug=True)
# plt.plot(res)
# plt.show()
