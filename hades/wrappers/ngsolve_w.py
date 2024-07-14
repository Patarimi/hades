from netgen import csg
from ngsolve import *
from ngsolve.webgui import Draw


def make_geometry():
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


geo = make_geometry()
mesh = Mesh(geo.GenerateMesh(maxh=0.5))
mesh.Curve(5)
Draw(mesh, clipping = { "pnt" : (0,0,0), "vec" : (0,1,0) })

fes = HCurl(mesh, order=4, dirichlet="outer", nograds=True)
print("ndof =", fes.ndof)
u, v = fes.TnT()

mur = {"core": 1000, "coil": 1, "air": 1}
mu0 = 1.257e-6
nu_coef = [1 / (mu0 * mur[mat]) for mat in mesh.GetMaterials()]

nu = CoefficientFunction(nu_coef)
a = BilinearForm(fes, symmetric=True)
a += nu * curl(u) * curl(v) * dx + 1e-6 * nu * u * v * dx

c = Preconditioner(a, type="bddc")

f = LinearForm(fes)
f += CoefficientFunction((y, 0.05 - x, 0)) * v * dx("coil")

u = GridFunction(fes)

a.Assemble()
f.Assemble()
solver = CGSolver(mat=a.mat, pre=c.mat)
u.vec.data = solver * f.vec

Draw(
    curl(u),
    mesh,
    "B-field",
    draw_surf=False,
    clipping={"pnt": (0, 0, 0), "vec": (0, 1, 0), "function": True},
    vectors={"grid_size": 10},
)
