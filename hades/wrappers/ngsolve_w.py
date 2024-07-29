from pathlib import Path
from gdstk import read_gds
from netgen import csg, occ
from ngsolve import Mesh, Draw


def make_geometry(gds_file: Path) -> csg.CSGeometry:
    """
    Make a netgen geometry from a gds file.
    :param gds_file:
    :return:
    """
    gdsii = read_gds(gds_file)
    face = None
    for polygon in gdsii.cells[0].polygons:
        wp = occ.WorkPlane(occ.Axes((0, 0, polygon.layer), n=occ.Z, h=occ.X))
        pts = polygon.points
        wp.MoveTo(*(pts[0]))
        [wp.LineTo(*pt) for pt in pts[1:]]
        wp.LineTo(*(pts[0]))
        face = wp.Face().Extrude(1) if face is None else face+wp.Face().Extrude(1)
    return occ.OCCGeometry(face)


def compute():
    ngmesh = make_geometry().GenerateMesh(maxh=2)
    ngmesh.Save("coil.vol")
    mesh = Mesh(ngmesh)


geom = make_geometry(Path("./tests/test_layouts/ref_cpl.gds"))
mesh = Mesh(geom.GenerateMesh())
Draw(mesh)
# ngmesh = geom.GenerateMesh(maxh=100)
