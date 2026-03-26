import xara
import sys
import veux
import numpy as np
from xsection.library import HollowRectangle
from xsection.analysis import SaintVenantSectionAnalysis
from shps.frame.extrude import ExtrudeHexahedron
from shps import plane
from shps.block import create_block
from xara.post import NodalStress
import matplotlib.pyplot as plt
from xsection._benchmarks import load_shape

def tube_section(d,b,tf,tw,    
                    nw  = 2,
                    nf  = 3,
                    nh  = 18,
                    nb  = 8,
                 order=1):
    # d = 24      # depth
    # b = 20      # width
    # tf = 4      # flange thickness
    # tw = 2      # web thickness
    h = d-2*tf  # Hole height
    w = b-2*tw  # Hole width


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


def analyze_rotation(s, shape, material, rotation: float, case="b"):
    d  = shape.d     # depth
    b  = shape.b     # width
    tf = shape.tf    # flange thickness
    tw = shape.tw    # web thickness
    L = d * s

    nw  = 2
    nf  = 3
    nh  = 19
    nb  = 17

    nodes, cells = tube_section(
        d=d, 
        b=b, 
        tf=tf, 
        tw=tw, 
        nw=nw,
        nf=nf,
        nh=nh,
        nb=nb,
        order=1)
    nodes = np.vstack(list(nodes.values()))
    cells = np.vstack(list(cells.values())) - 1

    ex = ExtrudeHexahedron((nodes, cells))

    model = xara.Model(ndm=3, ndf=3)
    model.material(material, 1)
    model.pattern("Plain", 1, "Linear")

    # n = 70  # number of divisions along the length

    dy_avg = d / (nf+nh) 
    
    # Width is split into (nw + nb + nw) = 16 elements
    dx_avg = b / (2*nw + nb)
    
    # Target element size in the Z direction
    h_2d = (dx_avg + dy_avg) / 2.0 
    
    # Calculate n to make dz = L/n roughly equal to h_2d
    # Ensure a minimum of 1 division
    n = max(1, int(round(L / h_2d)))


    end_nodes = {}
    for i in range(n):
        for tag, coords in ex.nodes():
            coords = np.array([coords[0] - b / 2, coords[1] - d / 2, coords[2]])
            x, y, z = coords

            model.node(tag, tuple(coords))

            if i == 0 and z == 0:
                model.fix(tag, (1, 1, 1))

            elif abs(z-L) < 1e-6: # i == n - 1:
            # elif i == n - 1:
                # Impose rigid rotation of the end cross-section about the z-axis.
                # ux = cs * x - sn * y - x
                # uy = sn * x + cs * y - y
                ux = -rotation * y
                uy =  rotation * x

                model.sp(tag, 1, ux, pattern=1)
                model.sp(tag, 2, uy, pattern=1)

                if case == "c":
                    # Fix axial warping in case 3
                    model.fix(tag, dof=3)
                end_nodes[tag] = (coords, (ux, uy, 0.0))
    
        element = "bbarBrick" #"H8E12"# "SSPbrick" #"stdBrick" # 
        for tag, cell in ex.cells():
            model.element(element, tag, tuple(cell), 1)

        ex.advance([0, 0, L / n])


    # Use a load factor ramp from 0 to 1 so the prescribed displacements
    # reach exactly the values above at the end of the analysis.
    steps = 500 #300
    dU = 1/steps
    dUmin = dU/8 #100
    dUmax = dU*1.3#*2
    model.integrator("LoadControl", dU, 
                      min_step=dUmin, max_step=dUmax, 
                      iter=2, 
                      exponent=2
    )
    model.system("mumps", symmetric=1)
    model.numberer("RCM")
    model.test("Energy", 1e-14, 15, 1)
    model.constraints("Transformation")
    model.analysis("Static")
    u = []
    T = []
    failures = 0
    rescale = 2/3
    while model.state.time < 1.0:
        try:
            if model.analyze(1) != 0:
                if failures > 5:
                    raise RuntimeError("Analysis failed to converge")
                print(f"Failed at time = {model.getTime():.4f}, rescaling step by {rescale}")
                failures += 1
                model.integrator("LoadControl", rescale**failures/steps)
                continue
        except KeyboardInterrupt:
            break

        torque = 0.0
        model.reactions()
        for tag, (coords, disp) in end_nodes.items():
            F = model.nodeReaction(tag)
            torque += np.cross(coords, F)[2]
        u.append(model.state.time*rotation)
        T.append(torque)
        print(model.state.time, torque)


    return model, (u, T)


def draw_model(model):
    artist = veux.create_artist(model, ndf=3)
    artist.draw_origin(extrude=True, size=10)
    return artist

if __name__ == "__main__":
    Save = True
    shape_name = "H03"
    s = 2 #1.4
    if len(sys.argv) > 1:
        shape_name = sys.argv[1]
    if len(sys.argv) > 2:
        s = float(sys.argv[2])
    # b = 20
    # d = 20
    case = "c"
    if len(sys.argv) > 3:
        case = sys.argv[3]

    material = xara.Material(
        "NonlinearJ2", #"J2", #"J2Simplified",
        E=29e3, 
        nu=0.27,
        Fy=60,
        Fsat=60,
        Hiso=0.03*29e3,
        # Hsat=1,
        tol=1e-14
    )
    shape = load_shape(shape_name, material=material)

    model, (u,T) = analyze_rotation(s, shape, material, rotation=0.15, case=case)

    a_model = draw_model(model)
    if Save:
        a_model.save(f"out/solid_{shape_name}_{int(s)}_{case}.glb")


    if Save:
        np.savetxt(f"out/solid_{shape_name}_{int(s)}_{case}.txt", np.column_stack((u, T)), header="u T")


    plt.plot(u, T, marker="o", markersize=3)
    plt.show()


    artist = veux.create_artist(model, ndf=3)
    artist.draw_origin(scale=10)
    artist.draw_outlines(state=model.nodeDisp)
    artist.draw_surfaces(state=model.nodeDisp, field=NodalStress(model, "svm"))
    veux.serve(artist)
