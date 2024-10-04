from pathlib import Path
from gdstk import read_gds
from netgen import csg, occ
import ngsolve as ng
from hades.layouts.tools import LayerStack
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
    for port in gdsii.cells[0].labels:
        port_face = metal.faces.Nearest(occ.gp_Pnt(*port.origin, port.layer + 0.5))
        port_face.name = "port" + port.text
        print(port_face.bounding_box)
    # append z to 2D bounding box
    limit = metal.bounding_box
    lim_margin = [
        tuple([(1 - sign(lim) * margin) * lim for lim in limit[0]]),
        tuple([(1 + sign(lim) * margin) * lim for lim in limit[1]]),
    ]
    oxide = occ.Box(*lim_margin).mat("oxide")
    oxide.faces.name = "oxide"
    oxide.solids.name = "oxide"
    # change color of oxide faces
    oxide.faces.col = (0, 0, 1, 0.3)
    oxide.bc("oxide")
    return occ.OCCGeometry(occ.Glue([metal, oxide - metal]))


def write_stl(gds_file: Path, stack: LayerStack, stl_file: Path = Path("./model.stl")) -> None:
    """
    Write a stl file from a gds file.
    :param gds_file: Input file to be simulated
    :param stack: Layer Stack use to construct the 3D model
    :param stl_file: Output file
    :return: None
    """
    geom = make_geometry(gds_file, stack)
    mesh = geom.GenerateMesh()
    mesh.Export(str(stl_file), format="STL Format")


def compute(geom: NGGeom, freq: float = 1e9, *, debug: bool = False):
    """
    [WIP] Help Needed.
    Compute the EM fields of a geometry.
    :param geom:
    :param freq:
    :param debug:
    :return: Z-parameters of the structure.
    """
    # permeability
    mu0 = pi * 4e-7  # H/m
    # permittivity
    # eps0 = 8.854e-12  # F/m
    # relative permittivity
    # epsr = {"metal": 1, "oxide": 4, "default": 1}
    # conductivity
    sigma = {"metal": 1e6, "oxide": 1e-6, "default": 1e-6}
    # frequency
    omega = 2 * pi * freq
    mesh = ng.Mesh(geom.GenerateMesh())
    if debug:
        ng.Draw(mesh)
    fes = ng.HCurl(mesh, order=3, dirichlet="oxide|default", complex=True)
    u, v = fes.TnT()

    # Set conductivity in the mesh
    sigma_coeff = ng.CoefficientFunction([sigma[mat] for mat in mesh.GetMaterials()])

    # Magnetic vector potential
    # see https://www.nic.funet.fi/index/elmer/doc/ElmerModelsManual.pdf (p144)
    # see https://youtu.be/jDvbnaJqkZY?si=fF6g0qdabd4LvxgT&t=777
    # $\Delta \vec{A} + \omega ^2 \mu \epsilon_0 \epsilon_r \vec{A} = -\mu \vec{J}$
    # $\Delta V + \omega ^2 \mu \epsilon_0 \epsilon_r V = -\frac \rho \epsilon$
    a_vec = ng.BilinearForm(fes, symmetric=True, condense=True)
    a_vec += 1 / mu0 * ng.curl(u) * ng.curl(v) * ng.dx
    a_vec += 1j * omega * sigma_coeff * u * v * ng.dx

    # Boundary current density
    def project(val, min_val, max_val):
        return ng.IfPos(val - min_val, ng.IfPos(val - max_val, val, max_val), min_val)

    projy = project(ng.y, 7.5, 12.5)
    projz = project(ng.z, 81, 82)

    # pot along y and tau along x ?
    pot = ng.CF((projz, 0, 0))
    tau = ng.CF((projy, 0, 0))
    f = ng.LinearForm(
        -tau * v.Trace() * ng.ds("port*", bonus_intorder=4)
        + pot / 0.025 * ng.curl(v) * ng.dx("port*", bonus_intorder=4)
    )

    gfu = ng.GridFunction(fes)
    c = ng.Preconditioner(a_vec, "bddc")
    mag = ng.CoefficientFunction((1, 0, 0)) * ng.CoefficientFunction(
        [1 if mat == "metal" else 0 for mat in mesh.GetMaterials()]
    )
    f += ng.SymbolicLFI(mag * ng.curl(v), definedon=mesh.Materials("metal"))
    with ng.TaskManager():
        a_vec.Assemble()
        f.Assemble()
        ng.solvers.CG(sol=gfu.vec, rhs=f.vec, mat=a_vec.mat, pre=c.mat)
    if debug:
        ng.Draw(ng.curl(gfu), mesh, "B-field", draw_surf=False)
    return gfu.vec
