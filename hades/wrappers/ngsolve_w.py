from pathlib import Path
from netgen import csg
import ngsolve as ng
from ngsolve.webgui import Draw


def make_geometry(input_file: Path, process_file: Path) -> csg.CSGeometry:
    geometry = csg.CSGeometry()
    box = csg.OrthoBrick(csg.Pnt(-1, -1, -1), csg.Pnt(2, 1, 2)).bc("outer")

    core = (
        csg.OrthoBrick(csg.Pnt(0, -0.05, 0), csg.Pnt(0.8, 0.05, 1))
        - csg.OrthoBrick(csg.Pnt(0.1, -1, 0.1), csg.Pnt(0.7, 1, 0.9))
        - csg.OrthoBrick(csg.Pnt(0.5, -1, 0.4), csg.Pnt(1, 1, 0.6))
        .maxh(0.2)
        .mat("core")
    )

    coil = (
        csg.Cylinder(csg.Pnt(0.05, 0, 0), csg.Pnt(0.05, 0, 1), 0.3)
        - csg.Cylinder(csg.Pnt(0.05, 0, 0), csg.Pnt(0.05, 0, 1), 0.15)
    ) * csg.OrthoBrick(csg.Pnt(-1, -1, 0.3), csg.Pnt(1, 1, 0.7)).maxh(0.2).mat("coil")

    geometry.Add((box - core - coil).mat("air"), transparent=True)
    geometry.Add(core, col=(0.5, 0.5, 0))
    geometry.Add(coil, col=(0, 1, 0))
    return geometry


def compute(input_file: Path, output_file: Path = None):
    geo = make_geometry()
    mesh = ng.Mesh(geo.GenerateMesh(maxh=0.5))
    mesh.Curve(5)
    Draw(mesh, clipping={"pnt": (0, 0, 0), "vec": (0, 1, 0)})

    fes = ng.HCurl(mesh, order=4, dirichlet="outer", nograds=True)
    print("ndof =", fes.ndof)
    u, v = fes.TnT()

    mur = {"core": 1000, "coil": 1, "air": 1}
    mu0 = 1.257e-6
    nu_coef = [1 / (mu0 * mur[mat]) for mat in mesh.GetMaterials()]

    nu = ng.CoefficientFunction(nu_coef)
    a = ng.BilinearForm(fes, symmetric=True)
    a += nu * ng.curl(u) * ng.curl(v) * ng.dx + 1e-6 * nu * u * v * ng.dx

    c = ng.Preconditioner(a, type="bddc")

    f = ng.LinearForm(fes)
    f += ng.CoefficientFunction((ng.y, 0.05 - ng.x, 0)) * v * ng.dx("coil")

    u = ng.GridFunction(fes)

    a.Assemble()
    f.Assemble()
    solver = ng.CGSolver(mat=a.mat, pre=c.mat)
    u.vec.data = solver * f.vec

    Draw(
        ng.curl(u),
        mesh,
        "B-field",
        draw_surf=False,
        clipping={"pnt": (0, 0, 0), "vec": (0, 1, 0), "function": True},
        vectors={"grid_size": 10},
    )
