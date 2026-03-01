# OpenSees -- Open System for Earthquake Engineering Simulation
#         Pacific Earthquake Engineering Research Center
#
import veux
import xara
import numpy as np
from xara.helpers import find_nodes, find_node
import matplotlib.pyplot as plt

Verbose = False
if Verbose:
    Progress = lambda *args, **kwds: None
else:
    from tqdm import tqdm as Progress


def create_model(L, d, b, tw, tf, linear=True):
    # create ModelBuilder (with three-dimensions and 6 DOF/node)
    model = xara.Model(ndm=3, ndf=6)
    element = "ASDShellQ4" #"ShellNLDKGQ" #,  #"ShellMITC4"  #
    if linear:
        flags = () 
    else:
        flags = ("-corotational",)

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
        nx = 200
        ny = 4

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
    linear=False
    fig, ax = plt.subplots()
    
    for case in [3]:
        model = create_model(L=900, b=10, d=30, tw=1, tf=1.6, linear=linear)
        artist = veux.create_artist(model)
    #   artist.draw_surfaces()
        artist.draw_outlines()

        if case == 1:
            for node in find_nodes(model, x=0):
                model.fix(node, (1,1,1, 1,1,1))
        elif case == 2:
    #       c = find_node(model, x=0,y=0,z=0)
    #       model.fix(c, (1,1,1,  1,1,1))
            for node in find_nodes(model, x=0, y=0):
                model.fix(node, (1,1,1, 1,1,1))
        else:
            model.fix(find_node(model, x=0,y=0.,z= 15), (1,1,1, 1,1,1))
            model.fix(find_node(model, x=0,y=10,z= 15), (1,1,1, 1,1,1))
            model.fix(find_node(model, x=0,y=0.,z=-15), (1,1,1, 1,1,1))
            model.fix(find_node(model, x=0,y=10,z=-15), (1,1,1, 1,1,1))


        tip = find_node(model, x=900,y=0,z=15)
        model.pattern("Plain", 1, "Linear", loads={
            tip: (0,0,-1, 0,0,0)
        })

        if linear:
            model.integrator("LoadControl", 10)
            model.analysis("Static")
            model.analyze(1)
        else:
            Pmax = 10
            u = []
            P = []
            model.system('mumps')
            model.test("Energy", 1e-16, 600, 2 if Verbose else 0)
            model.integrator("LoadControl", 
                             Pmax/400, # 50
                             min_step=Pmax/800,
                             max_step=Pmax/100, # 10
                             iter=300 # 50
            )
            model.analysis("Static")

            pbar = Progress(total=Pmax)
            try:
                while (time := model.getTime()) < Pmax:
                    if model.analyze(1) != 0:
                        break
                    if pbar is not None:
                        pbar.update(model.getTime() - time)
                        pbar.set_postfix(iter=model.numIter())
                    u.append(-model.nodeDisp(tip, 3))
                    P.append( model.getTime())
            except KeyboardInterrupt:
                pass

            ax.plot(u, P, label=f"Case {case}")

            np.savetxt(f"out/frame-0032-case{case}.txt",
                       np.column_stack((u, P)),
                       header="u3 P"
            )


    ax.grid(True)
    ax.legend()

    plt.show()
    artist.draw_surfaces(state=model.nodeDisp)
    veux.serve(artist)


