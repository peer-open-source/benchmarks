import sys
import veux
import xara
import numpy as np
import matplotlib.pyplot as plt


def create_prism(length:    float,
                 element:   str,
                 section:   dict,
                 boundary:  tuple,
                 orient: tuple  = (0, 0, 1),
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
        location = (x, 0.0, 0.0)

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


def analyze_moment(element, transform, scale=1/8, steps=1, ne=5):

    E  = 1.0
    I  = 2.0
    length = 1.0
    model = create_prism(
        length = length,
        element = element,
        section = dict(
            E   = E,
            G   = 1.0,
            A   = 2.0,
            J   = 2.0,
            Iy  = I,
            Iz  = I,
            Ay  = 2.0,
            Az  = 2.0),
        boundary = ((1,1,1,  1,1,1),
                    (0,0,0,  0,0,0)),
        transform = transform,
        divisions = ne
    )

    for node in model.getNodeTags():
        model.nodeRotation(node)

    model.test("EnergyIncr", 1e-7, 100, 1)

    model.pattern("Plain", 1, "Linear", load={
        ne+1: [0, 0, 0] + [0, 0, -1]}
    )

    model.integrator("LoadControl", 2*np.pi*(E*I/length)*scale/steps)
    model.analysis("Static")


    for i in range(steps):
        if model.analyze(1) != 0:
            break
            raise RuntimeError(f"Failed at step {i}")


    return model


if __name__ == "__main__":
    import veux
    m = analyze_moment(scale=1.1,
                       steps= 40,
                       ne=8,
                       transform="Corotational02",
                       element="PrismFrame")
    a = veux.create_artist(m)
    a.draw_outlines()
    a.draw_outlines(state=m.nodeDisp)
    veux.serve(a)

