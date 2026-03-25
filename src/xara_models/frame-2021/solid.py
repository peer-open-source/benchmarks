import xara
import veux
import numpy as np
from xsection.library import HollowRectangle
from xsection.analysis import SaintVenantSectionAnalysis
from shps.frame.extrude import ExtrudeHexahedron
from shps import plane
from shps.block import create_block
from xara.post import NodalStress
import matplotlib.pyplot as plt


def tube_section(d,b,tf,tw, order=1):
    # d = 24      # depth
    # b = 20      # width
    # tf = 4      # flange thickness
    # tw = 2      # web thickness
    h = d-2*tf  # Hole height
    w = b-2*tw  # Hole width

    nw  = 4
    nf  = 4
    nh  = 16
    nb  = 8

    # Define the element type; first-order Lagrange quadrilateral
    element = plane.Lagrange(order)
    points  = {
            1: (    0.0,   0.0),
            2: (b/2-w/2,   0.0),
            3: (b/2-w/2, d/2-h/2),
            4: (    0.0, d/2-h/2),
    }
    nodes, cells = create_block((nw,nf), element, points=points)
#
    points  = {
            1: (b/2+w/2,   0.0),
            2: (   b   ,   0.0),
            3: (   b   , d/2-h/2),
            4: (b/2+w/2, d/2-h/2),
    }
    other = dict(nodes=nodes, cells=cells)
    nodes, cells = create_block((nw,nf), element, points=points, join=other)
#
    points  = {
            1: (b/2+w/2, d/2-h/2),
            2: (   b   , d/2-h/2),
            3: (   b   , d/2+h/2),
            4: (b/2+w/2, d/2+h/2),
    }
    other = dict(nodes=nodes, cells=cells)
    nodes, cells = create_block((nw,nh), element, points=points, join=other)

#
    points  = {
            1: (b/2+w/2, d/2+h/2),
            2: (   b   , d/2+h/2),
            3: (   b   , d    ),
            4: (b/2+w/2, d    ),
    }
    other = dict(nodes=nodes, cells=cells)
    nodes, cells = create_block((nw,nf), element, points=points, join=other)
#
    points  = {
            1: (  0.0  , d/2+h/2),
            2: (b/2-w/2, d/2+h/2),
            3: (b/2-w/2, d      ),
            4: (  0.0  , d      ),
    }
    other = dict(nodes=nodes, cells=cells)
    nodes, cells = create_block((nw,nf), element, points=points, join=other)
#
    points  = {
            1: (  0.0  , d/2-h/2),
            2: (b/2-w/2, d/2-h/2),
            3: (b/2-w/2, d/2+h/2),
            4: (  0.0  , d/2+h/2),
    }
    other = dict(nodes=nodes, cells=cells)
    nodes, cells = create_block((nw,nh), element, points=points, join=other)
#
    points  = {
            1: (b/2-w/2, d/2+h/2),
            2: (b/2+w/2, d/2+h/2),
            3: (b/2+w/2, d      ),
            4: (b/2-w/2, d      ),
    }
    other = dict(nodes=nodes, cells=cells)
    nodes, cells = create_block((nb,nf), element, points=points, join=other)
# 
    points  = {
            1: (b/2-w/2,   0.0),
            2: (b/2+w/2,   0.0),
            3: (b/2+w/2, d/2-h/2),
            4: (b/2-w/2, d/2-h/2),
    }
    other = dict(nodes=nodes, cells=cells)
    nodes, cells = create_block((nb,nf), element, points=points, join=other)
#
    return nodes, cells


def analyze_rotation(shape, material, rotation: float):
    d  = shape.d     # depth
    b  = shape.b     # width
    tf = shape.tf    # flange thickness
    tw = shape.tw    # web thickness
    L = d * 2

    nodes, cells = tube_section(d=d, b=b, tf=tf, tw=tw, order=1)
    nodes = np.vstack(list(nodes.values()))
    cells = np.vstack(list(cells.values())) - 1

    ex = ExtrudeHexahedron((nodes, cells))

    model = xara.Model(ndm=3, ndf=3)
    model.material(material, 1)
    model.pattern("Plain", 1, "Linear")

    n = 70  # number of divisions along the length

    end_nodes = {}

    c = np.cos(rotation)
    s = np.sin(rotation)

    for i in range(n):
        for tag, coords in ex.nodes():
            coords = np.array([coords[0] - b / 2, coords[1] - d / 2, coords[2]])
            x, y, z = coords

            model.node(tag, tuple(coords))

            if i == 0 and z == 0:
                model.fix(tag, (1, 1, 1))

            elif i == n - 1:
                # Impose rigid rotation of the end cross-section about the z-axis.
                ux = c * x - s * y - x
                uy = s * x + c * y - y

                model.sp(tag, 1, ux, pattern=1)
                model.sp(tag, 2, uy, pattern=1)
                # Leave z free so the section can warp axially.
                end_nodes[tag] = (coords, (ux, uy, 0.0))
    
        element = "bbarBrick" #"H8E12"# "SSPbrick" #"stdBrick" # 
        for tag, cell in ex.cells():
            model.element(element, tag, tuple(cell), 1)

        ex.advance([0, 0, L / n])


    # Use a load factor ramp from 0 to 1 so the prescribed displacements
    # reach exactly the values above at the end of the analysis.
    steps = 300 # 400
    dU = 1/steps
    dUmin = dU/8 #100
    dUmax = dU*1.3#*2
    model.integrator("LoadControl", 1.0/steps, 
                      min_step=dUmin, max_step=dUmax, 
                      iter=2, 
                      exponent=2
    )
    model.system("mumps", symmetric=1)
    model.numberer("RCM")
    model.test("Energy", 1e-12, 15, 1)
    model.constraints("Transformation")
    model.analysis("Static")
    u = []
    T = []
    while model.state.time < 1.0:
        try:
            if model.analyze(1) != 0:
                break
                raise RuntimeError("Analysis failed to converge")
        except KeyboardInterrupt:
            break

        torque = 0.0
        model.reactions()
        for tag, (coords, disp) in end_nodes.items():
            F = model.nodeReaction(tag)
            torque += np.cross(coords, F)[2]
        u.append(model.state.time)
        T.append(torque)
        print(model.state.time, torque)
    
    K = torque*L/rotation
    print(f"Applied torque: {torque:.3f}")
    print(f"Stiffness: {K:.3f}")
    GJ = SaintVenantSectionAnalysis(shape).twist_rigidity()
    print(f"Twist rigidity: {GJ:.3f}")

    np.savetxt("out/frame-2021-twist.txt", np.column_stack((u, T)), header="u T")

    plt.plot(u, T, marker="o", markersize=3)
    plt.show()

    artist = veux.create_artist(model, ndf=3)
    artist.draw_origin(scale=10)
    artist.draw_outlines(state=model.nodeDisp)
    artist.draw_surfaces(state=model.nodeDisp, field=NodalStress(model, "svm"))
    veux.serve(artist)

    return model


if __name__ == "__main__":
    b = 10
    d = 2*b
    material = xara.Material(
        "NonlinearJ2", #"J2Simplified",
        E=29e3, 
        nu=0.27,
        Fy=60,
        Fsat=60,
        Hiso=0.01*29e3,
        tol=1e-14
    )
    shape = HollowRectangle(
        d=d, 
        b=b,
        tf=2*0.05*d, 
        tw=0.05*d, 
        material=material
    )

    analyze_rotation(shape, material, rotation=0.04)#(np.pi/3)/80)
