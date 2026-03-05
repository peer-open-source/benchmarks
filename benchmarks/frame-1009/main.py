#
# An example demonstrating spurious straining/displacement in the
# corotational formulation of OpenSees.
#
# A cantilever is oriented arbitrarily in space and discretized by
# 3 finite elements. An empty nodal load is applied at the tip
# and 200 steps of displacement control are performed.
#
# To install the script dependencies run the following in 
# an isolated virtual environment:
# 
# python -m pip install -U xara veux opensees openseespy numpy matplotlib
#
# The only constraint on the Python version is that imposed for
# openseespy.
#
import veux
import xara
import numpy as np

import matplotlib.pyplot as plt
from veux.motion import Motion


def create_prism(length:    float,
                 element:   str,
                 section:   dict,
                 boundary:  tuple,
                 orient:    tuple  = (0, 1, 1),
                 transform: str = None,
                 divisions: int = 1,
                 rotation = None):

    L  = length

    # Number of elements discretizing the column
    ne = divisions

    nn = ne + 1

    model = xara.Model(ndm=3, ndf=6)

    for i in range(1, nn+1):
        x = (i-1)/float(ne)*L
        location = (x, x/15, -x/15)

        if rotation is not None:
            location = tuple(rotation@location)

        model.node(i, location)


    # Define boundary conditions
    model.fix( 1, boundary[0])
    model.fix(nn, boundary[1])

    #
    # Define cross-section 
    #

    model.section("FrameElastic", 1, **section)

    # Define geometric transformation
    geo_tag = 1

    if rotation is not None:
        orient = tuple(map(float, rotation@orient))

    model.geomTransf(transform, 1, *orient)


    # Define elements
    for i in range(1, ne+1):
        model.element(element, i, (i, i+1),
                    section=1,
                    shear=1,
                    transform=1)


    model.pattern("Plain", 1, "Linear", load={
        ne+1: [0, 0, 0,   0, 0, 0]
    })
    return model


def analyze_moment(model, steps=1):
    tip = model.getNodeTags()[-1]
    model.system("BandGen")
    model.test("EnergyIncr", 1e-10, 10, 0)
    model.integrator("DisplacementControl", tip, 2, 0.1)
    model.analysis("Static")


    artist = veux.create_artist(model, model_config={"extrude_outline": "square"})
    artist.draw_axes()
    artist.draw_outlines()
    motion = Motion(artist)

    u = []
    for i in range(steps):

        if model.analyze(1) != 0:
            break

        motion.draw_sections(position=model.nodeDisp,
                             rotation=getattr(model, "nodeRotation", lambda i:  [0,0,0,1]))
        
        motion.advance(time=i/10)
        u.append(np.linalg.norm(model.nodeDisp(tip)[:3])/length)

    motion.add_to(artist.canvas)
    return model,u,artist


if __name__ == "__main__":

    E  = 10000
    I  = 200.0
    length = 100

    fig, ax = plt.subplots()


    model = create_prism(
        length = length,
        section = dict(
            E   = E,
            G   = E/2.0,
            A   = 20.0,
            J   = 20.0,
            Iy  = I,
            Iz  = I,
            Ay  = 20.0,
            Az  = 20.0),
        boundary = ((1,1,1,  1,1,1),
                    (0,0,0,  0,0,0)),
        divisions=3,
        transform="Corotational",
        element="PrismFrame"
    )

    m,u,artist = analyze_moment(model, steps=200)

    for node in m.getNodeTags():
        print(f"Node {node}: {np.linalg.norm(m.nodeDisp(node))} ({m.nodeDisp(node)})")


    ax.plot(u,'.')

    print("Done")

    model = create_prism(
        length = length,
        section = dict(
            E   = E,
            G   = E/2.0,
            A   = 20.0,
            J   = 20.0,
            Iy  = I,
            Iz  = I,
            Ay  = 20.0,
            Az  = 20.0),
        boundary = ((1,1,1,  1,1,1),
                    (0,0,0,  0,0,0)),
        divisions=3,
        transform="Corotational04",
        element="PrismFrame"
    )

    m,u,_ = analyze_moment(model, steps=200)

    for node in m.getNodeTags():
        print(f"Node {node}: {np.linalg.norm(m.nodeDisp(node))} ({m.nodeDisp(node)})")


    ax.plot(u,'.')
    # plt.show()
    # veux.serve(artist)
