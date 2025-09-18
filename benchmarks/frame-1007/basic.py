import sys
import veux
import xara
import numpy as np
import matplotlib.pyplot as plt
from shps.rotor import exp


def create_prism(length:    float,
                 element:   str,
                 section:   dict,
                 boundary:  tuple,
                 orient: tuple  = (0, 1, 1),
             #   orient = (0,  -1, 0)
                 geometry:  str = None,
                 transform: str = None,
                 divisions: int = 1,
                 rotation = None):

    L  = length

    # Number of elements discretizing the column
    ne = divisions

    elem_type  = element
    geom_type  = transform

    nn = ne + 1

    model = xara.Model(ndm=3, ndf=6)

    for i in range(1, nn+1):
        x = (i-1)/float(ne)*L
        location = (x, x/15, -x/15)

        if rotation is not None:
            location = tuple(rotation@location)

        model.node(i, location)

#       model.mass(i, *[1.0]*model.getNDF())


    # Define boundary conditions
    model.fix( 1, boundary[0])
    model.fix(nn, boundary[1])

    #
    # Define cross-section 
    #
    sec_tag = 1
    properties = []
    for k,v in section.items():
        properties.append("-" + k)
        properties.append(v)

    model.section("FrameElastic", sec_tag, *properties)

    # Define geometric transformation
    geo_tag = 1

    if rotation is not None:
        orient = tuple(map(float, rotation@orient))

    model.geomTransf(geom_type, geo_tag, *orient)

    # Define elements
    for i in range(1, ne+1):
        if geometry is None or geometry == "Linear" or "Exact" in elem_type:
            model.element(elem_type, i, (i, i+1),
                        section=sec_tag,
                        shear=1,
                        transform=geo_tag)
        else:
            model.element(elem_type, i, (i, i+1),
                        section=sec_tag,
                        order={"Linear": 0, "delta": 1}[geometry],
                        transform=geo_tag)

    return model


def analyze_moment(element, transform, steps=1, ne=5):


    E  = 1000
    I  = 200.0
    length = 5e9
    model = create_prism(
        length = length,
        element = element,
        section = dict(
            E   = E,
            G   = E/2.0,
            A   = 20.0,
            J   = 21.0,
            Iy  = I,
            Iz  = I,
            Ay  = 2.0,
            Az  = 2.0),
        boundary = ((1,1,1,  1,1,1),
                    (0,0,0,  0,0,0)),
        rotation = exp([0., -0.1, 0.000]),
        transform = transform,
        divisions = ne
    )

    for node in model.getNodeTags():
        model.nodeRotation(node)


    model.pattern("Plain", 1, "Linear", load={
        ne+1: [0, 0, 0] + [0, 0, 0]}
    )
    model.system("BandGen")
    model.test("EnergyIncr", 1e-10, 20, 1)
    model.integrator("LoadControl", 1)
    model.analysis("Static")


    u = []
    for i in range(steps):
        if model.analyze(1) != 0:
            break
            raise RuntimeError(f"Failed at step {i}")

        u.append(np.linalg.norm(model.nodeDisp(ne+1))/length)


    return model,u


if __name__ == "__main__":
    import veux
    m,u = analyze_moment(steps=1000,
                       ne=10,
                       transform="Corotational",
                       element="ForceFrame")
    
    for node in m.getNodeTags():
        print(f"Node {node}: {np.linalg.norm(m.nodeDisp(node))}")

    print(m.getTime())
    plt.plot(u)
    plt.show()
    # a = veux.create_artist(m)
    # a.draw_outlines()
    # a.draw_outlines(state=m.nodeDisp)
    # veux.serve(a)

