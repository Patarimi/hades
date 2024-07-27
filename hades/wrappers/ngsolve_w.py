from pathlib import Path
from gdstk import read_gds
from netgen import csg
from ngsolve import Mesh, Draw


def make_geometry(gds_file: Path) -> csg.CSGeometry:
    """
    Make a netgen geometry from a gds file.
    :param gds_file:
    :return:
    """
    gdsii = read_gds(gds_file)
    geometry = csg.CSGeometry()
    base = csg.Plane(csg.Pnt(0, 0, 0), csg.Vec(0, 0, 1))
    for polygon in gdsii.cells[0].polygons:
        poly = csg.SplineSurface(base)
        previous_point = None
        first_point = None
        for point in polygon.points:
            ng_point = poly.AddPoint(point[0], point[1], 0)
            if previous_point is not None:
                poly.AddSegment(previous_point, ng_point)
            else:
                first_point = ng_point
            previous_point = ng_point
        poly.AddSegment(previous_point, first_point)
        geometry.AddSplineSurface(poly)
    return geometry


def compute():
    ngmesh = make_geometry().GenerateMesh(maxh=0.5)
    ngmesh.Save("coil.vol")
    mesh = Mesh(ngmesh)

    # curve elements for geometry approximation
    mesh.Curve(5)


if __name__ == "__main__":
    geom = make_geometry(Path("./tests/test_layouts/ref_cpl.gds"))
    ngmesh = geom.GenerateMesh(maxh=0.2)
    ngmesh.Save("test.vol")
    mesh = Mesh(ngmesh)
    geom.Draw()
    Draw(mesh)
