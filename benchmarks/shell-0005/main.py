#!/usr/bin/env python
"""
Plate with rectangular cut-out, line load on the inner top edge.

Geometry:
  Plate     500 x 300 mm
  Cut-out   250 x 180 mm, centred (corners at (125, 60) and (375, 240))
  Thickness 20 mm
Material:
  E = 200 000 N/mm^2,  nu = 0.25
BCs:
  Left edge  (x = 0)   clamped, all 6 DOFs
  Top edge   (y = 300) clamped, all 6 DOFs
  Right and bottom edges free
Load:
  1 kN/mm directed along -z on the inner top edge of the cut-out (y = 240,
  125 <= x <= 375).
Quantity of interest:
  Transverse deflection w at point A = (375, 60), the bottom-right hole corner.
"""

import argparse

import xara
from xara.helpers import find_node
from xara.load import Line, SurfaceLoad


# Geometry (mm)
W,    H    = 500.0, 300.0
HX0,  HX1  = 125.0, 375.0
HY0,  HY1  =  60.0, 240.0
THICKNESS  =  20.0

# Material
E_MOD = 200_000.0   # N/mm^2
NU    = 0.25

# Load
Q_LINE = -1000.0    # N/mm along -z


# 8-block decomposition of the plate, leaving the centred hole empty.
# Naming: row letter (B=bottom, M=middle, T=top) then column letter (L, M, R).
_BLOCKS = {
    "BL": [(0.0,  0.0), (HX0,  0.0), (HX0,  HY0), (0.0,  HY0)],
    "BM": [(HX0,  0.0), (HX1,  0.0), (HX1,  HY0), (HX0,  HY0)],
    "BR": [(HX1,  0.0), (W,    0.0), (W,    HY0), (HX1,  HY0)],
    "ML": [(0.0,  HY0), (HX0,  HY0), (HX0,  HY1), (0.0,  HY1)],
    "MR": [(HX1,  HY0), (W,    HY0), (W,    HY1), (HX1,  HY1)],
    "TL": [(0.0,  HY1), (HX0,  HY1), (HX0,  H  ), (0.0,  H  )],
    "TM": [(HX0,  HY1), (HX1,  HY1), (HX1,  H  ), (HX0,  H  )],
    "TR": [(HX1,  HY1), (W,    HY1), (W,    H  ), (HX1,  H  )],
}

_COLUMN_WIDTHS = {"L": HX0,       "M": HX1 - HX0, "R": W   - HX1}
_ROW_HEIGHTS   = {"B": HY0,       "M": HY1 - HY0, "T": H   - HY1}


def _divs(name, h):
    """
    Return element counts (nx, ny) for a block, targeting edge length h.
    """
    row, col = name[0], name[1]
    nx = max(1, round(_COLUMN_WIDTHS[col] / h))
    ny = max(1, round(_ROW_HEIGHTS[row]   / h))
    return nx, ny


def _surface_points(corners):
    """4 corner tuples -> xara surface points dict, padded to z = 0."""
    return {i + 1: [float(p[0]), float(p[1]), 0.0] for i, p in enumerate(corners)}


def build_model(element, order, h):
    model = xara.Model(ndm=3, ndf=6)


    #
    # Material and section
    #
    mat = xara.TriaxialMaterial("ElasticIsotropic", E=E_MOD, nu=NU)
    model.material(mat)

    sec = xara.ShellSection("Elastic", mat, THICKNESS)
    model.section(sec)

    #
    # Mesh each block
    #
    # xara reuses nodes at coincident block corners.
    for name, corners in _BLOCKS.items():
        model.surface(
            _divs(name, h),
            element=element,
            args={"section": sec},
            order=order,
            points=_surface_points(corners),
        )

    #
    # Boundary
    #

    # Clamp the left (x = 0) and top (y = H) outer edges
    tol = 1e-6
    for tag in model.getNodeTags():
        x, y, _ = model.nodeCoord(tag)
        if abs(x) < tol or abs(y - H) < tol:
            model.fix(tag, (1, 1, 1, 1, 1, 1))

    if "plate" in element.lower():
        for tag in model.getNodeTags():
            # fix drill
            try:
                model.fix(tag, (0, 0, 0, 0, 0, 1))
            except:
                pass

    #
    # Loading
    #

    # collect nodes on the inner top edge of the cut-out: 
    #   y = HY1,   HX0 <= x <= HX1
    edge_nodes = [
        tag for tag in model.getNodeTags()
        if abs(model.nodeCoord(tag)[1] - HY1) < tol
        and HX0 - tol <= model.nodeCoord(tag)[0] <= HX1 + tol
    ]
    # Sort by x-coordinate to ensure consistent load application direction
    edge_nodes.sort(key=lambda n: model.nodeCoord(n)[0])

    def q(*_):
        return [0.0, 0.0, Q_LINE]

    load = SurfaceLoad(Line(model, edge_nodes), q)
    model.pattern(xara.StaticPattern([load]))
    return model


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("-e", "--element", default="ASDShellQ4",
                        choices=["ASDShellQ4", "ShellMITC4", "HeterosisPlate", "ShellMITC9"],
                        help="shell element name (default: ASDShellQ4)")
    parser.add_argument("--order", type=int, default=1, choices=(1, 2),
                        help="mesh order, 1 for Q4 or 2 for Q9 (default: 1)")
    parser.add_argument("--h", type=float, default=25.0,
                        help="target element edge length in mm (default: 25)")
    args = parser.parse_args()

    model = build_model(args.element, args.order, args.h)
    print(f"  Element: {args.element}")
    print(f"  {len(model.getNodeTags())} nodes")
    analysis = xara.StaticAnalysis(model, system="Umfpack")
    print(analysis)
    analysis.analyze()

    a_tag   = find_node(model, x=HX1, y=HY0)
    w_a     = model.nodeDisp(a_tag)[2]

    print(f"  w at point A     = {w_a:.6e} mm")

    import veux
    veux.serve(veux.render(model))


if __name__ == "__main__":
    main()

