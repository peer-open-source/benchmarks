# OpenSees -- Open System for Earthquake Engineering Simulation
#         Pacific Earthquake Engineering Research Center
#
import veux
import opensees.openseespy as ops
from xara.helpers import find_nodes, find_node


def create_model(L, d, b, tw, tf, linear=True):
    # create ModelBuilder (with three-dimensions and 6 DOF/node)
    model = ops.Model(ndm=3, ndf=6)
    element = "ASDShellQ4" #"ShellNLDKGQ" #,  #"ShellMITC4"  #
    flags = () #"-corotational",)

    E = 2.1e4

    # Define sections
    # ------------------
    #                            tag E   nu    h    rho
    model.section("ElasticShell", 1, E, 0.30, tw, 1.27)
    model.section("ElasticShell", 2, E, 0.30, tf, 1.27)

    # Define geometry
    # ---------------
    # these should both be even
    if linear:
        nx = 50 #240
        ny = 2 #8
    else:
        nx = 50
        ny = 2

    # Flanges
    model.surface((nx, ny),
                  element=element, args=(2, *flags),
                  points={
                      1: [ 0,  0, d/2],
                      2: [ L,  0, d/2],
                      3: [ L,  b, d/2],
                      4: [ 0,  b, d/2],
                  })

    model.surface((nx, ny),
                  element=element, args=(2, *flags),
                  points={
                      1: [ 0,  0, -d/2],
                      2: [ L,  0, -d/2],
                      3: [ L,  b, -d/2],
                      4: [ 0,  b, -d/2],
                  })

    # Web
    model.surface((nx, ny),
                  element=element, args=(1, *flags),
                  points={
                      1: [ 0,  0,  d/2],
                      2: [ L,  0,  d/2],
                      3: [ L,  0, -d/2],
                      4: [ 0,  0, -d/2],
                  })

    return model

if __name__ == "__main__":
    linear=True
    model = create_model(L=900, b=10, d=30, tw=1, tf=1.6, linear=linear)
    artist = veux.create_artist(model)
#   artist.draw_surfaces()
    artist.draw_outlines()

    if False:
        for node in find_nodes(model, x=0):
            model.fix(node, (1,1,1, 1,1,1))
    else:
#       c = find_node(model, x=0,y=0,z=0)
#       model.fix(c, (1,1,1,  1,1,1))
        for node in find_nodes(model, x=0, y=0):
            model.fix(node, (1,1,1, 1,1,1))

    model.pattern("Plain", 1, "Linear", loads={
        find_node(model, x=900,y=0,z=15): (0,0,-1, 0,0,0)
    })

    if linear:
        model.integrator("LoadControl", 10)
        model.analysis("Static")
        model.analyze(1)
    else:
        model.test("NormDispIncr", 1e-8, 20, 1)
        model.integrator("LoadControl", 20/5000)
        model.analysis("Static")
        while model.getTime() < 20:
            if model.analyze(1) != 0:
                break


    artist.draw_surfaces(state=model.nodeDisp)
    veux.serve(artist)


